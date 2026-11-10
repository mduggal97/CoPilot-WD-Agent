# Design change control - after sign-off

Before sign-off, the design doc is a living draft; edit freely with version bumps. After sign-off, it's a baseline that estimates, code, and test scenarios all reference - uncontrolled edits silently invalidate all three. This process is lightweight on purpose: heavyweight change control gets bypassed, and bypassed control is worse than none.

## The baseline

At sign-off: bump to the next major version (v2.0), record the sign-off date + approver in the Overview tab, and archive a copy (e.g. `_signed/` subfolder or the client's document system). This archived file is what "works as designed" means in defect triage (wd-testing).

## The change request flow

1. **Log it**: CR ID (CC-### or client convention), date, requester, description, reason. The CR log lives with the project tracker (wd-pm owns the log pattern; wd-smartsheet the transport) or as a section on the Open Items tab for small projects.
2. **Assess impact**: affected tabs/pages/BOs/orchestrations (use wd-extend-dev's design-to-code sweep in reverse), LOE estimate if material (wd-estimate's calibration data), schedule impact, testing impact.
3. **Decide**: client approves, defers, or rejects - with a named decider and date. Verbal approvals get confirmed in writing (wd-comms decision-needed template).
4. **Execute**: update the design doc (minor version bump; change-log entry on the Overview tab: version, date, CR ID, summary), THEN update code (wd-extend-dev) and test scenarios (wd-testing) against the new version.
5. **Trace**: the code change cites the CR ID in its comments; the CR log records which design version absorbed it.

## Redline vs. new version

- **Minor changes** (a CR touching a few tabs, clarifications, single-feature deltas): edit the SAME file - minor version bump, change-log entry on the Overview tab, and yellow cell markers on every changed cell until the change is built and verified (the standard yellow-highlight open-items convention). The file stays the one living baseline.
- **Major re-scopes** (new module, changed architecture, a batch of CRs that rewrites whole tabs): cut a NEW major-version file (v2.0 -> v3.0) from the current baseline, redline there, and re-run sign-off; archive the prior version alongside the original `_signed/` copy.
- **IDD note**: when an integration's requirements change, resync the Unit Testing tab's "Added to Test" column in the same edit - every added/changed requirement row needs its test row added or updated, or the IDD silently claims coverage it doesn't have (wd-testing consumes that column as the regression source).

## What is NOT a CR

- Fixing the doc where it mis-recorded an already-made decision (correct it, note it in the change log).
- Clarifications that don't change behavior (add them; no approval loop).
- Defects - code not matching the signed design goes through wd-testing's triage, not change control.

The boundary question is always: "does this change what was signed?" If yes, CR. If it changes only how it's written down, edit with a change-log entry.

## Change-log / version-comparison view

When the deliverable is a presentable "what changed between version A and B" summary (a SteerCo / client "what changed since last sign-off" artifact, not just the Overview-tab change-log entry), build a side-by-side before/after table and classify every item into exactly THREE types - do not invent a fourth:

- **Added** (new) - the empty (before) side shows a placeholder "-".
- **Removed** (deleted) - the empty (after) side shows a placeholder "-".
- **Modified** (edited; a move-only change = Modified "(reordered)").

Rules: use the **verbatim source language**, no clean-up or paraphrase; omit unchanged rows unless completeness is explicitly asked for; split at ~8-10 rows per slide/section with "(1 of N)" titles; color-code the three types consistently (the palette itself comes from the brand in use - neutral by default). Render via **pptx**; this is the classification pattern, not the layout. (adapted from an internal firm skill, 2026-08-28)
