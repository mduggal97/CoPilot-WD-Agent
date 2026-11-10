---
name: wd-extend-lifecycle
description: The map of the Workday Extend/Integration delivery lifecycle and its mandatory steps - and the GUIDED walkthrough that leads any user (novice to expert, colleague or client) through a project start to finish with enforced quality gates. Use this skill when starting a new Extend or integration project or phase, when the user says "walk me through it" / "what do I do next" / "I've never done this before", when asking "what's next / what am I forgetting / which skill handles X", at project kickoff, when planning phase transitions (design sign-off, build complete, go-live approaching), or for the checklist of Workday-required documents (Volumes Questionnaire, Performance Testing) and client prerequisites. Invoke directly with /wd-extend-lifecycle for the full phase map. Also the entry point for suite setup on a new machine ("set up this suite for me" - prerequisites, Python packages, script regeneration) and for "which skill handles X" routing questions.
---

# Workday Extend / Integration Delivery Lifecycle

This skill is the router: which skill owns each phase, plus the guide for when you want to be LED through a project rather than handed a map. When work is clearly inside one phase, go straight to that phase's skill and come back here at transitions.

## What do you want to do?

Describe your task in plain words and the matching skill loads. Common starting points:

- **"How much would this cost?" / review an RFP / size the hours** -> wd-estimate
- **"We won the deal - what's next?"** -> the phase map below, or [references/guided-delivery.md](references/guided-delivery.md) to be led step by step
- **Draft the SOW / contract** -> wd-contracts
- **Run discovery / "what should I ask the client?"** -> wd-discovery
- **"What web services or config objects are behind <domain>?"** -> wd-solution-playbooks
- **Write the design doc** -> wd-design-doc ; **wireframe / process flow / diagram** -> wd-design-visuals / wd-systems-diagrams
- **Build an Extend app or O4I orchestration / add a field / pull a list of records** -> wd-extend-dev
- **Build an EIB / Studio / Core Connector integration** -> wd-integration-dev
- **"Connect to the tenant" / login / a 401 or token error** -> wd-auth
- **Test the app in the browser** -> wd-test-execution ; **derive scenarios / triage a defect vs CR** -> wd-testing
- **Set up the tenant or create test data (live)** -> wd-tenant-config ; **the setup recipe + security model** -> wd-deployment
- **Deploy / cutover / go-live** -> wd-deployment ; **the app is live / an integration failed in prod** -> wd-post-go-live
- **Update the tracker** -> wd-smartsheet ; **draft a client email** -> wd-comms ; **user/admin guide** -> wd-kt ; **change management** -> wd-change-adoption
- **Report a problem with a skill / a gap** -> wd-suite-feedback ; **how does a full Workday program run?** -> wd-delivery-methodology

> **Wrong track?** This router is the **Workday delivery** map. Building a general **web app or agentic tool** (hosted on AWS, NOT a Workday Extend app)? That's the other track -> **app-architecture** (or **practice-lifecycle** if you're not sure which track you're on). Deciding **whether** to build a product at all -> **market-research** (platform-neutral).

> The gates and preflights that make delivery rigorous fire at **session start** and **when you ship** - they do NOT gate getting started. They live in **The rigor** section further down.

## Phase map

| Phase | What happens | Skill |
|---|---|---|
| RFP / Estimation | Review RFP, size LOE by role x phase, timeline, UET quote, proposal/pitch content | **wd-estimate** |
| Contracting | Draft the SOW / SaaS agreement from the estimate (always a draft for legal review) | **wd-contracts** |
| Discovery | Current-state intake or greenfield framework; integration questionnaire | **wd-discovery** |
| Design | Design doc (16-tab / BoW / IDD / customer), gap analysis, change control | **wd-design-doc** |
| Design visuals | Wireframes (Balsamiq) + process flows (swimlane / flowchart) | **wd-design-visuals** |
| PoC + Development (Extend app + O4I) | wdcli loop, PMD/orchestration builds, standards, co-ownership workflow | **wd-extend-dev** |
| Integration build (EIB / Studio / CC / DT) | Traditional integration build + naming + per-type build gates + XSLT | **wd-integration-dev** |
| Testing (design + record) | Unit scenarios (derived at design time!), UAT support, defect/CR triage, API-driven headless harness | **wd-testing** |
| Testing (browser execution) | DRIVE the in-app Browser pane through the test plan against the running app + tenant; assert + capture evidence; feed pass/fail back to wd-testing | **wd-test-execution** |
| Deployment / Cutover | Tenant promotion, Workday prod approval + gating docs, cutover, conversion | **wd-deployment** |
| In-tenant setup + test data (browser execution) | DRIVE the in-app Browser pane to run the tenant-setup recipes + create synthetic test data live, plan-first / confirm-each-write, dev tenants only (executes wd-deployment's recipe content) | **wd-tenant-config** |
| Post-Go-Live | Hypercare, adoption + value capture, retention/export, release regression, QBR/renewal, closeout actuals | **wd-post-go-live** |
| Cross-cutting | Session authentication + credential/token/OAuth preflight - run the auth preflight BEFORE the first wdcli/API/tenant action in a session (**wd-auth**) / PM routines/status/RAID + steering + meeting intake (transcripts->artifacts) (**wd-pm**) / Smartsheet transport (**wd-smartsheet**) / client comms (**wd-comms**) / knowledge transfer (**wd-kt**) / change management + user adoption, the OCM workstream (**wd-change-adoption**) / demos at any phase (**wd-demo**) / project-folder archiving (**wd-folder-hygiene**) / system-level integration landscape diagrams (**wd-systems-diagrams**) / found a suite problem / missing capability / a skill was wrong (**wd-suite-feedback**) | |
| Design input (per functional domain) | Per-domain TECHNICAL SOLUTION PLAYBOOKS - config objects + web services + RaaS/WQL sources + delivered connectors + named donors + design gotchas for HCM/recruiting/time/absence/talent/learning/comp/benefits/payroll/financials/projects-PSA/grants/student/analytics (**wd-solution-playbooks**) - open the domain playbook at solutioning before designing a build that touches that area | |
| Practice-level (not one engagement) | Practice operations - consultant onboarding/enablement, competency + certification tracking, cross-engagement staffing/utilization/capacity, and the Workday partner/alliance relationship, plus the reusable-asset / IP catalog that spans engagements (**wd-practice-ops** - references/reuse-and-asset-catalog.md) | |
| Full-program delivery methodology (vendor-neutral) | The phase model for a complete Workday deployment (HCM/FIN/Student/Adaptive/Prism), role playbooks + workstream RACI, standing delivery norms, the configuration-guide pattern, and the specialty tracks ("how does a full Workday program run end to end") (**wd-delivery-methodology**). A firm-private methodology skill, where installed, layers on top and wins on conflict. | |

**Before ingesting client material into AI tooling:** read [references/ai-data-governance.md](references/ai-data-governance.md) - the AI/Claude data-handling gate, human-review obligation, disclosure + IP-provenance rules.

**MANDATORY - session auth preflight (run FIRST):** BEFORE the first `wdcli` / API / tenant action in a session, run the **wd-auth** auth preflight ([wd-auth/references/auth-preflight.md](../wd-auth/references/auth-preflight.md)) - it confirms tokens are valid, the active account/org is the intended one, and the right auth mode is selected, so a build/deploy/API call does not fail later with a misleading "tenant not found" / 401 / invalid_grant error. This is a hard gate; it runs ahead of the operational checks below.

**At the START of any build / tenant session:** after the wd-auth preflight above, run the [references/operational-preflight.md](references/operational-preflight.md) checks - where am I (target tenant is dev not prod), is my copy current (pull-latest + diff), am I about to load the RIGHT version (upload-before-deploy), will I verify it landed. Ten seconds of pre-flight beats an hour chasing a wrong-version / stale-code ghost. It is the "session pre-flight" quality gate.

**MANDATORY - measure twice BEFORE you touch a script (requirements-first gate):** before writing or modifying ANY build artifact, capture the requirement set - functional + data/integration + **SECURITY (mandatory)** + tenant prereqs + NFRs - derived from the design and the owning skills, not remembered. **A blank/unresolved SECURITY section (domains, ISU, ISSG, API-client scopes) is a HARD STOP - do not build until it's enumerated.** Full gate + where each requirement is sourced: [references/quality-gates.md](references/quality-gates.md) ("Measure twice - the pre-build requirements gate"). This is the codified "measure twice, cut once": the tools to know what's required already exist; use them up front.

**Automate-first (STANDING):** for build/config/test, DEFAULT to automating via API / wdcli / in-app browser (plan-first + confirm-each-write, dev tenants only); prompt the user ONLY for the strictly-disallowed set (security policy ACTIVATION, credential/MFA entry, production, CAPTCHAs, settings/consent). The canonical policy + the disallowed-only handoff list live in wd-extend-dev `references/tenant-ops.md`.

### Common mis-routes

- App won't build/deploy in DEV (wdcli errors) -> **wd-extend-dev** references/wdcli-setup.md. Promoting past DEV / production approval -> **wd-deployment**.
- Client security/InfoSec questionnaire -> **wd-deployment** references/security-questionnaire.md - NOT the Workday-issued Volumes Questionnaire (that's the platform gating doc, also wd-deployment).
- Building/modifying an **O4I orchestration flow** -> **wd-extend-dev**; building a **traditional integration** (EIB / Studio / CLAR / Core Connector / Document Transformation / XSLT) or setting integration naming (INT IDs / ISU / ISSG) -> **wd-integration-dev**.
- Building a **Workday Extend app / O4I** (runs inside Workday) -> **wd-extend-dev**; building/hosting a **general web app or agentic tool on AWS** (React SPA + FastAPI + App Runner + Bedrock/Entra, not a Workday app) -> the **app-*** track (architecture / hosting / agentic / harness - see the sibling track below).
- Calling **Claude / GenAI / doing tool-use** FROM a Workday PMD page or O4I flow -> **wd-extend-dev** references/external-apis-and-genai.md; the agent runtime of a **hosted tool** (provider seam, tool-loop, spend cap, durable runs) -> **app-agentic**. Same words, two runtimes.
- Any **security** question routes via the ownership map in **wd-deployment** references/security-role-design.md: designing the client's END-USER security MODEL (roles, groups, SoD) lives there; an Extend APP's runtime security -> **wd-extend-dev** security-setup.md; an INTEGRATION's ISU/ISSG/segments -> **wd-integration-dev**; the client TECHNICAL TEAM's access -> this skill's customer-technical-roles.md.
- Deriving test scenarios / the Unit Testing tab / triage -> **wd-testing**; DRIVING the browser through the plan live (execute + evidence) -> **wd-test-execution**. Both are testing; one authors, one runs.
- Tenant-setup recipe CONTENT + the security model -> **wd-deployment**; EXECUTING that setup live in the browser (+ creating test data) -> **wd-tenant-config**. One owns the steps, one runs them.
- Auth failure (401 / 403 / token expiry / invalid_grant / invalid_client / "not logged in" / "tenant not found or is not a development tenant" / S22), storing a token/secret, OAuth/API-Client setup, wrong-org / account switching, "why can't the agent log in for me" -> **wd-auth** (run its auth-preflight.md BEFORE the first wdcli/API/tenant action).
- Found a suite problem / a skill was wrong, missing, or hard to use / a learning to fold in / a change proposal for a skill -> **wd-suite-feedback** (files a structured, triageable record for the maintainer).
- Full-program delivery methodology / phase model / RACI / role playbook / config-guide pattern / governance + delivery norms / specialty tracks / "how does a full Workday program run end to end" -> **wd-delivery-methodology**. The Extend/Integration phase map + gates + routing stay in THIS skill. A firm-private methodology skill, where installed, layers on top and wins on conflict.

**Routing confidence rule:** route silently only when **>=2 signals** point at the same skill - a trigger phrase plus a matching artifact type, or a phrase plus the current phase context. On a single ambiguous signal, ask ONE clarifying question and include a recommended answer ("sounds like a UAT defect -> wd-testing; if it's actually a design change, say CR and we'll take the Change path"). Never stack multiple clarifying questions - that's default-and-flag applied to routing.

## Change/enhancement path (the app is already live)

The greenfield phase map above assumes a net-new build. When the work is a **change to a live app** - enhancement, CR, post-go-live feature - the greenfield kickoff checklist does NOT apply. Entry conditions instead: **latest source pulled** (`wdcli app download`), **latest signed design doc located**, **CR approved** (no build on an unapproved CR). Then run this path:

| Step | Skill / reference | What happens |
|---|---|---|
| Intake | **wd-pm** references/raid-log.md (CR log) | CR logged with impact/approval fields |
| Scoping | **wd-extend-dev** references/app-review-audit.md + **wd-discovery** Playbook C | Audit current state from artifacts; delta-map only changed behavior |
| LOE (i) | **wd-estimate** (enhancement sizing) | Size against the enhancement archetype; regression + doc-refresh overhead included |
| Approval | **wd-design-doc** references/change-control.md; **wd-contracts** (change-order paper) (i) | Design baseline amended; change order vs new SOW decided (i) |
| Build | **wd-extend-dev** references/workflow.md | Pull-latest + diff; change-list mode when a client dev owns the code |
| Regression | **wd-testing** ("Regression scope for a change") | Changed-surface + critical-path set; full suite for schema/security/shared-code changes |
| Redeploy gate | **wd-deployment** references/marketplace-recert.md | Check the trigger table - does prod approval / recert re-trigger for this change? |
| Promote | **wd-deployment** | Promote the delta + per-tenant re-setup (promotion still carries no security/config) |
| Release notes + comms | **wd-kt** (release-notes pattern) + **wd-comms** templates section 7 | What changed / opt-in vs automatic / action required; changed-behavior notice to users |
| Doc refresh | **wd-kt** + **wd-deployment** + **wd-design-doc** | User/admin/deployment guides updated; design doc minor version bump |
| Close | **wd-pm** (CR log) + **wd-estimate** calibration (i) | CR marked Implemented; actuals written back (i) |

(i) = firm-internal step. **Client-side users following this path:** size the change with your own estimating practice, skip contract paper unless a firm engagement covers the work, and skip the calibration write-back - everything else applies unchanged.

## Kickoff checklist (day-0 blockers - start these BEFORE design)

Each of these has a lead time measured in weeks when it goes wrong; raise them at kickoff, not when blocked:

- [ ] Client owns Workday Extend / Innovation Services (SKU confirmed; capacity tier known). O4I enablement is a client-runnable opt-in for MSA customers: **Innovation Services and Data Selection Opt-In** report (WCP -> "Workday Orchestrate for Integration") + **Maintain Workday Build Company for Orchestrate for Integration**; UMSA customers have it automatically (per Workday Admin Guide (Integrations), Jul 2026 - detail: wd-deployment references/promotion-and-environments.md)
- [ ] Developer tenant access + App Manager rights for the build team; client dev-org account created
- [ ] Workday Community accounts for the team
- [ ] Tenant landscape mapped (dev / impl / sandbox / prod aliases + refresh schedule - sandbox refreshes weekly; unmigrated config is wiped)
- [ ] Client security-admin contact identified + their turnaround SLA (drives ISU/domain-grant timing - see wd-extend-dev security-setup)
- [ ] **Client technical-role owners identified + staged access plan started** - who on the client side owns integrations / Extend / Prism / reporting / security, and the phased provisioning + enablement plan that gets each productive early (references/customer-technical-roles.md; access milestones go on the project plan)
- [ ] SFTP / middleware / vendor request processes identified for integrations (vendor lead times gate timelines)
- [ ] Project tracker + RAID log stood up (wd-pm / wd-smartsheet); design-meeting transcript habit agreed (wd-pm meeting-intake)
- [ ] **Client onboarding packet issued** - "what we need from you and when" with named owners (wd-pm references/client-onboarding-packet.md)
- [ ] **Sponsor charter + decision-rights table set** - who decides what, with turnarounds; the CR log's Approval Body points here (wd-pm references/steering-committee.md)
- [ ] **AI-use terms confirmed** (the firm's AI policy + client MSA AI/confidentiality terms) and recorded in the engagement file - references/ai-data-governance.md
- [ ] **Regulated-data access cleared BEFORE any tenant access/ingestion** - for a PHI (healthcare) or FERPA-education-record (higher-ed) engagement, the BAA / data-handling agreement is confirmed EXECUTED before a consultant touches the tenant or its data (references/ai-data-governance.md section 1). Accessing PHI/FERPA before the paper is signed is a compliance breach, not a paperwork lag.

## The rigor - session start and ship time

The suite's quality backbone. These fire at the START of a session (preflights) and when you SHIP a deliverable (gates) - not when you begin exploring. Skip none when finalizing work.

- **[references/guided-delivery.md](references/guided-delivery.md)** - the walkthrough mode: leads any user (novice -> expert, colleague or client-side) through a project start to finish with a per-project Delivery Tracker and phase exit gates. Use it whenever the user wants to be LED, not handed a map.
- **[references/quality-gates.md](references/quality-gates.md)** - the every-time registry: every artifact type -> its named check. No artifact ships without its check, and the result is reported with the deliverable. All skills' gates in one table.
- **[references/writing-quality-gate.md](references/writing-quality-gate.md)** - the AI-draft -> release-ready writing check (no em dash, AI-tell sweep, context-profile strictness, human-in-the-loop) for ANY client-facing or external text; wd-comms / wd-estimate proposal-content / bow-sales-enablement / wd-kt point here.
- **[references/deliverable-review.md](references/deliverable-review.md)** - the content/argument review above the writing gate: read the deliverable in the RECEIVER'S voice, pre-mortem, verify claims, verdict + located fixes, and the "read-the-room" strategic flags. Run before any client/senior-facing deliverable ships.
- **[references/operational-preflight.md](references/operational-preflight.md)** - the start-of-session checks (pull-latest+diff, upload-before-deploy, verify-live, re-seed) that prevent wrong-version / stale-copy time-sinks; the AUTH portion (whoami org/account, token freshness) is owned by **wd-auth** references/auth-preflight.md.
- **[references/verify-in-tenant.md](references/verify-in-tenant.md)** - the standing "trust-but-verify" rule: never assume tenant state - read it programmatically (WQL / REST / RaaS / SOAP) before you rely on it. Fires before you reference/create/design-against tenant data and after any write; the "to confirm X, read Y" detail lives in wd-extend-dev references/tenant-state-verification.md.
- **[references/customer-technical-roles.md](references/customer-technical-roles.md)** - the client's technical counterparts (integrations / Extend / Prism / reporting / security): role model, staged least-privilege access plan (provision early so they can learn), enablement path.

## The mandatory-steps checklist (Workday-required + house-required gates)

| Gate | Required item | When | Owner skill |
|---|---|---|---|
| **Session auth preflight** | **Auth preflight** - tokens valid, active account/ORG is the intended one, right auth mode selected (catches expiry / wrong-org / missing-cred before a misleading failure) | BEFORE the first wdcli/API/tenant action in a session | wd-auth (references/auth-preflight.md) |
| Discovery close (net-new apps) | **Solution-options assessment** - approach matrix + recommendation + named client approver (the "should this even be Extend?" record) | Before design starts | wd-discovery |
| Design sign-off | Design doc complete per gap analysis; unit-test scenarios captured; visuals embedded (clean export) | End of design | wd-design-doc |
| Before build start | **Architecture review** - internal, reviewer != designer; ADR-lite appended to the Tech Spec tab | After design sign-off (or before PoC promotion) | wd-extend-dev |
| Before build on shared apps | Pull-latest + diff; change-list mode if client dev active | Every edit | wd-extend-dev |
| Before prod approval | **Extend Volumes Questionnaire** (.xlsm, per app) | Weeks before go-live - Workday review lead time | wd-deployment |
| Before prod approval | **Performance Testing Template** (required when >50K annual transactions) | With the Volumes Questionnaire | wd-deployment |
| Each tenant promotion | Security re-setup (domains, ISU, App Attributes, BP config) - promotion does NOT carry these | Every tenant | wd-deployment |
| Integration promotion | Integration System + RaaS reports promote SEPARATELY from the app | Every tenant | wd-deployment |
| Go-live | Cutover plan (conversion, legacy off/new on, rollback), go/no-go | Cutover week | wd-deployment |
| Closeout | Actuals vs estimate recorded into wd-estimate's calibration; KT sign-off | End of hypercare | wd-post-go-live / wd-kt |

When a project plan is drafted (wd-pm), these gates go in as named tasks with dates - a checklist nobody scheduled is a wish.

## Delivery -> sales handback (what each phase emits for growth)

Delivery produces assets sales needs - but only if someone hands them across. One row per
phase; each points at the owning skill (nothing here is extra work, it's routing):

| Phase | Emit | Where it goes |
|---|---|---|
| Pursuit close (won OR lost) | 20-minute win/loss debrief | wd-estimate references/win-loss.md |
| Discovery | 3-5 outcome-metric baselines; adjacent-use-case sightings | wd-post-go-live value-capture.md section 1; account-growth.md opportunity log |
| Build | Demo-ready staged tenant (reusable for SteerCo + future prospect demos) | wd-demo |
| Hypercare exit | Roadmap workshop output; CSAT pulse | wd-post-go-live account-growth.md; value-capture.md |
| Closeout | Value snapshot; reference-rights ask; case-study one-pager; claims-register rows | wd-post-go-live value-capture.md section 5-6 -> bow-sales-enablement claims register |
| Steady state | QBR value narrative (feeds renewal at T-6-months) | wd-post-go-live account-growth.md |

## Setup on a new machine / sharing the suite

Most of the suite is prose conventions that work with no setup. A subset of tasks run helper
scripts (Excel/Word generation, Balsamiq/draw.io rendering, Smartsheet/Workday REST).

**Easiest path - just ask Claude to set it up** ("set up this suite for me"), or run the **setup doctor**:
`python wd-extend-lifecycle/scripts/setup_doctor.py` (report only) / `--install` (installs missing core
packages after you confirm). It detects your OS, checks the whole toolchain, and tells you in plain language
what's ready vs missing - you don't need to know the tools in advance. Full detail + the secrets rule:
**`references/prerequisites.md`**.

**Standing convention - Claude drives setup, with your approval.** On first use, a skill checks its own
dependencies and offers to install or regenerate what's missing (never assumes you have it); you approve,
Claude does the work, and any secret is entered by YOU at a secure hidden prompt (keychain-backed) - Claude
never types a credential and never automates an interactive login (`wdcli`/tenant auth).

**Standing convention - adapt to the runtime (Claude Code vs claude.ai).** On **Claude Code** the full suite
runs (local machine, `wdcli`, live tenant, Office). On **claude.ai** a skill runs in a Linux sandbox with no
local machine, no `wdcli`/live-tenant network, and no Windows Office - so when a task needs one of those, do
the design/plan/draft and the cross-platform document you CAN here, then hand the user the exact steps to
finish in Claude Code (or via an MCP connector); never fail silently or pretend a local/live action ran. The
per-skill matrix + degradation rule is in [references/platform-compatibility.md](references/platform-compatibility.md).

Key point for sharing: **no task is blocked by a missing script** - small scripts ship inside the skill's
`scripts/` folder; larger ones carry a **build-spec** (in that skill's `references/scripts.md`) so Claude
regenerates an equivalent on demand rather than pointing at a path only the original author has.

## Sibling track - Marketplace / BoW go-to-market

The phases above are the **client-project delivery** lifecycle (one client's app: estimate -> design -> build -> deploy -> KT). **UPSTREAM of a productized app - deciding WHAT to build:** the **market-research** skill (platform-neutral - Workday Marketplace/BoW or any hosted-app marketplace / SaaS) runs opportunity discovery, whitespace + sizing + validation, a scorecard, and a build/no-build call, then hands a GO concept to the GTM + build skills. For a **productized Marketplace / Built-on-Workday app** sold to many customers, the go-to-market kit - Marketplace listing, BoW program application, messaging house, sales playbook, personas, ICP/scorecard, discovery/demo, prospecting, battlecards, pricing, value calculator, claims register - lives in the **bow-sales-enablement** skill (generated from one intake, with claims traceability). It shares hooks with this suite: pricing doctrine + the value calculator with **wd-estimate**, scope-boundary/term language with **wd-contracts**, the mutual action plan with **wd-pm**, and a canonical "About the firm" fact block that wd-estimate/wd-contracts read. Brand/file rendering uses the docx/pptx/xlsx skills with neutral formatting.

## Sibling track - Hosted web apps & agentic tools (app-*)

The phases above build **Workday Extend apps + integrations** (they run inside Workday). A separate,
parallel track builds **general web apps and agentic tools hosted on AWS** (React SPA +
FastAPI + Postgres + App Runner + Bedrock/Anthropic + Entra) - the Innovation-Lead mandate for
practice/customer tools that are NOT Workday Extend apps. **The full ordered Track-2 lifecycle + its
front door live in the `practice-lifecycle` skill** - that is the authoritative map; the table here is
the quick view (keep the two in sync via practice-lifecycle, do not hand-maintain two rosters):

| You are... | Skill |
|---|---|
| Deciding WHETHER to build (demand, go/no-go - any platform) | **market-research** |
| Deciding internal accelerator vs customer product (disposition + productize) | **product-strategy** |
| Structuring a hosted tool so it scales (discovery/design brief + estimate, module contract, FCIS, local-dev) | **app-architecture** |
| Hosting it on AWS (App Runner + RDS + Bedrock + Entra; deploy; observability/operations/run-cost) | **app-hosting** |
| Making it agentic (Bedrock/Anthropic provider seam, tool-loop, durable runs, MCP, evals, RAG) | **app-agentic** |
| Running the Claude Code build loop + guard hooks + conformance/testing | **app-harness** |
| Integrating it with non-Workday SaaS (Salesforce / ServiceNow / data platforms) | **saas-integration** |
| Taking it to market on non-Workday channels (SaaS / AppExchange / ServiceNow Store) | **product-gtm** |
| Running a SOLD product (SLA/incident/billing/customer-success/compliance) - customer products only | **product-operations** |

Modeled on a private reference architecture (patterns only). This track does NOT touch the Workday
delivery phases above; it is a distinct build-and-host lifecycle. Boundary: a **Workday Extend app or
O4I** -> wd-extend-dev; a **general hosted web app / agentic tool on AWS** -> the Track-2 skills.
**Scope note (2026-09-10): Track 2 is scoped to INTERNAL practice tools today** - a customer-SOLD hosted
product needs public/external hosting, per-customer multi-tenancy, and SLA/support/DPA content not yet
designed in this suite (see app-hosting + product-strategy scope flags).

## Suite conventions (who owns what - so skills don't drift)

| Concern (single owner) | Skill |
|---|---|
| Hosted web app / agentic tool architecture (module contract, FCIS, topology independence) - NOT Workday Extend | **app-architecture** |
| Hosting a tool on AWS (App Runner/RDS/Bedrock/Entra, parameterized CloudFormation, deploy, observability, operations) | **app-hosting** |
| The hosted agent runtime (Bedrock/Anthropic provider seam, tool-loop, spend metering, durable runs, MCP, evals, RAG) | **app-agentic** |
| The Claude Code build harness + guard hooks + conformance checklist + app testing for hosted tools | **app-harness** |
| Internal-tool-vs-customer-product disposition + productize-an-accelerator lifecycle | **product-strategy** |
| Non-Workday SaaS integration (Salesforce/ServiceNow/data platforms) + the unattended-Workday-from-a-hosted-tool pattern | **saas-integration** |
| Go-to-market on non-Workday channels (Workday Marketplace channel = bow-sales-enablement) | **product-gtm** |
| Running a SOLD hosted product as a business (SLA/incident/billing/customer-success/compliance-ops) - the Track-2 analogue of wd-post-go-live | **product-operations** |
| Forking work across agents/sessions/models (parallelize; route model up/down) - CROSS-CUTTING, both tracks | **session-orchestration** |
| Session authentication + credential/token/secret storage + OAuth/API-Client setup + the auth preflight (whoami org/account, token freshness) - every skill runs its auth-preflight before the first wdcli/API/tenant action; it does not restate the steps | **wd-auth** |
| Suite feedback + issue/learning/change-proposal capture and maintainer triage | **wd-suite-feedback** |
| Full-program delivery methodology + role/RACI model + config-guide pattern + specialty tracks (vendor-neutral) | **wd-delivery-methodology** |
| Yellow-highlight/open items + design change control | **wd-design-doc** |
| Smartsheet API mechanics | **wd-smartsheet** |
| test-scenario derivation | **wd-testing** |
| code standards (Extend + O4I) | **wd-extend-dev** |
| integration naming + traditional-integration build (EIB/Studio/CC/DT/XSLT) | **wd-integration-dev** |
| estimation calibration data | **wd-estimate** |
| OCM & adoption planning (change-impact, comms plan, training plan, adoption metrics) - message drafting stays wd-comms, training build stays wd-kt | **wd-change-adoption** |
| client end-user security-MODEL design + the security ownership map | **wd-deployment** security-role-design.md |
| reusable-asset catalog (cross-engagement delivery IP) + practice operations (staffing, enablement, certs, Workday alliance) | **wd-practice-ops** |
| market/product-opportunity research + build-no-build (platform-neutral, upstream of GTM) | **market-research** |
| the Flex-Credit + API-metering canonical fact block (entitlement, rate card, pricing) - every other skill points here, does not restate | **wd-estimate** references/flex-credits.md |
| per-functional-domain technical design cribs (config objects + web services + donors, the bridge from a domain use case to a concrete build) - functional LITERACY stays wd-discovery; BUILD craft stays wd-extend-dev/wd-integration-dev | **wd-solution-playbooks** |
| browser-driven test EXECUTION (drive the in-app browser through the test plan + capture evidence) - scenario derivation + Unit Testing tab + triage stay wd-testing | **wd-test-execution** |
| browser-driven in-tenant config + test-data creation (execute the setup recipes + seed synthetic data live, confirm-each-write) - recipe content + security model stay wd-deployment; login handoff stays wd-auth | **wd-tenant-config** |
| Office file mechanics | the xlsx/docx/pptx skills |
| firm-branded deliverables | neutral formatting via the docx/pptx/xlsx skills (no firm brand skill) |

### Writing standard - plain language / novice-reader (owned here)

**The principle every skill applies: write so a smart person who has never seen Workday can follow it - "explain it to your mother."** State intent in plain terms; the first use of any Workday/Extend/integration term gets a one-line gloss (or the reader's own adopted name for it). This is the single owner of the principle - the skills below reference it and add only their domain-specific application (what "the reader" is, and the reading level): code comments (wd-extend-dev standards.md; integration/XSLT comments wd-integration-dev), client-comms jargon glosses (wd-comms), end-user documentation reading level (wd-kt), novice tenant-task recipes (wd-deployment), diagram layperson annotations (wd-design-visuals).

**Suite-readability authoring convention (human-facing surfaces).** The plain-language standard above is about the READER's comprehension; this is about visual FORMATTING of the text a human actually reads (SKILL.md intros, setup/recipe steps, READMEs, checklists, anything walked through live). Write these for a reader who scans and may be dyslexic / ADHD: **chunk** into short blocks; **one action per line** in procedures; **verb-first bold lead-ins**; generous **white space**; prefer short lists and small tables over dense multi-clause paragraphs and stacked parentheticals; **use bold for emphasis, not italics**. (Dense, Claude-facing reference prose is exempt, but give any long human-facing reference a chunked "At a glance" lead block.) This complements the comprehension standard - one governs *what words*, this governs *how it's laid out*.

**Invocation risk:** destructive or consequential skills (wd-folder-hygiene moves, wd-smartsheet writes, wd-deployment promotions) stay natural-language invocable BY DESIGN - their protection is plan-first + explicit confirmation + dry-run defaults, not invocation lockout, which would break front doors like "clean up this folder".
