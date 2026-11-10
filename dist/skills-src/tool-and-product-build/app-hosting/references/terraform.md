# Terraform (client-mandated / cross-cloud IaC alternative)

CloudFormation stays the house default on AWS - see
[cloudformation-pipeline.md](cloudformation-pipeline.md) and
[aws-architecture.md](aws-architecture.md). This file covers the two cases
where that default does not fit: a client mandates Terraform, or the target is
not AWS. For GCP there is no strong native alternative, so Terraform is the
working choice there; for Azure the native option is Bicep, with Terraform as
the cross-cloud alternative - each sibling file carries its own IaC ranking
(plain-text pointers, not skill files here: app-hosting azure-hosting.md and
app-hosting gcp-firebase.md). The module shape below mirrors the CloudFormation
parameterized-stack pattern on purpose, so a team fluent in one can read the
other. All HCL below is an INVENTED ILLUSTRATION of the SHAPE, same convention
as cloudformation-pipeline.md - placeholder values only, never a real account
ID, state bucket name, or endpoint.

---

## 1. Decision matrix - CloudFormation, Terraform, or OpenTofu

| Situation | Use |
|---|---|
| AWS-only, no client mandate, want native drift detection, no state to manage | **CloudFormation** (house default) |
| Client contract or client platform team mandates Terraform | **Terraform** |
| Multi-cloud / cross-cloud (app also ships on Azure or GCP) | **Terraform** (one HCL dialect, three clouds; CloudFormation is AWS-only) |
| Client's licensing stance rules out HashiCorp's BUSL-1.1 terms | **OpenTofu** (the fork) |
| Fluent in CloudFormation, single AWS account, no cross-cloud/licensing driver | **CloudFormation** - don't switch just because Terraform is trendier |

**When to keep CloudFormation even under pressure to switch.** If the ask is
"can we use Terraform" with no client mandate and no cross-cloud need: push
back. CloudFormation already gives no-new-templates-per-app reuse, native AWS
drift detection, and zero state-file custody. Terraform adds the state-
management burden in section 2 to solve a problem the suite does not have yet.

**Terraform vs OpenTofu (verify-current: 2026-09-10).** HashiCorp relicensed
Terraform from MPL-2.0 to the Business Source License (BUSL-1.1) in August
2023; OpenTofu forked from the last MPL-2.0 release, is Linux Foundation
governed, and was accepted into the CNCF in April 2025. Both track their own
1.x lines on the same core HCL syntax (verify the exact patch - both move
monthly); OpenTofu is a near-drop-in CLI replacement for `init`/`plan`/`apply`
but has started to diverge on newer features (it shipped ephemeral-resources /
write-only-attribute work ahead of Terraform) - check the specific feature
before relying on parity. Provider registries are shared either way.

**What does not change regardless of which you pick:** the AWS architecture
target (App Runner private ingress, RDS schema-per-module, Bedrock, Entra) is
the same shape as aws-architecture.md - HCL instead of YAML, not a different
architecture.

---

## 2. State management

Terraform's state file is the thing CloudFormation does not make you own: a
JSON record of every resource's real-world ID, used to compute the next
plan's diff.

- **State is sensitive data.** It commonly contains DB endpoints, secret ARNs,
  and sometimes plaintext attribute values (a password set via a resource
  argument). Treat the state backend like a secrets store - encrypt at rest,
  restrict read access, never widen access "to make CI easier."
- **NEVER commit state to git.** No `.tfstate`/`.tfstate.backup`, ever - not
  even in a private repo. Add `*.tfstate*` to `.gitignore` at the module root;
  a committed state file is a secrets leak, not a hygiene issue.
- **Backend: S3 + native locking (verify-current: 2026-09-10).** The old
  pattern was an S3 bucket for state plus a DynamoDB table for locking.
  Terraform 1.10 added S3 native locking as an experimental `use_lockfile`
  argument on the `s3` backend (a conditional-write `.tflock` object, no
  DynamoDB needed); 1.11 promoted it to GA and deprecated `dynamodb_table`
  (removal planned for a future minor). Prefer `use_lockfile = true` for a NEW
  module; an existing DynamoDB-locked module keeps working - migrate later.

  ```hcl
  # INVENTED ILLUSTRATION - placeholder bucket/key/region only.
  terraform {
    backend "s3" {
      bucket       = "<APP_NAME>-tfstate-<ENV>"
      key          = "<APP_NAME>/<ENV>/terraform.tfstate"
      region       = "<REGION=us-east-2>"
      encrypt      = true
      use_lockfile = true   # native S3 locking, GA since Terraform 1.11 - verify-current
    }
  }
  ```

- **HCP Terraform (formerly Terraform Cloud)** - a managed alternative to
  self-managing S3: hosts state, locking, run history, and policy-as-code
  (Sentinel/OPA), with a free tier. Consider it for a client-facing UI-driven
  approval workflow, or when IAM-scoping a bucket per app costs more than the
  app is worth. A backend choice, not an architecture change.
- **State-per-environment.** Dev and prod get separate state files (separate
  `key` or CLI workspace per env) - never one file describing both. Mirrors
  the two-account split in cloudformation-pipeline.md section 2.

---

## 3. Repo / module structure (mirrors the CloudFormation parameterized-stack shape)

CloudFormation's rule is "no new template per app - supply parameters instead";
the Terraform equivalent is "no new module per app - supply a `.tfvars` file":

```
infra/terraform/
  modules/module-service/    # the ONE reusable app-layer module (mirrors module-service.yaml)
    main.tf                  # App Runner service, ECR repo, IAM roles, secret
    variables.tf             # every input the module accepts
    outputs.tf               # service URL, ECR repo URI, role ARNs
  environments/
    dev/  <APP_NAME>.tfvars, backend.hcl   # one var file + backend config per app, per env
    prod/ <APP_NAME>.tfvars, backend.hcl
```

- **The module boundary is the app-layer stack, not the whole account.** One
  `module-service` module takes `service_name`, `env`, `image_uri`,
  `db_endpoint`, `vpc_connector_arn`, `enable_bedrock`, etc. - the same
  parameter list as `module-service.yaml`. A new app is a new `.tfvars` file
  calling the SAME module, never hand-written resources.
- **Variables/outputs discipline.** Every variable gets a `description` and a
  `type`; anything without a sane default is required. Outputs expose only
  what a caller needs - service ARN, URL, ECR repo URI - not every attribute.
- **No shared "everything" module.** Don't fold pipeline, networking, and app
  layer into one module - same as `module-service.yaml` never defining the VPC
  connector or ingress endpoint (shared, referenced by ARN/ID, never created
  here - aws-architecture.md section 3.2-3.3).

---

## 4. Workflow

- **init / plan / apply, in CI, never from a laptop against shared state.**
  `terraform init` (providers + backend) -> `terraform plan -out=plan.tfplan`
  -> `terraform apply plan.tfplan`. Applying a plan FILE (not re-running
  `apply` bare) guarantees what's applied is exactly what was reviewed.
- **Plan in CI, apply on approval** - the same shape as the CodePipeline
  `ApproveProd` manual gate in cloudformation-pipeline.md section 3: a PR
  triggers `plan` and posts the diff as a comment/check; a human reviews it;
  merge (or an explicit approval job) triggers `apply`. Never let `apply` run
  unattended against prod on every push. For the job wiring (OIDC auth,
  plan-artifact hand-off, environment protection rules), see app-harness
  references/github-actions.md - plain-text pointer, that file owns CI
  mechanics.
- **Drift detection.** Schedule a periodic `terraform plan` (nightly), no
  apply step; a non-empty plan means something changed outside Terraform and
  should alert, not auto-correct. CloudFormation gets this for free.
- **Importing existing (CloudFormation-built) resources.** When an app moves
  from a CloudFormation stack to Terraform management, don't delete-and-
  recreate - use an `import` block (Terraform 1.5+):

  ```hcl
  # INVENTED ILLUSTRATION - id is a placeholder ARN.
  import {
    to = aws_apprunner_service.this
    id = "arn:aws:apprunner:<REGION>:<ACCOUNT_ID>:service/<APP_NAME>-<ENV>/<SERVICE_ID>"
  }
  ```

  Run `terraform plan` after adding the block - it should show the resource
  ADDED with no other changes. If the plan also shows attribute changes, the
  HCL does not match the real resource yet; fix it until the import plan is a
  no-op, THEN apply. Import one resource at a time so each diff is reviewable.
- **Targeted destroys are a danger zone.** `destroy -target=...` bypasses the
  dependency graph and can leave state inconsistent with reality. Reserve it
  for isolated cleanup, always follow with a full `plan` - never as a routine
  "just fix this resource."

---

## 5. Worked minimal example - the App Runner + ECR + RDS shape in HCL

Illustrative SHAPE only, matching aws-architecture.md - placeholder values
throughout, not a real module.

```hcl
# INVENTED ILLUSTRATION - variables.tf + main.tf excerpt, placeholders only
variable "service_name"   { type = string }
variable "env"            { type = string }
variable "image_uri"      { type = string, default = "" }  # empty = bootstrap pass
variable "db_endpoint"    { type = string }
variable "vpc_connector_arn" { type = string }
variable "ingress_vpc_endpoint_id" { type = string }
variable "enable_bedrock" { type = bool, default = false }

resource "aws_ecr_repository" "this" {
  name                 = "${var.service_name}-${var.env}"
  image_tag_mutability = var.env == "prod" ? "MUTABLE" : "IMMUTABLE"
}
resource "aws_secretsmanager_secret" "app" {
  name = "${var.service_name}-${var.env}"
}
resource "aws_apprunner_service" "this" {
  count        = var.image_uri == "" ? 0 : 1   # Pass 2 only - same two-pass gate as CFN
  service_name = "${var.service_name}-${var.env}"
  source_configuration {
    image_repository {
      image_identifier      = var.image_uri
      image_repository_type = "ECR"
      image_configuration { port = "8080" }
    }
  }
  health_check_configuration { protocol = "HTTP", path = "/health" }
  network_configuration {
    ingress_configuration { is_publicly_accessible = false }
    egress_configuration { egress_type = "VPC", vpc_connector_arn = var.vpc_connector_arn }
  }
}
resource "aws_apprunner_vpc_ingress_connection" "this" {
  count       = var.image_uri == "" ? 0 : 1
  service_arn = aws_apprunner_service.this[0].arn
  ingress_vpc_configuration { vpc_endpoint_id = var.ingress_vpc_endpoint_id }  # shared, never created here
}
# RDS is a SHARED instance referenced by endpoint, not created per app.
output "service_url" {
  value = var.image_uri == "" ? "" : aws_apprunner_service.this[0].service_url
}
```

The `count = var.image_uri == "" ? 0 : 1` gate is the direct HCL equivalent of
`Condition: CreateAppLayer` in cloudformation-pipeline.md section 4 - same
two-pass fix for the same chicken-and-egg problem.

---

## 6. Provider auth in CI - OIDC, no long-lived keys

Same principle as the AWS-native pipeline: no static keys in CI config - the
runner exchanges a short-lived OIDC token for cloud credentials at run time.

**AWS provider** - CI job assumes an IAM role trusting the CI platform's OIDC
issuer (GitHub Actions: issuer `https://token.actions.githubusercontent.com`,
audience `sts.amazonaws.com`) before `terraform` runs. Full job wiring: see
app-harness references/github-actions.md.
```hcl
provider "aws" {
  region = "<REGION>"   # credentials via the CI job's assumed role, OIDC federation - no keys here
}
```

**Azure provider** - a federated credential on an Entra app registration
trusts the CI issuer/subject combo, no client secret stored in CI. See
app-hosting azure-hosting.md (plain-text pointer) for the Azure hosting shape.
```hcl
provider "azurerm" {
  features {}
  use_oidc        = true
  subscription_id = "<AZURE_SUBSCRIPTION_ID>"
}
```

**GCP provider** - Workload Identity Federation exchanges the CI job's OIDC
token for a short-lived GCP access token, no service-account key file checked
in. See app-hosting gcp-firebase.md (plain-text pointer) for the GCP/Firebase
hosting shape.
```hcl
provider "google" {
  project = "<GCP_PROJECT_ID>"
  region  = "<REGION>"
}
```

Constant across all three: **no long-lived cloud credential in CI config or a
repo secret** - only a trust relationship to the CI platform's OIDC issuer,
resolved to a short-lived token per run.
