# RAID Log + CR Log + Decisions Discipline

RAID = **R**isks, **A**ssumptions, **I**ssues, **D**ecisions (some programs' sheets also carry
Actions and Questions - RAIDQ). One log per project; one program-level log with
app tags in program mode (see program-mode.md).

## Storage

Smartsheet-backed via **wd-smartsheet**. The program's RAID sheets already exist -
pull sheet IDs and column schemas from the ENGAGEMENT'S PROJECT MEMORY (recorded in the
shape of wd-smartsheet `references/smartsheet-registry-template.md`) rather than
duplicating IDs here (e.g., RAIDS High Priority & Leadership; Extend RAIDQ;
Change Control Log). wd-pm decides content; wd-smartsheet moves it.

When this RAID sheet is co-edited (humans in the Smartsheet UI + this tool via the API),
follow wd-smartsheet SKILL.md section 4b (two-way sync / anti-clobber) - declare per-column
ownership, skip blank source cells, upsert by RAID ID - so tool writes never clobber a human edit.

## Item types and when to use them

| Type | Definition | Test |
|---|---|---|
| **Risk** | Might happen; would hurt if it did | Has probability < 100% |
| **Assumption** | Treated as true without confirmation | If false, plan changes |
| **Issue** | Happening now; hurting now | A risk that landed |
| **Decision** | A choice made, with rationale | Someone could later ask "why?" |
| Action | Task with owner + due date | Lives here too (one list - see SKILL.md) |
| Question | Needs an answer, not yet a decision | Converts to Decision when answered |

A Risk that materializes converts to an Issue (link the rows, don't duplicate).

## Columns

Core set (align to the existing program schema via wd-smartsheet before adding sheets):

| Column | Notes |
|---|---|
| ID | `RAID-####` (common convention) |
| Type | Risk / Assumption / Issue / Decision / Action / Question |
| Title + Description | Title fits in a status report line |
| App / Workstream | Tag - mandatory in program mode |
| Priority | 1-Blocker / 2-Critical / 3-Major / 4-Minor (Extend RAIDQ scale) |
| Likelihood (risks) | 1-Unlikely / 2-Likely / 3-Highly Likely |
| Impact (risks) | 1-Low / 2-Medium / 3-High |
| Score | Likelihood x Impact (1-9); >=6 = leadership visibility |
| Owner | One name - never a team |
| Raised / Due / Closed dates | Age = today - raised, while open |
| Status | Not Started / In-Progress / Completed / Cancelled / Deferred |
| Mitigation / Resolution | For risks: the mitigation IS what earns Amber vs Red |
| Escalation Level | Team / PM / Leadership |

## Review cadence

**Weekly, inside the status meeting** - not a separate ceremony:

1. New items since last week (30 seconds each: right type, right owner, right score).
2. Open Blocker/Critical items: any change? Mitigation still credible?
3. Risks scored >=6: still scored right? Any converting to Issues?
4. Stale check: anything untouched 2+ weeks gets re-owned, re-dated, or closed.

Keep it to 10 minutes. The RAID review feeds the RAG directly: an unmitigated
high-score risk on a milestone = Amber at best; an open Blocker issue = Red.

## Decisions log discipline

**Every design decision gets a row with date + decider + rationale.** This is
what saves you in month 6, when someone asks "why does the app do X?" and the
person who decided has rolled off. The transcript is gone; the row isn't.

Minimum per decision row:

- **Date** decided
- **Decider** - the person (client-side where applicable), not "the team"
- **Decision** - one sentence, stated positively ("Use X"), not "discussed X"
- **Rationale** - why, and what was rejected ("chose A over B because ...")
- **Design doc reference** - Open Item # or tab, so the doc and log reconcile

Capture same-day from the meeting's "Decisions needed" agenda section; reconcile
against the transcript via meeting intake (`meeting-intake.md`). If a decision is later reversed,
add a NEW row that supersedes and links the old one - never edit history.

## Change Request (CR) log pattern

The CR **log** lives here; the change-control **process** (design baselining,
what triggers a CR, re-approval flow) is **wd-design-doc**'s. The end-to-end
change path an approved CR then follows (scoping -> build -> regression ->
redeploy -> comms -> doc refresh) lives in **wd-extend-lifecycle**'s
Change/enhancement path (SKILL.md).

Columns (mirrors a program Change Control Log - IDs via wd-smartsheet):

| Column | Notes |
|---|---|
| CR ID | `CC-###` (common convention) |
| Title / Description | What changes and why |
| App / Workstream | Tag |
| Raised by / Date | |
| RAID ID | Link to the driving risk/issue/decision |
| Impact | Scope / effort (Total Estimated Hours) / timeline / cost |
| Status | Draft / Submitted / Approved / Rejected / Implemented |
| Approval Body + Date | Who can say yes (per governance) |
| Design doc version | Baseline version the CR amends (wd-design-doc owns versioning) |

Rules: no build work on an unapproved CR; every approved CR updates the design
doc (wd-design-doc) and the plan (project-plan-format.md) before it's "done."

**CR financial rollup:** keep one standing rollup line - cumulative approved-CR
hours/$ vs the change budget/contingency (per-CR cost is already in the Impact
column; this is just the sum). It feeds the SteerCo budget slide
(steering-committee.md) and the financial RAG's contingency-exhausted trigger
(status-reporting.md).
