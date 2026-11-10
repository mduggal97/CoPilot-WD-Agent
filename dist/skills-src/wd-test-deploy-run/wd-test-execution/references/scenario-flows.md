# Standard reusable test-scenario flow templates

A library of PARAMETERIZED templates for the test actions that recur across Extend apps AND
integrations - proxy-in as a persona, create-and-read-back, negative security, drive a BP,
grid-at-volume, async/timeout, plus running a report or integration and VALIDATING the
integration event and its attachments (files/logs). Each is the executable-scenario shape from
references/test-plan.md (UT-### + REQ + preconditions + numbered browser actions +
observable + evidence) with the varying bits pulled out as **Parameters**. You do not
re-derive coverage here: wd-testing DERIVES the UT-### rows onto the Unit Testing tab; you
INSTANTIATE the matching template below into a concrete UT-### script, fill the parameters,
and run it via the loop in references/execution-workflow.md with the techniques in
references/browser-mechanics.md.

Each template names the wd-testing Extend derivation-checklist row it satisfies. Templates are
labelled SF-# for reference only - the runnable script keeps its wd-testing UT-### id (the join
key); a path with no UT row routes back to wd-testing to derive first. Every write-side
precondition (seed, security grant, proxy identity) is handed to wd-tenant-config - you never
fake data or switch identity in the run.

---

## SF-1 - Proxy-as-persona and verify visibility

- **Verifies:** the app renders the RIGHT tiles/data for a given worker identity (checklist:
  Every security domain -> positive; Every page -> render path). The building block every
  persona-scoped scenario reuses.
- **Parameters:** app (launch target); test worker (the persona); expected org/context;
  the tiles/records that SHOULD render for that persona.
- **Preconditions:** worker exists with the security groups the app needs (seed/grant ->
  wd-tenant-config; grants are Tier-3); the data the persona should see is seeded and Active
  (boolean-Active gotcha - an unset flag hides the row). Login handoff done (wd-auth).
- **Steps:**
  1. USER does Workday **Start Proxy / "Sign In As"** the test worker (Tier-3 handoff - you
     never switch identity; Global Search "Start Proxy" -> type name -> **press Enter to chip
     the name** -> OK). WAIT for their "done".
  2. Open the app (Global-Search the app/task name -> click the suggestion row -> use the app's
     own nav; do NOT hand-build a hub URL).
  3. `read_page`; assert the landing rendered - title present, expected tiles/records in the
     tree, no error page.
- **Observable + evidence:** the expected tiles/records appear in the `read_page` tree; screenshot
  the rendered home. `read_console_messages(onlyErrors)` empty.
- **Notes/pitfalls:** a page BLANK under the wrong worker or wrong ORG is a PRECONDITION fault,
  not a Fail - re-check the proxied identity and the org picker (wrong org silently empties) first.
  `workers/me` returns S21 for implementer/admin accounts, so an app calling it MUST run proxied.

## SF-2 - Create-record happy path + read-back

- **Verifies:** the app's create flow persists a record (checklist: Every page -> submit path).
- **Parameters:** app + create page; the field set and values; the BO/collection to read back;
  the expected status/id.
- **Preconditions:** persona with create rights (SF-1 proven first); any SINGLE_INSTANCE
  targets the form picks (worker, cost center) seeded Active in dependency order -> wd-tenant-config.
- **Steps:**
  1. From the app, `find` the Create/New control -> `computer` left_click by ref.
  2. `read_page` (refs stale after nav); `form_input` the required fields; for a picker,
     click it, `type` the value, **press Enter, wait ~2-3s**, then select by ref (a fast
     "No Items" is a timing artifact, not empty).
  3. Click Submit/OK by ref.
  4. In tab 2, read the record back - a report, Related Actions, or a REST GET / WQL SELECT on
     the BO.
- **Observable + evidence:** confirmation page/banner shows the new id (`read_page` /
  `get_page_text`); the tab-2 read-back shows ONE new instance with the entered values and the
  designed status. Evidence: confirmation screenshot with the id + the read-back result.
- **Notes/pitfalls:** the UI banner alone is NOT a pass - script-side `.invoke()` writes can roll
  back, so the read-back is mandatory. Confirm the record is present AND Active (created without
  its active flag set true, it vanishes from filtered lists).

## SF-3 - Negative security (wrong role sees nothing)

- **Verifies:** no data leak to a role without access (checklist: Every security domain ->
  negative).
- **Parameters:** app/page URL; the no/less-access persona; the target record whose fields
  must NOT appear.
- **Preconditions:** the target record exists (e.g. from SF-2); a worker WITHOUT the app's
  domain - confirm the app fails CLOSED (pre-grant state should also deny).
- **Steps:**
  1. USER proxies the no-access worker (Tier-3 handoff); WAIT for "done".
  2. `navigate` to the same app/page target; `read_page`.
- **Observable + evidence:** ABSENCE - the target record's fields appear NOWHERE in the page
  tree, and the page shows access-denied/empty (not merely a different landing page). Evidence:
  screenshot of the denied/empty page + a `read_page` excerpt showing the fields are absent.
- **Notes/pitfalls:** the page is ONE surface. A blocked page does NOT prove the WQL/REST/RaaS
  reads are blocked - they are separate paths (wd-extend-dev model.md). State in the report
  that this row covers the PAGE surface; API-level negative checks belong to wd-testing
  automation-harness.md.

## SF-4 - Drive a business process to a named step + verify routing

- **Verifies:** a submit lands in the EXPECTED approver's inbox (checklist: Every custom BP ->
  one scenario per configured step).
- **Parameters:** app + submittable record; the BP; the target step's approver worker; the
  step name.
- **Preconditions:** BP configured with the routing under test; the submitter persona and the
  approver persona both exist with their groups (grants -> wd-tenant-config, Tier-3).
- **Steps:**
  1. As the submitter (SF-1 proxy), create + Submit a record (SF-2 steps 1-3).
  2. USER proxies the expected approver (Tier-3 handoff); WAIT for "done".
  3. Open the approver's Workday inbox (or the app's approval page); `read_page`.
- **Observable + evidence:** the submitted item is in THAT approver's inbox at the expected step -
  not a different approver, not lost. Evidence: inbox-row screenshot + the record/event id.
- **Notes/pitfalls:** a tenant-token/implementer identity cannot launch or receive BP steps -
  proxy real workers on both sides. If the item is absent, re-check the proxied identity/org
  before a Fail (routing to the wrong group is a real Fail; wrong-proxy is not).

## SF-5 - Approve / Deny / Send-back on a Model BP

- **Verifies:** each configured step outcome drives the right record/event end-state
  (checklist: Every custom BP -> Approve, Deny, Send-back).
- **Parameters:** app + in-flight record at an approval step; the outcome under test
  (Approve | Deny | Send-back); the expected end-state per outcome.
- **Preconditions:** a record sitting at the step (from SF-4); the approver persona proxied.
  Send-back only applies if `SEND_BACK` + `revisePageRoute` is configured (optional - skip the
  Send-back instance if it is not).
- **Steps:**
  1. As the approver, open the inbox/approval item; `read_page`.
  2. Take the outcome: click Approve, or Deny, or Send Back by ref (a committing click - drive
     it as its own action, not buried in a batch).
  3. For Send-back: proxy back to the submitter, open the revise page, edit, resubmit (full
     PUT); confirm routing restarts.
  4. Read the record/event state back in tab 2.
- **Observable + evidence:** Approve advances to the next step / completes; Deny writes the denied
  status + submitter notification + record end-state; Send-back returns to the submitter and
  re-routes on resubmit. Evidence: resulting-status screenshot + the read-back state per outcome.
- **Notes/pitfalls:** run one outcome per instance (Deny ends the event - you cannot then test
  Approve on the same record). A "fixed" step stays Retest until re-verified post-deploy.

## SF-6 - Grid / >100-row data check

- **Verifies:** rows past the BO REST 100 cap are reachable, not silently dropped (checklist:
  Volumes).
- **Parameters:** app list/dashboard page; a seeded dataset of MORE than 100 rows; a filter
  whose match lies past row 100.
- **Preconditions:** the >100-row dataset seeded (bulk -> hand to wd-tenant-config / an EIB or
  API loader; a 5-row seed does NOT test this); a persona that can view the list.
- **Steps:**
  1. `navigate` to the list/dashboard; `read_page`.
  2. Exercise paging / server-side filtering (next page, or apply the filter) -> re-`read_page`
     after each control. For a virtualized grid, `scroll_to` the target row's ref (off-screen
     rows have no refs) then re-`read_page`.
- **Observable + evidence:** a row beyond 100 is reachable via paging or filtering; a truncation
  to the first 100, a short count, or a "Property Error found: .data" is a FAIL (BO REST cap
  truncates silently - pmd-gotchas #15). Evidence: page 1 + a later page + console(onlyErrors).
- **Notes/pitfalls:** work the grid ONE row at a time with a re-read between rows (any
  add/remove/commit shifts every other row's refs); row action buttons share generic names, so
  take the ROW-SCOPED ref, never a bare coordinate.

## SF-7 - Async / 25s-cap flow

- **Verifies:** a flow that may exceed the page-sync cap behaves as designed; the timeout IS the
  recorded result (checklist: Every orchestration -> success + timeout).
- **Parameters:** the app action that launches the flow; the completion signal (status flip /
  rendered data); the read-back surface.
- **Preconditions:** the flow deployed; a submittable record; persona with rights.
- **Steps:**
  1. Drive the record through Submit (the outbound POST `<Flow>/launch` is the only page->flow
     bridge).
  2. If page-synchronous: `read_page` for the returned result. If async/BP-triggered: the page
     returns immediately - POLL: `computer` action `wait` a short beat -> re-`read_page` / re-read
     the BO status in tab 2 -> repeat, up to the 25-second cap. Never one long fixed sleep.
- **Observable + evidence:** on success the status/data reflects the flow output; on async, the
  page returns immediately and the BO status updates on the read-back. If nothing completes by the
  cap, RECORD THAT (a sync flow that can exceed 25s is a design finding - route per triage).
  Evidence: status screenshot + `/launch` status from `read_network_requests` + read-back.
- **Notes/pitfalls:** a FAILED submit is a page NAVIGATION to an applicationException page, NOT a
  red XHR (pmd-gotchas #33) - assert the error-page text, not the network tab.

## SF-8 - Boundary / null-field on a pre-existing record (EDIT/VIEW an old record after a BO field was added)

- **Verifies:** a record created BEFORE a BO field was added still renders, edits, and re-saves
  cleanly - nulls on newly added fields do not crash the page (checklist: Boundary data - old
  records with null values in newly added BO fields). A mandatory row on every BO field addition.
- **Parameters:** app + the EDIT/VIEW page; a pre-existing record that predates the new field(s);
  the newly added field name(s); the expected render (empty/default, not an exception) + a clean
  re-save.
- **Preconditions:** a genuinely OLD record exists (created before the field add - do NOT just
  null the field on a new record; the staging-model history is what bites). If none exists in the
  tenant, seed one that matches the pre-add shape -> wd-tenant-config. Persona with view/edit rights
  (SF-1 proven). Login handoff done (wd-auth).
- **Steps:**
  1. Open the old record on its VIEW page (Global-Search / Related Actions -> the app page);
     `read_page` - assert the page renders (no applicationException) and the new field shows
     empty/default rather than erroring.
  2. Open the same record on its EDIT page; `read_page`. Confirm the new field renders as an
     editable empty input (not a crash, not a stuck spinner).
  3. Set a value in the new field; Submit/Save by ref (a committing click - its own action).
  4. In tab 2, read the record back (report / Related Actions / REST GET / WQL) and confirm the
     new value persisted AND the previously populated fields are intact (full-replace PUT ripple -
     a save must not blank the old fields).
- **Observable + evidence:** the old record renders and edits without an exception, the new field
  is empty/default on first load, and the re-save persists the new value while preserving prior
  fields. Evidence: VIEW + EDIT screenshots, the read-back showing new value + intact old fields,
  `read_console_messages(onlyErrors)` empty.
- **Notes/pitfalls:** a page 500 / applicationException on the OLD record but not a new one is the
  classic null-on-new-field crash (a real delivered-app landmine) - a genuine Fail, route to
  triage. A full-replace PUT that silently blanks unlisted fields is ALSO a Fail (wd-extend-dev
  model.md field-change checklist). Assert the failure from the resulting error page, not the
  network tab (pmd-gotchas #33).

## SF-9 - Run a report / RaaS and validate the output

- **Verifies:** a custom report or RaaS produces the expected data (checklist: KPI/Reporting
  outputs; and the data an app/integration depends on is correct). Methodology for output-vs-spec
  reconciliation is wd-testing integration-testing.md; this template EXECUTES the run + check.
- **Parameters:** the report name (or the RaaS web-service URL); run prompts; the expected
  columns / row count / aggregates; the persona (report security governs results).
- **Preconditions:** the report exists and is shared / enabled-as-web-service (for RaaS); the
  persona has report security AND the underlying data is seeded; login handoff done (wd-auth).
- **Steps:**
  1. Global-Search the report name -> open it; `read_page`. Fill prompts (picker: `type` ->
     press Enter -> wait ~2-3s -> select by ref). Run/View.
  2. `read_page` the result grid; for a wide/long result use the grid nav (SF-6: paging,
     `scroll_to`, row-scoped refs). For RaaS, open the web-service URL in a tab and `get_page_text`
     the JSON/XML body, or Export to Excel/CSV and inspect (see the SF-11 attachment note on
     reading exported files).
- **Observable + evidence:** the columns / row count / aggregate values match expected. Evidence:
  result-grid screenshot + the `read_page`/`get_page_text` excerpt (or the RaaS body).
- **Notes/pitfalls:** report security gates results - an empty/short result may be MISSING DATA or
  a security scope, not a broken report (verify per SF-1 / the financial-picker rule) before a Fail.
  Respect the report hard limits (matrix rows/cols, worklet 100-row cap - report-writer-admin.md);
  a large extract belongs in RaaS/Prism, not a screen scrape.

## SF-10 - Launch an integration and validate the integration event

- **Verifies:** an integration run completes with the expected STATUS and MESSAGES (checklist:
  wd-testing integration-testing.md - transport/connectivity, error/audit, run outcome). This is
  the browser execution of that methodology; field-level output reconciliation is SF-11 + wd-testing.
- **Parameters:** the integration system / INT to launch; launch parameters (incl. VALIDATION
  mode where supported); the expected completion status + expected messages / rows-processed count.
- **Preconditions:** the integration system + ISU + security are set up (wd-tenant-config
  config-flows.md "integration system" flow); **DEV/SANDBOX tenant confirmed**; **if the
  integration EGRESSES externally, use validation mode / mock / a test endpoint - never fire a
  real outbound to a client or partner from a test**; login handoff done.
- **Steps:**
  1. **Launch (a committing action with side effects - confirm dev/sandbox + no external egress
     FIRST):** Global-Search "Launch / Schedule Integration" (or the integration system Related
     Action -> Launch) -> select the integration -> set launch params (validation mode ON when you
     only want to validate) -> run.
  2. **Find the event:** open **Process Monitor** (or the integration-event / background-process
     list) -> locate the run by integration name + initiation moment; `read_page`.
  3. **Poll to completion:** integration runs are async - `computer` `wait` a beat -> re-`read_page`
     -> repeat until Status is Completed / Completed With Errors / Failed. Never one fixed sleep.
  4. Open the event -> read Status, Percent Complete, and the **Integration Messages** grid
     (severity Critical / Error / Warning / Info - grid nav per SF-6).
- **Observable + evidence:** Status = Completed as designed AND no unexpected Critical/Error
  messages AND the rows-processed / message counts match expected (or the IDD). Evidence:
  event-detail screenshot + the messages-grid `read_page`.
- **Notes/pitfalls:** a Completed status WITH Error-severity messages is NOT a clean pass - inspect
  the messages. Import integrations surface per-row results in Import_Process messages
  (wd-integration-dev eib.md). Deep field-level output-vs-IDD reconciliation needs the output file
  (SF-11). Integration-event triage detail: wd-deployment tenant-task-recipes.md R11b.

## SF-11 - Verify integration event ATTACHMENTS (output files + logs)

- **Verifies:** the event's output file(s) and log(s) exist and are correct (checklist: wd-testing
  integration-testing.md - output vs IDD mapping, error/audit trail).
- **Parameters:** the integration event (from SF-10); the expected output file(s) (name pattern +
  format) + expected content (record count, header, sample rows) + log expectations (no errors,
  audit entries present).
- **Preconditions:** SF-10 run completed; persona with access to the event and its attachments.
- **Steps:**
  1. Open the integration event -> the **Output Files / Attachments / View Output** area;
     `read_page` to list the attached files + logs (names, sizes).
  2. **Verify existence + metadata:** the expected file(s) present with the right name pattern and
     non-zero size; the audit/log attachment present.
  3. **Verify content with the helper (byte-level).** Get the downloaded file's path (confirm the
     Browser pane's download location, or have the user save it to a known path), then run
     `scripts/validate_output_file.py <path>` with the expected spec - it parses delimited / XML /
     JSON / XLSX / log and reports encoding + record count + header + sample, and PASS/FAIL against
     `--expect-header`, `--min-rows` / `--exact-rows`, `--required-cols`, `--record-tag`, and a log
     severity scan (exit 1 on any failed check, so it gates the step). Usage + regeneration:
     [scripts.md](scripts.md). For text/CSV/XML that renders in a tab you can ALSO `get_page_text`
     as a quick look, but the helper is the check of record.
  4. **Verify the log:** run the helper on the log/audit attachment (format `log`) to scan for
     ERROR / CRITICAL / Fault / FAILED severity markers and confirm the expected audit entries
     (record counts, run summary); or open it in a tab and `get_page_text`.
- **Observable + evidence:** expected files/logs attached with correct names/sizes; the helper's
  record count + header + required-column checks PASS against the IDD mapping; the log scan is clean.
  Evidence: attachments-list screenshot + the helper's report (paste or `--json`).
- **Notes/pitfalls (honest limitation):** the helper covers the common Workday output formats
  (delimited / XML / JSON / XLSX / text log) and fixed-width at line-count + sample only. A TRULY
  opaque binary (PDF, encrypted, PGP) or a proprietary format the helper cannot parse still needs a
  hand-off to the user / a format-specific tool - verify existence + UI-exposed counts (rows-processed
  in the event messages, file size) and say the byte check was handed off. Never mark
  content-verified from a filename/size alone. Field-level output-vs-IDD reconciliation methodology
  is wd-testing integration-testing.md; this helper executes the mechanical checks.

## SF-12 - Smoke round-trip (pre-test setup check)

- **Verifies:** the app is actually set up to be tested - catches skipped Activate-Pending,
  missing group membership, or an ungranted domain as SETUP faults before a full run
  (cross-ref execution-workflow.md preflight).
- **Parameters:** app; one test worker; the expected home tiles/data.
- **Preconditions:** app deployed; a re-seed done if any upload/deploy just wiped dev BO data.
- **Steps:** proxy the test worker (Tier-3) -> open the app home -> `read_page` to confirm the
  expected tiles/data render -> stop proxy / back to admin. Two minutes, before any UT-### run.
- **Observable + evidence:** the home renders with the expected tiles/data. A BLANK smoke = fix
  the TENANT SETUP (wd-tenant-config), not the app - do NOT open a defect. Evidence: one
  screenshot of the rendered (or blank) home.
- **Notes/pitfalls:** run first on any freshly set-up or deployed app; a blank home here saves a
  full run mislabeling S22 / missing-group setup faults as app defects.

---

## Where results land

These templates produce executed UT-### results that feed the tracker per wd-testing: the
**unit cycle** records onto the design doc's **Unit Testing tab** (format owned by
wd-design-doc); an **E2E / UAT cycle** records onto the live **Smartsheet (or PM-tool) tracker**
via wd-smartsheet (match rows by UT-###, write Status + evidence link + run date, respect its
write rules). Keep whichever is the source of truth current; route every Fail to wd-testing
defect-triage.md - these flows prove behavior, they do not decide what a failure means.
