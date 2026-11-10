# Integration review checklist - the reviewer's QA pass (IDD stage + Build/CLAR stage)

This is the **second-set-of-eyes review scorecard** for a traditional integration - the pass a
reviewer runs over someone else's IDD or build. It is distinct from [integration-build.md](integration-build.md),
which owns the *builder's* gates (what the person building must do). This file owns the *reviewer's*
lens: a stage-appropriate checklist, pass/fail/partial/N-A rules, and a Studio code-quality rubric.
Design-stage gates also live in the **wd-design-doc** IDD reference; naming rules in
[integration-naming.md](integration-naming.md); the Extend-app equivalent is `app-review-audit.md` in
the wd-extend-dev skill.

> Distilled from a firm integration-review tool, vendor-neutralized (dev-tenant identifier
> genericized to "the dev tenant"). One number reconciled: the source tool defaulted document
> retention to 90 days; the better-sourced figure is in integration-build.md (house default 180,
> Workday ships 30) - **use integration-build.md for retention; treat any 90-day value as a client
> override to confirm, not a standard.**

## Two review stages

- **IDD review (design stage):** review the Integration Design Document *before* build. Naming,
  requirements completeness, contacts, PII, ISSG/ISU display names, flow, unit-test plan, open issues.
  Build-level artifacts (XSLT, Ref IDs, integration-system objects) are **N-A at this stage** if absent -
  they don't exist yet.
- **Build/CLAR review (build stage):** review the built artifact (CLAR / PDF / XML export) against the
  IDD. Everything from reports through DART and the migration checklist, plus a confirmation that the
  IDD tabs were updated.

## Review principles (both stages)

- **Never fail an item that is genuinely N-A.** Mark it N-A with a one-line reason; do not fail it.
- **Only fail where content is genuinely absent, incorrect, or incomplete.** A documented item that
  meets the minimum bar is a **Pass**, not a Partial. Reserve Partial for "present but thin."
- **Do not flag missing approval dates** (Design/Build approval is often not captured at review time).
- **Do not fail on what a text export cannot show.** Yellow-highlight removal, SharePoint folder
  contents, and other visual/environment facts **cannot be verified from a text or CSV extraction** -
  mark them N-A with a note rather than failing them. (This "auto-N-A the unverifiable" rule is what
  keeps an automated or text-only review honest; a human reviewing the live workbook re-enables them.)
- **Naming failures must quote the evidence.** If a name is wrong, quote the exact name found vs. what
  the standard requires (integration-naming.md). Never fabricate a discrepancy.
- **Downgrade, don't inflate.** A weak Open-Issues entry is a minor finding, not a Fail.

## Automatic N-A items (mark without evaluating)

- Anything unverifiable from a text/CSV export (highlighting removal, SharePoint artifact location).
- Build-Approval sign-off at IDD stage (not expected yet).
- File-output items (filenames, date stamps on output) for an **API-type integration with no file output**.
- Outbound-only items when the integration is **Inbound**, and inbound-only items when it is **Outbound**.
- Flow-diagram item for a **simple Outbound O4I or API-type** integration.
- XSLT / transformation names / integration-system Ref IDs at **IDD stage** (build-level - N-A if absent).

## IDD-stage checklist (design review)

| # | Tab / area | Item | Pass rule |
|---|---|---|---|
| 1 | Artifacts | Design-doc name follows the naming standard | matches integration-naming.md pattern |
| 2 | Artifacts | All technical artifacts follow naming conventions; **the tool type appears in the name** (EIB/O4I/Studio/PECI/PICOF/CC...) | Fail + quote name if the tool type is missing |
| 3 | Artifacts | Artifacts in the INT folder; no keys/passwords on SharePoint | N-A from text export (verify live) |
| 4 | Questions | Status set to Answered for resolved questions | "Have to ask" with a blank answer = Pass; Fail only if an answer is populated but status still says "Have to ask" |
| 5 | Questions | Yellow highlighting removed from resolved columns | N-A from text export |
| 6 | Questions | File names include a date / datetime stamp | N-A if API-type, no file output |
| 7 | Overview | Yellow highlighting removed from resolved sections | N-A from text export |
| 8 | Overview | Contact list updated (emails, roles, details) | populated = Pass |
| 9 | Overview | Design/Build approval contact info updated | do not fail on missing dates |
| 10 | Overview | Workday future state elaborated in "About the Integration" | described = Pass |
| 11 | Overview | File names include a date / datetime stamp | N-A if API-type, no file output |
| 12 | Overview | PII noted or marked Not Applicable | any documented content = Pass; completely blank = Partial; **never Fail** |
| 13 | Requirements | Sample rows removed | Fail if template sample data remains |
| 14 | Requirements | **Outbound:** population, filter criteria, data details provided | N-A if Inbound; documented + meets bar = Pass |
| 15 | Requirements | **Inbound:** load details + target Workday objects provided | N-A if Outbound; documented + meets bar = Pass |
| 16 | File | Field details + Workday mapping completed | "Researching" = Pass if an open issue exists; no open issue = Partial with note |
| 17 | File | Sample rows removed | Fail if template sample data remains |
| 18 | WD Solution | ISSG and ISU **display names** documented | both present = Pass; Fail only if **both** absent; never fail for missing Ref IDs at IDD stage |
| 19 | Flow | Flow diagram updated | N-A for simple Outbound O4I / API-type |
| 20 | Unit Testing | Unit-test cases documented | cases present = Pass |
| 21 | Open Issues | Open questions documented | issues documented = Pass; RAID links **not** required; note in comments only issues that are **both** overdue **and** have no RAID link |

## Build/CLAR-stage checklist (build review)

Grouped; each is Pass/Fail/Partial/N-A under the principles above. Items 1-30 and 40-41 come from the
**build artifact**; items 31-39 confirm the **IDD tabs** were updated (highlighting removal is N-A from
a text export).

**Reports (1-5):** Share tab shared with the correct user-based (security) group; ownership transferred
to the ISU; report core logic identifies the population (via calc fields); object prompts included;
population/filter criteria correct and consistent with the connector's Population Eligibility.

**Naming & tagging (6-13):** names + Ref IDs per the standard; XSLT attachment Ref ID documented;
tagged with the correct system + division tag; ISSG Ref ID documented; EIB Template Ref ID documented;
**File Names have a Ref ID per environment** (IMPL/SBX/PRD); output files/logs include a date/datetime
stamp; **Sequence Generators have a Ref ID per environment.**

**Config (14-17):** document retention set (see integration-build.md for the sourced default - do not
assume 90); Environment Restrictions used on BP/SFTP where applicable (>=2 endpoints, PROD + non-PROD);
default integration notification configured correctly (standard subject/body calc fields).

**Studio / O4I (18-20):** descriptive component names (flag defaults like `Component_1`, `Step_2`);
Cloud Log used instead of CSV; unused attributes/maps/components removed.

**Version control (21-22):** SharePoint/Git URL recorded in the IDD Overview links; code in source
control updated to the latest version.

**Integration attributes (23-25):** web-service version documented; log-file names as an integration
attribute with a date/datetime stamp; campus/entity name in the log if the integration is
campus/entity-specific.

**Unit testing & run (26-30):** all unit tests completed + documented; **a successful run with ISU
assignments in the dev tenant**; test-event links updated in the Unit Testing tab; functional-team test
scenarios + employee list included; Integration Tracker SFTP columns updated.

**IDD tab updates (31-39):** Question, Overview, Requirements (Added-to-Test col Y/N), Report, File, WD
Solution, Example, Flow, Open Issues tabs updated (highlighting-removal sub-checks are N-A from a text
export).

**Build-reviewer actions (40-41):** DART integration run in the tenant + findings resolved; all objects
added to the Migration Checklist (wd-deployment `references/migration-checklist.md`).

## Studio code-quality rubric (only when the CLAR contains Studio/O4I assembly code)

One sentence per lens; omit the whole section if there is no Studio code:

- **Component names** - all descriptive? Flag any defaults (`Component_1`, `Step_2`).
- **Logical sequencing** - clear flow, no dead-end paths or out-of-order steps.
- **XSLT / transformation readability** - consistent indentation; complex mappings readable.
- **Comments & documentation** - inline comments on non-obvious logic; note complex uncommented sections.
- **Overall maintainability** - one sentence on how easily another developer could maintain this assembly.

## Completion score (optional summary metric)

Score = passing-or-partial applicable items / total applicable items (N-A items excluded from the
denominator). Report as a single percent with a one-paragraph **Critical Findings** summary (or "None
identified"). Bands: >=80% green, 60-79% amber, <60% red. The score is a communication aid, not a gate -
the Critical Findings paragraph is what drives the go/no-go.

## Lifecycle neighbors

previous = wd-design-doc (the IDD being reviewed at design stage); this skill = the build being reviewed;
sibling = wd-extend-dev `app-review-audit.md` (the Extend-app equivalent). Migration-checklist confirmation
routes to wd-deployment.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in
wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the
result with the deliverable.
