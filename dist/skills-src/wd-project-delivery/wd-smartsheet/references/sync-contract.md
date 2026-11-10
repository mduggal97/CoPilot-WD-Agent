# Two-way sync - column ownership (anti-clobber)

When a sheet is edited by BOTH a human (in the Smartsheet UI) and this tool (via the API) - a
live defect / RAID / tracker register - never let the two sides overwrite each other. This is the
generic anti-clobber MECHANIC (adapted from an internal firm sheets-sync contract, 2026-08-28);
the specific column-to-owner taxonomy for a given register lives with the register that owns it.

## The contract

- **Declare each column HUMAN-OWNED or TOOL-OWNED up front.** This skill owns only the generic
  mechanic; the column model for a defect register lives in
  `wd-testing/references/defect-triage.md`. Apply the same split to any co-edited register (RAID,
  tracker).
- **PULL (sheet -> local):** read ONLY human-owned columns into your working copy.
- **PUSH (local -> sheet):** write ONLY tool-owned columns back. Neither direction touches the
  other side's columns, so simultaneous edits cannot collide.
- **An automation-mirrored column is NEVER declared tool-owned-writable.** A Latest Comment /
  Notes / Status Update column fed by a sheet automation (see the comment rule in SKILL.md section 4
  and api-details.md) is off-limits to PUSH - comment via a row Conversation, never PUSH-write the
  cell. Watch the name-proximity trap: "Status" (a plain, writable pick column) vs "Status Update"
  (an automation-mirrored comment column) - the two-word one is the automation's, not yours.
- **SKIP BLANK SOURCE CELLS on import** - a blank never overwrites a real value (empty = "no
  update," not "clear it").
- **UPSERT BY A STABLE KEY** (defect ID / RAID ID), not row position - rows reorder.
- **On an Excel/CSV re-import, SCORE the first ~10 rows to find the real header** (a title row above
  the header must not hijack the import); unknown headers go to an "extra" bag, not dropped.

Used when wd-pm (raid-log) and wd-testing (defect intake) drive a shared Smartsheet register.
