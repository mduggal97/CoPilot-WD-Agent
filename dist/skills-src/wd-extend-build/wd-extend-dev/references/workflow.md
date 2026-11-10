# Change workflow - pull-latest, diff, change-lists, design-to-code validation

## Why this file exists

Extend apps end up co-owned: a client developer starts editing while the delivery firm still supports the app, or two source trees exist for two orgs. The workflows here prevent the two failure modes that actually happened: clobbering a client developer's work, and shipping a "complete" change that missed one of the pages it touched.

## Rule 0 - Turn the ask into acceptance criteria before you touch code

The entry step of every build or change, run BEFORE the pull-and-diff below and before a
single `wdcli` edit: convert the request into a short list of **scoped, testable acceptance
criteria** - what must be true for this change to count as done, in the user's language,
each one you could later mark pass/fail. High-impact changes get this without exception:
anything touching security domains, data/BO shape, a tenant migration, or an integration
write. A fuzzy ask there is exactly how scope creep and silent regressions get in.

Keep each criterion concrete: "approver at step 3 can send back; the submitter's revise
page reloads the prior values" beats "fix the revise flow." Unknowns become explicit
questions (yellow/open-item), never silent assumptions. These criteria then scope the
design-to-code sweep (Rule 3) and seed the test scenarios - but wd-testing
(`references/unit-testing.md`) OWNS scenario derivation: hand it the criteria, don't
re-derive scenarios here.

(Inspiration: skillsmp `intent-driven-development` - pin the intent before the build.)

## Rule 1 - Pull latest and diff before ANY edit

```powershell
wdcli app download <refId> -d <fresh-dir>
# diff <fresh-dir> against your local tree before touching anything
```

If the diff shows changes you didn't make, someone else is active in the app. STOP and switch to change-list mode (Rule 2) unless the lead explicitly says to edit. If the download fails with an auth error, the token expired - ask the user to re-auth, don't skip the pull.

## Rule 2 - Change-list deliverable when a client developer owns the code

Instead of edit -> build -> deploy, deliver a numbered list the client developer executes:

```
1. presentation/addLine.pmd - in the quantity field's validations array, change the
   value expression to allow 0 when "No items expired" is selected.
   Why: per 7/22 design decision (OI-31), a checked-clean bin records quantity 0.
2. presentation/scripts/reportCalc.script - in computeAll(), skip lines where
   noItemsExpired == true when totaling expiries.
   Why: checked-clean lines count toward coverage, not expiry totals.
```

Each item: file -> exact change -> why (with design/open-item reference). This format doubles as KT (the wd-kt skill builds on it) and as a review record. Offer to pair on the first few changes.

## Rule 3 - Design-to-code validation before executing changes

When the design or requirements changed, do the full sweep BEFORE writing code:

1. Read the CURRENT design doc version (check you have the latest - versions move during design).
2. Enumerate every code surface the change touches: pages (including confirm/detail/report pages that display the field), script files, orchestrations, BOs (+ the full-replace-PUT ripple), AMD routes/flows, seed scripts, security domains.
3. Write the complete change plan, then execute it as one coherent edit set - partial updates that miss a display page are the most common defect class. Carry the design's **invariants contract** through this sweep (architecture-review.md) - each invariant with its how-to-check - so no builder quietly drops a load-bearing assumption.
4. Update code comments and the design doc's affected tabs in the same change set.
5. After build + deploy, run the affected unit scenarios (wd-testing) and record results.

## Multi-tree hygiene (two orgs, same app)

When an app exists in two orgs (e.g., a firm dev org + client org): edit ONE tree, mirror `model/` + `presentation/` (and `orchestration/`) to the other deliberately, then upload under each account. Respect declared freezes - a frozen tree diverges intentionally; note the divergence and catch it up only when the lead says so. Track which tree is deployed where in the app's DESIGN.md or the design doc.

## Test data

Keep seed/wipe scripts alongside the app (pattern: `seed-<tenant>.ps1` / `wipe-<tenant>.ps1`, deleting child->parent to avoid referential 500s, reading a token from `wdcli tenant token <alias> --ci`). Rebuild test data from scripts rather than hand-entering - reproducible data makes retests cheap.
