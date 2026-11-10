---
name: wd-testing
description: >-
  DERIVES the test scenarios and runs the testing lifecycle for Workday Extend
  apps and integrations - unit test scenario derivation (at design time), UAT
  planning and support, and E2E/UAT defect and change-request triage. Use when
  the user mentions unit test, test scenarios, test scripts, UAT, defect, bug
  logged, change request, E2E, test results, regression, or asks "did we test",
  "was this tested", or "is this a bug or a CR". Owns scenario-derivation
  methodology and defect-vs-CR triage decisions. Use THIS for DERIVING scenarios
  / UAT / triage; for browser-driven EXECUTION of the plan see wd-test-execution;
  the design doc's Unit Testing tab format see wd-design-doc; code fixes see
  wd-extend-dev; performance testing see wd-deployment.
---

# wd-testing - Unit Testing, UAT Support, and Defect/CR Triage for Workday Extend

Part of the Workday Extend delivery-lifecycle suite. This skill owns
**how test scenarios are derived**, **how results are executed and recorded**,
and **how defects and change requests are triaged** during E2E and UAT.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **Deriving unit-test scenarios** at design time (the derivation checklist below is the quick form) | [references/unit-testing.md](references/unit-testing.md) |
| **UAT planning + support** - entry/exit criteria, tester experience, req<->case coverage matrix | [references/uat-support.md](references/uat-support.md) |
| **Defect vs CR triage** + the defect-register human/tool column model | [references/defect-triage.md](references/defect-triage.md) |
| **Integration testing** (EIB / Studio / Core Connector / O4I) | [references/integration-testing.md](references/integration-testing.md) |
| **The API-driven headless test harness** | [references/automation-harness.md](references/automation-harness.md) |
| **Testing Workday agents** (SSA / BP Optimize / Extend `.agent`, Flex Credits) | [references/agent-testing.md](references/agent-testing.md) |

## Core principle: scenarios are derived at DESIGN time, not after build

The house standard: the unit test scenario list is written **while the
design doc is being authored**, requirement-by-requirement, and lands on the
Unit Testing tab before design sign-off - not reverse-engineered from the
built app. If a requirement can't produce a testable scenario, the requirement
is too vague; push it back through the design (that's a design-quality signal,
not a testing problem).

**Method:** walk the Requirements tab (16-tab standard doc) or the Discovery
tab (BoW 10-tab doc) row by row. Every requirement yields **at least one
happy-path scenario plus its failure/edge modes**. Then sweep the
Extend-specific checklist below to catch scenarios no single requirement
names.

**And keep them current:** every design change adds or updates its scenarios
in the SAME pass (wd-design-doc enforces this at each version). A design
version with new screens or behaviors and an unchanged Unit Testing tab is
incomplete - scenario drift is how requirements ship untested.

**Scenario quality gate:** before any scenario row lands on the tab, it must
clear the four-gate authoring check in unit-testing.md Section 1a (names the
behavior/invariant it protects, names a credible regression, deduplicates
against existing coverage, anchors the expected result to an independent source
of truth). Scenarios that fail any gate are reframed or dropped - the three
anti-patterns to reject on sight: implementation-coupled (breaks on a
behavior-preserving refactor), tautological (expected value derived the same
way the code derives it), and horizontal-slice (scenarios written in bulk
ahead of the build they describe).

## Extend derivation checklist (the differentiator)

Apply every line to the app being designed. Full worked detail and examples:
[references/unit-testing.md](references/unit-testing.md).

| Design element | Mandatory scenarios |
|---|---|
| Every page (PMD) | Render path (loads with valid context) AND submit path (POST/PUT succeeds, confirmation shown). Also: **open without expected URL context** (no eventId/eventStepId) - pages 500 unless read endpoints are guarded (a real costing-app defect). |
| Every custom BP | Approve, Deny, Send-back (only if `SEND_BACK`+`revisePageRoute` is configured - it's optional and easy to omit), Cancel/rescind. One scenario per configured step in multi-step chains (e.g. a request app with a 4-step approver chain). |
| Every security domain | Positive test (right role sees/does) AND negative test (**wrong role sees nothing** - no data leak through pages, WQL reads, or API endpoints). |
| Every orchestration | Success, API-error response, empty-data result, and timeout - page-synchronous flows have a 25-second cap (owned by wd-extend-dev orchestration.md); anything that can exceed it needs an async/BP-triggered design and a scenario proving the timeout behavior. |
| Every integration / web-service call | Happy payload, malformed/rejected payload (capture the tenant-side error surfaced to the user), and retry/replay behavior (is the operation idempotent? Put vs Submit matters). |
| Boundary data | **Old records with null values in newly added BO fields** - nulls on new fields crash pages that assume them. Known Extend landmine: on one delivered app a Request BO lost fields 20-24 in a staging-model mishap and later grew fields 26+; every BO field addition mandates a "pre-existing record renders and edits cleanly" scenario. |
| Volumes | Grids/lists expected to exceed 100 rows hit the BO REST collection limit (owned by wd-extend-dev pmd-gotchas.md) - scenario must load a >100-row dataset and prove paging/filtering, not just a 5-row seed. |
| App Attributes / tenant config | Any tenant-specific value (instance WIDs, subtype IDs) read via `site.<attr>` gets a "wrong/missing attribute" scenario - e.g. on one delivered app, subtype WIDs that differ per tenant silently emptied the pickers. |

## Integration functional testing (EIB / Studio / CC / DT)

The checklist above is for Extend apps. **Traditional integrations are tested differently** - no UI, so you
verify the OUTPUT (file or API result) against the IDD field mapping, plus transport/connectivity, security,
schedule, full-volume, and error/audit behavior - and for outbound, an **output-reconciliation parallel run**
against the legacy integration and **integration UAT in the downstream system** (not just "the file
generated"). Derive these from the IDD at design time, same as app scenarios. Full checklist + parallel-run +
reconciliation-chain + integration-UAT detail: [references/integration-testing.md](references/integration-testing.md).

## Accessibility scenarios (derived here, executed via the browser)

Accessibility is an NFR captured at design time (wd-design-doc nfr-accessibility.md section 1);
this skill DERIVES the a11y test scenarios from those NFR rows (keyboard-only path + focus order,
visible focus, accessible name/label, contrast, error identification, target size - to the client's
confirmed WCAG level, default WCAG 2.1 AA). They are executed against the built PMD pages via the
browser: **wd-test-execution/references/accessibility-execution.md** owns the verification method -
do not duplicate it here. Failures route back through defect-triage.md like any other scenario.

## Scenario format

One row per scenario, in this shape (the Unit Testing tab layout itself is
owned by wd-design-doc - populate whatever columns that tab defines with
these fields):

- **ID** - `UT-###`, stable, referenced by defects and UAT scripts
- **Requirement ref** - REQ-### / Discovery row it verifies (traceability both ways: every REQ has >=1 UT; every UT names its REQ or checklist source)
- **Preconditions** - role/security group, BP config state, seeded data
- **Steps** - numbered, exact (page, button, values entered)
- **Expected result** - observable outcome, including what the BO/event record should show afterward
- **Tenant / data needs** - which tenant, which seeded records, any App Attribute overrides

## Execution and results recording

1. **Run in the dev/implementation tenant against seeded data.** Use the
   seed/wipe script pattern (wd-extend-dev documents it) so runs are
   repeatable - never test against whatever data happens to be lying around.
2. **Record every run** into the RIGHT tracker for the cycle:
   - **Unit cycle -> the design doc's Unit Testing tab** (format + editing
     mechanics per **wd-design-doc**): Pass/Fail status, evidence (screenshot
     path or event/record ID), execution date, tester. A fixed defect flips
     Retest -> Successful only after visual/functional re-confirmation (on one
     delivered app a fixed defect stayed "Retest" until the approve page was
     re-verified post-deploy).
   - **E2E / UAT cycle -> the live test tracker, usually a Smartsheet sheet**
     (or another PM tool). Update Status + evidence link + run date on the
     matching row via **wd-smartsheet**, following its SKILL.md write rules (the
     owner - do not restate them here). For a non-Smartsheet PM tool, same pattern via its connector or
     an exported run-report table. Keep ONE source of truth current per cycle
     (design tab for unit, the tracker for E2E/UAT) - do not silently diverge them.
   - When the run is driven through the in-app browser, **wd-test-execution**
     produces the executed results + evidence that feed both of the above; this
     skill owns which tracker is authoritative and the recording discipline.
3. **Failures become defects or open items** - triage per
   [references/defect-triage.md](references/defect-triage.md); design-doc
   Open Items and yellow-cell conventions per wd-design-doc.
4. **Currency gates:** the Unit Testing tab must be fully current (a) before
   the design sign-off gate and (b) again before deployment hand-off to
   wd-deployment. A stale tab blocks the gate.

## UAT support

UAT is **client-executed, consultant-supported** - distinct from E2E (which
the consulting team drives). This skill:

- Generates UAT scripts **from** the unit scenarios (translate tester-speak
  to business-user-speak, strip tenant/tooling jargon)
- Defines entry criteria (unit tests pass, data converted/seeded, security
  assigned to real test users) and exit criteria (no open Sev1/Sev2,
  signed-off artifact)
- Sets up the defect intake channel and daily triage rhythm for the UAT window

Full detail: [references/uat-support.md](references/uat-support.md).

## Defect and change-request triage (E2E/UAT)

For every logged defect or CR, **first validate the latest code against the
latest signed design** - the disagreement is often doc-vs-build drift, not a
bug. Then classify:

- **(a) Code != signed design** -> code fix via **wd-extend-dev**'s workflow
  (pull latest via `wdcli app download` + diff; deliver a change-list when a
  client developer owns the code)
- **(b) Design ambiguous or silent** -> decision meeting with the named
  decision-makers; outcome recorded via **wd-design-doc** (requirement update
  or Open Item)
- **(c) Works as designed, client wants different** -> **CHANGE REQUEST** into
  wd-design-doc's change control; LOE assessed via **wd-estimate**
  calibration if material (e.g., a real CR - a checkbox -> Program
  worktag change, ~40 hrs, held until change-control approval - do NOT build ahead
  of approval)
- **(d) Data / config / tenant issue** -> tenant fix, no code change (e.g.,
  empty pickers because a client's custom-org subtypes don't exist in the
  dev tenant - environment, not defect)
- **(e) Combination** -> split into separate tracked items per class

For class (a) code fixes, defect-triage.md Step 2 governs the investigation
approach: name the root cause before touching code, one hypothesis at a time,
3-attempt escalation rule (three failed attempts signal an architectural
assumption that is wrong - escalate to class (b) design review rather than
continuing to guess).

Severity guide, notification matrix, and worked examples:
[references/defect-triage.md](references/defect-triage.md).

## Regression scope for a change (enhancement / CR / defect fix on a live app)

Regression scope is **derived from the change plan**, not guessed. Three layers, all mandatory:

- **(a) Changed-surface scenarios** - re-run every Unit Testing tab row that
  touches the pages/BOs/scripts/orchestrations in the change plan.
  **wd-extend-dev** references/workflow.md Rule 3 already enumerates the
  changed surfaces - use its list, don't re-derive one here.
- **(b) Always-on critical-path set** - the app's standing 5-15 scenario
  list sourced from the Unit Testing tab; the selection pattern is
  **wd-post-go-live** references/release-regression.md - adopt it by
  reference, don't duplicate it.
- **(c) Mandatory boundary scenarios** - old records with null values in
  newly added BO fields (see the Boundary-data row above), plus every page
  in the full-replace-PUT ripple (**wd-extend-dev** references/model.md
  field-change checklist names them).

**Full-suite regression** is warranted when the change touches BO schema,
security domains, or a shared script/orchestration everything calls.
Otherwise changed-surface + critical path is the scope.

This section is the regression evidence **wd-deployment**'s
references/marketplace-recert.md points at ("wd-testing owns the evidence").

## Automating the smoke / regression harness

The stable critical-path and negative/security scenarios are worth **automating** into a repeatable
seed -> exercise -> assert -> reset harness (API-driven), so per-build smoke checks and each R1/R2 release
regression run cheaply instead of by hand. It assembles pieces that already exist (tenant-ops seed/wipe +
`check-tenant` write gate + `workday_rest.py`, WQL/RaaS read-backs, orchestration direct-launch) rather than
new tooling; exploratory/UX/UAT testing stays human. Full pattern, what-to-automate, and guardrails:
[references/automation-harness.md](references/automation-harness.md).

## Boundaries

- **Unit Testing TAB FORMAT** (columns, styling, editing mechanics) ->
  **wd-design-doc**. This skill supplies the scenario content and results;
  that skill owns the workbook.
- **Requirement changes and change control** -> **wd-design-doc**. Triage
  routes CRs there; it does not adjudicate scope itself.
- **Code fixes** -> **wd-extend-dev** (pull-latest + diff before edits;
  change-list instead of direct edits when a client dev owns the code).
- **Performance testing** -> **wd-deployment**. Workday's mandated Performance
  Testing Template / Volumes Questionnaire process is a deployment gate, not
  functional testing - do not fold it into unit/UAT plans here.
- **Browser-driven EXECUTION of the test plan** -> **wd-test-execution**. This
  skill derives the scenarios and records the results; the sibling drives the
  in-app Browser pane through them against the running app + tenant, asserts, and
  captures evidence, then feeds pass/fail back here (Unit Testing tab) and routes
  failures to defect-triage.md. The API-driven headless harness (automation-harness.md)
  stays here; wd-test-execution is the human-visible UI-walk arm. Test-DATA creation
  in a tenant -> **wd-tenant-config**.

## Agent and API metering test considerations

Solutions with Workday agents (SSA, BP Optimize, Payroll Monitoring, custom agents) or
meaningful API/integration volume need agent-specific test scenarios and metering-aware
test design (non-prod is free but verify per-agent; production smoke tests DO consume
credits). Full test-design implications - agent scenario checklist, API-volume validation,
and the credit-awareness rules: [references/agent-testing.md](references/agent-testing.md)
(all Flex Credit NUMBERS defer to `wd-estimate/references/flex-credits.md`).

## Lifecycle neighbors

- **Previous:** `wd-extend-dev` - the build whose output this skill tests;
  source of the seed/wipe data pattern and the code-fix workflow.
- **Next:** `wd-deployment` - receives a current Unit Testing tab and a
  clean Sev1/Sev2 slate; owns performance testing and migration gates.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
