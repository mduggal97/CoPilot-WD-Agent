---
name: tool-and-product-build
description: "Use when the work is a general web app, internal tool or agentic tool that is NOT a Workday Extend app: structuring the code into modules, hosting on AWS (App Runner, RDS, Bedrock, Entra, CloudFormation), adding an AI agent runtime (tool-use loop, spend caps, long-running jobs, MCP server), build discipline and guard hooks, integrating with non-Workday SaaS such as Salesforce, ServiceNow, Snowflake, Databricks, Epic or UKG, deciding internal accelerator versus customer product, and operating a sold product (SLA, incidents, billing, customer success, compliance)."
---

# Building and running hosted tools and products (not Workday Extend)

This skill bundles several skills from the Workday Practice Delivery suite.
Each one lives in its own folder with its full method in `GUIDE.md`.

## How to use this skill

1. **Pick the one member skill** below that owns the task.
2. **Read that member's `GUIDE.md` first.** It is the full method. Do not answer from the summary here.
3. **Open only the reference files the guide points to.** Paths inside a guide are relative to that member's folder.
4. **Follow the guide's quality check** before presenting work as final, and report the check result with the deliverable.
5. **Never invent Workday facts.** If the guide and its references do not cover it, say so.

## Reading a guide written for another tool

The guides were written for Claude Code, which runs on the user's own machine. Translate as you read:

- **"SKILL.md" of a named skill** means that skill's `GUIDE.md`.
- **"Invoke skill X" or "route to X"** means open X's guide. Find X in the suite map below.
- **`../<skill>/references/<file>`** points at another member's folder, possibly in another skill.
- **`scripts/...` files are not included here.** Describe what the script does and produce the result by hand, or hand the step off.
- **You cannot run `wdcli`, call a live Workday tenant or Smartsheet, drive a browser, or touch local folders.**
  - Do the design, plan, draft, payload or row values here.
  - Then name the boundary plainly and give the exact steps under a heading **"Finish this on your machine"**.
  - Never say or imply that a live action ran.
- **Never ask for, accept or repeat a password, token or API key.**

## Member skills

### app-architecture

**Use for:** Structure a hosted web app or agentic tool so it can grow from a single service into many without moving code. Owns the module contract (how one liftable unit is shaped), the functional-core/imperative-shell (FCIS) split, schema-per-module data isolation, per-module migrations, and topology independence (a module runs in a monolith or as its own service by changing a composition root, not by moving files). START HERE when scaffolding a new hosted tool, adding a feature module to an existing one, or deciding where code and data boundaries go. TRIGGERS: "new app", "new tool", "add a module", "how should I structure this", "module contract", "monorepo", "extract a service", "composition root", scaffolding, FCIS, import-linter, schema isolation. Hands off to app-hosting for the AWS deploy pipeline, app-agentic for the Bedrock/Anthropic agent layer, and app-harness for the build-discipline loop. Modeled on a private reference architecture - patterns only, no client code copied.

**Start here:** `app-architecture/GUIDE.md`

**Reference files:**

- `app-architecture/references/data-store-decisions.md` - Data Store Decisions - when NOT Postgres
- `app-architecture/references/discovery-and-design-brief.md` - Discovery & Design Brief - the front-end before you scaffold
- `app-architecture/references/estimating.md` - Estimating - sizing a hosted-tool build (LOE + run cost)
- `app-architecture/references/frontend-react-vite.md` - Frontend React/Vite - UI craft for a module SPA
- `app-architecture/references/local-dev.md` - Local Dev - run the whole stack on a laptop
- `app-architecture/references/module-contract-ts.md` - Module Contract - TypeScript/Node Parity Spec
- `app-architecture/references/module-contract.md` - Module Contract - the shape of one liftable unit
- `app-architecture/references/multi-tenancy.md` - Multi-Tenancy - the per-CUSTOMER data-isolation model
- `app-architecture/references/repo-layout.md` - Repo Layout - where everything lives and why
- `app-architecture/references/starter-kit.md` - Starter Kit - the worked example this family lacked
- `app-architecture/references/topology-independence.md` - Topology Independence - repo layout is decoupled from runtime shape

### app-hosting

**Use for:** Deploy and host a web app or agentic tool on AWS the reference-architecture way: App Runner behind the VPN, RDS Postgres, Amazon Bedrock and Microsoft Entra auth, wired by parameterized CloudFormation (no new infrastructure code per app). Owns the two-account (dev/prod) pipeline, the reusable per-service stack, and runtime config (one image serves dev and prod). Also the decision-gated variants (customer-mandated Azure or GCP, Firebase prototypes, Terraform/OpenTofu, EKS); AWS stays the default. START HERE to ship a tool to AWS, set up its pipeline, or debug a deploy. TRIGGERS: "host this", "deploy to AWS", "App Runner", "CloudFormation", "CodeBuild", "RDS", "Entra", "put it behind the VPN", ECR, buildspec, promotion, dev vs prod, "how do we run this in production", "host on Azure", "GCP / Cloud Run", "Firebase", "Terraform", "Kubernetes / EKS". Hands off to app-architecture (code shape) and app-agentic (AI runtime). Patterns only; genericize every account ID, endpoint and URL.

**Start here:** `app-hosting/GUIDE.md`

**Reference files:**

- `app-hosting/references/aws-architecture.md` - AWS Hosting Architecture (reference-architecture pattern)
- `app-hosting/references/azure-hosting.md` - Azure Hosting Variant - when a customer mandates Azure
- `app-hosting/references/cloudformation-pipeline.md` - CloudFormation + Pipeline (reference-architecture pattern)
- `app-hosting/references/customer-hosting.md` - Customer Hosting Variant - public ingress, external identity, multi-tenant
- `app-hosting/references/deploy-runbook.md` - Deploy Runbook (reference-architecture pattern)
- `app-hosting/references/gcp-firebase.md` - GCP + Firebase Lane
- `app-hosting/references/kubernetes-eks.md` - Kubernetes on EKS - the scale-beyond-App-Runner path
- `app-hosting/references/observability.md` - Observability - the RUN phase (structured logs, alarms, agent tracing)
- `app-hosting/references/operations.md` - Operations - migration safety, prod rollback, run cost / TCO
- `app-hosting/references/terraform.md` - Terraform (client-mandated / cross-cloud IaC alternative)

### app-agentic

**Use for:** Add an AI agent runtime to a hosted tool - the layer that calls the model, runs tool-use loops, meters spend, and survives long-running jobs. A swappable provider seam picks Amazon Bedrock via boto3 (the default behind a corporate TLS proxy) or the Anthropic API by config, never by code change. Owns the model registry, the budgeted tool-use loop (run_tool_loop), spend governance to a ledger (SpendGuard), declarative agent specs (model cards), durable async runs that resume after a restart, and hosting an MCP server with a prompt-injection trust boundary. START HERE to make a hosted tool agentic. TRIGGERS: "make it an agent", "call Bedrock", "call Claude", "tool use", "agent loop", "spend cap", "budget", "long-running agent", "background job", "async run", "MCP server", "model routing", boto3, Converse. Hands off to app-hosting for where it deploys and app-architecture for how the module is shaped. Modeled on a private reference architecture - patterns only.

**Start here:** `app-agentic/GUIDE.md`

**Reference files:**

- `app-agentic/references/agent-loop.md` - Agent Loop - budgeted, metered, multi-turn tool use
- `app-agentic/references/durable-runs.md` - Durable Runs - agent jobs that survive a closed tab and a restart
- `app-agentic/references/evals.md` - Evals - output-quality testing for an agentic tool
- `app-agentic/references/mcp-hosting.md` - MCP Hosting - serving tools to other agents over HTTP
- `app-agentic/references/provider-seam.md` - Provider Seam - one model-call interface, two swappable backends
- `app-agentic/references/retrieval.md` - Retrieval - grounding an agentic tool in your own data (RAG)

### app-harness

**Use for:** Run the build with discipline when developing a hosted tool with Claude Code - the "how we build" layer, distinct from the "what we host" layers. Owns complexity routing (Simple: implement; Standard: plan first; Complex: stop for a human design), the stateless-worker model (a supervisor dispatches one-shot workers that coordinate through git and issues), read-only reviewers, commit-at-every-green, mutation-proof testing, and guard-hook templates (secrets/client-data, branch guard, Bedrock/AWS-SSO credential preflight). START HERE to set up a repeatable Claude Code build loop or add guard hooks. TRIGGERS: "build discipline", "how should the agents work", "supervisor", "complexity routing", "review loop", "guard hook", "pre-commit hook", "secrets hook", "client-data guard", "branch guard", "model tier". Hands off to app-architecture, app-hosting and app-agentic for what gets built. Modeled on the jackal, ed3d and superpowers harnesses - patterns only, not copied.

**Start here:** `app-harness/GUIDE.md`

**Reference files:**

- `app-harness/references/complexity-routing.md` - Complexity Routing and Orchestration Invariants
- `app-harness/references/conformance-checklist.md` - Conformance Checklist - grade a hosted agentic tool before it ships
- `app-harness/references/github-actions.md` - GitHub Actions as a CI/CD Alternative (Evaluation + Recipes)
- `app-harness/references/security-hooks.md` - Security and Guard Hooks (Reusable Templates)
- `app-harness/references/testing.md` - Testing - the test pyramid for a hosted tool's own code

### saas-integration

**Use for:** Integrate a hosted tool or product with NON-Workday SaaS: Salesforce, ServiceNow, data platforms (Snowflake, Databricks, Workday Data Connect) and healthcare or higher-ed adjacent systems (Epic/FHIR, UKG, GHX, Kyriba, TouchNet, symplr, Ellucian Banner/Colleague). Owns the decisions: auth, sync style (webhook, polling, batch), idempotency, retries, rate limits, pagination, dead-letter, mapping, iPaaS vs code. TRIGGERS: "integrate with Salesforce", "ServiceNow integration", "Snowflake / Databricks / data platform", "call the X API", "webhook", "OAuth to a SaaS", "iPaaS", "sync data between systems", "ETL / ELT", "reverse ETL", "Epic / FHIR", "UKG / Kronos", "GHX", "Kyriba", "TouchNet", "symplr", "Banner / Colleague", "healthcare or higher-ed adjacent system", "Workday Data Connect / zero-copy". NOT Workday integrations: EIB / Studio / Core Connector go to wd-integration-dev, O4I to wd-extend-dev, Workday auth to wd-auth. The app-* family hosts the runtime that makes these calls.

**Start here:** `saas-integration/GUIDE.md`

**Reference files:**

- `saas-integration/references/data-platforms.md` - Data Platform Integration (Snowflake, Databricks, generic warehouse/lakehouse)
- `saas-integration/references/healthcare-epic-fhir.md` - Healthcare: Epic / FHIR Boundary
- `saas-integration/references/healthcare-highered-adjacents.md` - Healthcare + Higher-Ed Adjacent Systems
- `saas-integration/references/patterns.md` - SaaS Integration Patterns (platform-neutral)
- `saas-integration/references/salesforce.md` - Salesforce Integration
- `saas-integration/references/servicenow.md` - ServiceNow Integration
- `saas-integration/references/workday-from-a-hosted-tool.md` - Workday from a hosted tool - unattended RaaS/WQL/REST calls

### product-strategy

**Use for:** Owns the DISPOSITION DECISION for anything the practice builds - an INTERNAL practice accelerator (a tool the team runs for itself) or a CUSTOMER-SOLD product? - and the productize-an-internal-accelerator lifecycle. The call sets very different bars (support / SLA, GTM, security / compliance / data residency, IP / licensing, TCO, polish), so it is made once, before the build hardens: the "you build it, you run it" question for the practice's own tools. Use when deciding "internal tool or customer product?", "should we productize this", "productize this accelerator", "internal accelerator vs product", "what support / SLA does this need", "is this sellable", "build-it-run-it ownership", or setting the posture for a tool worth building. Comes after market-research. NOT demand validation (market-research); NOT the build or hosting (app-* family); NOT go-to-market for a chosen product (product-gtm, or bow-sales-enablement for the Workday Marketplace).

**Start here:** `product-strategy/GUIDE.md`

**Reference files:**

- `product-strategy/references/disposition-gate.md` - Disposition gate - internal accelerator or customer product?
- `product-strategy/references/productization-lifecycle.md` - Productization lifecycle - turn an internal accelerator into a sellable product

### product-operations

**Use for:** Run a SOLD, customer-hosted product as a business - the Track-2 analogue of wd-post-go-live. Owns everything that starts once a customer is PAYING: SLA tiers and support/incident response, release and deprecation management, billing and metering against the pricing model, customer success (onboarding through renewal), and the operational side of compliance (SOC 2, GDPR/CCPA, security questionnaires). Use when the ask is "run a sold product", an SLA or support tier, incident/on-call/escalation, a status page, a versioning or deprecation policy, billing/metering/entitlements, customer onboarding / success / renewal / churn, SOC 2 or a DPA in practice, a security questionnaire, or "operate a SaaS product". Downstream of product-strategy (sets the support-model bar) and product-gtm (sets the pricing); runs on top of app-hosting (the infra). NOT the Workday post-go-live phase (wd-post-go-live) and NOT the contract paper (wd-contracts) - it operates against both but owns neither.

**Start here:** `product-operations/GUIDE.md`

**Reference files:**

- `product-operations/references/billing-and-metering.md` - Billing and metering - turning pricing into an invoice
- `product-operations/references/compliance-ops.md` - Compliance operations - running the posture, not writing the paper or the audit
- `product-operations/references/customer-success.md` - Customer success - onboarding through renewal, the account-growth analogue
- `product-operations/references/release-management.md` - Release management - versioning and deprecation for a customer product
- `product-operations/references/sla-and-support.md` - SLA and support - the promise you make to a paying customer

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, wd-suite-feedback, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build** (this skill): app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: the Marketplace sales-enablement and product go-to-market skills. If a guide points to `bow-sales-enablement` or `product-gtm`, say that content is not included.
