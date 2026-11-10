# Test-automation / regression harness

Scenario execution in this skill is mostly manual. This reference assembles the pieces that already exist into
a repeatable, API-driven **smoke/regression harness** for an app's critical paths - the thing that makes
per-build smoke checks and twice-yearly release regression cheap and reliable, instead of a manual re-run.

## What the harness is

A scripted loop over a config-driven test list: **seed -> exercise -> assert -> reset.**
1. **Seed** synthetic data (the seed/wipe pattern in wd-extend-dev `tenant-ops.md`).
2. **Exercise** each critical path via API - create/route a record (BO REST POST/PUT), launch an orchestration
   (direct `POST .../launch`), advance a BP step - the same calls the app makes.
3. **Assert** the expected outcome - read it back (WQL / RaaS / BO GET), check response codes, and verify BP
   event state. Record pass/fail with evidence (the response body / record id).
4. **Reset** - clean up what you created (soft-delete flags set on create, or wipe) so the next run is repeatable.

It reuses existing building blocks - do NOT reinvent them: `workday_rest.py` and the seed/wipe + `check-tenant`
identity gate (wd-extend-dev `references/scripts.md` + `tenant-ops.md`), WQL/RaaS reads, and the orchestration
direct-launch diagnostic (wd-extend-dev `orchestration.md`). A thin runner ties them together from a test-list
file; regenerate it from those build-specs if it is not on the machine.

## What to automate (and what to keep human)

- **Automate:** the stable **critical-path smoke set** (5-15 paths - the same standing list wd-post-go-live
  `release-regression.md` defines), plus **negative/security cases** (a wrong role gets nothing - the security
  domain rows from the Extend derivation checklist), and boundary cases (old records with null new-BO fields).
- **Keep manual:** exploratory testing, UX/usability judgment, and client-run UAT. Automation proves the
  known paths still work; humans find the unknowns.

## The test-list format (config, not code)

One row per automated check: id (maps to a `UT-###` scenario) | path/endpoint + method | preconditions
(role/ISU, seed set) | inputs | expected (status code, read-back assertion, BP state) | cleanup action. The
runner iterates the list, executes, asserts, records, and cleans up - adding a test is a data row, not new code.

## When to run

- **After every build in DEV** - smoke the critical set before calling a build good.
- **Before promotion** - run the changed-surface + critical-path regression (scope derived from the change
  plan; see this skill's "Regression scope for a change").
- **Every R1/R2 preview window** - this harness IS what wd-post-go-live's release-regression pass runs against
  the app's critical paths; the release calendar + deprecation scan stay with wd-extend-dev `release-impact.md`.

## Guardrails (non-negotiable)

- **The WRITE GATE applies** (wd-extend-dev `tenant-ops.md`): never prod, identity-checked target, allowlisted
  BOs, **synthetic data only**, and a cleanup plan filed with the run. Production person-data stays out per
  ai-data-governance.md.
- **Idempotent + isolated:** a run must be safe to repeat and must clean up after itself; set soft-delete flags
  explicitly on create so "deleted" test rows do not pollute filtered lists.

## Boundaries

- **Scenario DERIVATION** (what to test, from the design) stays with this skill's core (`unit-testing.md`) -
  the harness EXECUTES scenarios, it does not invent them.
- **Code fixes** for failures -> wd-extend-dev. **Performance testing** -> wd-deployment (a separate gate).
- **Release-regression workflow + per-app critical-path list** -> wd-post-go-live `release-regression.md`;
  **release calendar + deprecation scan** -> wd-extend-dev `release-impact.md`. This harness is the runnable
  engine those two drive.
