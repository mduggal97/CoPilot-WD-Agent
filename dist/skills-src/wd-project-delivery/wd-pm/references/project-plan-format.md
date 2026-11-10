# Project Plan Format (Smartsheet-Importable Excel)

The proven format is a Master Project Plan workbook, e.g.
`<your workspace>\Master_Project_Plan.xlsx`

A reusable generator (`generate_project_plan.ps1`) builds the plan - there is **no fixed
file to depend on**; the plan is regenerated from the build-spec in
[scripts.md](scripts.md) (Windows/Excel-COM; on other OSes ask for the openpyxl
variant). It builds task arrays as `[PSCustomObject]` rows and calls a shared
`Build-Sheet` function per tab, then a milestone-based MASTER TIMELINE tab moved
to position 1. To create a new plan, feed it new task arrays - the sheet builder,
formatting, and header logic are already correct. For post-generation edits use
the **xlsx** skill; for pushing into Smartsheet use **wd-smartsheet** (Smartsheet's
native Excel import also accepts this layout directly).

## Workbook structure (5-tab pattern)

1 summary tab + 1 tab per workstream/app:

| Tab | Purpose |
|---|---|
| `MASTER TIMELINE` (first) | Milestones only, across all workstreams |
| One tab per workstream/app | Full phase/task/subtask plan |

### Workstream tab columns

`ID | Task Name | Phase | Level | Assigned To | Duration (Days) | Start Date | End Date | Predecessors | Status | Notes`

- **ID**: `<APP>-P<n>` for phase rows, `<APP>-<phase>.<seq>` for tasks
  (e.g., `UC3-P2`, `UC3-2.1`) - IDs are what Predecessors reference.
- **Level**: 1 = phase (bold, shaded), 2 = task (indent 1), 3 = subtask (indent 2).
  This hierarchy maps to Smartsheet parent/child rows on import.
- **Duration (Days)**: working days; phases carry rollup duration; `Ongoing` /
  `Recurring` allowed for post-production rows.
- **Predecessors**: comma-separated IDs (finish-to-start assumed).
- **Assigned To**: one owner per row - a role during drafting (Architect / Lead /
  Developer / SME / Admin), swapped to a named person before baseline.
- **Status**: `Not Started` at generation; Smartsheet picklist after import.
  Add a `% Complete` column when the plan will drive Smartsheet rollups
  (Smartsheet's project settings can auto-roll parent %).

### MASTER TIMELINE tab columns

`Use Case/App | Phase | Milestone | Target Date | Owner | Status | Notes`

Milestones only - phase completions, SME/go-no-go gates, and GO-LIVE rows
(mark go-lives visually bold/highlighted). This is the tab leadership reads.

## Standard Extend project phase skeleton

Use this to draft a new app plan in minutes, then tune. Proportions are of total
elapsed build-cycle time (typical Extend app: 10-16 weeks Discovery->Deploy):

| # | Phase | ~% of timeline | Typical content | Exit gate |
|---|---|---|---|---|
| 1 | Discovery | 10% | Kickoff, scope, current-state, volumes questions, open-questions capture | Scope confirmed |
| 2 | Design | 20% | Design doc (16-tab, per wd-design-doc), wireframes, process flow, weekly design reviews, security/domain design | Design sign-off (baseline) |
| 3 | PoC | 10% | Prototype riskiest slice (custom widget, SOAP call, orchestration pattern) | PoC demo accepted |
| 4 | Build | 25% | App model + PMD pages + orchestrations (wd-extend-dev), iterative demos | Feature-complete |
| 5 | Unit Test | 10% | Developer testing per design-doc test tab, defect burn-down | Exit criteria met |
| 6 | UAT / E2E | 10% | Client testers, defect triage cadence, BP/security regression | UAT sign-off |
| 7 | Perf / Volumes docs | 5% | Workday gating docs: Volumes Questionnaire (always) + Perf Testing Template when over Workday's volume threshold (~50K annual txns - wd-deployment owns the rule); batch across apps in program mode | Workday approval |
| 8 | Deploy | 5% | Production migration, security config, cutover checklist, go-live | Live in PROD |
| 9 | Hypercare | 5%+ | 2-4 weeks elevated support, defect triage, transition to wd-post-go-live cadence | Handover complete |

Skeleton rules of thumb:

- Every phase gets a Level-1 row; 3-8 Level-2 tasks each; subtasks only where
  ownership actually splits.
- Every SME/client review is its own row with an SME owner and `Go/no-go gate`
  in Notes - reviews are where plans slip, so make them visible.
- Perf/Volumes docs (phase 7) can overlap UAT but must PRECEDE deploy -
  Workday's approval is a hard gate; never leave it off the plan.
- Milestone rows from each app's gates populate the MASTER TIMELINE tab.
- Durations come from **wd-estimate** where an estimate exists; otherwise draft
  with the proportions above and flag as unestimated.

## Build-demo cadence (named plan tasks)

The Build phase's "iterative demos" are a standard, not a vibe - plan them:

- **Bi-weekly, 30 minutes, working software in the tenant.** Never slides, never
  localhost-style mockups; everything shown maps to design-doc requirement refs
  ("REQ-12 is this screen") so the client tracks build progress against the
  baseline they signed.
- **Fixed structure:** what's new (demo, ~20 min) -> what's next (the coming
  fortnight's refs) -> feedback capture. Feedback routes through **wd-testing**'s
  triage classes (`references/defect-triage.md`) - defect vs design gap vs CR -
  so demos surface drift early WITHOUT becoming a scope-creep channel; nothing
  gets absorbed as a "quick tweak" live.
- **Demos are NAMED plan tasks:** one Level-2 row per demo in the Build phase
  (`<APP>-4.x`, owner = build lead, SME/client attendees in Notes), not an
  implied recurring habit. A demo nobody scheduled is a demo that gets skipped
  the week it matters most.
- Demo staging and delivery craft (tenant seed data, smoke run, live-question
  triage) -> **wd-demo** `references/demo-playbook.md`.
