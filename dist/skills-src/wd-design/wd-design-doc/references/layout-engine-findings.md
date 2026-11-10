# Layout engine - build outcomes (2026-08-11)

Companion to `layout-engine.md`. This started as a build plan for the structural-fidelity work; that
work is now DONE and render-verified. Kept as a concise record of what was built and the traps that
shaped it. The authoritative "how it works" is `layout-engine.md`; the run order and gates are in
`document-quality-gates.md`.

## What shipped
- **Calibrated column widths** (`xlsx_extract_layout.py` -> `tab_layouts` -> `xlsx_apply_layout.py`,
  widths only, balancer defers). Proportions match the reference.
- **Safe structural directives** (`tab_layouts[tab].structure` + `xlsx_apply_structure.py`):
  `merge` / `unmerge` / `move` / `inject` / `border`, optional `row_pt`. Reproduces callouts, panels,
  authored labels WITHOUT a wholesale transplant. Calibrated for all 22 IDD tabs from `_josh_upds`.
- **Mandatory coverage guard** (`xlsx_coverage_guard.py`): value-multiset snapshot at pipeline start,
  `check` after EVERY step, abort on any dropped value.
- **Transplant fallback** (`xlsx_transplant_sheet.py`): copy a fully-authored reference sheet
  wholesale, coverage + branding checked. The escape hatch; the directive engine is the default.
- **Gridlines off, hidden-tab branding bracket, uniform-to-worst-row heights, role-weighted widths**
  for non-calibrated tabs. Render-verified.

## The cascade - SOLVED
Reproducing `Requirements!J7:J35` via COM `Merge()` cascaded into `B7:R35` because the backup holds a
stack of overlapping `J7:R7 ... J49:R49` merges and a naive merge ABSORBS their horizontal extent
(proven by isolated experiment). Fixes, all in place:
1. `apply_structure` **unmerges every intersecting merge FIRST**, then merges the exact target.
2. Merges are the **LAST structural op** - `apply_structure` runs AFTER `normalize` (which has many
   internal `Merge()` sites and is proven-safe on the backup's own topology), and WITHIN a tab merges
   come after moves/injects (so a band never merges before its label is in place - the bug that
   stacked Flow's diagram-band labels; fixed in `derive_structure`'s emit order).
3. Every merge has a **tail-empty assert** (skips + reports rather than silently deleting) and the
   pipeline-wide coverage guard is the backstop (it caught a real 197-cell deletion during the build).

## Result
Merges match `_josh_upds` on 20/22 tabs; widths within rounding; coverage held every step. Two tabs
carry a flagged best-effort gap (Question `B70:F70`, WD Solution - O4I `H67:I67`) where OUR content
occupies the cell the reference merged, so the merge is safely REFUSED. `tab_layouts` `inject`/`move`
directives carry THIS reference's content - re-derive (`extract_layout --baseline`) for a different
integration's IDD rather than injecting one doc's content into another.

## Calibration leaked onto every doc - FIXED (2026-10-17)
That warning was prose only, and the calibration sat in `templates/idd.json`, which every script
loads by default. So regenerated IDD skeletons got the reference's injected text, and Extend docs
(three shared tab names) got its widths and merges. Every gate passed, because adding text deletes
nothing. Now each calibration is its own file in `templates/layouts/`, bound to its document's
identity cells (IDD `Overview!J8` / `J9`), and applies to no other workbook; `check_profiles.py`
check 7 keeps it out of template profiles. The `_josh_upds` calibration was moved there verbatim and
is UNBOUND until bound on its own backup. How it works: layout-engine.md, "A calibration belongs to
one document".

## Visibility restore bug - FIXED
`xlsx_sheet_visibility.py restore` once left three tabs (`WD Solution - General/CC`,
`Field Overrides - CC`) wrongly VISIBLE: Excel SILENTLY refuses to hide the ACTIVE sheet (and the last
visible one) with `DisplayAlerts` off. Restore now (a) activates a keeper-visible sheet before hiding
anything, (b) VERIFIES every sheet against the map and re-applies, and (c) RAISES on any residual
mismatch so the pipeline fails loudly instead of shipping wrong visibility. Final O4I output verified:
every sheet's visibility matches the recorded map.

## Regenerated templates: blocks, empty tables, long headings - FIXED (2026-10-17)
Once builder output got branded bands and headers (templates/idd.json roles), the layout pass saw its
tables for the first time and three defects surfaced. The shared judgements now live in ONE module,
`xlsx_layout_rules.py`, imported by the styler, the notes pass and normalize, with a self-test that
reads both builders' sheet tables and pins the results.
1. **Welded columns.** The notes pass merged across the gutter, normalize counted merged columns as
   in use, and every IDD tab logged `blocks=1`. Now a gutter is an empty column between two
   band-headed regions (merges never decide it; of several empty columns only the last), the notes
   pass stops at its block, and bands/rules are grouped per block, not per row.
2. **Hint row boxed as table body.** The body scan skipped blank rows under a header. Now the body
   is the filled rows directly under it; an empty table frames its header only; the "Need more
   rows?" hint, a band, a rule or another header ends a table. Headings size from the table
   directly under them, and the 18pt band minimum is applied in the plan.
3. **Long heading demoted to a note.** Prose is now judged by sentence punctuation (over 70 chars),
   or length over 120 - not a bare 70-char cut-off. Band text over the format gate's own
   `LONG_TEXT` (60) wraps; shorter text overflows, so the layout pass never trips the gate.
Verified on regenerated IDD + Extend with synthetic rows: full 12-step pipeline, coverage guard OK
after every step, populated tabs render pixel-identical except IDD Requirements (its table now
closes at H instead of running over the Notes column).

## Balance rewrote widths that were already right - FIXED (2026-10-18)
With the calibration no longer applied to regenerated docs, `xlsx_balance_columns.py` ran on every
tab, and its role-weighted re-allocation rewrote the builders' hand-tuned widths: on a freshly
regenerated, seeded IDD 108 width changes across 18 tabs, and 76 across 15 Extend tabs, with almost
nothing starved. Three misreads drove the worst of them:
- **Roles taken per column across stacked tables.** Extend Unit Testing's legend header labelled the
  scenario columns: Scenario 40 -> 18, Expected Behavior 46 -> 22, Linked Req 18 -> 54.
- **A section band read as a column header.** "Key Details" made IDD Overview's caption column prose:
  label I 19 -> 77, value J 81 -> 23.
- **Header keywords that misfire.** "Display Options" is prose by keyword, so Custom Object L and M
  swapped (16.7 -> 71.2, 56.6 -> 21.6). Per-table roles alone still cut "Expected Behavior" to 18,
  because "behavior" is in no word list. No word list can be complete.

Also: formula TEXT was measured as content, and a column grouped with an equal neighbour read as the
8.43 default. Fix: `--mode relieve` (the default) moves width only where content needs it.
- **Pass 1:** a column that needs more than ~6 lines, or whose word does not fit, is paid by its
  neighbours' spare width, flag columns first.
- **Pass 2:** only IDLE width (width a column does not use) moves, to cut-off text or text wrapping
  past 3 lines - never from a prose column or an empty table.
- **Roles** are read per TABLE; label/value panels keep width on the value column; formulas and
  grouped widths are handled.
The same two docs now get 15 and 11 changes, each a word, a text that did not fit or a cut-off
text. The old method is `--mode reallocate`. `xlsx_balance_columns.py --self-test` holds the cases;
each defect, re-planted, fails it.

**Found on the way - short text is cut off and no gate sees it.** The format audit flags unwrapped
text only over 60 characters. A shorter unwrapped text beside a filled cell renders cut off, and the
audit passes it: 1 such cell on a regenerated IDD and 5 on an Extend doc before this fix (Extend Unit
Testing's scenarios at 18 wide). Which cells it hits moved with every width change. Balance now
offers idle width to it, but the cure is wrapping it - a follow-up for the layout pass and the audit.

## Oracle & harnesses
- `_josh_upds.xlsm` is the hand-cleaned reference for ALL 22 tabs - a ground truth to diff against.
- Beside the doc: `compare_to_josh.py` (per-tab col/row-delta + merge-set diff) and `render_tabs.py`
  (named-tab PDF/PNG, renders to a LOCAL dir - OneDrive locks the synced path). RENDER is the arbiter (G18).
- COM gotchas: late-bound `win32.Dispatch` only; clear `%TEMP%/gen_py`; kill orphaned EXCEL.EXE; start
  every run from `_prestyle_backup_*.xlsm`; `xlsx_coverage_guard` retries on OneDrive file locks. See
  the memory file `project_idd_formatting_skill.md`.
