---
name: wd-deployment
description: >-
  Workday Extend deployment lifecycle, the tenant-setup RECIPE CONTENT, and the end-user SECURITY
  MODEL. Owns tenant promotion (DEV, IMPL, SBX, PROD), cutover and data-conversion planning,
  go-live EXECUTION, and Workday's production-approval docs (Extend Volumes Questionnaire,
  Performance Testing Template). Owns the setup recipes (R1-R12: security domains, ISU/API
  clients, App Attributes, BP config, schedules) and the client's production security design
  (roles, security groups, constrained vs unconstrained, segregation of duties / SoD, security
  design workbook) - the security HUB that maps every security question to its owner. Use when the
  user says deploy to production, promote, sandbox, impl tenant, cutover, go-live, the
  tenant-setup recipe, migrate the app, data conversion, volumes questionnaire, performance
  testing, or security design. DRIVING the browser to do setup or test data live is
  wd-tenant-config; wdcli build/deploy ERRORS are wd-extend-dev; hypercare/closeout is
  wd-post-go-live.
---

# wd-deployment - Tenant Promotion, Production Approval & Cutover

This skill owns the path from "the app works in DEV" to "the app is live in PROD
and Workday has approved it": environment promotion, the two Workday gating
documents, cutover/data-conversion planning, and go-live execution.

## Boundaries

- **.xlsm editing mechanics** (openpyxl, merges, VBA preservation details) -
  use the **xlsx skill** for file mechanics; this skill owns the *content and
  rules* for the two Workday templates (which cells, what values, how to
  classify).
- **Yellow-highlight convention** (highlight unknowns/follow-ups with a note,
  unhighlight when answered) - owned by **wd-design-doc**; apply it here by
  reference.
- **wdcli command details** (auth, build loop, flags) - owned by
  **wd-extend-dev**. The 2-3 promotion-specific commands are restated in
  `references/promotion-and-environments.md`.

## Reference map - read what you need

| File | When |
|---|---|
| `references/promotion-and-environments.md` | Tenant path, one-way promotion, wdcli promote, per-tenant re-setup matrix, kickoff environment prerequisites |
| `references/volumes-questionnaire.md` | Filling the Extend Volumes Questionnaire .xlsm |
| `references/perf-testing-template.md` | Filling the Performance Testing Template .xlsm |
| `references/cutover-planning.md` | Data conversion, legacy coordination, go-live day, hypercare |
| `references/migration-readiness-gates.md` | Wave-by-wave go/no-go scorecard for a phased data conversion (Pass / Conditional Pass / Fail per gate) - sits on top of the conversion build and feeds the cutover go/no-go |
| `references/tenant-setup-guide.md` | Authoring the per-tenant setup deliverable (the step-ordered content that feeds the Deployment Guide) |
| `references/deployment-guide.md` | Authoring the client-facing **Deployment Guide** deliverable (install/deploy + promote-across-tenants), grounded in two delivered guides |
| `references/tenant-task-recipes.md` | Numbered, novice-grade click-level recipes (R1-R12, incl. R8b/R11b) embedded into the setup / deployment guides |
| `references/security-role-design.md` | Designing the CLIENT's end-user production security model (functional/aggregation/role-based groups, constrained vs unconstrained, domain + BP-policy access, the SoD matrix, security design workbook, security testing) - **plus the security ownership map (which reference owns which security question)** |
| `references/security-setup-section.md` | The reusable novice **Security Setup Section** every guide embeds: exact tasks + naming conventions + the enumerated domains-and-permissions table |
| `references/configurable-security-admin.md` | The CONCEPT+RULES layer under security-role-design + the recipes (doc-sourced, Workday Education manuals): security framework, all 12 group types w/ composition restrictions, the activation asymmetry (policy edits pending vs group changes immediate), the union rule, report security, ISU/ISSG mechanics + DIS exception |
| `references/bp-configuration-admin.md` | NATIVE tenant business process configuration (doc-sourced): definition resolution (walks up the org hierarchy, silently skips definitions w/ errors), step types + letter ordering, condition-rule legality by step kind, approval/denial rules, BP security policies |
| `references/marketplace-recert.md` | Enhancing/re-certifying an already-shipped Marketplace/BoW app: versioning, re-approval triggers, delta promotion |
| `references/go-live-agent-checklist.md` | Agent/Flex-Credit go-live gates (UMSA, ASOR, PCC, complimentary credit, API baseline, non-prod-first, New WD Experience); defers all numbers to `wd-estimate/references/flex-credits.md` |
| `references/security-questionnaire.md` | Answering a CLIENT security/InfoSec questionnaire about an Extend app: inherited-Workday vs app-specific vs firm-process answer bank (NOT the Workday Volumes Questionnaire) |
| `references/migration-checklist.md` | Per-integration tenant-migration checklist tracker (traditional INTs): check columns, type-applicability matrix, migrator/reviewer workflow, design-change-note convention (regenerate the workbook via `scripts/build_migration_checklist.py`, or use the firm's branded master) |
| `references/scripts.md` | Build-specs for the cross-platform template builders (`scripts/build_migration_checklist.py`, `scripts/build_cutover_spreadsheet.py`) that regenerate vendor-neutral blank worksheets |

## The Deployment Guide is a named client deliverable

The **Deployment Guide** is the client-facing document that gets the app live in a tenant
and promoted across tenants - a distinct, named deliverable (see
`references/deployment-guide.md`). It **overlaps heavily with the tenant-setup guide**: for
a **UI Extend app** the tenant-setup guide usually *is* the Deployment Guide (wrapped with
overview + promote-across-tenants + support); for an **O4I / no-UI integration** the
delivered pattern is a **separate Deployment Guide** carrying config, ISU/ISSG, reference
attributes, and schedule (precedent: a delivered O4I no-UI integration shipped a User Guide
*and* a Deployment Guide). Author the click-level steps once via
`references/tenant-task-recipes.md` and reuse them in whichever deliverable ships.

**Executing the recipes live in a tenant (browser):** when the user is in a dev/sandbox
tenant and wants the setup DONE (not just documented), the **wd-tenant-config** skill drives
the in-app browser through these recipes plan-first / confirm-each-write, and creates
synthetic test data. This skill still OWNS the recipe content + security model; wd-tenant-config
is the execution arm (security/system-settings commits are handed back to the user per its
safety model). Login handoff is wd-auth. **Verify each setup step actually applied** (suite
rule): wd-extend-lifecycle references/verify-in-tenant.md - confirm programmatically that the
ISU exists, the domain is granted, and the policy is activated, not just that the task ran.

**Traditional integrations (EIB/Studio/Connector):** tenant migration mechanics differ from
Extend promotion - notably **API Clients and PGP private keys are NOT migratable** (create
them in the master tenant so refreshes carry them down). Those rules live in the
**wd-integration-dev** skill's integration-build reference (Keys & API clients section); fold
them into every integration cutover plan.

## The production-approval process (the docs are only half of it)

Why Workday reviews at all: Extend apps run on shared platform infrastructure -
your app's API calls ride the same gateway and tenant capacity as every other
customer's payroll runs. The review protects that shared capacity, the other
tenants on it, and the API infrastructure itself. Read the reviewer's stance as
**"prove your load story, at peak, per API surface"** - every question in both
documents traces back to that sentence. The same principle governs how the app
should be built in the first place: the platform-citizenship non-negotiables in
**wd-extend-dev** `references/standards.md` (bounded retries/reads, bulked
writes, no polling) are what make the load story provable.

Every Extend app going to production needs Workday's sign-off, gated on two
documents submitted to a **Workday Customer Care case**:

1. **Extend Volumes Questionnaire** (.xlsm) - required for **every** app at
   production readiness. Declares users, transaction volumes, custom objects,
   APIs used, orchestrations, attachments, retention. The hidden threshold:
   **50,000 active Extend application workers** - under it, the
   Recommendations tab auto-concludes "does not exceed thresholds."
2. **Extend Performance Testing Template** (.xlsm) - companion doc, required
   when the app **exceeds ~50K annual transactions** (the Volumes
   Questionnaire drives whether it's required at all). Even under threshold,
   completing it is good practice and often requested.

These are **two different ~50K numbers** - do not conflate them: the Volumes
Questionnaire gate is **50,000 active Extend application workers**; the Perf
Testing trigger is **~50,000 annual transactions**.

Red flag: "volumes are obviously low, skip the questionnaire" - the
questionnaire is Workday's gate, not ours; obvious is not submitted.

### Process mechanics

- **Submit EARLY - build in lead time.** Workday review is not same-day.
  Target submitting both docs **4-6 weeks ahead of the planned
  move-to-production date**; the review can round-trip on questions.
- **Who reviews:** Workday Customer Care / the Extend product team, via the
  case. They check volumes against platform thresholds and look at the API
  inventory for load concerns.
- **One case per app** (a tightly-coupled app pair with shared users/volumes
  can share one questionnaire, delivered as one combined file).
- **Bump and resubmit** if the design changes materially after submission
  (new API surface, order-of-magnitude volume change, new orchestration
  schedule). The Perf Testing header F4 tracks the design-doc version for
  exactly this reason.

### Common rejection / round-trip causes
The full rejection-cause playbook - missing API inventory, volumes-without-a-basis, peak-vs-average, and overwritten formula tabs - lives in [references/volumes-questionnaire.md](references/volumes-questionnaire.md) (the owner). In short: enumerate EVERY Workday API surface (SOAP/RaaS/orchestrations/attachments, not just WQL/REST), state a basis for every volume, use peak-hour not annual-average, and never overwrite the formula-driven Recommendations tab.

## Go / no-go cutover checklist

Run this before authorizing the production deploy. Every item is a gate.

**Workday approval**
- [ ] Volumes Questionnaire submitted and accepted (case closed or approved)
- [ ] Performance Testing Template submitted; testing executed if required
      (>50K annual transactions) with results recorded in the C/D time columns

**Build & promotion readiness**
- [ ] Final version built clean and deployed/tested in IMPL (E2E signed off -
      wd-testing owns the test evidence)
- [ ] Integration System and any RaaS custom reports promoted **separately**
      alongside the app (they do NOT ride with the app promotion)
- [ ] Tenant setup guide written and walked through for PROD (see
      `references/tenant-setup-guide.md`)
- [ ] All platform features used are GA in the target release - no preview
      dependencies without a documented fallback (wd-extend-dev
      `references/release-impact.md`)

**Production tenant prerequisites**
- [ ] Security domains granted + Activate Pending Security Policy Changes run
      (BO calls return S22 until this is done)
- [ ] ISU/ISSG provisioned with the required domain permissions; API client /
      refresh token registered if external REST is used
- [ ] App Attributes set with PROD-specific WIDs
- [ ] BP definitions configured with the real approver chains + initiation
      security
- [ ] Production security groups populated with real members
- [ ] The tenant-readiness read-set passes - app BO call returns data (no S22),
      design-doc RefIDs resolve, App Attribute WIDs verified, RaaS responds under
      the ISU (wd-extend-dev references/tenant-ops.md; subject to the ISSG/scope
      grant)

**Data & coordination**
- [ ] Data conversion dry-run completed in IMPL with reconciliation counts
      matching (see `references/cutover-planning.md`)
- [ ] Legacy-system freeze window scheduled and communicated
- [ ] Rollback plan written and agreed (what "abort" means, who calls it,
      by when)
- [ ] End-user comms sent (what changes, when, where to get help)

**People readiness** (measures defined in **wd-post-go-live**
`references/adoption-and-feedback.md`)
- [ ] % of target users trained meets the threshold agreed at UAT exit;
      job aid distributed to the full user population
- [ ] Champion / office-hours coverage confirmed on the go-live-week roster
- [ ] Help path verified end-to-end by a real end user (question in ->
      answer back within SLA)

**Agent / Flex Credit** (only if the app uses AI agents or consumes Flex Credits; full detail in `references/go-live-agent-checklist.md`)
- [ ] UMSA signed (blocker - no agent features in prod without it); ASOR
      registrations + PCC access confirmed
- [ ] Complimentary-credit tier active, API-entitlement baseline documented,
      agent/API testing completed in non-production first

**Day-of**
- [ ] Smoke test script ready (create -> route -> approve -> write-back -> verify)
- [ ] Hypercare roster and escalation path confirmed (handoff to
      wd-post-go-live)

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Move-to-Production window** - the target go-live date range and first-use
  date for the app(s), driven by the program's pre-prod/Gold deploy schedule
  (watch for stale dates in older design-doc text; the memory value supersedes).
- **Dev tenant** - the DEVELOPMENT-level tenant alias used for build/unit
  testing (the only level `wdcli app deploy` reaches).
- **IMPL tenant(s)** - the IMPLEMENTATION-level tenant alias(es) used for E2E /
  client validation.
- **Perf Test Lead** - the named person who coordinates executed performance
  testing; route executed-test coordination through this role.
- **Volume posture vs. the thresholds** - whether the program's apps run under
  or over Workday's gates (50,000 active Extend workers for the Volumes
  Questionnaire; ~50K annual transactions for Perf Testing). Program practice
  may still complete the Perf Testing Template per app even when under
  threshold.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).

## Agent and Flex Credit go-live considerations

When the implementation includes Workday AI agents, Flex-Credit-consuming Extend apps, or
API-heavy integrations under the Aug 2026 consumption model, run the agent/Flex-Credit go-live
gates (UMSA sign-off, ASOR registration, PCC access, complimentary-credit activation,
API-entitlement baseline, non-prod-first testing) - full checklist in
[references/go-live-agent-checklist.md](references/go-live-agent-checklist.md). Boundaries:
commercial NUMBERS (tiers, pricing, Rate Card, metering) stay with `wd-estimate/references/flex-credits.md`;
post-go-live PCC cadence + agent monitoring belong to **wd-post-go-live**.

## Lifecycle neighbors

- **Previous: wd-testing** - E2E/UAT sign-off in IMPL is the entry condition
  for this skill's go/no-go checklist.
- **Next: wd-post-go-live** - hypercare, incident triage, and enhancement
  backlog pick up the day after go-live.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
