# Driving the in-app Browser pane against Workday

The shared "how to operate the Browser pane (mcp__Claude_Browser__*) against a Workday
Extend app and its tenant" reference. Task-neutral on purpose: wd-test-execution uses it to
run a test plan, and wd-tenant-config points here for browser-driven tenant work. Nothing
here decides WHAT to click - only how to drive the pane reliably and read state back.

---

## Tool map - which tool for which job

| Job | Tool | Notes |
|---|---|---|
| Start a dev-server app + open its tab | `preview_start {name}` | name from .claude/launch.json; wdcli preview loop in wd-extend-dev wdcli-workflow.md |
| Open a tenant-hosted app / native tenant page / any URL | `preview_start {url}` | user permission gate applies (external site) |
| Go to a URL, or back/forward | `navigate` | refs from a prior read_page go stale after this |
| Server logs (build/preview errors) | `preview_logs`, `preview_list`, `preview_stop` | dev-server side only, not tenant |
| Multiple tabs (app in one, tenant read-back in another) | `tabs_context` / `tabs_create` / `tabs_select` / `tabs_close` | tabs_context first to see what exists |
| Read page text + STRUCTURE + get element refs | `read_page` | YAML accessibility tree, tags interactive elements [ref_N] - PREFER this for assertions |
| Find a ref in the last read_page by description | `find` | query the tree instead of eyeballing a screenshot |
| Extract visible body/article text only | `get_page_text` | fast text-only read; no refs |
| Click / type / scroll / key / hover / wait / drag | `computer` | accepts `ref` (stable) OR `coordinate`; screenshot action for evidence |
| Set a form field/checkbox/select/contenteditable by ref | `form_input` | more reliable than click-then-type for inputs |
| Run several predictable actions in ONE round trip | `browser_batch` | use once a sequence is known; stops on first error |
| Console output (errors) | `read_console_messages` (onlyErrors) | assertion + evidence for JS/client errors |
| Network requests (list, or fetch a body by requestId) | `read_network_requests` | inspect API calls the page fires |
| Emulate viewport / color scheme | `resize_window` | mobile/tablet/desktop + light/dark; reset to desktop after |
| Inspect only - computed CSS, DOM probe | `javascript_tool` | DEBUG/INSPECT ONLY - never to implement or "fix" a change |

### House rules (non-negotiable)
- **Assert from `read_page`/`find`, not screenshots.** The accessibility tree is the source
  of truth for text and structure; a screenshot is evidence for a human, not a machine
  assertion. Screenshot AFTER you have asserted, to prove the observable.
- **Batch once steps are predictable.** Drive the first pass step-by-step (re-reading between
  navigations); once a sequence is proven, replay it via `browser_batch` to move fast. Note
  coordinates inside a batch refer to the screenshot taken BEFORE the batch, so prefer refs.
  **When driving tenant WRITES (wd-tenant-config), a committing click (OK/Submit/Confirm/Save)
  is NEVER inside a batch** - batch only the free steps leading up to it, then commit as its
  own confirmed action (wd-tenant-config safety-and-scope.md).
- **`javascript_tool` is inspect-only.** Use it to read computed CSS, poll a value, or probe
  DOM shape while diagnosing. Never use it to click, set values, or work around a bug - that
  hides the real defect and produces false passes.

---

## The auth boundary and login handoff (read before opening any tenant)

The Browser pane is a fresh Chromium with **no SSO session, no cookies, no saved
credentials** - it is not your corporate Chrome, and the Claude-in-Chrome bridge is blocked
by policy. Workday needs SSO + MFA, so **you cannot log in and must never try.**

- **Never type credentials, MFA codes (Duo/TOTP/SMS/hardware), or solve CAPTCHAs** - ever.
  This is a safety boundary, not a limitation to engineer around.
- **The user logs in interactively.** Open the tenant with `preview_start {url}` (or
  `navigate`), then emit a USER-ACTION block and WAIT for their "done" before driving.
  Block format and MFA specifics: wd-auth mfa-and-browser-auth.md.
- **Mid-session expiry:** Workday sessions time out. When `read_page` suddenly shows a login
  or "session expired" screen mid-run, PAUSE the scenario, hand back a re-login USER-ACTION
  block, and resume only after confirmation. Do not re-authenticate yourself; do not mark the
  in-flight scenario Fail for an auth timeout - it is an environment event, re-run it.

Login handoff block (defer wording to wd-auth):
```
YOUR STEPS (in the Browser pane on the right):
1. The tenant sign-in page is open -> enter your Workday SSO credentials there
2. Complete MFA (Duo push / authenticator code) on your device
3. When you see the Workday home page, tell me "done"
```

---

## Opening targets

- **Dev-server app (local preview):** `preview_start {name}` where name matches a
  configuration in .claude/launch.json. This is the wdcli preview loop; build/preview error
  triage stays in wd-extend-dev wdcli-workflow.md, not here.
- **Tenant-hosted app or a native tenant page:** `preview_start {url}` with the tenant URL
  (for example the app's launch URL or a Workday task/report page). External-URL permission
  gate applies - the user approves the navigation. Do the login handoff first.
- **Already open:** `tabs_context` to list tabs, `tabs_select` to front the right one,
  `navigate` to move within it. Keep the app in one tab and a tenant read-back page (a report
  or the BO's related actions) in a second tab when you need to confirm record state.

---

## Workday-UI navigation and selector strategy

Workday is a heavy, dynamic SPA that re-renders constantly and reuses generic control names -
so drive it by the accessibility tree, not by pixels.

- **read_page -> act by ref.** `read_page` returns the tree with `[ref_N]` on every
  interactive element; act on those refs with `computer`/`form_input`. Refs are stable within
  a page state and far more reliable than coordinates. Use `find` to locate an element by
  description ("the Add button", "the Quantity field") when the tree is large.
- **Global Search bar** is the fastest way to reach a task or report: click the search ref,
  `type` the task/report name, then pick the result from a fresh `read_page`. **Reach an Extend
  app page via Search-then-navigate, NOT a hand-built hub URL.** Constructed
  `/w/hub/<appId>/<taskId>.htmld` and `/d/inst/` URLs are UNRELIABLE - seen returning "Not
  Found" / "Instance ID cannot be parsed", especially after a session/cache change (verified
  2026-08-26). Search the app/task name, click the result, then use the app's own hub/nav to
  move between its pages - that always works.
  - **Enter in Global Search does NOT navigate** to a results page (it is a no-op or opens
    nothing useful) -- always **click the suggestion row** that appears in the dropdown.
  - **Clear the search field with the field's X button** (visible after typing); triple-click
    and Ctrl+A do NOT clear it reliably (verified 2026-08-26).
- **Related Actions menus** (the "..."/twinkle on an object) open the actions you often need
  to verify a record; open, re-read, then act - the menu contents are async.
- **`intsys:` search prefix reaches an Integration System directly** (verified): global search
  `intsys: <name>` jumps to the Integration System; from its Related Actions -> Integration ->
  Launch / Schedule opens the modal with the Integration field PRE-CHIPPED. Prefer this over
  the bare Launch/Schedule task, whose Integration picker ignores typed text (scrolling the
  full INT list is impractical).
- **If a prompt/dropdown search fully HANGS** (spinner never resolves, or results stay stale
  after type -> Enter -> wait): press `key` Escape to close it, RE-`read_page`, then re-open and
  retry with a shorter/exact term; clear via the field's X button first (not Ctrl+A). A hung
  dropdown is a recover-and-retry, not a Fail - but after 2-3 retries record it as a Blocked step
  with the evidence rather than looping. (User-reported recurring pain 2026-08; recovery recipe -
  verify live.)
- **Grids, pickers, prompts:** these load asynchronously and paginate. Re-`read_page` after
  opening a picker; type to filter, then select by ref. For grids expected to exceed 100 rows,
  the app itself is bound by the BO REST 100 cap (wd-extend-dev pmd-gotchas.md #15) - test the
  paging/filtering, do not assume all rows render.
- **Grids with ROW ACTION BUTTONS or IN-CELL config** (a common Workday-tenant pain - config
  grids, editable grids; techniques recommended, verify live):
  - Off-screen rows have NO refs until scrolled into view - `scroll_to` the target row's ref, or
    `computer scroll` within the grid's coordinates, then RE-`read_page`. A virtualized grid only
    exposes its visible window; never assume a row exists in the tree because it exists logically.
  - Row action buttons are usually icons with generic/duplicate names across rows - do NOT click
    by name alone. Take the ROW-SCOPED ref from `read_page` (the tree nests the button under its
    row) or `find` with a row-identifying description ("the Edit button in the row for <value>");
    disambiguate by row, act by ref, never by a bare coordinate.
  - In-cell inputs usually need the CELL clicked to enter edit mode FIRST, then `form_input` /
    `type`; a `form_input` on a non-active cell can silently no-op.
  - Per-row "..."/related-action menus open an async overlay that may render OUTSIDE the row's
    subtree - open, RE-`read_page` to capture the overlay, then act.
  - Add a row: click the +/Add control, RE-`read_page` (the new empty row appears), then fill the
    new row's cells by their FRESH refs.
  - Work ONE ROW AT A TIME with a re-read between rows - adding/removing/committing rows shifts
    every other row's refs (same staleness rule as navigation). After a grid commit, assert the
    row state from the FRESH tree, not the pre-edit one.
  - **(!) "No Items" in a WQL-backed picker is often a TIMING artifact, not a real empty.**
    Pickers fire async WQL searches; a screenshot taken right after typing catches the
    pre-result "No Items" state. Recipe: **type -> press Enter -> wait ~2-3s** -- Enter selects
    the top result once the search returns, even if "No Items" is still on screen. Do NOT
    conclude "no data" from a fast "No Items" display; always press Enter and wait, then
    cross-check data truly exists via a related native task (e.g. Edit Fund, Edit Cost Center)
    before diagnosing a data gap. Verified 2026-08-26 in a client dev tenant (Fund, Cost Center,
    and Proxy worker fields all behaved this way).
  - **Native Workday category multi-select prompts** (e.g. BP security-policy -> Security
    Groups field) resist the driver: typing surfaces only a category folder (not leaf
    results) and the typed text does NOT carry into the drill-in; form_input closes the menu
    via blur; find() cannot see off-screen items in the virtualized list. **CONFIRMED working
    fallback: open the CATEGORY folder, then scroll the virtualized popup in 5-10-notch steps
    with a `find` after each batch** (items enter the DOM only when scrolled into view);
    re-`find` right before clicking, because row coordinates shift as the list virtualizes.
    Reliable but slow (budget ~1 find per scroll batch) on huge lists. Never use form_input on
    these fields. (The earlier type -> wait -> "drill-in renders filtered" hypothesis is
    REFUTED - typed text does not filter the drill-in; use the scroll+find fallback.)
  - **CONFIRMED (2026-08-31, UAP v2): the "Security Groups allowed for Workflow Step" picker
    in the BP definition step editor IS checkbox-based (not the multi-select text prompt
    above) and DOES work for the driver.** Open the step's "Security Groups" dialog -> it
    renders a checkbox list of groups -> click the target group's checkbox -> OK. Prerequisite:
    the group must be on the ACTIVE policy (model-bp.md tenant notes) or it will not appear
    in the list. For the text-based multi-select prompts (e.g. BP policy Security Groups
    field itself), the SUSPECTED recipe above remains unvalidated.
  - **CONFIRMED (2026-08-31, UAP v2): chip edits in grid cells commit on SELECTION, not on
    OK.** Pressing Escape to exit a fullscreen view of a cell does NOT discard a chip that
    was already clicked/selected -- the chip is committed at selection time. The Escape key
    only closes the fullscreen overlay; it does not roll back committed chip state. Implication:
    always read back the cell value after closing fullscreen to confirm the expected chip is
    present (the expected chip may not have been selectable at all if prerequisites were
    missing, e.g., group not on active policy).
  - **Native single-select dropdowns that ignore clicks OPEN ON TYPE-AHEAD** (verified): a
    select that will not open on click often opens its full option list when you type a letter
    while it is focused -> then click the option.
  - **Segmented MM/DD/YYYY date inputs resist BOTH `type` and `form_input`** (form_input
    reports filled but framework state stays empty). Use the field's **Calendar button** -
    month-arrow clicks + a day click commit reliably.
  - **Native time prompts do not filter on typed text**: the popup lists hours with a minutes
    SUBMENU per hour - scroll to the hour row, click it, then click the exact minute in the
    submenu.
  - **Tab is DESTRUCTIVE in these forms** (verified): Tab cleared a typed Start Time and
    blanked the adjacent Time Zone chip. Commit a value by clicking the popup option or
    clicking neutral whitespace - never Tab.
  - **Brand-new objects lag GLOBAL search by minutes** (index catch-up) while prompt CATEGORY
    lists show them immediately; and "No Items" under a Search-for-Value drill-in is an
    artifact of the drill-in clearing the typed text, NOT proof of absence - verify via the
    category list before concluding an object does not exist.
  - **Extend `onSearch` picker stuck on "No Items" though the SERVER search succeeded**
    (verified): read the page's `w/prompt/context/<id>` POST response via
    `read_network_requests` - if the result list is there, the search worked and only the
    popup refresh failed. The user's PHYSICAL Enter refreshes it; the driver can then CLICK
    the result rows / prompt icons reliably (real clicks commit selection, dependent-dropdown
    onChange, and checkbox toggles to the widget model). A mid-test required-field validation
    banner SHIFTS the layout - re-screenshot / re-`read_page` before clicking by coordinate.
    - **Reliable commit recipe for this picker (verified reproducible 2x live, 2026-09-09,
      UAP v2 checkout scope picker): (1) click the field, (2) type the term, (3) wait ~2s for
      the onSearch WQL to land, (4) click the picker's trailing LIST/PROMPT icon (the hamburger
      at the right edge of the field).** The icon-click is the load-bearing step - it re-opens
      the stale menu, which re-reads the now-populated result set and commits the single match
      as a selected pill. `type` + Enter does NOT work; `type` + wait alone does NOT work; the
      trailing-icon re-trigger is what commits. (Hypothesis, not yet root-caused: onSearch
      resolves async but the rendered menu only refreshes on a re-open event - the icon click
      is that event.) Distinct from the native-Workday-prompt recipe above (type -> Enter ->
      wait), which is for tenant WQL prompts, not Extend `onSearch` pickers.
- **`workers/me` returns S21 for implementer/admin accounts** (e.g. impl-user@<tenant> has
  no Worker record). Any Extend app that calls `workers/me` will fail or show empty pages for
  these accounts. **Workaround: Start Proxy as a real worker** (Global Search "Start Proxy"
  -> type worker name -> **must press Enter to chip the name** -> OK; stop with "Stop Proxy").
  The proxied worker's own security then governs which data the app can see (pickers, BOs).
  - **Financial-data pickers (Fund, Balancing Unit, etc.) are security-gated** by the
    signed-in or proxied worker's security. A worker without financial-data access shows
    "No Items" on Fund/Balancing-Unit pickers even when the data exists. Verify the data
    truly exists first (Edit Fund search in the tenant), then use a worker known to have
    financial-data security. Verified 2026-08-26: Logan McNeil (HR worker) saw empty Fund
    pickers; Teresa Serrano (financial worker) saw them populated.
- **iframes and pop-ups:** Workday hosts some surfaces (and Extend pages) in frames or new
  tabs. If `read_page` looks empty or stale, check `tabs_context` for a new tab and select it.
- **Waiting for async loads - never a fixed sleep.** Use `computer` action `wait` for a short
  beat, then RE-`read_page` and check for the expected element; poll (re-read up to a few
  times) rather than guessing a duration. Page-synchronous Extend flows have a hard 25-second
  cap (wd-extend-dev orchestration.md) - if nothing has appeared by then, that is a result to
  record, not a reason to wait longer.

---

### Breaking a vendor call for one click (learned 2026-10-05, UT-313)

- **Flows read App Attributes at run time; the page reads some at open.** Break the attribute BEFORE the page opens and the app fails at its own sign-in step, never reaching the code under test.
- **So: open the page first, break the attribute from a SECOND tab, click once, restore from that tab.** `tabs_create` keeps the page under test alive.
- **The attribute edit grid holds values in inputs only after its row is clicked;** a JS scan before that finds empty inputs. Click the row, then check `document.activeElement.value` by length and suffix only - never echo the value.
- **Append a short marker (e.g. `-ut313`) and remove exactly that many characters to restore;** verify the restored length matches the original before OK.
- **Wait about a minute after saving the attribute before the click (learned 2026-10-05, second run).** A click ten seconds after the save still used the old value - the lookups answered normally. Allow ~60 s, or prove the break is live with a throwaway call first.
- **Prove a click actually reached the server - read the `flowController` call.** Every PMD button click is one POST to `.../w/flowController`; the response body (`read_network_requests` with its `requestId`) is the page-state diff, including the exact text written to status and error widgets. No new `flowController` entry means the click never fired (first-click focus quirk, a hidden modal, or a stale coordinate) - the screen alone cannot tell you.
- **Escape inside an Extend editor opens "Discard Changes?"** and every click after that lands on the modal overlay. Close value lists by clicking elsewhere, not with Escape; if the prompt appears, choose Continue.
- **Locate the attribute cell by its content, not by eye.** The edit grid's rows are dense and a near-miss click focuses the neighbouring attribute. Read `document.activeElement.value.length` (and a suffix check) BEFORE typing; abort if it is not the expected field. The pane's screenshot frame can differ from CSS pixels, so take a fresh screenshot and click what it shows.
- **The requisition's own tab may fail to open while the vendor is broken** (other flows run on load) - open every editor you need before the break.
- **Find the attribute's value in the row AFTER its label row (learned 2026-10-07).** In the edit grid the label and its value sit in consecutive `tr` elements of the same table, so a same-row scan finds nothing. Read lengths from `labelRow.nextElementSibling` - never print the text.
- **The edit grid scrolls when you click into it.** A coordinate measured before the first click can land on the next row after it. Re-measure the cell (or re-screenshot) right before each click, and convert CSS pixels to the screenshot frame (frame width / `innerWidth`).
- **Click the attribute's LABEL first, then its value (learned 2026-10-07).** A first click on the value cell twice opened a neighbouring attribute's input instead (7 and 19 characters; nothing typed, caught by the length check). A click on the label text selects the row (`activeElement` is the `tr`, no input opens) and lets the grid finish scrolling; re-measure, then click the value.
- **Allow about three minutes, not one, for an attribute change to reach the flows.** On 2026-10-07 a click 2 min 15 s after the save still used the old value (and, being a success, re-saved a result). Prove the break is live before trusting a "pass".
- **An attribute with no value has NO value row (learned 2026-10-08).** The next row after its label is the next attribute's label. Reading "the row after the label" then records the next label's length, which made 5 empty attributes look set and a header look like a 19th attribute, for four days. Walk the rows instead and print lengths only:

  ```js
  // label rows: name in cell 1, type in cell 2; value rows: value in cell 4
  let cur = null; const out = {};
  [...document.querySelectorAll('tr')].forEach(r => { const c = [...r.children];
    const name = (c[1]?.innerText || '').trim(), type = (c[2]?.innerText || '').trim();
    if (/^[A-Za-z]+$/.test(name) && type && !['Attribute', 'Value'].includes(name)) { cur = name; out[cur] = 0; }
    const len = (c[4]?.innerText || '').trim().length; if (cur && len && out[cur] === 0) out[cur] = len; });
  out  // 0 = empty attribute
  ```
  Keep the result as the baseline file for that app, and compare by name, not position.
- **Breaking the call proves only half of a failure guard (learned 2026-10-08).** UT-313's wrong-path and no-host runs all passed, yet the guard reported the vendor's ordinary "no data" reply (HTTP 404 with a readable body) as a failed call. Also send a request the vendor answers with no data through the guarded path, and expect the vendor's own message. A gateway launch of the flow with the page's headers is enough; no attribute break is needed.
- **Idle tabs drop to the sign-in page while the session is still alive (2026-10-07).** After a long gap, every other tab showed `.../login.htmld` while the tab in use worked. Navigating those tabs back to their page loaded them with no sign-in. Check one tab's URL before asking the user to sign in again.

## Evidence capture primitives

- **`computer` screenshot** - the human-visible proof of an observable result; capture AFTER
  asserting from the tree, and after each Pass/Fail decision point.
- **`read_console_messages` (onlyErrors)** - client-side JS errors; part of the assertion for
  any page load and mandatory proof on a Fail.
- **`read_network_requests`** - list the calls a page fired; fetch a specific body by
  `requestId` to inspect an API request/response (payload, status). Essential for
  API-touching steps - but remember Extend submits are server-rendered (see Reliability).
- **`get_page_text`** - quick text-only capture (confirmation banners, error summaries).
- **`resize_window`** - mobile/tablet/desktop presets plus light/dark `colorScheme` for
  responsive and dark-mode checks; **reset to desktop** when done so later steps aren't
  emulated.

---

## Reliability patterns

- **Refs go stale after navigation.** Any `navigate`, page transition, submit, tab switch, or
  picker open invalidates prior `[ref_N]` values - RE-`read_page` before acting again. A ref
  used across a navigation is the most common false-negative cause.
- **Server-rendered pages hide failures (pmd-gotchas.md #33).** Extend pages are
  server-rendered, so a failing submit is a page NAVIGATION to an error/exception page - NOT a
  red XHR you can catch in `read_network_requests`. Assert failures by reading the resulting
  page (applicationException / error summary text) via `read_page`, not by watching the
  network tab.
- **Retry + re-read.** Transient blank reads happen; re-`read_page` once before concluding an
  element is absent. Distinguish "not loaded yet" (wait + re-read) from "genuinely absent"
  (the negative assertion you want).
- **Escape inside an Extend pop-up closes the WHOLE pop-up** (verified 2026-10-04, a client app
  Fair Pay Ranges editor opened from a requisition tab). The hang-recovery advice above (press
  Escape) is for full-page tasks. In an app page shown as a pop-up, close an open dropdown by
  clicking blank page space instead; Escape discards the page and you reopen it from scratch.
- **The first click after using a dropdown may only close it.** Clicking a button right after
  choosing a dropdown value often just blurs the dropdown; the button's action does not run.
  Re-read the page for the expected change, and click again when it is absent. Never count the
  first click as proof the action ran.
- **Refs go stale after a re-layout too, not only after navigation.** When rows render into a
  grid, or a note line appears above a widget, everything below shifts. A ref captured before
  the shift can land on the neighbouring widget (seen: a button ref opened the multi-select
  above it). After any render that adds content, screenshot and click by coordinate, or
  re-`find` first.
- **A dropdown list can screenshot blank while its options exist.** The popup paints late; the
  accessibility tree already holds the `Search Results` menu. Use `find` / `read_page` on that
  menu instead of waiting for the screenshot.
- **Type-ahead plus Enter auto-selects a single match** - and fires the widget's onChange (a
  dependent value picker opens). Type a term that matches several options when you only want to
  list them.
- **App Manager instance links go stale.** The App Details URL embeds a timestamp and returns
  HTTP 404 later. Navigate App Manager (task) -> Configure each time instead of reusing the URL.
- **Edit Application Attributes Values shows plain-text attributes in clear text, secrets
  included.** `scroll_to` the attribute you are changing and keep screenshots to those rows;
  never `get_page_text` that page. The saved summary page masks values.
- **Saving a screenshot as evidence:** the tool result names the image's source path; copy that
  file to a named evidence file (e.g. `evidence-<date>-<item>-<scenario>.jpg`) straight away.
- **One action-batch per predictable sequence.** After a sequence is proven interactively,
  collapse it into a single `browser_batch` so re-runs and regression sweeps are fast and
  deterministic.

---

## Safety boundary (writes belong to the sibling)

This skill is read-and-drive-the-APP: it exercises the app's own pages/flows and reads tenant
state back to confirm results. Driving the browser to CONFIGURE the tenant, change security,
or CREATE test data is wd-tenant-config, whose safety-and-scope.md owns the WRITE gate and the
no-real-customer-data rule. When a scenario needs setup or seed data that does not exist, hand
to wd-tenant-config rather than improvising a tenant write here. And regardless of surface, the
prohibited actions above (credentials, MFA, CAPTCHA) never happen in this pane.

- **A hidden Browser pane stalls Workday pages - a screenshot unsticks them (verified 2026-10-21).** With the desktop window hidden, Workday search results and modals stay blank: `find` and `read_page` return nothing for 30 seconds or more. One `computer` screenshot (it may time out once - retry) forces the page to draw, and `find` then works. In a batch, put a small-scale screenshot after each navigate or task open. Also: after an EDIT modal saves, Workday returns to the page it came from (here the search results), and "Your changes have been saved" appears in `get_page_text` - that line is the save signal, not proof of what was stored. Read the record back.
