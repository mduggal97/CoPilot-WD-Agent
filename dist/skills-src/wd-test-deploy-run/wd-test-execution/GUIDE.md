---
name: wd-test-execution
description: DRIVES the in-app browser to RUN a written test plan and capture evidence - navigates the deployed Extend app / integration and its tenant via the Browser pane (mcp__Claude_Browser__*), exercises each scenario, asserts the observable result, captures screenshots / console / network reads, and records pass/fail. Use when the user says "test the app" (a bare "test the app" defaults here - run it), "test the app in the browser", "run the test plan", "validate these scenarios", "click through the app and check it works", "walk the app", or turn a written plan into an actual executed run with proof. Use THIS for browser-driven EXECUTION + evidence; for DERIVING scenarios / UAT scripts / defect-vs-CR triage see wd-testing; API-driven headless smoke/regression see wd-testing automation-harness.md; driving the browser to CONFIGURE a tenant or create test data see wd-tenant-config; code fixes see wd-extend-dev. NEVER types credentials, MFA codes, or CAPTCHAs - login is a user handoff (wd-auth).
---

# wd-test-execution - browser-driven validation of an Extend / integration test plan

This skill turns a test plan into an actually-executed run: it drives the in-app
Browser pane through each scenario against the deployed app (dev-server preview OR a
tenant-hosted app) and the tenant behind it, asserts the observable outcome, captures
evidence, and records pass/fail - then hands failures to wd-testing for triage.

It is the BROWSER arm of testing. wd-testing owns what to test and how results are
recorded; this skill owns doing it through the UI with proof.

## What this skill owns vs. what it defers

| This skill (wd-test-execution) | Deferred to |
|---|---|
| Driving the in-app browser through scenarios; asserting UI/console/network; capturing evidence | - |
| The EXECUTABLE test-plan format (scenario -> concrete browser actions + observable + evidence) | scenario DERIVATION + the Unit Testing tab -> **wd-testing** / **wd-design-doc** |
| Recording each run's pass/fail + evidence, then routing failures | defect/CR classification -> **wd-testing** defect-triage.md |
| Browser-driving-Workday mechanics (tool map, selectors, waits, evidence) | login/MFA handoff -> **wd-auth** mfa-and-browser-auth.md |
| Live UI validation with a human-visible walk | fast API-driven headless smoke/regression -> **wd-testing** automation-harness.md |
| Driving the app's own pages/flows + reading tenant state to confirm results | CONFIGURING the tenant or creating test data -> **wd-tenant-config** |

## The non-negotiable auth boundary (consult wd-auth FIRST)

Before navigating the Browser pane to any Workday tenant URL, **invoke the wd-auth skill**
to run its auth preflight and emit the appropriate USER-ACTION login block. The Browser pane
is NOT your SSO Chrome - it has no tenant session. Workday needs SSO + MFA. **You do not
type credentials, MFA codes, or solve CAPTCHAs - ever.** The user signs in interactively in
the Browser pane; you drive the authenticated session AFTER they confirm they are logged in.
If the session will also use wdcli commands, run the wdcli auth preflight check from wd-auth
as well. If a session expires mid-run, pause and hand back for re-login via a fresh wd-auth
USER-ACTION block; never attempt to re-authenticate yourself. Full mechanics:
[references/browser-mechanics.md](references/browser-mechanics.md).

## The run loop (short version)

1. **Open the target.** Dev-server app -> `preview_start {name}`; tenant-hosted app or a
   native tenant page -> `preview_start {url}` (user permission gate applies). Get the login
   handoff done first for any tenant target.
2. **Load the executable plan.** Each scenario = preconditions + numbered browser actions +
   the observable expected result + the evidence to capture. Author it from wd-testing's
   derived scenarios: [references/test-plan.md](references/test-plan.md). For common cases,
   instantiate a ready-made template (proxy-as-persona, create + read-back, negative security,
   drive-a-BP-to-a-step, approve/deny/send-back, >100-row grid, async/25s-cap, run a report/RaaS,
   launch an integration + validate the event, verify event attachments/logs, smoke round-trip):
   [references/scenario-flows.md](references/scenario-flows.md). For accessibility scenarios
   (keyboard-only + focus order, visible focus, accessible name via the a11y tree, contrast,
   error identification, target size) verified against the built PMD pages to a confirmed WCAG
   2.1 AA bar: [references/accessibility-execution.md](references/accessibility-execution.md).
3. **Drive + assert per scenario.** Prefer `read_page` (accessibility tree, returns refs) and
   `find` over screenshots for verifying text/structure; use `computer`/`form_input` to act;
   check `read_console_messages` / `read_network_requests` for errors. **The app's OWN logging
   is not in the browser console** - when a page renders but shows the wrong thing, read the
   developer-site log stream: [references/app-log-stream.md](references/app-log-stream.md). Full workflow, waits,
   and assertion patterns: [references/execution-workflow.md](references/execution-workflow.md).
4. **Capture evidence + record.** Screenshot the observable result, save console/network proof
   for API-touching scenarios; record Pass/Fail per scenario. Evidence + report format +
   the hand-back to wd-testing's Unit Testing tab: in execution-workflow.md. For a downloaded
   integration output/log the browser can't inspect, validate it byte-level with the bundled
   `scripts/validate_output_file.py` (build-spec + usage: [references/scripts.md](references/scripts.md)).
5. **On failure: diagnose, don't fix.** Read source to locate the cause, capture the repro +
   evidence, and route to wd-testing defect-triage.md (bug vs CR vs data/config vs
   doc-drift). Code fixes go through wd-extend-dev; this skill proves the failure, it does not
   patch it. **When the defect report links a tester's screen recording,** review it frame by
   frame and match it to the app log before classifying:
   [references/recording-review.md](references/recording-review.md) (script:
   `scripts/extract_frames.py`).

## Evidence discipline (house standard)

No scenario is "Pass" without a captured observable. A green build proves nothing about
runtime (the whole reason pmd-gotchas.md exists). Every Pass row carries a screenshot or a
record/event ID; every Fail carries a repro + the console/network/screenshot proof. Never
report a scenario as passed that you did not actually drive and observe.

**Assert real tenant state, not the UI's word for it** (suite rule):
wd-extend-lifecycle references/verify-in-tenant.md - a browser "None"/empty picker is not proof
a collection is empty; confirm programmatically (REST GET / WQL / RaaS read-back) before a Pass.

## Data + environment

Run against seeded data in a dev/impl tenant (wd-extend-dev seed/wipe pattern; note an
upload+deploy can wipe dev BO data - check and re-seed first). Never test against real customer data in a
shared dev tenant. Test-data creation itself is wd-tenant-config.

## Lifecycle neighbors

previous = wd-testing (derives the scenarios this executes) + wd-extend-dev (the build under
test); sibling = wd-tenant-config (browser-driven tenant setup + test data); next = wd-testing
triage + wd-deployment (receives a current, evidenced Unit Testing tab).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in
wd-extend-lifecycle references/quality-gates.md - run it before presenting work as final and
report the result with the deliverable.
