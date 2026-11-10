---
name: wd-scope-and-contract
description: "Use for the front end of a Workday Extend or integration engagement: deciding whether an app or product is worth building (market research, opportunity sizing, build or no-build), reviewing an RFP, estimating level of effort by role and phase, building a timeline or quote, filling the estimate workbook, drafting a statement of work or subscription agreement, and running discovery (intake questions, kickoff questions, current-state documentation, requirements gathering, solution-options assessment)."
---

# Scope, estimate, contract and discovery

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

### market-research

**Use for:** Identify and validate MARKET / PRODUCT opportunities - whether there is unmet demand for an app you could build and ship to a marketplace, and whether it is worth building. Platform-neutral: Workday Marketplace / Built-on-Workday AND any other marketplace or SaaS (Salesforce AppExchange, ServiceNow Store, Microsoft AppSource, standalone SaaS). Use for market research, opportunity or whitespace / gap analysis, "what should we build", a demand assessment, competitive analysis, market sizing (TAM/SAM/SOM), idea prioritization, a build-vs-buy or build/no-build (go/no-go) decision, product-market-fit hypothesis, or an opportunity brief for a new productized app. Use THIS for the upstream "whether and what to build" call; it hands a validated concept to bow-sales-enablement (GTM), wd-estimate (build LOE), and the design skills. NOT client-requirements discovery for a delivery engagement (wd-discovery); NOT go-to-market for an app already chosen (bow-sales-enablement).

**Start here:** `market-research/GUIDE.md`

**Reference files:**

- `market-research/references/assess-and-prioritize.md` - Moves 2-4 - Whitespace, sizing & validation, then score and rank
- `market-research/references/opportunity-signals.md` - Move 1 - Opportunity signals: where demand shows up, and how to read it
- `market-research/references/platform-fit-and-brief.md` - Move 5 - Platform fit, then the opportunity brief + go/no-go

### wd-estimate

**Use for:** Estimate and quote Workday Extend / Integration work - review a customer RFP or opportunity, size level of effort (LOE) by role and phase, build a proposed timeline, and fill the UET (Unified Engagement Tool) workbook. Use this skill whenever the task involves an RFP, RFI, proposal, pursuit, quote, pricing, LOE, level of effort, scoping an opportunity, staffing plan, estimate, "how many hours", or the UET - even informal "what would this roughly take?" questions.

**Start here:** `wd-estimate/GUIDE.md`

**Reference files:**

- `wd-estimate/references/bow-pricing-and-value.md` - BoW / Marketplace pricing - the estimation-side slice
- `wd-estimate/references/calibration.md` - Estimation calibration - archetypes and program history
- `wd-estimate/references/flex-credits.md` - Flex Credits + API metering - the canonical fact block (single owner)
- `wd-estimate/references/proposal-content.md` - Proposal & pitch content - selling the work, not just pricing it
- `wd-estimate/references/sow-handoff.md` - Pre-sales qualification + SOW handoff
- `wd-estimate/references/uet-guide.md` - UET (Unified Engagement Tool) - fill procedure
- `wd-estimate/references/win-loss.md` - Win/loss debrief - the pursuit-side feedback loop

### wd-contracts

**Use for:** Draft Workday Extend contract documents - statement of work (SOW), SaaS agreement, subscription agreement, provisioning SOW, engagement letter, scope language, contract terms. Use this skill whenever the task involves a contract, "draft the SOW", an SOW for a Marketplace/BoW app subscription, a SaaS/subscription agreement for a firm-built app, contract scope/assumptions/exclusions language, term/renewal/fees sections, or turning a won estimate into contract paper. The docx skill owns Word mechanics; wd-estimate owns the estimate/assumptions/pricing that feed the SOW; this skill owns contract structure and drafting.

**Start here:** `wd-contracts/GUIDE.md`

**Reference files:**

- `wd-contracts/references/saas-agreement.md` - SaaS Agreement - section-by-section drafting guide
- `wd-contracts/references/saas-data-processing.md` - SaaS Data Processing, Residency & Subscription Security - contract paper for a hosted product
- `wd-contracts/references/services-sow.md` - Professional-Services SOW - content skeleton (bespoke Extend build)
- `wd-contracts/references/sow.md` - Provisioning SOW - section-by-section drafting guide

### wd-discovery

**Use for:** Run Workday Extend and integration discovery - plan requirements gathering, generate intake/kickoff questions, document current state, and structure greenfield scoping. Use whenever the user mentions discovery, discovery call prep, a scoping session, requirements gathering, current state, intake questions, kickoff questions, or asks "what should we ask the client" for an Extend app or integration build. Also use when preparing for a first client session on a new use case, reviewing a discovery doc, or turning DISCOVERY-session notes into structured discovery/requirements output. (A meeting transcript, recording, or notes meant to UPDATE a design or tracker belongs to wd-pm meeting intake; this skill owns discovery-session capture.)

**Start here:** `wd-discovery/GUIDE.md`

**Reference files:**

- `wd-discovery/references/discovery-to-design.md` - From Discovery to Design Doc
- `wd-discovery/references/functional-analytics.md` - Functional literacy - Analytics & Reporting
- `wd-discovery/references/functional-financials.md` - Functional literacy - Financials
- `wd-discovery/references/functional-hcm-talent-rewards.md` - Functional literacy - Talent Acquisition/Development & Rewards
- `wd-discovery/references/functional-hcm.md` - Functional literacy - HCM Core, Security, Time & Absence
- `wd-discovery/references/functional-payroll.md` - Functional literacy - Payroll & Global Payroll Connect
- `wd-discovery/references/functional-student.md` - Functional literacy - Workday Student (higher-ed SIS)
- `wd-discovery/references/integration-discovery.md` - Integration Discovery Questionnaire
- `wd-discovery/references/solution-options.md` - Solution Options Assessment - Decide WHAT to Build Before Designing It
- `wd-discovery/references/workday-functional-skus.md` - Workday Functional SKUs - domain literacy for delivery

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract** (this skill): market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: `bow-sales-enablement`, `product-gtm`, `wd-suite-feedback`. If a guide points to one of these, say that content is not included.
