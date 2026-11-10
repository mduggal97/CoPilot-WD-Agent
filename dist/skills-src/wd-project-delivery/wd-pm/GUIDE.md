---
name: wd-pm
description: >-
  Project-management routines for Workday Extend delivery - agendas, project plans,
  timelines, status reports, weekly status, RAID (risks and issues), action items,
  follow-ups, task trackers, milestones, and "who owns what" questions. Use when asked
  for a meeting agenda, a project plan or timeline, a weekly status report, a
  RAID log update, action-item capture or follow-up review, a task tracker, milestone
  tracking, or program-level coordination across multiple Extend apps and integrations.
  Also owns meeting intake: a pasted or attached meeting transcript, a Teams/Zoom
  transcript, meeting recording or notes, or "update the design/tracker from this
  meeting" WITH the transcript provided - it extracts decisions/answers/actions and
  delegates the edits. Authoring a recap or minutes WITHOUT source input belongs to
  wd-comms. This skill owns PM content and routines; Smartsheet API mechanics belong
  to wd-smartsheet (this skill calls it for transport).
---

# wd-pm - PM Routines for Extend Delivery

PM content and cadence for Workday Extend projects: meetings, actions, status,
RAID, plans, and multi-app program coordination.

## Reference map - read what you need

| Need | Go to |
|---|---|
| Weekly status format, RAG rules, financials block, escalation notes | `references/status-reporting.md` |
| RAID + CR + Decisions log columns, scoring, cadence | `references/raid-log.md` |
| Smartsheet-importable Excel plan, phase skeleton | `references/project-plan-format.md` |
| Multi-app program coordination (a large multi-app program) | `references/program-mode.md` |
| SteerCo deck skeleton, sponsor charter + decision rights, exec one-pager, no-surprises protocol | `references/steering-committee.md` |
| Client-facing onboarding packet (responsibilities-by-phase, decision calendar, long-lead asks) | `references/client-onboarding-packet.md` |
| Meeting intake: transcript/recording/notes -> extract decisions/answers/actions and delegate the edits | `references/meeting-intake.md` |

## Boundaries

- **Smartsheet transport** - sheet/row/column API calls, auth, the program's sheet IDs -> **wd-smartsheet**. This skill decides *what* goes in the sheet; wd-smartsheet moves it.
- **Excel mechanics** - openpyxl, formatting, formula preservation -> **xlsx** skill.
- **Change control** - the CR *log* pattern lives here (see `references/raid-log.md`), but the change-control *process* (design baselining, re-approval flow) is **wd-design-doc**'s.
- **Sensitive data in the tracker** - RAID/CR/status entries attract PHI/PII (a worker's data issue, an accommodation, a PIP). Do not record person-identifying or sensitive detail beyond what the tracker's audience is entitled to; use the least-identifying form (worker ID/role, not name+SSN). Owner rule: wd-extend-lifecycle `references/ai-data-governance.md` section 6 (enforced at write time by **wd-smartsheet**).
- **Meeting transcripts** - ingestion/parsing of recordings and transcripts is a wd-pm routine now; see `references/meeting-intake.md`. It extracts and delegates: design-doc mechanics -> **wd-design-doc**, tracker mechanics -> **wd-smartsheet**. A recap or minutes with NO source input -> **wd-comms**.

## Meeting routines

### Agenda template

Every design/status meeting agenda has five sections, in this order:

```
# <App / Workstream> - <Meeting type> - <Date>

## 1. Objectives (2-3 bullets: what "done" looks like for THIS meeting)

## 2. Open actions review  <- FIRST, before new content
   Walk the open action list from last meeting: done / not done / re-dated.

## 3. Open items to close TODAY
   Pull the yellow-highlighted items from the design doc (via wd-design-doc)
   that are answerable by the people in the room. List each with its Open
   Item # and the specific question. Target: leave with answers, not notes.

## 4. Decisions needed
   Explicit list - each one framed as a question with options if known.
   Every decision made goes to the Decisions log same day (see raid-log.md).

## 5. Parking lot + actions recap (last 5 minutes)
   Read back every new action aloud: WHAT, WHO, WHEN.
```

### Design-review cadence

- **Active design phase:** weekly working sessions per app; agenda driven by the
  design doc's yellow open items - the meeting exists to burn that list down.
- **Sign-off approaching:** shift to a walkthrough session (full doc, tab by tab),
  then a formal sign-off meeting with decision-makers only.
- **Post-baseline:** design topics only enter meetings as CRs (wd-design-doc owns
  that process); don't reopen settled design in status meetings.

### The follow-up discipline

This is the routine that stops actions rotting:

1. **Capture at the moment:** every action gets an **owner** (one name, never a
   team) and a **due date** at capture time. No owner or no date = not an action,
   it's a wish. Push for both before the topic moves on.
2. **Review at the START of the next meeting** - not the end, when time's gone.
   Open actions are agenda item #2, before any new content. Each item is done,
   not done (why + new date), or explicitly dropped.
3. **Age visibly:** track days-open. Anything past due twice gets escalated or
   killed - don't let it ride a third time.
4. **One list:** actions live in one place (the RAID/actions sheet via
   wd-smartsheet), not scattered across notes files.

### After every meeting

- Recap actions in writing same day (owner, due date, exact ask).
- **Prompt the user for the meeting transcript** so meeting intake can ingest it
  (`references/meeting-intake.md`) - decisions and actions in the transcript
  reconcile against what was captured live.
- Update the design doc's open items (answered items get unhighlighted -
  wd-design-doc owns that mechanic) and the Decisions log.

## Status rhythm (summary - full format in references/status-reporting.md)

- Weekly status per workstream/app: RAG + accomplished / planned / blockers + metrics.
- RAG is rule-based, not vibes-based - never Amber out of politeness. Rules in the reference.
- RAID review happens weekly inside the status meeting, not as a separate ceremony.

## Project plans (summary - full format in references/project-plan-format.md)

- Excel, Smartsheet-importable, one tab per workstream + a Master Timeline tab.
- Reusable generator `generate_project_plan.ps1` - regenerate from `references/scripts.md` if it isn't on your machine (don't fork; don't rely on the author's path).
- Standard Extend phase skeleton with typical proportions lets a new plan draft in minutes.

## Program mode (summary - full reference in references/program-mode.md)

When multiple Extend apps run in parallel (a large program can run 8+), switch to program mode:
shared tracker with per-app workstreams, single program-level RAID with app tags,
cross-app collision checks (reference IDs, security domains), shared-component
reuse, and batched Workday gating docs. Details in the reference.

## Lifecycle neighbors

wd-pm is cross-cutting - it supports every phase from **wd-estimate** through
**wd-post-go-live**:

- **wd-estimate** -> estimates seed the plan's durations and phase proportions.
- **wd-design-doc** -> yellow open items feed agendas; design decisions feed the
  Decisions log; change-control process (baselining, re-approval) lives there.
- **wd-comms** -> authoring a recap or minutes WITHOUT source input (meeting intake
  here handles the transcript-provided case).
- **wd-smartsheet** -> transport for every sheet-backed artifact here (RAID,
  actions, plans, trackers); owns the program sheet-ID registry.
- **wd-extend-dev** -> build status feeds weekly status; shared-component reuse
  patterns (`wdcli app copy`) referenced in program mode.
- **wd-deployment** -> the Workday gating docs (Volumes Questionnaire, Performance
  Testing Template) tracked as plan milestones and batched in program mode.
- **wd-post-go-live** -> hypercare cadence is the last phase of every plan.
- **your org's delivery-methodology skill (if installed)** -> when building a RACI or staffing model, pull the role definitions and the STAGE|TASK|A/R/I RACI format from it rather than reinventing them here.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
