# Meeting Intake - Transcript -> Synchronized Artifacts

Use this routine when the user PASTES or attaches transcript-shaped source input:
"here's the transcript", a pasted Teams/Zoom transcript, an attached meeting-notes
file, meeting-recording output, or "update the design/tracker from this meeting"
WITH the transcript provided.

This is an EXTRACT-AND-DELEGATE workflow. Your job is to extract structured facts
from a transcript and route each fact to the skill that owns the target artifact.
Do NOT restate design-doc tab formats, fill colors, or tracker column mechanics
here - those live in **wd-design-doc** and **wd-smartsheet**, and duplicating them
causes drift.

Boundary reminder: authoring a recap or minutes WITHOUT source input is **wd-comms**,
not this routine. Meeting intake fires only when transcript-shaped source is provided.

Why this routine exists: on a large multi-app program, the transcript-drop habit is
what keeps design docs and trackers current. A decision made on a call that never
lands in the Open Items tab is a decision that gets re-litigated - or worse,
silently contradicted - three weeks later.

## Step 1 - Ingest

Transcripts are the highest-sensitivity routine input this suite handles (names,
verbatim quotes, HR/finance detail) - the data gate in **wd-extend-lifecycle**
references/ai-data-governance.md applies BEFORE ingestion; minimize person records
and production data the sync doesn't need.

Accept either pasted transcript text or a file path (Read it). Before extracting,
establish context - every downstream update needs it:

- **Meeting date.** From the transcript header or filename; ask if absent. This
  date goes on every open-item resolution and decision note as provenance.
- **Attendees.** Map speaker names to roles where known (client SME, delivery-team lead,
  vendor PM, etc.). Role matters: a scope statement from the client sponsor is
  a decision; the same sentence from a junior analyst is a candidate.
- **Which app/project.** One program call routinely covers several apps (e.g.
  a costing app, a reconciliation app, a forms app...). If the transcript is ambiguous about
  which design doc(s) it touches, ASK before extracting - routing decisions to
  the wrong workbook is worse than a delay.

## Step 2 - Extract, with quotes

Walk the full transcript once and bucket every substantive statement. For each
item, capture the decisive sentence VERBATIM with the speaker - the quote is
the provenance that makes a design-doc note defensible in client review.

Buckets:

1. **Decisions** - anything that resolves a design question. Quote + speaker + date.
2. **Answers to existing open items** - match against the current Open Items tab
   (read it in Step 3 first if you haven't). Note which open-item row each answers.
3. **New requirements / scope changes** - anything the design doc doesn't cover yet.
4. **Action items** - every item carries owner + due date + a one-line
   acceptance criterion (what done looks like). Unknowns are written as
   explicit `TBD-owner` / `TBD-date` / `TBD-done-means` - never guessed,
   never left blank.
5. **Parking lot** - explicitly deferred topics ("let's take that offline"),
   plus any unresolved discussion that fits no other bucket - route it here
   rather than dropping it.
6. **Contradictions** - anything that conflicts with the current design. FLAG
   THESE LOUDLY at the top of your summary. Contradictions are the expensive
   category: a silently-absorbed reversal means the doc and the client's mental
   model diverge, and that surfaces in UAT, not review.
7. **Commitments made (delivery team)** - any consultant statement on the call that
   promises scope, dates, or system behavior ("we'll include that", "that'll be
   ready by...", "the app will handle X"). Quote + speaker + date, same as
   decisions. These are what fee disputes mine - capture them even when casual.

## Step 3 - Reconcile against artifacts (the heart)

Read the current design doc's **Open Items tab** and the relevant content tabs
before writing anything - reconciliation means comparing transcript facts to
current artifact state, not appending blindly.

Then route each extracted item:

- **Answered open item** -> update the item's row and the content cell it points
  to, replace placeholder text with the confirmed answer, and remove the yellow
  highlight - follow **wd-design-doc**'s yellow-highlight convention for the
  mechanics (which fills, which statuses; do not improvise colors here). Add the
  meeting date + speaker quote as the resolution note.
- **New requirement or discovery answer** -> route into the Requirements /
  Discovery tabs via **wd-design-doc**.
- **Requirement CHANGE after design sign-off** -> this is NOT a silent edit.
  Route to **wd-design-doc**'s change-control process so the change is logged
  and versioned. If unsure whether the doc is signed off, ask.
- **Tracker/task updates** (action items, status changes, dates) -> **wd-smartsheet**.
- **Action items with owners** -> also register with the wd-pm follow-up discipline
  (see SKILL.md "The follow-up discipline") for tracking.
- **Parking lot** -> append to the Open Items tab as new open (yellow) rows via
  **wd-design-doc**, so deferred topics don't evaporate.
- **Commitments made (delivery team)** -> check each against the SOW's enumerated scope:
  in scope = confirmation, note it; beyond scope = route to scope review and the
  CR log (wd-pm `references/raid-log.md`) - a casual "sure, we'll add that" on a
  call is a scope change and gets change-controlled, not silently absorbed.

## Step 4 - Output

Post back to the user, in this order:

1. **Contradiction flags** (if any) - first, and unmissable.
2. **Minutes summary** - Decisions / Answers / New items / Actions (owner + date),
   each with its verbatim quote.
3. **Changelog** - for EVERY file touched: file path, tab/row/cell, what changed
   (e.g., "Open Item #12 -> Resolved, yellow cleared on Field Specs B24"). The user
   spot-checks from this list; an update he can't find is an update he can't trust.

Never mark an open item resolved without listing it in the changelog.

## Step 5 - Habit prompt

If you notice design work happening on an Extend app (doc edits, requirement
discussions, wireframe updates) and there has been no meeting sync recently
for that app, REMIND the user: "Any recent call transcripts for <app> I should
sync?" The transcript habit - not memory - is what keeps a program's designs and
trackers current; a gentle nudge after design meetings protects that. This pairs
with the wd-pm "After every meeting" routine, which prompts for the transcript.

## Worked micro-example

Transcript snippet (costing-app design call):

```
[Client Finance Lead] For the default allocation, use the position's cost center - not the worker's.
[Consultant] Got it. And the Program-worktag question from last week?
[Client Finance Lead] Confirmed - the Program worktag is required on every allocation line.
[Consultant] I'll get the RaaS validation spec drafted by Friday.
[Client IT Lead] Let's park the retro-costing question for the next session.
```

Extraction:

- **Decision:** default allocation source = position's cost center. Quote: "use
  the position's cost center - not the worker's" - Client Finance Lead, 2026-07-29.
- **Open-item answer:** Open Item on the Program worktag -> Resolved. Update
  the row + the Field Specifications cell it references, clear yellow (per
  **wd-design-doc**), note: "Confirmed required on every allocation line -
  Client Finance Lead, 2026-07-29 call."
- **Action item:** <owner> - draft RaaS validation spec - due Fri 2026-07-31 ->
  **wd-smartsheet** task + wd-pm follow-up.
- **Parking lot:** retro-costing question -> new open (yellow) Open Items row.

## Delegation boundaries (summary)

- **Design-doc mechanics** (yellow-highlight convention, tab routing, requirement
  change control) -> **wd-design-doc**.
- **Tracker transport** (sheet/row/column updates, task and status changes) ->
  **wd-smartsheet**.
- **Action-item follow-up** (owner + due date + aging) -> wd-pm follow-up discipline
  (SKILL.md) and the RAID/CR log (`references/raid-log.md`).
- **Recap or minutes with NO source input** -> **wd-comms**.

**Quality-gate rule (suite-wide):** this routine produces no artifact of its own -
every output is a delegated edit, so the named checks live in the owning skills it
routes to (**wd-design-doc** for doc/open-item edits, **wd-smartsheet** for tracker
rows, wd-pm for action items). Run each owning skill's check on the artifact it
produced and report the results with the changelog.
