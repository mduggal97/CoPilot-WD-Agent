# GitHub Actions as a CI/CD Alternative (Evaluation + Recipes)

Reference for `app-harness`. The suite's blessed pipeline is AWS CodePipeline +
CodeBuild, with GitHub as the CodePipeline SOURCE only - see the app-hosting
skill, references/cloudformation-pipeline.md.
This file evaluates GitHub Actions as a FULL alternative (CI and deploy, not
just repo checks) and gives working recipes for the parts that differ. It does
not change the blessed stack - read this before choosing Actions for a given
app, not as a default swap-in.

The practice ships from private repos in an enterprise GitHub org; hosting is
AWS App Runner + ECR + RDS Postgres behind private/VPN ingress; IaC is
CloudFormation. Actions replaces the CI/CD ENGINE below, not the AWS
architecture.

Cross-link: git/PR/branch discipline (PR-only landing on `main`, the
branch-guard hook) already lives in [security-hooks.md](security-hooks.md)
Hook 2 and [complexity-routing.md](complexity-routing.md) - not repeated here.

---

## 1. Evaluation - Actions-full-pipeline vs CodePipeline/CodeBuild

Read this before picking a pipeline for a new app. The honest answer is "it
depends on the app," not a flat winner.

**Cost** (verify-current: 2026-09-10). GitHub Actions private-repo minutes:
2,000 free Linux minutes/month on the Free plan (Team 3,000; Enterprise Cloud 50,000), then roughly $0.006/min
Linux, $0.010/min Windows, $0.062/min macOS (a $0.002/min platform fee is
folded into these rates; a matching self-hosted-runner fee was proposed then
withdrawn, so self-hosted minutes stay free). AWS CodeBuild: per-second
billing, ~$0.005/min on `general1.small`, ~100 free minutes/month. AWS
CodePipeline V2: ~$0.002 per action-execution-minute plus a small free
allotment (CodeBuild/CodeDeploy billed separately). At the suite's volumes
neither wins on cost alone; confirm the org's actual GitHub plan tier before
treating this as decided.

**Security - OIDC keyless federation (the headline pattern).** GitHub issues a
short-lived OIDC token per job; AWS IAM trusts GitHub's OIDC provider
(`https://token.actions.githubusercontent.com`, audience `sts.amazonaws.com`)
and hands out temporary STS credentials scoped by a trust-policy condition on
the token's `sub` claim (repo/branch/environment) - no long-lived AWS keys in
GitHub at all (verify-current: 2026-09-10, GitHub Docs "Configuring OpenID
Connect in Amazon Web Services"). CodePipeline's GitHub source instead uses a
CodeStar Connections link (AWS pulling from GitHub), keeping IAM roles
entirely inside AWS. Both are keyless in the direction that matters; the
piece worth scoping tightly on the Actions side is the trust policy's `sub`
condition (recipe 2b) - an unscoped `sub:*` is the most common real-world
misconfiguration.

**Enterprise controls.** Environments + required reviewers, branch
protection/rulesets, and org policies (allowed-actions list, required
workflows) are native Actions/GitHub features (section 3 flags Enterprise
gating). CodePipeline's equivalents (manual-approval stages, SCP enforcement,
cross-account roles) live in IAM/Organizations instead. Neither is weaker;
they sit in different admin surfaces, which costs something if the org wants
ONE place to audit deploy gates. Rulesets are displacing branch protection
rules as GitHub's recommended mechanism (org-wide enforcement, bypass lists
with an audit trail, a one-click migration from branch protection - verify-
current: 2026-09-10).

**Ecosystem / maintainability / lock-in.** Actions has a far larger
third-party marketplace and is what most hires already know; CodeBuild
buildspecs are hand-rolled YAML (the suite's reusable-buildspec pattern,
cloudformation-pipeline.md s1, is the mitigation). A workflow file lives with
the code and is reviewed in the same PR as the change it builds; CodePipeline
stage definitions live one hop away in a separate CloudFormation stack.
CodePipeline ties the CI/CD engine to AWS; Actions ties it to GitHub - but
the org is already fully committed to GitHub as its source control and to
AWS for hosting, so Actions adds no new vendor. Deploy steps are just `aws`
CLI calls a workflow happens to run, so the AWS side is unaffected either
way.

**Runner considerations - GitHub-hosted vs self-hosted behind the corporate
VPN/proxy.** GitHub-hosted runners cannot reach anything behind private
ingress (the App Runner VPC endpoint, an in-VPC-only RDS instance) without an
explicit bridge - the same constraint that forces the suite's CodeBuild
Migrate stage to run inside the VPC (cloudformation-pipeline.md s3). Most
deploy calls (`aws ecr`, `aws apprunner`) hit AWS's public API endpoints over
the internet with SigV4 auth, not private ingress, so GitHub-hosted runners
are fine for CI, build, and most deploy steps; only a migration-equivalent
step reaching directly into the VPC needs a self-hosted runner or a bridge.
If self-hosting behind the corporate TLS-inspecting proxy, expect the same
failure class the reference architecture already documents for `pip
install`/AWS CLI behind that proxy (TLS-proxy failures in
cloudformation-pipeline.md s3; the `AWS_CA_BUNDLE` fix lives in the app-hosting
skill, references/aws-architecture.md): the runner agent does its own TLS check and most
marketplace actions run on Node, which ignores the OS certificate store - so
trust the corporate CA explicitly (OS store AND `NODE_EXTRA_CA_CERTS`), never
set `GITHUB_ACTIONS_RUNNER_TLS_NO_VERIFY=1` (verify-current: 2026-09-10,
GitHub Docs self-hosted runner troubleshooting).

**Audit/compliance.** CodePipeline activity is CloudTrail-native end to end.
Actions activity is GitHub's own audit log plus CloudTrail once it federates
in via OIDC - not weaker, but a compliance review pulls from two systems.

**Recommendation.** Adopt GitHub Actions as the full pipeline (CI + deploy)
for new, standalone apps that do not need an in-VPC migration/test step on
every build, using OIDC to assume scoped deploy roles the same way
CodePipeline's cross-account model already does (cloudformation-pipeline.md
s2). Keep CodePipeline when: a CI step must reach directly into the VPC and
no self-hosted runner fleet is already justified; the org wants pipeline
audit and approval entirely inside CloudTrail/IAM; or the app team is already
maintaining a working CodeBuild/CodePipeline setup - don't migrate a working
pipeline just to be on the newer tool. Never run both engines against the
same App Runner service for the same app; pick one per app and record it in
that app's design doc.

---

## 2. Recipes

Action versions below are current as of 2026-09-10 (verify-current: pin the
exact minor via Dependabot or a manual check before adopting - these drift).
Replace `<APP_NAME>`, `<AWS_ACCOUNT_ID>`, `<REGION>`, `<GITHUB_ORG>/<REPO>`
placeholders; never commit real values.

### 2a. Repo CI on PR - lint + typecheck + tests, Postgres service container

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U app" --health-interval 5s
          --health-timeout 5s --health-retries 10
    env:
      DATABASE_URL: postgresql://app:app@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4        # verify-current: v5/v6 exist as of Sep 2026
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install uv
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run mypy .
      - run: uv run alembic upgrade head
      - run: uv run pytest -q
```

A `strategy.matrix` on Python/Postgres version is worth adding only when a
real fork exists (e.g., testing a Postgres major upgrade) - a single-module
service rarely needs one. The Postgres service container mirrors
`testcontainers-postgres` (app-harness/references/testing.md) without
Docker-in-Docker. This mirrors the suite's "Test before Build" rule
(cloudformation-pipeline.md s3): no image is built or pushed here, so a red
run never produces an artifact.

### 2b. OIDC setup - IAM OIDC provider + trust policy scoped to repo/branch

One-time per AWS account, in the account's own IaC (INVENTED illustration):

```yaml
Resources:
  GitHubOIDCProvider:
    Type: AWS::IAM::OIDCProvider
    Properties:
      Url: https://token.actions.githubusercontent.com
      ClientIdList: [sts.amazonaws.com]
      # AWS IAM auto-validates GitHub's TLS chain; a hand-pinned thumbprint
      # is no longer required (verify-current if the account predates 2023).

  GitHubActionsDeployRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "${AppName}-gha-deploy"
      PermissionsBoundary: !Ref PermissionsBoundaryArn
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal: { Federated: !Ref GitHubOIDCProvider }
            Action: sts:AssumeRoleWithWebIdentity
            Condition:
              StringEquals:
                token.actions.githubusercontent.com:aud: sts.amazonaws.com
              StringLike:
                # Scope to ONE repo + branch (or :environment:prod) - a bare
                # "repo:<org>/<repo>:*" trusts every branch and every PR.
                token.actions.githubusercontent.com:sub: >-
                  repo:<GITHUB_ORG>/<REPO>:ref:refs/heads/main
      Policies:
        - PolicyName: deploy-scope
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action: [ecr:GetAuthorizationToken, ecr:BatchGetImage, ecr:PutImage,
                          ecr:InitiateLayerUpload, ecr:UploadLayerPart, ecr:CompleteLayerUpload]
                Resource: !Sub "arn:aws:ecr:${AWS::Region}:${AWS::AccountId}:repository/${AppName}-*"
              - Effect: Allow
                Action: [apprunner:StartDeployment, apprunner:DescribeService, apprunner:UpdateService]
                Resource: !Sub "arn:aws:apprunner:${AWS::Region}:${AWS::AccountId}:service/${AppName}-*"
```

Workflow side needs only `permissions: { id-token: write, contents: read }`
plus the credentials step:

```yaml
      - uses: aws-actions/configure-aws-credentials@v6   # verify-current: v6.2.x as of Sep 2026
        with:
          role-to-assume: arn:aws:iam::<AWS_ACCOUNT_ID>:role/<APP_NAME>-gha-deploy
          aws-region: <REGION>
          # default role-session-name is "GitHubActions"; some orgs report
          # that literal name misbehaving with certain policies - set your own.
```

Gotchas: scope the `sub` condition to a branch or `environment:`, never a
bare wildcard; `id-token: write` must be set at job/workflow level or the
credentials step fails with an unhelpful error; a two-role chain (mirroring
the dev-assumes-into-prod pattern in cloudformation-pipeline.md s2) needs
`role-chaining: true` on the SECOND `configure-aws-credentials` step, and the
second role's trust policy must let the first role's principal
`sts:AssumeRole` + `sts:TagSession`.

### 2c. Build + push to ECR

```yaml
      - uses: aws-actions/amazon-ecr-login@v2   # verify-current: v2.1.x as of Sep 2026
        id: ecr-login
      - env:
          ECR_REGISTRY: ${{ steps.ecr-login.outputs.registry }}
          ECR_REPOSITORY: <APP_NAME>-dev
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" .
          docker push "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
```

Same dev-immutable-tag discipline as cloudformation-pipeline.md s5: every dev
push is a distinct `:<git-sha>`, nothing overwritten; these bytes get
re-tagged in 2d, never rebuilt.

### 2d. Deploy to App Runner - matching the suite's rollback pattern

Mirrors the dev-immutable / prod-mutable split (cloudformation-pipeline.md
s5, operations.md s3) exactly - only the engine running the calls changes.

```yaml
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: dev
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::<DEV_ACCOUNT_ID>:role/<APP_NAME>-gha-deploy
          aws-region: <REGION>
      - name: update-service (read-modify-write; dev only - see note below)
        run: |
          aws apprunner describe-service --service-arn "$DEV_SERVICE_ARN" > current.json
          ./scripts/merge-image-tag.sh current.json "${{ github.sha }}" > merged.json
          aws apprunner update-service --service-arn "$DEV_SERVICE_ARN" \
            --source-configuration file://merged.json
      - run: ./scripts/poll-apprunner-status.sh "$DEV_SERVICE_ARN" RUNNING

  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: prod        # gates on required reviewers - see 2e
    permissions: { id-token: write, contents: read }
    steps:
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::<PROD_ACCOUNT_ID>:role/<APP_NAME>-gha-deploy
          aws-region: <REGION>
      - name: retag tested dev image to prod :latest (no rebuild)
        run: |
          MANIFEST=$(aws ecr batch-get-image --repository-name <APP_NAME>-dev \
            --image-ids imageTag=${{ github.sha }} --query 'images[0].imageManifest' --output text)
          aws ecr put-image --repository-name <APP_NAME>-prod \
            --image-tag latest --image-manifest "$MANIFEST"
      - name: start-deployment ONLY - never update-service in prod (SCP denies it)
        run: aws apprunner start-deployment --service-arn "$PROD_SERVICE_ARN"
      - run: ./scripts/poll-apprunner-status.sh "$PROD_SERVICE_ARN" RUNNING
```

`merge-image-tag.sh` swaps ONLY the image identifier into the existing
`SourceConfiguration` - a partial `update-service` call would drop
`RuntimeEnvironmentSecrets`/`Variables` (cloudformation-pipeline.md s5).
Rollback stays the operations.md s3 runbook exactly (retag the previous good
digest to `:latest`, `start-deployment`, never `update-service` in prod) -
the engine firing the CLI does not change the AWS-side mechanics.

### 2e. Environments + required approvals for prod

Add `environment: { name: prod, url: https://<app-runner-prod-url> }` to the
`deploy-prod` job (already shown in 2d), then configure the `prod`
environment in repo Settings -> Environments: **required reviewers** (up to 6
people/teams; any ONE approval unblocks the job; auto-fails after 30 days
unapproved - the Actions-native equivalent of CodePipeline's `ApproveProd`
stage); **deployment branch/tag rules** (restricts which branches may deploy,
mirroring the branch-guard hook's protected-branch concept at the platform
level); **environment secrets** (store the prod role ARN there, not as a repo
secret, so only jobs targeting `prod` can read it).

---

## 3. GitHub Enterprise-plan-gated features

Confirm the org's actual plan (Team vs Enterprise Cloud/Server) before
designing around these - a Team plan does not get them (verify-current:
2026-09-10):

- **Required reviewers for environments on PRIVATE repos is Enterprise-only**
  - on Free/Pro/Team it only works on public repos, so the recipe-2e approval
    gate needs Enterprise Cloud/Server to actually enforce on a private repo.
- **Organization-wide rulesets**, **required workflows / reusable-workflow
  enforcement at the org level**, and **org-level self-hosted runner groups
  with access policies** are Enterprise Cloud; Team is limited to per-repo
  rulesets/branch protection and per-repo runner configuration.
- **SAML SSO enforcement + IP allow lists** and the **audit-log streaming
  API** (vs the audit-log UI, which every plan gets) are Enterprise
  Cloud/Server - relevant to locking down deploy-role-holding accounts and to
  the two-system audit note in section 1.

On a Team plan, the practical workaround is per-repo rulesets/required checks
instead of org-wide, and a branch-protection-based reviewer requirement as a
proxy for the prod approval gate until/unless the org upgrades.

---

## 4. What not to do

- Do not run CodePipeline and an Actions deploy workflow against the same App
  Runner service for the same app - two engines racing `update-service`/
  `start-deployment` on one service produces confusing deploy flapping.
- Do not store a long-lived AWS access key as a GitHub secret when OIDC is
  available; treat a static key as a scoped, rotated exception, not a default.
- Do not leave the OIDC trust policy's `sub` condition unscoped (recipe 2b).
- Do not disable TLS verification on a self-hosted runner to work around the
  corporate proxy - trust the corporate CA explicitly instead (section 1).
