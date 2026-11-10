---
name: wd-extend-build
description: "Use for building, changing, reviewing or debugging a Workday Extend app or an Orchestrate for Integrations (O4I) orchestration: PMD pages, pods, scripts, business objects, security domains, Model business processes, wdcli commands, coding standards, platform limits, code review and audits, reading Workday data with WQL or RaaS or custom reports, Prism, custom agents and GenAI calls. Also use for Workday authentication: OAuth API clients, tokens, credential storage, login failures such as 401, 403, invalid_grant or tenant not found, and choosing an auth mode."
---

# Workday Extend and Orchestrate build, and authentication

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

### wd-extend-dev

**Use for:** Build, modify, review, and deploy Workday Extend apps and O4I (Orchestrate for Integrations) orchestrations - and pull/list/report on Workday records. Use whenever the work touches an Extend app or O4I flow: PMD pages, pods, cards, scripts, business objects, security domains, Model BPs, wdcli commands (create/upload/deploy/download), PoC builds, code review or audits of Extend/O4I source, or "add a field / change a page / fix a bug". Also OWNS reading Workday data - "get me a list of employees", workers, orgs or any records via RaaS, WQL, or a custom report / calculated field. Even one-line PMD changes hide runtime landmines; consult before editing. Also covers limits, coding standards, UI design, Prism/reporting, custom agents, and GenAI calls. Traditional integrations (EIB, Studio/CLAR, Core Connector, Document Transformation, XSLT) and integration naming (INT IDs, ISU/ISSG) are wd-integration-dev; a domain's config objects and web services are wd-solution-playbooks.

**Start here:** `wd-extend-dev/GUIDE.md`

**Reference files:**

- `wd-extend-dev/references/app-catalog-registry.md` - Workday App Catalog - sample registry (which sample shows X)
- `wd-extend-dev/references/app-review-audit.md` - App & integration review/audit - the playbook and the findings report
- `wd-extend-dev/references/architecture-review.md` - Architecture Review - the Internal Pre-Build Gate
- `wd-extend-dev/references/build-from-scratch.md` - Build from scratch - compose any Extend/O4I artifact from primitives
- `wd-extend-dev/references/charts.md` - PMD charts (Chart 2.0) - widget vocabulary
- `wd-extend-dev/references/custom-agents.md` - Workday-native custom agents - the build model (DevCon 2026, forward-looking)
- `wd-extend-dev/references/data-conversion.md` - Data conversion / migration - as a BUILD workstream
- `wd-extend-dev/references/data-loading-and-retrieval.md` - Data loading and retrieval - the load-in / read-out hub
- `wd-extend-dev/references/dev-tenant-migration.md` - Migrating an Extend app to a NEW developer tenant (dev-tenant expiry / refresh)
- `wd-extend-dev/references/domain-apply-safety.md` - Security Domain Apply - Safety Design
- `wd-extend-dev/references/domain-patterns-hc-highered.md` - Domain patterns - Healthcare & Higher-Ed (discovery/design cheat-sheet)
- `wd-extend-dev/references/efficiency.md` - Efficient PMD/script patterns - externalized WQL, compute-once, set-based helpers
- `wd-extend-dev/references/error-handling.md` - Error handling, logging, retries, and recovery
- `wd-extend-dev/references/external-apis-and-genai.md` - Calling external APIs (incl. GenAI/LLMs) from an Extend app
- `wd-extend-dev/references/model-bp.md` - Custom Business Process on a BO ("Model BP") - verified schema
- `wd-extend-dev/references/model.md` - Business objects, fields, BO REST API, security domains
- `wd-extend-dev/references/orchestration-nodes.md` - O4I node catalog - config keys and minimal JSON shapes
- `wd-extend-dev/references/orchestration.md` - Orchestrations / O4I - flows, node vocabulary, limits, call patterns
- `wd-extend-dev/references/pmd-gotchas.md` - PMD runtime gotchas - the build validator does NOT catch these
- `wd-extend-dev/references/pmd.md` - PMD / presentation layer - app anatomy, widgets, layout
- `wd-extend-dev/references/prism-and-reporting.md` - Prism & reporting - building the analytics side as a delivery workstream
- `wd-extend-dev/references/private-ws-loading.md` - Private web services loading - guided workflow
- `wd-extend-dev/references/release-impact.md` - Workday release (R1/R2) impact on in-flight builds
- `wd-extend-dev/references/report-writer-admin.md` - Report Writer, calculated fields, and report administration
- `wd-extend-dev/references/rest-api-catalog.md` - Workday REST API catalog (local OpenAPI snapshot)
- `wd-extend-dev/references/scripts.md` - Scripts this skill references - regenerate-on-demand build-specs
- `wd-extend-dev/references/security-setup.md` - Security & access setup - ISUs, domains, API clients, who does what
- `wd-extend-dev/references/solutioning.md` - Solutioning - design the best fit, not the familiar one
- `wd-extend-dev/references/standards.md` - Coding standards - naming, comments, change logs
- `wd-extend-dev/references/tenant-ops.md` - Live tenant operations - check, verify, load
- `wd-extend-dev/references/tenant-state-verification.md` - Tenant-state verification cookbook - to confirm X, read Y
- `wd-extend-dev/references/ui-design-principles.md` - UI design principles - how to design an ENGAGING PMD app (the craft layer)
- `wd-extend-dev/references/wdcli-setup.md` - wdcli - install, verify, sign in, and fix common errors (novice guide)
- `wd-extend-dev/references/wdcli-workflow.md` - wdcli - the build/deploy workflow
- `wd-extend-dev/references/widget-catalog.md` - PMD widget catalog - per-widget property reference + Grid deep-dive
- `wd-extend-dev/references/workflow.md` - Change workflow - pull-latest, diff, change-lists, design-to-code validation
- `wd-extend-dev/references/wql.md` - WQL (Workday Query Language) - language and invocation reference

### wd-auth

**Use for:** Workday authentication, credentials, and OAuth setup across all surfaces - wdcli, REST/SOAP/WQL/RaaS APIs, tenant UI, and the developer portal. PREFLIGHT GATE: consult BEFORE the first wdcli command in a session, BEFORE opening any Workday URL in the in-app browser (no SSO session there, so a login handoff is needed), and BEFORE any API call - to catch expired tokens and wrong-org state early. TRIGGERS: storing credentials, API tokens or secrets, configuring OAuth API Clients, auth failures (401, 403, token expiry, invalid_grant, invalid_client, "not logged in", "tenant not found or is not a development tenant", S22 permission denied), choosing an auth mode (wdcli vs refresh vs basic vs PKCE), rotating or revoking credentials, multi-org switching (wdcli account switch, wdcli whoami), MFA/SSO constraints, or "why can't the agent log in for me" / "how do I connect Claude to the tenant". Owns the auth DECISION; wdcli install, the build loop, and ISU/ISSG grants live in wd-extend-dev.

**Start here:** `wd-auth/GUIDE.md`

**Reference files:**

- `wd-auth/references/auth-decision-tree.md` - Auth decision tree - which mode for which task
- `wd-auth/references/auth-preflight.md` - Auth preflight check - run before every build/deploy/API session
- `wd-auth/references/auth-troubleshooting.md` - Auth troubleshooting - consolidated error table
- `wd-auth/references/credential-store-setup.md` - Credential store setup
- `wd-auth/references/mfa-and-browser-auth.md` - MFA, SSO, and browser auth - what the agent can and cannot do
- `wd-auth/references/oauth-setup-guide.md` - OAuth API Client setup & debugging - end-to-end guide

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build** (this skill): wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: `bow-sales-enablement`, `product-gtm`. If a guide points to one of these, say that content is not included.
