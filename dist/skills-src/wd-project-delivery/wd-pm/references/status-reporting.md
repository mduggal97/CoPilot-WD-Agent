# Weekly Status Reporting

Format and rules for the weekly status report - per workstream/app, rolled up to
program level when in program mode.

## The RAG rule (state it, apply it, never bend it)

| RAG | Rule |
|---|---|
| **Green** | On plan. All milestones tracking to committed dates. |
| **Amber** | A **risk to a milestone** exists **AND a mitigation is named**. Amber without a mitigation is just Red with better manners - name the mitigation or go Red. |
| **Red** | A milestone **will slip without intervention**. Red is a request for help, not an admission of failure. |

**Never Amber out of politeness.** If the milestone will slip without someone
above the team acting, it's Red. Sandbagging the RAG delays the intervention
that would have saved the date. Conversely, don't hold Green while quietly
absorbing risk - the moment a mitigation is needed, it's Amber.

RAG transitions get one sentence of explanation (what changed since last week).

## Weekly status format

One block per workstream/app:

```
## <App / Workstream> - Status w/e <Friday date>
RAG: <Green|Amber|Red>  (prior week: <RAG>)
<If Amber: risk + named mitigation. If Red: what slips + intervention needed.>

### Accomplished this week
- <shipped/decided/closed items - outcomes, not activity ("designed X" only if X is done)>

### Planned next week
- <specific, checkable next Friday - avoid "continue working on">

### Blockers
- <blocker> - **unblocked by: <name>** - needed by <date>
  (Every blocker names WHO unblocks it. A blocker without a name is a status
  observation, not a blocker.)

### Metrics
- Open items: <count> open (<n> aged >2 weeks; oldest: #<id>, <days> days)
- Actions: <n> open, <n> past due
- [During testing] Defects: <n> open (<n> critical) / <n> closed this week
- Milestones: next milestone <name> - <date> - <on track / at risk / slipped>
- Financials: budget <hrs/$> / actuals <hrs/$> / EAC <hrs/$> / variance <+/-%> -
  financial RAG <Green|Amber|Red>
```

## Metrics guidance

- **Open items count + age** is the leading indicator during design - a flat or
  growing count with rising age means the design meetings aren't closing items
  (fix the agenda, see SKILL.md meeting routines).
- **Defect counts** replace open-item counts as the headline metric during Unit
  Test / UAT / E2E. Track open by severity + weekly close rate.
- Pull counts from the Smartsheet trackers via **wd-smartsheet**; don't hand-count.

## Financials block

One financial line per app, every week - budget comes from the estimate/SOW
(**wd-estimate** / **wd-contracts**), actuals from time tracking, and the line
feeds the SteerCo budget slide directly (see steering-committee.md).

**Financial RAG is rule-based, parallel to the schedule RAG:**

| RAG | Rule |
|---|---|
| **Green** | EAC no more than 10% over budget (significantly UNDER budget is Green for cost but worth a note - it can signal under-delivery or a scope miss) |
| **Amber** | EAC 10-15% over budget |
| **Red** | EAC >15% over budget, **or** contingency exhausted |

**EAC discipline:** EAC = actuals to date + an **honest** estimate-to-complete -
not budget minus actuals, and not last month's EAC carried forward. Re-baseline
only via a logged decision (Decisions log, raid-log.md), never silently; a
quietly re-baselined budget is the financial version of Amber-out-of-politeness.

In-flight actuals are also the closeout data: **wd-post-go-live** already
mandates writing actuals back at closeout (calibration for future estimates) -
keeping this block current weekly means no end-of-project reconstruction.

## Escalation note (when Red needs leadership)

Keep it to five lines - leadership acts on Reds that are easy to act on:

```
ESCALATION - <App>: <one-line problem statement>
Impact:   <which milestone/date slips, and what that costs downstream>
Cause:    <one sentence - fact, not blame>
Ask:      <the specific decision or resource needed, from whom>
Deadline: <date the ask must be answered by to save the date>
```

Send it the day the workstream goes Red - not in Friday's report if Red was
known Tuesday. Log the escalation as an Issue in the RAID (see raid-log.md).

## Rollup (program mode)

Program-level status = one RAG line per app (table), then only the Amber/Red
blocks in full. Green apps get one line each. See program-mode.md.
