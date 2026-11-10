# KT Session Planning

**Upstream input.** When a change/OCM workstream is running, scope this session series from
**wd-change-adoption**'s training-needs analysis and role-based training plan - they set which
roles need training and to what depth. Build the series to match that plan; don't re-derive the
audiences here.

## A series, not a monolith

Never run one giant "KT session." Run a **series: one session per audience**, each
60-90 minutes, each recorded. A single 3-hour omnibus session guarantees every
audience sits through two hours that aren't for them and retains none of the hour
that is.

Standard series for a typical Extend app (trim per app - an integration-only app has
no end-user session):

| # | Audience | Focus | Prerequisite deliverable |
|---|---|---|---|
| 1 | End users (per role if flows differ) | Task walkthroughs, where to get help | User guide (draft OK) |
| 2 | Client admins | Security, config attributes, schedules, tenant tasks | Admin/config guide + Deployment Guide (wd-deployment `references/deployment-guide.md`) |
| 3 | Support desk | Triage runbook, log reading, escalation path | Runbook + error-message table |
| 4-6 | Client developers | Code walkthrough -> guided change -> solo change | Comment sweep passed (see client-dev-enablement.md) |

The deliverable exists BEFORE its session - the session teaches the document, so the
document outlives the session.

## Demo-then-do format

Every session follows the same two halves:

1. **Demo (first half):** the delivery team performs the tasks live in the tenant, narrating
   against the guide ("this is page 12 of your user guide").
2. **Do (second half):** attendees perform the same tasks themselves while the
   delivery team watches. Nobody leaves having only watched. Where they stumble is exactly where
   the guide needs another screenshot or plainer wording - fix the guide same week.

## Capture everything

- **Record every session** and store the recording with the app's documents.
- **Capture transcripts via wd-pm meeting-intake.** Every question asked in a session
  is FAQ raw material - harvest Q&A from the transcripts into the user guide's FAQ
  and the runbook after each session. Questions asked in KT are the questions the
  help desk will get in month one.

## Attendance + teach-back tracking

Track per audience in one table (this table IS the evidence for sign-off):

| Audience | Deliverable (link) | Session date | Recording | Named recipient | Attended | Teach-back demonstrated | Teach-back date |
|---|---|---|---|---|---|---|---|
| End users | User Guide v1.0 | | | | | | |
| Admins | Admin Guide v1.0 | | | | | | |
| Support desk | Runbook v1.0 | | | | | | |
| Developers | Code walkthrough + change list | | | | | | |

Rules:

- **Named recipient** is a person, not a team. "The AP team" can't demonstrate a
  skill back; Maria can.
- **Teach-back beats attendance.** The row is green only when the recipient
  DEMONSTRATED the skill: ran the task, cleared a failed run, implemented a solo
  change (developers - Session 3 in client-dev-enablement.md), or walked a mock
  ticket through the runbook. Attendance without teach-back = incomplete KT.
- If the named recipient changes (turnover), the row reopens.

## The KT Plan workbook (topic-level planning)

The audience table above tracks KT at deliverable/session altitude. For a large KT
effort (a functional area, an integration portfolio, a full workstream handoff),
plan and track at **topic** altitude with the KT Plan workbook. Get the blank
workbook one of two ways: **regenerate the clean, vendor-neutral blank via
`scripts/build_kt_plan.py`** (cross-platform, openpyxl - see `references/scripts.md`),
**or obtain the firm's branded master per engagement** (environment/project memory).

Shape (mine the workbook, don't rebuild it):

- **One sheet per functional area** (rename the `<Name>` sheet; add sheets as
  needed). Rows are grouped under knowledge-area section headers: *Core
  Configuration, Processes, Tasks, Reporting/Integrations, Documents* (the exact
  labels `build_kt_plan.py` emits).
- **One row per topic**, columns: Knowledge Area | Related Tasks & Reports in
  Workday (the exact searchable task/report names) | Topic Description | Primary
  Transferor | Primary Transferee | Transfer Method | Target Completion Date |
  Status | Notes | Final Sign-Off (Transferee) | Sign-Off Date.
- **Topic descriptions are "Be able to:" bullets** - competencies, not agenda
  items ("Be able to: close ledger periods; open ledger periods"), which is what
  makes teach-back checkable per row.
- **Status is a four-step maturity ladder** (dropdown, with a COUNTIF summary
  block at the top of each sheet):
  1. `NS: Not Started`
  2. `U: Understood` - attended/heard it
  3. `D: Demonstrated` - performed it observed (the teach-back bar above)
  4. `R: Responsible` - owns it in production without the delivery team
  KT closes at **R**, not D - Demonstrated is the session exit bar; Responsible is
  the engagement exit bar.
- **Transfer methods are letter-coded**, several per row (observed codes:
  `P: Monitored Practice`, `S: Shadowing`; extend the legend per engagement).
- **Sign-off is per topic and belongs to the transferee** - the same
  named-recipient rule as above, at finer grain. The workbook's completed sheets
  roll up into the one-page sign-off artifact below.

## The sign-off artifact

KT closes with a one-page sign-off the client signs: **"Client confirms readiness to
operate, support, and extend the application."** It contains:

- The completed tracking table above (all rows green).
- The named recipients per audience.
- Links to each deliverable and recording.
- Client signature + date.

This artifact **gates project closeout in wd-post-go-live** - hypercare doesn't end
and the project doesn't close until KT sign-off exists. Because KT runs in parallel
with hypercare, schedule sessions early in the hypercare window: hypercare tickets
feed the runbook and FAQ, and the support-desk session lands best while real tickets
are flowing.
