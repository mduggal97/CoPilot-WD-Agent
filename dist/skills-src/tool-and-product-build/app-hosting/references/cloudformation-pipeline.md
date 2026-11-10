# CloudFormation + Pipeline (reference-architecture pattern)

How a new hosted app gets its infrastructure and its CI/CD pipeline
WITHOUT writing new CloudFormation. This is the pattern; every real value is a
placeholder (`<APP_NAME>`, `<REGION=us-east-2>`, `<DEV_ACCOUNT_ID>`,
`<PROD_ACCOUNT_ID>`, `<INGRESS_VPCE_ID>`, `<VPC_CONNECTOR_ARN>`). Apply the
scrub list in `deploy-runbook.md` before adopting any real infra file.

The YAML fragments below are INVENTED illustrations of the SHAPE. Do not copy a
real source template - reproduce this shape with your own parameter values.

For an evaluated alternative to this CodePipeline/CodeBuild engine, see
app-harness references/github-actions.md (GitHub Actions full-pipeline
evaluation and recipes - when to adopt Actions vs when this pattern stays).

---

## 1. The core idea: no new CloudFormation per app

A new app does NOT get its own hand-written stack. There are exactly two
reusable, parameterized templates, and a new service is stood up by supplying
**parameters**, not by authoring new IaC:

| Template (generic name)     | What it is                                            |
|-----------------------------|-------------------------------------------------------|
| `service-pipeline.yaml`     | One reusable per-service CI/CD pipeline. Instantiated once per service. |
| `module-service.yaml`       | One generalized app-layer stack (ECR + IAM + logs + secret + App Runner service + private ingress). Every resource name derives from `${ServiceName}-${Env}`; no service name is hardcoded. |

There are dev and prod variants of the app-layer stack
(`module-service-dev.yaml` / `module-service-prod.yaml`) because dev and prod
differ in ways that cannot be a single parameter (see the immutable/mutable
split in section 5). The PIPELINE template is a single file reused for every
service, dev and prod alike.

**Why this matters.** Adding an app becomes "instantiate two stacks with these
parameters," reviewable in minutes, instead of "author and review a few hundred
lines of new YAML." The templates carry all the hard-won posture (private
ingress, retain policies, IAM boundary, scoped secrets) so a new app inherits it
by construction rather than by remembering to copy it.

### Illustrative pipeline-instance parameters for a new service

```
ServiceName            = <APP_NAME>
ECRRepository          = <APP_NAME>-dev
DevAppRunnerServiceName= <APP_NAME>-dev
GitHubRepo             = <GITHUB_ORG>/<REPO>
BranchName             = main
SourceFilePaths        = services/<APP_NAME>/**,packages/modules/<APP_NAME>/**,packages/shared/**
AppSecretId            = <APP_NAME>-dev            # Secrets Manager id holding DATABASE_URL
BuildBuildspec         = infra/buildspecs/buildspec-module-service.yml
MigrateBuildspec       = infra/buildspecs/buildspec-module-migrate.yml   # REAL migrate for a DB-backed service
DockerfilePath         = services/<APP_NAME>/Dockerfile
```

Notes that bite if you get them wrong:
- **The module package MUST be in `SourceFilePaths`.** The extracted service's
  Dockerfile copies `packages/modules/<APP_NAME>/`, so a path filter that omits
  it would let a module-code-only change build and deploy a STALE image.
- **A DB-backed service MUST use the real migrate buildspec, never the no-op
  one.** The no-op migrate is only for genuinely DB-less services; pointing a
  DB-backed service at it silently skips migrations and leaves the schema
  un-applied.
- Path-filter Includes are capped (reportedly at most ~8 patterns - (!) verify
  against the current CodePipeline source-trigger limits before relying on the
  exact number) - keep the list tight so unrelated changes (docs, other modules)
  don't trigger this service's pipeline.

### Illustrative app-layer parameters (dev)

```
ServiceName          = <APP_NAME>
Env                  = dev
ECRImageURI          = ""                          # empty = Pass 1 (see section 4)
DBEndpoint           = <SHARED_RDS_HOST>
DBName               = <SHARED_DB_NAME>
DBCredentialsSecretId= <SHARED_DB_CREDENTIALS_SECRET>
VpcId                = <VPC_ID>
VpcConnectorArn      = <VPC_CONNECTOR_ARN>          # reused, never created
IngressVpcEndpointId = <INGRESS_VPCE_ID>            # shared vpce-*, never created
PermissionsBoundaryArn = <IAM_PERMISSIONS_BOUNDARY_ARN>
EntraTenantId        = <ENTRA_TENANT_ID>            # stub GUID default; real via override
EntraClientId        = <ENTRA_CLIENT_ID>
BedrockRegion        = <REGION=us-east-2>
EnableBedrock        = "false"                      # per-service toggle
```

A lean service and a Bedrock-using service deploy from the SAME template - the
`EnableBedrock` / `EnableArtifactsRead` toggles (default `"false"`) gate the
optional IAM policies so the template never has to fork.

---

## 2. The two-account model (dev and prod are separate AWS accounts)

- **Dev account (`<DEV_ACCOUNT_ID>`)** hosts the pipeline, the dev App Runner
  service, the dev ECR repo, and the dev RDS/secrets. The pipeline LIVES in the
  dev account and runs all stages from there.
- **Prod account (`<PROD_ACCOUNT_ID>`)** hosts the prod App Runner service, prod
  ECR, prod RDS/secrets, and a cross-account **deploy role** that trusts the dev
  account's CodeBuild role principal.
- **Cross-account promotion:** the dev-account pipeline's prod stages
  `sts:assume-role` into the prod deploy role to push the image to prod ECR and
  trigger the prod deployment. There is no separate prod pipeline.
- **Dormant prod.** Before a prod account exists, the prod-related pipeline
  parameters (`ProdAppRunnerServiceArn`, `ProdDeployRoleArn`, `ProdEcrRepo`,
  `ProdAccountId`) default to `""` and the three prod buildspec stages **exit 0
  cleanly**. You build and run the whole dev half first; standing up prod later
  is "fill in those parameters + deploy the prod app-layer stack," no pipeline
  rewrite.

```
   +-------------------- Dev account <DEV_ACCOUNT_ID> --------------------+
   |  CodePipeline (all stages run here)                                  |
   |  Source Test Build Migrate DeployDev ScanGate ApproveProd           |
   |                                        |         PushProdImage        |
   |  dev ECR, dev App Runner, dev RDS      |         MigrateProd          |
   +----------------------------------------|---------DeployProd-----------+
                                            | sts:assume-role
                                            v
   +-------------------- Prod account <PROD_ACCOUNT_ID> ------------------+
   |  cross-account deploy role (trusts dev CodeBuild role)               |
   |  prod ECR (:latest, MUTABLE)  prod App Runner  prod RDS              |
   +---------------------------------------------------------------------+
```

---

## 3. The buildspec stage sequence

The pipeline is a fixed, ordered set of stages, each a CodeBuild project driven
by a buildspec in `infra/buildspecs/`:

```
Source -> Test -> Build -> Migrate -> DeployDev -> ScanGate -> ApproveProd
       -> PushProdImage -> MigrateProd -> DeployProd
```

| Stage         | What it does                                                        |
|---------------|--------------------------------------------------------------------|
| Source        | Path-filtered trigger on push to the branch; pulls the repo.        |
| Test          | Lint + unit/integration tests. **Runs BEFORE Build on purpose.**    |
| Build         | `docker build` the one image; push to DEV ECR under an immutable `:<git-sha>` tag; emit `build-meta.env` (IMAGE_TAG, IMAGE_URI). |
| Migrate       | Apply Alembic migrations to the dev DB (in-VPC CodeBuild; needs `VpcConfig` to reach RDS). |
| DeployDev     | Deploy the new SHA to the dev App Runner service, poll to RUNNING.  |
| ScanGate      | Fail promotion if the dev image has any ECR/Inspector finding at or above a severity floor (e.g. HIGH). |
| ApproveProd   | Manual approval gate (SNS-notified). A human clicks Approve.        |
| PushProdImage | Retag the EXACT dev-tested image bytes and push to prod ECR `:latest` (cross-account). No rebuild. |
| MigrateProd   | Apply migrations to the prod DB (runs BEFORE the prod app boots).   |
| DeployProd    | `start-deployment` on the prod App Runner service, poll to RUNNING. |

**Why Test precedes Build.** If Build (and its ECR push) ran first, a failing
lint/test gate would still have produced and pushed an image to ECR. Testing
first means a red test never produces or publishes an image at all.

**Why MigrateProd precedes DeployProd.** The app must never boot against a
schema that does not exist yet. Migrations land first, then the new image rolls.

**Kick the FIRST build with `start-pipeline-execution`, not `start-build`.** The
first image must flow through the whole ordered pipeline (Source -> Test ->
Build -> Migrate ...). `start-build` runs a single CodeBuild project and bypasses
that ordering. (Also: the Build project runs INSIDE the VPC, where the corporate
TLS-inspection proxy is absent, so `pip install` behind that proxy in a local
Docker build fails - another reason the pipeline, not a laptop, builds the
image.)

**ScanGate is a toggle-able gate.** It is in the canonical order above, but it
can be temporarily removed if the scanner misbehaves in CI. Keep the scan-gate
CodeBuild project and its parameters in the template even when the stage is
pulled, so re-adding the stage is a one-block change rather than a rewrite.

---

## 4. The two-pass, ECR-gated deploy (the chicken-and-egg)

**The problem.** The app-layer stack wants to create an
`AWS::AppRunner::Service`, and an App Runner service REQUIRES an
`ImageIdentifier` - a concrete ECR image URI. But that image does not exist
until the pipeline builds and pushes it. And the pipeline cannot deploy to a
service that does not exist. Each needs the other first.

**The solution: one template, two passes, gated on an `ECRImageURI` parameter.**

```yaml
# INVENTED ILLUSTRATION of the gating condition - not a real source template.
Parameters:
  ECRImageURI:
    Type: String
    Default: ""            # empty = Pass 1 (bootstrap only)

Conditions:
  CreateAppLayer: !Not [!Equals [!Ref ECRImageURI, ""]]

Resources:
  ECRRepository:           # always created (both passes)
    Type: AWS::ECR::Repository
    # ... immutable tags in dev; scan-on-push ...

  AppRunnerInstanceRole:   # always created (both passes)
    Type: AWS::IAM::Role
    # ...

  AppSecret:               # always created (both passes)
    Type: AWS::SecretsManager::Secret
    # ... holds DATABASE_URL ...

  AppRunnerService:        # ONLY on Pass 2
    Type: AWS::AppRunner::Service
    Condition: CreateAppLayer
    Properties:
      SourceConfiguration:
        ImageRepository:
          ImageIdentifier: !Ref ECRImageURI     # the URI that did not exist in Pass 1
          ImageRepositoryType: ECR
          ImageConfiguration:
            Port: "8080"
      HealthCheckConfiguration: { Protocol: HTTP, Path: /health }
      NetworkConfiguration:
        IngressConfiguration: { IsPubliclyAccessible: false }
        EgressConfiguration:  { EgressType: VPC, VpcConnectorArn: !Ref VpcConnectorArn }

  IngressConnection:       # ONLY on Pass 2 - registers a consumer on the SHARED vpce
    Type: AWS::AppRunner::VpcIngressConnection
    Condition: CreateAppLayer
    DeletionPolicy: Retain
    Properties:
      ServiceArn: !GetAtt AppRunnerService.ServiceArn
      IngressVpcConfiguration:
        VpcId: !Ref VpcId
        VpcEndpointId: !Ref IngressVpcEndpointId   # shared, pre-existing
```

**The bootstrap order is therefore:**

1. **Pass 1** - deploy the app-layer stack with `ECRImageURI=""`. This creates
   ECR + IAM + log group + secret ONLY (`CreateAppLayer` is false, so no App
   Runner service). Now an ECR repo exists to push to.
2. **First pipeline run** - `start-pipeline-execution`. Build pushes the first
   image to the ECR repo Pass 1 created. DeployDev will FAIL on this first run,
   because the App Runner service does not exist yet - expected.
3. **Pass 2** - re-deploy the SAME app-layer stack with
   `ECRImageURI=<the-image-uri-just-pushed>`. Now `CreateAppLayer` is true and
   the App Runner service + private ingress connection are created against that
   image.
4. **Re-run the pipeline** - DeployDev now succeeds against the live service.

Full step-by-step is in `deploy-runbook.md`.

---

## 5. Dev-immutable vs prod-mutable - and WHY

This is the subtlest split in the whole pattern, and it exists because of an
**org-wide Service Control Policy (SCP) that DENIES
`apprunner:UpdateService` in the prod account.**

**(!) Confirm this in YOUR target account before relying on the split.** This is
a live org-policy observation from the reference architecture, not a permanent
AWS fact - org SCPs change and differ per account. Verify the SCP still denies
`apprunner:UpdateService` in your prod account (ask your AWS org admin, check
`aws organizations describe-policy`, or attempt an `update-service` and observe
the AccessDenied). If the deny is NOT present, the dev-immutable/prod-mutable
split is optional, not forced - but the immutable-dev discipline is still good
practice. (deploy-runbook.md's scrub list already tells you to drop the real
`p-...` policy id when adopting.)

| Aspect            | DEV                                   | PROD                                       |
|-------------------|---------------------------------------|--------------------------------------------|
| ECR tag mutability| IMMUTABLE                             | MUTABLE                                     |
| Image identifier  | pinned to a specific `:<git-sha>`     | pinned to a moving `:latest`               |
| Deploy call       | `update-service` (swap SHA) + poll    | `start-deployment` only + poll             |
| `iam:PassRole`    | REQUIRED on `<svc>-access`/`-instance`| NOT needed                                 |

**Dev (no SCP).** Dev uses IMMUTABLE ECR tags for provenance - every image is a
distinct `:<git-sha>`, nothing is ever overwritten. To deploy, the pipeline
calls `update-service` to swap the running `ImageIdentifier` to the new SHA,
then `start-deployment`. Because `update-service` re-supplies the whole
`SourceConfiguration`, App Runner re-assumes the service's `access` and
`instance` roles, so the CodeBuild role needs **`iam:PassRole`** on both (scoped,
gated to the App Runner service principals). IAM is eventually consistent - a
deploy run within minutes of granting PassRole can still 403; re-run, don't
assume failure.

  Read-modify-write caveat for `update-service`: it REPLACES the
  `SourceConfiguration` members you send. Sending a partial config (e.g. Port
  only) would DROP the service's `RuntimeEnvironmentSecrets` (DATABASE_URL) and
  `RuntimeEnvironmentVariables` (ENTRA_*, BEDROCK_REGION). So the deploy reads
  the CURRENT config via `describe-service`, swaps ONLY the image identifier,
  and passes the merged config back - preserving env/secrets without the
  pipeline having to know them.

**Prod (SCP denies `UpdateService`).** Because prod cannot call
`update-service` at all, prod cannot swap an image identifier - so the prod App
Runner service is pinned to a MOVING `:latest` tag, the prod ECR repo is
therefore MUTABLE, PushProdImage OVERWRITES `:latest` with the tested bytes, and
DeployProd calls **`start-deployment` only** (which redeploys whatever `:latest`
now points at). No `update-service`, no `PassRole` needed.

**The trap to know.** The SCP denial surfaces confusingly as an `iam:PassRole`
AccessDenied. Chasing the PassRole grant in prod is a dead end - granting it
does not help, because the real block is the `UpdateService` SCP. If you see
that error in PROD, switch to the `:latest` + `start-deployment` mechanism; do
not go hunting for a missing PassRole.

  (Same-account CloudFormation stack UPDATES in prod are fine - the SCP only
  blocks a direct cross-account `UpdateService` API call. Folding, say, a new
  env var into the live prod service via a same-account CFN update is permitted.)

---

## 6. Generic parameter reference

### Pipeline template (reused per service)

| Parameter              | Meaning / default                                         |
|------------------------|-----------------------------------------------------------|
| `ServiceName`          | Spine for every resource name (`${ServiceName}-${Env}`).  |
| `ECRRepository`        | Dev ECR repo the Build stage pushes to.                   |
| `DevAppRunnerServiceName` | Dev service DeployDev targets.                         |
| `SourceFilePaths`      | Path-filter Includes (<= 8). MUST include the module pkg. |
| `BuildBuildspec`       | Build stage buildspec.                                    |
| `MigrateBuildspec`     | Migrate stage buildspec (real vs no-op).                  |
| `DockerfilePath`       | Path to this service's Dockerfile.                        |
| `AppSecretId`          | Secrets Manager id holding DATABASE_URL.                  |
| `VpcId`/`SubnetA/B`/`SecurityGroupId` | VpcConfig for the in-VPC Migrate project.  |
| `PermissionsBoundaryArn` | IAM boundary applied to every role created.            |
| `ProdAppRunnerServiceArn`/`ProdDeployRoleArn`/`ProdEcrRepo`/`ProdAccountId` | Empty = prod dormant. |
| `ScanFailSeverity`     | Severity floor that blocks prod promotion (e.g. HIGH).    |
| `ApprovalEmail`        | Subscribed to the ApproveProd SNS topic (empty = skip).   |

### App-layer template (dev/prod variants)

| Parameter              | Meaning / default                                         |
|------------------------|-----------------------------------------------------------|
| `ServiceName` / `Env`  | Drive all resource names via `Fn::Sub`.                   |
| `ECRImageURI`          | Empty = Pass 1; set = Pass 2 (creates the service).       |
| `DBEndpoint`/`DBName`/`DBCredentialsSecretId` | Shared RDS + existing creds secret. |
| `VpcConnectorArn`      | Reused egress connector (never created).                  |
| `IngressVpcEndpointId` | Shared `vpce-*` ingress endpoint (never created).         |
| `EntraTenantId`/`EntraClientId` | Stub GUID defaults; real values via override.    |
| `BedrockRegion`        | `<REGION=us-east-2>`.                                      |
| `EnableBedrock`/`EnableArtifactsRead` | Toggle optional IAM policies (default false). |
| `PermissionsBoundaryArn` | IAM boundary on both App Runner roles.                 |

---

## 7. Invariants to preserve when adopting the pattern

- App Runner port is **8080**; health path is **/health** (unauthenticated).
- **Never create** a VPC connector or a VPC ingress endpoint in an app-layer
  stack - both are shared, pre-existing, IT-owned resources; you register
  additional consumers / reuse the connector.
- `IsPubliclyAccessible: false` is permanent - there is no public flip.
- Credentials arrive as `RuntimeEnvironmentSecrets`; everything else
  per-environment is a plain `RuntimeEnvironmentVariable`. Nothing
  environment-specific is baked into the image (see `aws-architecture.md` s4).
- Put `DeletionPolicy: Retain` on ECR repo, DB credentials, app secret, and the
  ingress connection - and know that Retain means a re-deploy after a stack
  delete FAILS on the orphaned resources until you clean them up manually (see
  `deploy-runbook.md`).
- Every role created carries the IAM permissions boundary; instance policies are
  managed policies (not inline) if a no-inline-policy guard is enforced.
- Keep each module's Alembic version table isolated
  (`alembic_version_<module>`).
