# The executable test-plan format

wd-testing DERIVES scenarios (requirement -> happy path + edge/failure modes, into the design
doc's Unit Testing tab; the derivation checklist lives in wd-testing unit-testing.md). This
file turns each derived scenario into a BROWSER-RUNNABLE script the Browser pane can execute
step for step and assert against. Same scenarios, expressed as concrete drive-and-observe
actions - not a second source of scenarios.

Do not re-derive coverage here and do not invent scenarios wd-testing did not derive. If a gap
appears while executing (a path with no UT row), route it back to wd-testing to derive and
record on the Unit Testing tab, then script it.

---

## One executable scenario = five parts

Each script carries the wd-testing IDs plus the browser specifics:

- **UT-### + REQ ref** - copied verbatim from the Unit Testing tab so results map back both
  ways (every REQ has >=1 UT; every result names its UT).
- **Preconditions** - the concrete environment the script assumes BEFORE step 1: role /
  security group of the logged-in user, seeded data (exact records/IDs), tenant, and any App
  Attribute (`site.<attr>`) overrides. If a precondition does not exist, hand to
  wd-tenant-config to create it - do NOT fake it inside the run.
- **Actions** - numbered, CONCRETE Browser-pane steps: which tool, which target. "navigate to
  X", "read_page; find 'Add' -> click ref", "form_input 'Quantity' = 5", "click Submit ref".
  Written so a re-run (or a browser_batch replay) is unambiguous.
- **Observable expected result** - the exact text / element / record state to assert, and HOW:
  read_page for on-page text/structure, a read-back (second tab: report or Related Actions or
  a REST/WQL read) for record state, read_console_messages for no-errors, read_network_requests
  for an API status.
- **Evidence to capture** - the screenshot + console/network artifact that proves the pass or
  fail (see execution-workflow.md for the evidence folder and report format).

Traceability rule: the UT-### is the join key. A script with no UT-### is not runnable output -
it is an untracked click-through.

---

## Worked template - a typical Extend app

Mirrors the wd-testing Extend derivation checklist rows: create-flow happy path, security
negative, orchestration/async result, and a >100-row grid paging check. Values are
placeholders - fill from the actual app and Unit Testing tab.

### UT-012 - Create-flow happy path (Every page: render + submit)
- **REQ:** REQ-004 (user submits a new request)
- **Preconditions:** logged in as a Requester-role user; seeded cost center CC-TEST-01 exists;
  tenant = dev/impl.
- **Actions:**
  1. navigate to the app launch URL (or preview_start {name} for a dev-server build).
  2. read_page; assert the landing page rendered (title present, no error page) - RENDER path.
  3. find "Create Request" / New button -> computer left_click by ref.
  4. read_page (refs stale after nav); form_input the required fields (Description = "Test
     req", Quantity = 5); select Cost Center picker -> type "CC-TEST-01" -> pick by ref.
  5. click Submit / OK ref.
- **Observable:** confirmation page/banner shows the new request ID (read_page /
  get_page_text); read-back in tab 2 (report or REST GET on the BO) shows one new instance with
  Quantity = 5, status as designed; read_console_messages(onlyErrors) empty.
- **Evidence:** screenshot of the confirmation with the ID; the read-back showing the record.

### UT-018 - Security negative (Every domain: wrong role sees nothing)
- **REQ:** REQ-004 security constraint
- **Preconditions:** logged in as a role WITHOUT access to the request domain (e.g. a
  no-access test user); the UT-012 record exists.
- **Actions:**
  1. navigate to the same app launch URL / the request page URL directly.
  2. read_page.
- **Observable:** NO data leak - the page shows an access-denied / empty state, NOT the
  UT-012 record's data anywhere in the tree. Confirm the surface separately: a page block does
  not prove the WQL/REST read is blocked (they are separate surfaces per wd-extend-dev
  model.md) - note that API-level negative checks belong to wd-testing automation-harness.md,
  this script covers the PAGE surface.
- **Evidence:** screenshot of the denied/empty page; read_page excerpt showing the record's
  fields are absent.

### UT-024 - Orchestration / async result (Every orchestration: success + 25s cap)
- **REQ:** REQ-009 (submitting the request launches the posting orchestration)
- **Preconditions:** Requester role; a submittable request (from UT-012); the flow deployed.
- **Actions:**
  1. Drive UT-012 through submit (the outbound POST <Flow>/launch is the only page->flow
     bridge - wd-extend-dev pmd.md).
  2. If page-synchronous: read_page for the returned result. If async/BP-triggered: poll -
     computer wait, then re-read the status page / read-back the BO status in tab 2, up to the
     25-second page-sync cap.
- **Observable:** on success the result/status reflects the flow output (record status flips
  to Posted, or the sync flow's data renders); on the async path the page returns immediately
  and the BO status updates on the read-back. read_network_requests confirms the /launch call
  status; remember a FAILED submit is a page NAVIGATION to an error page, not a red XHR
  (pmd-gotchas #33) - assert the error page text, not the network tab.
- **Evidence:** screenshot of the completed status; the /launch request body/status from
  read_network_requests; the read-back record.

### UT-031 - Grid paging at volume (>100 rows: BO REST 100 cap)
- **REQ:** REQ-012 (list all requests) + checklist Volumes row
- **Preconditions:** a seeded dataset of MORE than 100 request rows (hand to wd-tenant-config /
  bulk load - a 5-row seed does not test this); a role that can view the list.
- **Actions:**
  1. navigate to the list/dashboard page; read_page.
  2. Exercise paging / filtering controls (next page, or apply a filter) -> re-read_page each
     time.
- **Observable:** rows beyond 100 are reachable via paging or server-side filtering (NOT
  truncated to the first 100 with the rest silently dropped - the BO REST limit is 100 and the
  cap truncates silently, pmd-gotchas #15 / model.md); a "Property Error found: .data" or a
  short count is a FAIL.
- **Evidence:** screenshots of page 1 and a later page (or a filtered result whose match lies
  past row 100); read_console_messages(onlyErrors).

---

## Coverage sweep specific to browser execution

The full derivation checklist is wd-testing's; when SCRIPTING, make sure each derived row
becomes an actual browser assertion for both paths and the browser-only landmines:

- **Render path AND submit path per page** - a page that loads is not a page that submits;
  script both (a page can open cleanly and still 500 on POST, and vice versa).
- **Wrong-role negative per domain** - always a real second login as a no/less-access user;
  assert absence of data in the page tree, not just a different landing page.
- **Async / 25s-cap flows** - poll to completion; prove the timeout/async behavior, not just
  the happy sync return.
- **Boundary / null-field on OLD records** - script an EDIT/VIEW against a pre-existing record
  created before a BO field was added (nulls crash pages that assume the field - pmd-gotchas
  #7/#8); a fresh seed will not surface it.
- **Responsive / dark-mode where relevant** - resize_window mobile/tablet + colorScheme dark
  on any page the requirement says end users hit on a phone or in dark mode; reset to desktop
  after.

---

## What does NOT go in this file (defer to wd-testing)

- **Severity** of a failure - wd-testing defect-triage.md.
- **Bug vs CR vs data/config vs doc-drift triage** - wd-testing defect-triage.md.
- **UAT business-speak translation** of scenarios - wd-testing uat-support.md.
- **The scenario derivation itself** and the Unit Testing tab format - wd-testing
  unit-testing.md + wd-design-doc.

This file only makes derived scenarios executable in the Browser pane; it decides nothing about
what a failure MEANS.
