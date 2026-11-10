# Azure Hosting Variant - when a customer mandates Azure

This file is a VARIANT, not a replacement. AWS (App Runner, RDS Postgres, ECR,
Secrets Manager, Bedrock, CloudFormation) stays the DEFAULT hosting stack for
every internally built tool - see `aws-architecture.md`, `cloudformation-pipeline.md`,
and `operations.md`. Reach for THIS file only when a specific customer's IT
estate is Microsoft-shaped (a hospital or university running everything on
Azure/Microsoft 365/Entra already) and either they will not sign off on data
leaving their Azure tenant/subscription, or their procurement/security team
mandates Azure as the hosting cloud. That is a CUSTOMER-MANDATED constraint,
not a firm preference - never default a new internal tool to Azure.

## 0. The decision gate - have this conversation before picking a stack

Ask it directly, in the same discovery conversation that already covers data
residency and security review (see `wd-discovery`): "Does your organization
require this application to run inside your own Azure tenant, or is a
hosted AWS service with Microsoft Entra sign-in acceptable?" Most
customers asking for "Microsoft" actually mean "our people sign in with their
Microsoft work account" - which the AWS default already gives via Entra auth
(`aws-architecture.md` s3.6; unchanged regardless of hosting cloud, and
cross-linked, not restated, below). Only escalate to this file when the
answer is genuinely "the workload, database, and compute must sit inside our
Azure subscription" - a data-residency clause, an existing Azure security
perimeter the customer's InfoSec team already audits, or a procurement rule
against a non-Azure vendor. Confirm which reason it is; that determines
whether this is a one-time exception or a pattern worth standardizing for
that customer's future engagements.

---

## 1. Service mapping - AWS default to Azure equivalent

| AWS (default) | Azure equivalent | Note |
|---|---|---|
| App Runner | **Azure Container Apps (ACA)** | See s2 for why ACA over App Service/AKS. |
| RDS Postgres (schema-per-module) | **Azure Database for PostgreSQL - Flexible Server** | Same engine; schema-per-module carries over unchanged (s3). |
| ECR | **Azure Container Registry (ACR)** | Managed-identity pull auth, no static token (s2c). |
| Secrets Manager | **Azure Key Vault** | Fetched via managed identity, not a static key (s2c). |
| CloudWatch (logs/metrics/alarms) | **Azure Monitor + Application Insights** | Monitor = the alarms analog (`observability.md`); App Insights = the APM/tracing layer on top. |
| ALB / CloudFront + WAF (customer-hosting variant) | **Front Door + Application Gateway (with WAF)** | Front Door = global-edge analog to CloudFront; App Gateway = regional L7 analog to an ALB. Pick per the same traffic-shape logic `customer-hosting.md` s2 uses. |
| Bedrock | **Claude in Microsoft Foundry** (or Azure OpenAI, or the direct Anthropic API) | Not a clean lift-and-shift - read s1a before assuming. |
| CloudFormation | **Bicep** (or ARM; Terraform also viable) | See s5's IaC note and the sibling `terraform.md` reference. |
| Microsoft Entra ID auth | **unchanged** | Already Azure-native in the AWS default - see s6. |

**(!) Verify-current, checked 2026-09-11.** Azure product names and tiers in
this space (Container Apps and Foundry especially) move faster than AWS's -
re-confirm before finalizing a design older than a few months.

### 1a. What is actually available for Claude on Azure (verify-current: 2026-09-11)

- **Claude is now GENERALLY AVAILABLE in Microsoft Foundry on Azure** (GA
  complete since June 2026). Claude Opus and Haiku tiers are reachable via
  the Messages API from inside Azure, with Azure-native auth, billing,
  governance, and a global-or-US data-zone inference choice, running on
  Azure-hosted infrastructure (https://azure.microsoft.com/en-us/blog/introducing-anthropics-claude-models-in-microsoft-foundry-bringing-frontier-intelligence-to-azure/,
  https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry).
  Closest analog to "Bedrock in us-east-2" - the call stays inside the
  customer's Azure boundary, usually the whole point of the mandate.
- **Azure OpenAI Service is a separate, OpenAI-model-only (GPT) product** - it
  does NOT host Claude. Don't treat it as a substitute; if the mandate is
  Azure-hosted AI generally rather than Claude specifically, Azure OpenAI is a
  legitimate alternative, but that's a model-choice call in `app-agentic`'s
  provider seam, not a hosting-shape substitution here.
- **The direct Anthropic API** still works inside an Azure-mandated deployment
  (only compute/data plane must be Azure) if the customer's data-handling
  terms allow the model call to egress off-Azure - confirm explicitly; a
  residency-driven mandate usually argues for Foundry instead. Either way,
  `app-agentic`'s swappable-provider seam ("one interface, interchangeable
  backends" - Bedrock via boto3, or the Anthropic API direct) simply gains a
  THIRD backend (a Foundry SDK/REST client) - a registry config choice, not a
  fork of the agent loop.

---

## 2. Azure Container Apps - the App Runner recipe, ported

**Why ACA and not App Service or AKS.** All three run "a container, reachable
over HTTP, autoscaled" - the call comes down to orchestration owned, the same
axis `aws-architecture.md` s3.1 used to pick App Runner over ECS/EKS/Lambda:

| Option | Orchestration owned | Fit |
|---|---|---|
| **Container Apps (recommended)** | Near-zero - Microsoft runs the Kubernetes control plane; you supply a container, ingress, and scale rules. Native revisions (s2b) and KEDA autoscaling incl. scale-to-zero. | Closest match to App Runner's "one service, no cluster to patch" posture - default pick for a single-service tool. |
| **App Service (containers)** | Also low, but container support is secondary to a code-first PaaS; lacks ACA's native revisions/traffic-split and KEDA model. | Fine if the team already runs App Service elsewhere; not the recommended default. |
| **AKS** | High - you own the cluster, node pools, upgrades, ingress end to end. | Only once real orchestration needs (custom CNI/mesh, large multi-team scale) exceed ACA's managed layer - same "don't reach for a cluster you don't need" logic that ruled out ECS/EKS. |

(https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview,
https://developersvoice.com/blog/azure/azure_container_apps_vs_aks_framework/ - verify-current: 2026-09-11.)

### 2a. Environment and ingress (VPN parity)

Every ACA app lives in a **Container Apps Environment** - the analog to the
VPC an App Runner connector reaches into. To mirror `aws-architecture.md`
s3.2's private-ingress-behind-the-VPN posture: create the environment with
**VNet integration** in a customer-owned or firm-managed subnet, and set
ingress to **internal** - the environment-level setting giving an
internal-only endpoint reachable from the VNet and, from there, over the
customer's VPN/ExpressRoute. That is direct parity for `IsPubliclyAccessible:
false`: no public `*.azurecontainerapps.io` hostname resolves off-network.
(https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
Keep the same **unauthenticated liveness route** design as
`aws-architecture.md` s3.1 - ACA's health probe points at it identically.

**(!) Known rough edge, verify-current: 2026-09-11** - Microsoft Q&A has live
threads on internal-ingress reachability issues in VNet-integrated
environments (timeouts, admission-webhook failures). Smoke-test the private
path explicitly before go-live rather than assuming App-Runner-grade parity.

### 2b. Scale rules and revisions (the deploy/rollback analog)

**Scale rules are KEDA-based**, running automatically once defined (no
separate KEDA install). Default min/max replicas are 0-10 (up to 1,000). An
**HTTP scale rule** is the closest analog to App Runner's request-driven
autoscaling, with the same min-size-costs-money tradeoff as `operations.md`
s4-s5 - raise min-replicas above 0 only for cold-start or background-work
reasons. (https://learn.microsoft.com/en-us/azure/container-apps/scale-app)

**Revisions are the deploy/rollback analog.** In **single-revision mode**, a
new image/config replaces the running revision directly (the
`update-service` model). In **multiple-revision mode**, each deploy creates a
new IMMUTABLE revision alongside the old one, with traffic split or cut over
explicitly - closer to blue/green than the AWS default, and it gives a
built-in rollback (shift traffic back) without the AWS default's
retag-`:latest` maneuver (`operations.md` s3). Prefer multiple-revision mode
here - no Azure-side SCP forces a mutable-tag workaround the way AWS prod
does. Migrations still run before the new revision takes traffic - same
MigrateProd-before-DeployProd ordering as `cloudformation-pipeline.md` s3;
the expand-contract discipline in `operations.md` s1 is unchanged.

### 2c. Managed identity to Key Vault and ACR

Assign the Container App a **user-assigned managed identity** (preferred over
system-assigned when IaC needs to reference the identity before the app
exists, e.g. to pre-grant Key Vault access).
(https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
Grant it **Key Vault Secrets User** (RBAC) or an access policy scoped to
`get`/`list` on secrets - the app fetches `DATABASE_URL` at startup via that
identity, never a static vault key, the direct analog to Secrets Manager's
`RuntimeEnvironmentSecret` (`aws-architecture.md` s3.4). Grant the same or a
separate pull-only identity the **AcrPull** role for image pulls, never an
admin-user credential or static token - the ACR analog to the AWS default's
ECR instance-role pull.
(https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-authentication-managed-identity)

**Runtime-not-build-time config is unchanged.** The "fetch environment config
at runtime from an unauthenticated `/api/v1/auth/config` route" principle
(`aws-architecture.md` s4) is platform-agnostic - keep it exactly as designed;
do not bake per-environment Entra values into the image.

---

## 3. Postgres Flexible Server essentials

Flexible Server is the engine-for-engine analog to RDS Postgres; the
schema-per-module pattern and per-module Alembic version-table isolation
(`aws-architecture.md` s3.4, `cloudformation-pipeline.md` s7) carry over
unchanged - only provisioning and connection details differ.

- **Private access (VNet integration).** Deploy with **private access** in a
  delegated subnet of the same VNet as the ACA environment, no public
  endpoint - direct analog to RDS with no public IP.
  (https://learn.microsoft.com/en-us/azure/postgresql/network/concepts-networking-private)
  A private-access server with Entra auth also needs an outbound NSG/route
  rule permitting traffic to the `AzureActiveDirectory` service tag - AWS has
  no equivalent outbound rule for IAM auth, so it's easy to miss.
- **Entra-auth-to-DB** (optional hardening, same posture as AWS's IAM-auth
  option) - Flexible Server natively accepts Entra access tokens for DB login,
  avoiding a long-lived password, the analog to `aws-architecture.md` s3.4's
  IAM-database-auth hardening. Only a Microsoft Entra administrator can enable
  Entra-authenticated DB users; a managed identity can be the authenticating
  principal so the app never holds a password
  (https://learn.microsoft.com/en-us/azure/postgresql/security/security-entra-configure,
  https://learn.microsoft.com/en-us/azure/postgresql/security/security-connect-with-managed-identity).
  Off by default (password-via-Key-Vault, s2c); turn on per environment when
  the customer's posture calls for it.
- **Backups and PITR mirror `operations.md`'s posture, different knobs** -
  retention is configurable **7-35 days** (7 default, same floor guidance as
  `operations.md` s2). PITR covers any moment in the retention window; `az
  postgres flexible-server restore --restore-time <ISO8601>` always creates a
  **new server**, never overwrites the live one - identical in shape to RDS
  PITR. Recovery move: restore to a new server just before the bad change,
  verify, repoint `DATABASE_URL` (now in Key Vault).
  (https://learn.microsoft.com/en-us/azure/postgresql/backup-restore/concepts-backup-restore,
  https://learn.microsoft.com/en-us/azure/postgresql/backup-restore/how-to-restore-latest-restore-point)
- **Geo-redundant backup is create-time-only** - enable it at server creation
  if the customer's DR posture requires cross-region backup copy; it cannot be
  turned on later without recreating the server.
  (https://learn.microsoft.com/en-us/azure/postgresql/backup-restore/how-to-restore-paired-region)
- **Expand-contract migration discipline is unchanged** - `operations.md`
  s1's additive-migration rule has nothing AWS-specific in it.

---

## 4. Networking - VNet, private endpoints, the VPN-parity story

The AWS default is a shared IT-owned VPC Ingress Endpoint, a shared VPC
connector for egress, and the corporate VPN as the reachability boundary
(`aws-architecture.md` s3.2-3.3). The Azure shape mirrors each piece:

| AWS piece | Azure piece | Note |
|---|---|---|
| VPC | **VNet** | Usually lives in the CUSTOMER's own subscription, not the firm's - confirm ownership/RBAC boundaries during design. |
| Shared VPC Ingress Endpoint | **Private Endpoint** (Key Vault, ACR, Flexible Server) + ACA **internal ingress** (s2a) | Azure splits "private reachability for a PaaS resource" from "private reachability for compute" - two mechanisms doing one AWS endpoint's job. |
| Shared VPC connector (egress) | ACA environment's **VNet integration** (outbound) | Handles egress to Postgres, Key Vault, Foundry/Anthropic the way the App Runner connector reaches RDS and Bedrock. |
| Corporate VPN as boundary | **Customer's own VPN or ExpressRoute** into their VNet | Usually already exists, owned by the customer's IT team - often the entire reason Azure was mandated. Confirm reachability requirements with them; do not assume the firm provisions this leg. |

**Parity in one line:** the AWS invariant "never publicly accessible, reachable
only over the VPN plus a validated Entra token" is achievable here too - the
pieces just map across more distinct Azure primitives than AWS's single VPC
Ingress Endpoint concept.

---

## 5. CI/CD - GitHub Actions with Azure OIDC

The suite already has a full GitHub Actions OIDC evaluation and recipe set for
the AWS default - see the app-harness skill, references/github-actions.md.
The Azure version is the same shape with Azure's federated-identity
primitives substituted in:

- **Federated identity credential on a Microsoft Entra application (or a
  user-assigned managed identity), trusting GitHub's OIDC issuer** - the
  analog to the AWS OIDC provider + trust-policy `sub` condition. GitHub
  requests a short-lived OIDC token; Entra trusts
  `token.actions.githubusercontent.com` and exchanges it for a short-lived
  Azure access token - no long-lived Azure client secret in GitHub at all.
  (https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect,
  https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
- **The `azure/login` action** consumes that credential the way
  `aws-actions/configure-aws-credentials` consumes the AWS OIDC role - set
  `permissions: { id-token: write, contents: read }` at job or workflow level
  (same gotcha as the AWS recipe if omitted), and **scope the federated
  credential's subject claim** to a specific repo + branch (or GitHub
  Environment) - the same misconfiguration risk as an unscoped AWS
  trust-policy `sub:*`. Environment-gated prod approval (required reviewers)
  carries over unchanged - a GitHub-side control that does not vary by cloud.
- **(!) Verify-current, checked 2026-09-11** - `azure/login` and the
  federated-credential API surface move on their own cadence; pin and verify
  current minors the way the AWS-side actions are already pinned.

**IaC engine note.** CloudFormation's reusable-template approach
(`cloudformation-pipeline.md` s1) has no Azure equivalent by that name; the
native options are **Bicep** (most direct CloudFormation analog in spirit,
ARM-backed, no state file) or raw **ARM JSON** (Bicep compiles to this - write
Bicep by hand, not ARM), with **Terraform** as a third, cloud-agnostic option
already used elsewhere in the suite. See the sibling `terraform.md` reference
in this same folder for the fuller Bicep-vs-Terraform-vs-ARM tradeoff.

---

## 6. What does NOT change

- **Module contract, FCIS split, schema-per-module data isolation** -
  `app-architecture`'s boundaries care about code/schema organization, not
  which cloud runs the container or database - unchanged for Flexible Server.
- **Microsoft Entra authentication** - already Azure-native in the AWS
  default (`aws-architecture.md` s3.6): one Entra app registration per
  environment, JWT validation against Entra's JWKS, the derived
  `api://<client_id>/access_as_user` scope. Cross-link s3.6 and s4 (runtime
  SPA config-fetch) as-is; do not re-design identity for this variant.
- **The design-doc and security-review lifecycle** - a customer-mandated
  Azure deployment runs the same design-doc gates and sign-off expectations as
  any hosted tool (`wd-design-doc`; the posture `customer-hosting.md` s7
  models). Cloud provider is a decision recorded IN the design doc, not a
  reason to skip the lifecycle around it.
- **The agentic layer's contract** - `app-agentic`'s model registry, budgeted
  tool-use loop, and SpendGuard ledger are provider-seam-based already (s1a);
  a Foundry backend behind the seam changes nothing about the loop or ledger.
- **Migration and rollback discipline** - expand-contract (`operations.md`
  s1) and "verify before trusting a rollback" apply identically; only the CLI
  commands executing a rollback differ (s2b).

---

## 7. What to remember

- **AWS stays the default** - reach for this file only on an explicit
  customer mandate, confirmed via the s0 conversation, never assumed.
- **ACA is the recommended App Runner analog**; multiple-revision mode gives
  a cleaner rollback than AWS's retag-`:latest` maneuver.
- **Flexible Server keeps schema-per-module unchanged** - only provisioning
  (private access, Entra-auth-to-DB, 7-35 day PITR, create-time-only
  geo-redundancy) differs from RDS.
- **Claude on Azure means Microsoft Foundry, not Azure OpenAI** - verify-current
  before finalizing (s1a).
- **CI/CD mirrors the existing GitHub Actions OIDC pattern** with Entra
  federated credentials substituted for AWS's OIDC provider.
- **Identity, module architecture, and the design-doc/security lifecycle do
  not change** - this file only replaces the compute/data/CI-CD hosting shape.
