---
name: app-hosting
description: >-
  Deploy and host a web app or agentic tool on AWS the reference-architecture way: App Runner
  behind the VPN, RDS Postgres, Amazon Bedrock and Microsoft Entra auth, wired by parameterized
  CloudFormation (no new infrastructure code per app). Owns the two-account (dev/prod) pipeline,
  the reusable per-service stack, and runtime config (one image serves dev and prod). Also the
  decision-gated variants (customer-mandated Azure or GCP, Firebase prototypes,
  Terraform/OpenTofu, EKS); AWS stays the default. START HERE to ship a tool to AWS, set up its
  pipeline, or debug a deploy. TRIGGERS: "host this", "deploy to AWS", "App Runner",
  "CloudFormation", "CodeBuild", "RDS", "Entra", "put it behind the VPN", ECR, buildspec,
  promotion, dev vs prod, "how do we run this in production", "host on Azure", "GCP / Cloud Run",
  "Firebase", "Terraform", "Kubernetes / EKS". Hands off to app-architecture (code shape) and
  app-agentic (AI runtime). Patterns only; genericize every account ID, endpoint and URL.
---

# Hosted App AWS Hosting & Deploy

This skill is a thin index over a working AWS hosting playbook proven by a private reference
architecture. Read the reference for the layer you're touching. The governing goal: **stand up a
new tool on AWS without writing new infrastructure - parameterize once, reuse forever.**

## The hosting shape in one breath

A container image (SPA static files + FastAPI, one image) runs on **AWS App Runner** with
**private ingress** (IsPubliclyAccessible: false) behind the corporate VPN, serving on port 8080
with an unauthenticated `GET /health`. State lives in **RDS Postgres** (schema-per-module). The AI
runtime is **Amazon Bedrock in us-east-2**. Users authenticate with **Microsoft Entra** (a single
app registration; the SPA fetches Entra config at runtime from an unauthenticated
`GET /api/v1/auth/config`). Everything is provisioned by **parameterized CloudFormation** - the
same reusable stack for every app.

## The rule that saves the most work

**No new CloudFormation per app.** There is one reusable per-service pipeline template and one
generalized module-service stack, both parameterized. A new tool supplies parameters, not new IaC.
Read [references/cloudformation-pipeline.md](references/cloudformation-pipeline.md) before you
write any infrastructure - odds are you don't need to write any.

## The two constraints that shape every deploy

- **Two-pass, ECR-gated deploy** - the service stack needs an image URI that doesn't exist until
  the pipeline builds it, so the first deploy is two-pass (bootstrap, then deploy gated on
  ECRImageURI). Detailed in cloudformation-pipeline.md.
- **Dev is immutable, prod is mutable - by org policy, not preference.** An org-wide SCP
  denies `apprunner:UpdateService`, so **dev** uses immutable ECR tags + update-service while
  **prod** uses a mutable `:latest` + start-deployment. This is not a style choice; a deploy that
  ignores it fails against the SCP. Runbook in [references/deploy-runbook.md](references/deploy-runbook.md).

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **The AWS architecture** - App Runner private ingress, RDS schema-per-module, Bedrock region, Entra single-registration, VPN front door, runtime-not-build-time config | [references/aws-architecture.md](references/aws-architecture.md) |
| **The CloudFormation + pipeline** - two-account, two-pass, reusable per-service pipeline, generalized module-service stack, buildspec stages (Test to DeployProd), dev-immutable vs prod-mutable | [references/cloudformation-pipeline.md](references/cloudformation-pipeline.md) |
| **The deploy runbook** - step-by-step first deploy and subsequent deploys, the genericize-before-adopt scrub list, common failures | [references/deploy-runbook.md](references/deploy-runbook.md) |
| **Observability (RUN phase)** - structured logging + run_id correlation, CloudWatch alarms (5xx/health/latency, agent failure rate, SpendGuard budget burn), agent-run tracing | [references/observability.md](references/observability.md) |
| **Operations** - migration expand-contract safety + RDS PITR, prod rollback (retag :latest + start-deployment), and hosted-app run-cost/TCO sizing | [references/operations.md](references/operations.md) |
| **Customer-hosting variant (CUSTOMER-SOLD product)** - the public + multi-tenant variant: public ALB/CloudFront + WAF ingress, external identity (Cognito / customer SSO), per-customer provisioning. The INTERNAL architecture above stays for internal tools; this is the paying-customer variant | [references/customer-hosting.md](references/customer-hosting.md) |
| **Azure hosting variant (CUSTOMER-MANDATED CLOUD)** - service mapping, Azure Container Apps recipe, Postgres Flexible Server, networking parity, GitHub Actions + Azure OIDC, Claude via Microsoft Foundry. AWS stays the default; use this only when a customer mandates Azure | [references/azure-hosting.md](references/azure-hosting.md) |
| **Scaling beyond App Runner (EKS)** - the gate for when Kubernetes is actually warranted, EKS Auto Mode vs Fargate vs managed node groups, minimal Deployment/Service/Ingress recipe, kubectl/Helm/GitOps deploy path | [references/kubernetes-eks.md](references/kubernetes-eks.md) |
| **GCP + Firebase lane (customer-mandated / prototype)** - Cloud Run/Cloud SQL/Vertex AI mapping for GCP-mandated production, Firebase (Auth/Firestore/Hosting) as the rapid-prototype lane that gets REBUILT on graduation, BigQuery zero-copy adjacency | [references/gcp-firebase.md](references/gcp-firebase.md) |
| **Terraform / OpenTofu** - the client-mandated / cross-cloud IaC alternative to CloudFormation: decision matrix, state management, module structure, plan/apply workflow, import from CloudFormation, OIDC provider auth | [references/terraform.md](references/terraform.md) |

## Boundaries

- **How the code/module is shaped (module contract, FCIS, schemas):** app-architecture
- **The Bedrock/Anthropic agent runtime + spend metering:** app-agentic
- **Workday tenant auth (wdcli, OAuth for Extend/API):** wd-auth (this skill is Entra/AWS, not Workday)

## Lifecycle neighbors

Runs after app-architecture has shaped the modules and before/alongside app-agentic fills in
the AI runtime. This is the "make it live on AWS" skill.

**Ship gate for this track (not the Workday `quality-gates.md` registry):** before a hosted tool ships, run the conformance checklist in **app-harness** (AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps). The app-* family deliberately does not use the Workday delivery quality-gate footer.

> Modeled on a private reference architecture. **Genericize before adopt:** the reference architecture's real AWS account IDs,
> VPC endpoint IDs, connector ARNs, and App Runner URL are internal topology - never copy them into
> a tool or a skill. The scrub list is in references/deploy-runbook.md.
