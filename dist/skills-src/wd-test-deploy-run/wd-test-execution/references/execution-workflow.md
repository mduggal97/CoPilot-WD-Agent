# The run loop, assertions, evidence, and reporting

How to actually execute an executable plan (references/test-plan.md) against a Workday Extend
app in the Browser pane, assert each result, capture proof, and hand results back to wd-testing.
This adapts the standard "preview -> verify in the browser" loop to Workday's auth,
server-rendered pages, and separate read surfaces. Browser mechanics themselves:
references/browser-mechanics.md.

---

## The end-to-end run loop

**0. Preflight (once per run).**
- Confirm the target is open and authenticated. Dev-server app -> `preview_start {name}`;
  tenant-hosted app / native page -> `preview_start {url}` (permission gate) then the login
  USER-ACTION handoff (wd-auth mfa-and-browser-auth.md) - WAIT for "done".
- Confirm the tenant + seed state. A deploy CAN WIPE dev BO data (wd-extend-dev wdcli-workflow.md):
  if the app was just uploaded/deployed, check the seeded records the plan assumes - if gone, re-seed
  (hand to wd-tenant-config) BEFORE running, or every data-dependent scenario false-fails.
  Environment note: run against a dev/sandbox tenant. An IMPL tenant is acceptable for a
  READ-ONLY walk, but any scenario that CREATES or MODIFIES records there goes through
  wd-tenant-config, which forbids writing to an IMPL that holds real customer data - treat
  such an IMPL as read-only (see wd-tenant-config safety-and-scope.md).
- Open a second tab for read-backs (a report, Related Actions, or a REST/WQL read surface) so
  you can confirm record state without leaving the app tab.

**Per scenario (loop over the plan):**

1. **Set the precondition.** Ensure the role/data/App-Attribute state the script names. Seed
   or config that does not exist -> hand to wd-tenant-config; note the dependency in the run
   notes. Never fabricate data inside the app to make a scenario pass.
   - **Persona-scoped scenarios need the RIGHT worker identity.** A negative security test or a
     "manager sees X, specialist sees Y" test must run AS that persona. The user does the
     Workday **Proxy / "Sign In As"** to the exact test worker (Tier-3 handoff - you never
     switch identity yourself; wd-tenant-config safety-and-scope.md). A page that comes back
     EMPTY under the wrong identity is NOT a Fail - it is the wrong precondition; re-check who
     you are signed in as (and which ORG - wrong-org pickers silently empty) before recording.
   - **Run a 2-minute smoke round-trip FIRST** on any freshly set-up app: proxy to the test
     worker -> open the app home -> confirm the expected tiles/data render -> back to admin.
     This catches the classic setup faults (skipped Activate Pending, missing group membership,
     ungranted domain -> S22) as SETUP problems, before you burn a full run mislabeling them as
     app defects. A blank smoke = fix the tenant setup (wd-tenant-config), not the app.
2. **Drive the numbered actions.** First pass step-by-step, re-`read_page` after every
   navigation/submit (refs go stale). Once the sequence is proven, replay via `browser_batch`
   for speed on re-runs.
3. **Assert the observable** (patterns below) - from the accessibility tree + console/network +
   a read-back, NOT from a screenshot alone.
4. **Capture evidence** - screenshot the observable; save the console/network artifact for any
   API-touching step; note record/event IDs.
5. **Record Pass/Fail** with the evidence ref into the run report.
6. **On Fail: diagnose, don't fix** (see the failure section).

---

## Assertion patterns

**Positive (expected present, record created/changed).**
- Assert the on-page observable from `read_page` (confirmation banner, new ID, updated field) -
  exact text/element, not "looks right in the screenshot".
- Confirm the RECORD by read-back, not just the UI banner: second tab report / Related Actions,
  or a REST GET / WQL / RaaS read of the BO. A UI "success" without a persisted record is a
  real failure mode - script-side `.invoke()` writes roll back (pmd-gotchas #52), so read-back
  is mandatory for anything claiming to persist.
- `read_console_messages(onlyErrors)` empty is part of every positive assertion - but it is
  **NOT an all-clear**. An Extend app's own `console.*` output does not reach the browser
  console; it lands in the developer-site log stream. A silently-failing app looks clean here.
  See [app-log-stream.md](app-log-stream.md).

**Negative (wrong role sees nothing).**
- Assert ABSENCE: the target record's fields do not appear anywhere in the page tree, and the
  page shows access-denied/empty - not merely a different landing page.
- The page is ONE surface. A blocked page does not prove the WQL/REST/RaaS reads are blocked -
  they are separate paths (wd-extend-dev model.md). API-level negative assertions belong to
  wd-testing automation-harness.md; state in the report that this row covers the PAGE surface
  so the API surface is not assumed-covered.

**Async (poll, respect the 25s cap).**
- Page-synchronous flows have a hard 25-second cap (wd-extend-dev orchestration.md). Poll:
  `computer` wait a short beat -> re-`read_page` / re-read the BO status in tab 2 -> repeat a
  few times. Do not use one long fixed sleep.
- If nothing completes by the cap, that IS the result - record it (a sync flow that can exceed
  25s is a design finding, route per triage). For BP-triggered async, the page returns
  immediately; assert the eventual state on the read-back, not on the submit response.

**Error-surfacing (server-rendered, not a red XHR).**
- Extend pages are server-rendered: a failing submit is a page NAVIGATION to an
  applicationException / error page, NOT a failed XHR you can see in the network tab
  (pmd-gotchas #33). Assert the FAILURE by reading the resulting page (error summary /
  exception text) via `read_page` / `get_page_text`.
- Use `read_network_requests` for the calls the page DID fire (the /launch POST status, a REST
  GET body) - useful evidence - but never conclude "no error" from a quiet network tab on a
  submit.

**Computed-CSS / visual checks.** Use `javascript_tool` INSPECT-only to read a computed style
(color, visibility, layout) when the assertion is truly visual; `resize_window` for responsive
+ dark-mode. Never use `javascript_tool` to change the page.

---

## Evidence artifacts

- **Running evidence folder** for the run (per app + date). Save into it, don't scatter.
- Per scenario, at minimum: the observable **screenshot**; for API-touching steps the
  **network** request/response (fetch the body by requestId) and **console** errors
  (onlyErrors); the **record/event ID** from the read-back.
- Name artifacts by UT-### so they self-join to the report row (e.g. `UT-012_confirmation.png`,
  `UT-012_readback.json`).
- Evidence discipline (SKILL.md house standard): no row is "Pass" without a captured
  observable; every "Fail" carries a repro + console/network/screenshot proof. Never report a
  scenario passed that you did not actually drive and observe.
- **For critical-path and Sev1-prevention scenarios run more than once** (regression sweeps,
  go/no-go verification), log the run count with the result: "3 runs: 3/3 Pass (pass^3)".
  A single pass is pass@1 evidence - enough for capability verification, not for gating a
  go/no-go decision. Go/no-go gating requires pass^3 (all 3 runs succeed); Sev1-prevention and critical
  data-write paths require pass^k (all runs must succeed). Framing: wd-extend-lifecycle
  quality-gates.md Verification mechanics.

---

## Test-run REPORT format

A scenario-by-scenario table plus a summary. This is the run record; the authoritative results
land on the design doc's Unit Testing tab (below).

```
Run: <app name> - <tenant> - <date> - <tester>
Build/version under test: <wdcli version or deploy id>

| UT-### | REQ    | Status        | Evidence ref            | Notes                          |
|--------|--------|---------------|-------------------------|--------------------------------|
| UT-012 | REQ-004| Pass          | UT-012_confirmation.png | new id R-1007, read-back OK    |
| UT-018 | REQ-004| Pass          | UT-018_denied.png       | page surface only; API = harness|
| UT-024 | REQ-009| Fail          | UT-024_errorpage.png    | submit -> applicationException  |
| UT-031 | REQ-012| Blocked       | -                       | needs >100-row seed (tenant-cfg)|

Summary: <n> Pass / <n> Fail / <n> Blocked of <total>.
Blockers: <precondition/data/auth handoffs outstanding>.
Failures routed: UT-024 -> wd-testing defect-triage.md.
```

Status vocabulary: **Pass / Fail / Blocked** (Blocked = precondition/data/auth not in place -
not a defect; route to wd-tenant-config or the login handoff). Keep severity/triage OUT of this
report - that is wd-testing's call.

---

## Hand-back and failure routing

- **Results feed the Unit Testing tab.** Pass/Fail + evidence get recorded onto the design
  doc's Unit Testing tab (tab format + editing mechanics owned by wd-design-doc; the recording
  discipline - e.g. a fixed defect stays "Retest" until re-verified post-deploy - is
  wd-testing). This skill supplies the executed results + evidence; it does not own the tab.
- **Results ALSO feed the E2E/UAT test tracker where one exists (Smartsheet or another PM
  tool).** For end-to-end / UAT cycles the live tracker is usually a Smartsheet sheet, not the
  design-doc tab. Push each scenario's Status + evidence link + run date to the matching tracker
  row via **wd-smartsheet** (find the sheet, match rows by the UT-###/scenario id, write Status
  and the evidence/notes columns), following its SKILL.md write rules (the owner - do not restate
  them here). Which artifact is authoritative is wd-testing's call - unit cycle ->
  design-doc Unit Testing tab; E2E/UAT cycle -> the Smartsheet tracker; keep whichever is the
  source of truth current, and do not silently diverge the two. For a PM tool other than
  Smartsheet, the same pattern applies through whatever connector exists, or export the run-report
  table for manual paste - say which you did. Mapping the run to tracker columns is a wd-testing +
  wd-pm decision; this skill supplies the executed results.
- **Failures route to triage.** Every Fail goes to wd-testing defect-triage.md for
  classification (bug vs CR vs data/config vs doc-drift) and severity. Do not assign severity
  or decide bug-vs-CR here.
- **Diagnose, don't fix.** On a Fail, read the source to LOCATE the likely cause (which
  page/script/flow/BO), capture a clean repro (the exact steps + the error-page text +
  console/network), and route the FIX to wd-extend-dev. This skill proves the failure with
  evidence; it never patches code or works around a defect to force a pass.

---

## Practical notes

- **Deploy can wipe dev BO data** - check and re-seed before a run after any upload/deploy, or data
  scenarios false-fail (wd-extend-dev wdcli-workflow.md).
- **Batch predictable steps** with `browser_batch` once proven - fast, deterministic re-runs
  and regression sweeps.
- **Keep the evidence folder running** across the whole session; append, don't overwrite.
- **Missing setup/data -> hand to wd-tenant-config**, never fake it. A Blocked row with the
  named dependency is honest; a faked pass is not.
- **Session expiry mid-run** is an environment event, not a Fail - pause, hand back the
  re-login block (wd-auth), resume, and re-run the interrupted scenario.
