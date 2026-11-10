# Deploy Runbook (reference-architecture pattern)

Step-by-step for a FIRST deploy (the two-pass bootstrap) and for SUBSEQUENT
deploys, the genericize-before-adopt SCRUB LIST you must apply before reusing
any real source infra file, and the common failures with their fixes. Read
`cloudformation-pipeline.md` first - this file assumes you know the two-account,
two-pass, dev-immutable/prod-mutable shape.

Placeholders: `<APP_NAME>`, `<REGION=us-east-2>`, `<DEV_ACCOUNT_ID>`,
`<PROD_ACCOUNT_ID>`, `<INGRESS_VPCE_ID>`, `<VPC_CONNECTOR_ARN>`, `<GITHUB_ORG>`.

---

## 0. GENERICIZE BEFORE ADOPT - the scrub list (do this FIRST)

The the reference architecture infra files are ANOTHER TEAM'S private code. Before you adopt any of
them as a template for a new app, strip and replace every real value below.
Copying a source file verbatim would (a) leak that team's account/network
identifiers into your repo and (b) point your app at their infrastructure. Treat
those source files as READ-ONLY reference for the SHAPE, and rebuild that shape with
your own values.

Scrub / replace EVERY one of these before committing an adopted file:

| Category                      | What to strip                              | Replace with               |
|-------------------------------|--------------------------------------------|----------------------------|
| AWS account IDs               | the real 12-digit dev and prod account numbers | `<DEV_ACCOUNT_ID>` / `<PROD_ACCOUNT_ID>` |
| VPC endpoint IDs              | any real `vpce-...` ingress endpoint id    | `<INGRESS_VPCE_ID>`        |
| VPC / subnet / SG IDs         | real `vpc-...`, `subnet-...`, `sg-...`     | your environment's IDs     |
| VPC connector ARN            | the real `arn:aws:apprunner:...:vpcconnector/...` | `<VPC_CONNECTOR_ARN>` |
| Cross-account role / connector ARNs | real deploy-role ARNs, CodeConnections ARN | your ARNs           |
| IAM permissions boundary ARN  | the real `.../policy/<boundary>` ARN       | your boundary ARN          |
| App Runner URL                | any real `*.awsapprunner.com` host         | resolve at runtime; never hardcode |
| Friendly / internal hostname  | any real `*.<firm-domain>` host | `<APP_NAME>.<internal-domain>` |
| GitHub org / repo             | the reference project's real GitHub org + repo names | `<GITHUB_ORG>/<REPO>`      |
| Entra tenant / client IDs     | any real GUIDs                             | stub GUIDs; real via param override |
| RDS endpoints / DB names      | real `*.rds.amazonaws.com` hosts, DB names | your shared RDS values     |
| Region-specific ARNs          | ARNs embedding a real account/region       | rebuild from your values   |
| Product / client / person names | reference-specific service, module, client, people names | `<APP_NAME>` and yours |
| Secret names / IDs            | real Secrets Manager ids                   | `<APP_NAME>-<env>`         |
| SCP / org policy IDs          | real `p-...` policy ids                    | drop (describe your own)   |

Mechanical check before commit: grep the adopted file for `vpce-`, `vpc-`,
`subnet-`, `sg-`, `arn:aws:`, `.awsapprunner.com`, `.rds.amazonaws.com`,
12-digit number runs, and any known org/product name. Anything that matches a
REAL resource must become a placeholder or your own value. (A secrets/PII
pre-commit guard - see the `app-harness` skill - catches most of this
automatically; the grep is the belt-and-suspenders pass.)

---

## 1. FIRST deploy - the two-pass bootstrap (dev)

Prereqs: the two reusable templates exist in your repo (scrubbed per section 0),
the shared VPC connector + ingress endpoint exist (IT-owned), and you know your
shared RDS endpoint + credentials secret id.

1. **Pass 1 - bootstrap the app layer (no service yet).**
   Deploy the dev app-layer stack with `ECRImageURI=""`. This creates ECR + IAM
   + log group + secret only; the App Runner service is gated OFF
   (`CreateAppLayer` is false). Result: an empty ECR repo now exists to push to.

2. **Populate the app secret out-of-band.**
   Put the real `DATABASE_URL` DSN into the Secrets Manager secret the stack
   created (`<APP_NAME>-dev`). CloudFormation names the secret; it does not put
   the credential in it. (For a DB-less service, the secret can be a placeholder
   the no-op migrate never reads.)

3. **First pipeline run - build and push the first image.**
   Kick it with `start-pipeline-execution` (NOT `start-build` - see
   `cloudformation-pipeline.md` s3). Source -> Test -> Build push the first
   image to the ECR repo from Pass 1. **DeployDev will FAIL on this run** because
   the App Runner service does not exist yet. This is EXPECTED, not a real
   failure.

4. **Pass 2 - create the service against the pushed image.**
   Re-deploy the SAME dev app-layer stack, now with
   `ECRImageURI=<the-image-uri-just-pushed>` (the `:<git-sha>` URI from the Build
   stage's `build-meta.env` / ECR). `CreateAppLayer` is now true, so the App
   Runner service + private `VpcIngressConnection` are created.

5. **Re-run the pipeline - DeployDev now succeeds.**
   `start-pipeline-execution` again (or re-run from the failed execution).
   DeployDev finds the live service and deploys the SHA. Wait for RUNNING.

6. **Smoke-test over the VPN.**
   From a machine on the corporate VPN:
   - `GET /health` -> `200 {"status":"ok"}` (no auth).
   - `GET /api/v1/auth/config` -> `200` with your dev tenant/client id.
   - Open the SPA; confirm a `GET /api/v1/auth/config` fires BEFORE any redirect
     to Entra, and that the sign-in redirect carries YOUR dev client id (not a
     stub, not prod's).

### Standing up prod later (activation)

Prod stays dormant until you fill it in:

1. Deploy the PROD app-layer stack (`module-service-prod.yaml`-shaped) in the
   prod account, two-pass, same as dev. It also creates the cross-account
   **deploy role** that trusts the dev pipeline's CodeBuild role.
2. Set the pipeline's dormant prod parameters
   (`ProdAppRunnerServiceArn`, `ProdDeployRoleArn`, `ProdEcrRepo`,
   `ProdAccountId`) to the real values and update the pipeline stack.
3. Populate the prod app secret out-of-band; set real prod Entra IDs via
   parameter override on the prod app-layer stack.
4. The next pipeline run now lights up ScanGate -> ApproveProd ->
   PushProdImage -> MigrateProd -> DeployProd. A human approves ApproveProd;
   the EXACT dev-tested image bytes are retagged to prod `:latest` and rolled
   out with `start-deployment`.

---

## 2. SUBSEQUENT deploys (the steady state)

Once bootstrapped, a deploy is just a merge:

1. Merge a change to the trigger branch (`main`). The path-filter Source stage
   fires only if a file matching `SourceFilePaths` changed.
2. Test -> Build -> Migrate -> DeployDev run automatically. Dev now runs the new
   `:<git-sha>` (immutable tag, `update-service` swap).
3. Verify in dev (health, auth/config, the actual feature).
4. ScanGate must clear (no finding at/above the severity floor).
5. A human clicks **Approve** on ApproveProd.
6. PushProdImage retags the SAME tested bytes to prod `:latest`; MigrateProd
   applies prod migrations; DeployProd `start-deployment` rolls prod.

No CloudFormation change is needed for a normal code deploy - only a merge. You
touch the stacks only when infrastructure changes (a new env var, a new module
service, enabling Bedrock, etc.).

---

## 3. Common deploy failures and fixes

| Symptom                                                        | Cause                                                                 | Fix |
|---------------------------------------------------------------|-----------------------------------------------------------------------|-----|
| DeployDev exits 1: "service ... not found" on the FIRST run   | Pass 2 has not run yet; the App Runner service does not exist         | Run Pass 2 (`ECRImageURI=<pushed-uri>`), then re-run the pipeline. Expected on first bootstrap. |
| Prod deploy fails with `iam:PassRole` AccessDenied            | The org SCP DENIES `apprunner:UpdateService` in prod; it surfaces as a misleading PassRole error | Do NOT chase the PassRole grant - it will not help. Use the prod mechanism: `:latest` (MUTABLE ECR) + `start-deployment` only. See `cloudformation-pipeline.md` s5. |
| Dev deploy 403s on PassRole right after granting it           | IAM is eventually consistent (propagation delay)                      | Re-run the pipeline; do not assume a real failure. |
| App Runner never reaches RUNNING; health check failing        | Server not bound to `0.0.0.0:8080`, or `/health` not returning 200 without auth, or health path/protocol mismatch | Bind `0.0.0.0` and expand `$PORT` (default 8080) at runtime; make `/health` unauthenticated and `200`; confirm the stack's `HealthCheckConfiguration` is `Protocol: HTTP, Path: /health`. |
| `update-service` boots the app WITHOUT DB/auth config         | A partial `SourceConfiguration` dropped `RuntimeEnvironmentSecrets`/`Variables` | Read-modify-write: `describe-service`, swap ONLY the image identifier, pass the merged config back. |
| Build fails on `pip install` behind the TLS-inspection proxy  | A local Docker build runs where the corporate proxy intercepts TLS    | Build via the pipeline (in-VPC CodeBuild, proxy absent) - `start-pipeline-execution`, not a laptop build. |
| First build only ran one CodeBuild project, skipped ordering  | Used `start-build` instead of `start-pipeline-execution`              | Always kick the first build with `start-pipeline-execution` so Source -> Test -> Build -> Migrate order holds. |
| Re-deploy fails `ResourceExistenceCheck` after a stack delete | `DeletionPolicy: Retain` left ECR repo / secrets / ingress connection orphaned | Manually delete the orphaned retained resources, then re-deploy. |
| Migrate stage cannot reach RDS                                | The Migrate CodeBuild project has no `VpcConfig`                       | Give the Migrate project `VpcConfig` (VPC + subnets + SG) so it can reach the shared RDS. |
| SPA sign-in shows a stub client id or `missing client_id`     | The SPA baked Entra config at build time, or `/api/v1/auth/config` didn't wire through | Confirm the SPA fetches `/api/v1/auth/config` at runtime and the backend has real `ENTRA_*` env vars set by the stack. See `aws-architecture.md` s4. |
| Prod off-VPN smoke test cannot reach the service              | Private ingress - `IsPubliclyAccessible: false`, resolves only on VPN | Run prod checks from a machine on the corporate VPN. Not a bug. |

---

## 4. USER-ACTION checklist (the human-run steps)

Some steps in this runbook cannot be done by an agent - they need a human at an
AWS console with SSO, or a human decision (a prod approval). Hand the operator
this checklist. Each item names WHERE, the VALUES to use, the EXPECTED result,
and the DONE signal.

```
[ ] 1. SSO login to the DEV account
       WHERE:   AWS access portal (SSO) -> <DEV_ACCOUNT_ID> -> the deploy role
       DO:      sign in with corporate SSO + MFA
       EXPECT:  a CLI session / console access to <DEV_ACCOUNT_ID> in <REGION=us-east-2>
       DONE:    `aws sts get-caller-identity` shows <DEV_ACCOUNT_ID>

[ ] 2. Confirm you are ON the corporate VPN (for every smoke test)
       WHERE:   corporate VPN client
       EXPECT:  connected; internal hosts resolve
       DONE:    the dev App Runner private host answers over the VPN

[ ] 3. Populate the app secret (out-of-band, after Pass 1)
       WHERE:   Secrets Manager (dev) -> secret "<APP_NAME>-dev"
       VALUES:  the real DATABASE_URL DSN for the shared RDS + this app's schema
       EXPECT:  secret has a DATABASE_URL value
       DONE:    the Migrate/DeployDev stages no longer fail on a missing DSN

[ ] 4. Kick the first pipeline run
       WHERE:   CodePipeline console (dev) OR CLI
       DO:      start-pipeline-execution on the <APP_NAME> pipeline
       EXPECT:  DeployDev FAILS on this first run (service not created yet)
       DONE:    Build succeeded + an image is in ECR; DeployDev's failure is the
                expected "service not found" (proceed to Pass 2)

[ ] 5. Approve the prod promotion (ApproveProd manual gate) - PROD ONLY
       WHERE:   CodePipeline console (dev account) -> paused execution ->
                ApproveProd action -> Review -> Approve
       DECISION: only approve after dev smoke tests pass and ScanGate is clear
       EXPECT:  PushProdImage -> MigrateProd -> DeployProd proceed
       DONE:    the paused execution resumes; prod reaches RUNNING
       NOTE:    this promotes the EXACT dev-tested bytes - no rebuild for prod

[ ] 6. Confirm the SNS approval-notification subscription (first time only)
       WHERE:   the confirmation email AWS sends to ApprovalEmail
       DO:      click "Confirm subscription"
       EXPECT:  future ApproveProd gates email you
       DONE:    a test/first notification arrives

[ ] 7. Prod smoke test (on VPN)
       WHERE:   a machine on the corporate VPN
       DO:      GET /health, GET /api/v1/auth/config, sign in through the SPA
       EXPECT:  /auth/config returns PROD's client id from the SAME image bytes
                that served dev's client id
       DONE:    prod resolves the correct prod client id; sign-in works
```

Reminder: entering credentials, MFA, or approving org-level changes is always a
human action. An agent can prepare the commands and watch the pipeline state,
but the SSO login, the secret population, and the prod approval are yours.
