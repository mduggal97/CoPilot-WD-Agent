# Efficient PMD/script patterns - externalized WQL, compute-once, set-based helpers

These patterns are distilled from a client developer's production refinements on a delivered inventory-tracking app (build-verified - the app runs this code in a live tenant). Each entry: the pattern, a trimmed real snippet, why it beats the naive version, and where it generalizes. App-specific table/page names appear only as illustrative examples; substitute your own.

---

## 1. Externalize WQL into `presentation/wqlQueries/*.wqlquery`

Instead of building a WQL string inline in an endpoint `url` (hand-encoding with `string:pathEncode`, escaping quotes, duplicating the same SELECT across pages), define the query once in its own file and reference it by id.

**Query file** - `presentation/wqlQueries/getExpiryAssignment.wqlquery`:

```json
{
  "id": "getExpiryAssignment",
  "query": "
    SELECT workdayID, ExpiryAssignment, site, assignmentDate, transactionType, weekOf, assignedWorkers, status, parLocation
    FROM <app>_expiryAssignments
  "
}
```

**Endpoint that uses it** - in any `.pmd`:

```json
{
  "baseUrlType": "workday-wql",
  "name": "getExpiryAssignment",
  "url": "data",
  "authType": "sso",
  "wqlQuery": { "queryId": "getExpiryAssignment" }
}
```

**Parameterized query file** - declare `parameters[]`, reference with `<% name %>` placeholders inside the SQL:

```json
{
  "id": "getExpiryLinesbyTransaction",
  "parameters": ["transactionId"],
  "query": "
    SELECT workdayID, lineId, transaction, purchaseItem, quantityExpired, unitCost, parLocation
    FROM <app>_expiryLines
    WHERE transaction = '<% transactionId %>'
  "
}
```

**Endpoint passes the parameter** (works with `deferred: true` for type-aheads/on-demand lookups too). A deferred endpoint's `parameters` expressions evaluate at INVOKE time and CAN read live page widgets - so there are TWO binding sources, and picking the wrong one fails silently:

**(a) `queryParams.<name>`** - populated only AFTER a page round trip. Correct for a detail page reached by navigation or a `parameterBindings` hand-off:

```json
{
  "baseUrlType": "workday-wql",
  "name": "getExpiryLinesbyTransaction",
  "url": "data",
  "authType": "sso",
  "wqlQuery": {
    "queryId": "getExpiryLinesbyTransaction",
    "parameters": { "transactionId": "<% queryParams.transactionId %>" }
  }
}
```

**(b) a direct widget read** - evaluated live at invoke time. Correct for a cascading picker or any dependent lookup fired from the SAME page (runtime-verified 2026-08-20):

```json
{
  "deferred": true,
  "wqlQuery": {
    "queryId": "getLinesByFiscalYear",
    "parameters": { "fy": "<% empty fyPicker.getSelectedEntries() ? '' : ('' + fyPicker.getSelectedEntries()[0].id) %>" }
  }
}
```

**WARNING:** a deferred endpoint invoked from the same page that binds `queryParams` returns an EMPTY result set with NO error - query params only exist after a round trip, so the WQL runs `WHERE x = ''` and the symptom reads as a data problem. Same-page cascade = widget read; navigation hand-off = queryParams. (Also note `.invoke({args})` does NOT override a declared `parameters` binding - pmd-gotchas #49.)

**Why better than inline `url: "<% 'data?query=' + string:pathEncode('SELECT ...') %>"`:**
- One definition, many callers - the same SELECT reused across pages changes in one place. In the naive form the identical query is copy-pasted into every page and drifts.
- No manual `string:pathEncode` and no `\"`-escaping of literals - the platform binds `parameters` for you, which also removes a WQL-injection footgun from string concatenation.
- The column list and FROM clause are readable on their own line instead of buried in a one-line encoded string.
- Query files diff cleanly and can be reviewed/owned separately from page layout.

**Where it applies:** any WQL read used on more than one page, or any query complex enough that inline encoding hurts readability. Note the platform still supports inline `wqlQuery: {query: "..."}` and the encoded-`url` form; migrate the shared/complex ones and leave genuinely one-off, page-local queries inline if you prefer. In practice a page can mix both (externalized for the reused reads, inline `deferred` for a page-specific search).

**Alternate `.wqlquery` shape seen in Workday App Catalog samples (sample-verified) - full-expression body + top-level `limit`:** instead of a plain SQL string with `<% name %>` placeholders, the samples author the whole `query` as a **`<% ... %>` expression** whose value is a backtick-template string with `{{param}}` interpolations, and add a **top-level string `limit`** field on the query file to cap rows:
```json
{ "id": "getLinesByTxn",
  "limit": "1000",
  "parameters": ["transactionId", "table"],
  "query": "<% `SELECT lineId, quantityExpired FROM {{table}} WHERE transaction = '{{transactionId}}'` %>" }
```
Because the body is an expression, **even the FROM clause can be parameterized** (`{{table}}`) - impossible in the plain-string form. Same `wqlQuery.parameters` binding on the endpoint. Use this variant when the table/columns vary at runtime or you want the row cap in the query file rather than on the endpoint; the plain-string form above stays fine for fixed queries.

---

## 2. Compute once in `onLoad`, stash in `pageVariables`, read everywhere

When several widgets need the same derived list/figure, compute it a single time in `onLoad` (or once at the top of the page `script`) and store it on `pageVariables`. Widgets and cell templates then read the pre-computed value instead of each re-running the filter/loop.

```jsonc
"onLoad": "<%
    // Filter assignments down to the caller's par-location scope, once.
    let locationAssignment = list:filterMultiple(getExpiryAssignment.data, 'parLocation.id',
                                getParLocations.data.map(x => {x.parLocation.id}));
    pageVariables.locationAssignment = locationAssignment.filter(x => {x.status != 'Complete' && x.status != 'Canceled'});
 %>",
"script": "<%
    let activeAssignmentStatus = function(parLocationId) {
      // reads the already-scoped list - no re-filter of the raw endpoint
      let activeAssignment = pageVariables.locationAssignment.filter(x => {x.parLocation.id == parLocationId});
      return empty activeAssignment ? 'Unassigned' : activeAssignment[0].status;
    };
 %>"
```

The reporting page takes this furthest: a single `reporting(startDate, endDate)` function returns ONE map of every figure the page shows (`totalQuantity`, `totalCost`, per-location totals, last-completed dates, in-progress counts), called once in `onLoad` into `pageVariables.rep`. Every tile/grid then reads `pageVariables.rep.totalCost` etc. - the whole report is one pass, and re-running it on a "Run Report" button is just another call with new dates.

**Why better:** grid/tile expressions can be evaluated many times; putting a heavy `.filter()`/loop directly in each binding re-does the work per widget (and per re-render). Compute-once collapses N recomputations to one. It also gives every widget a single consistent snapshot.

**Where it applies:** any page where two or more widgets derive from the same source, and any page with an expensive aggregation feeding a dashboard.

---

## 3. Set-based `list:` helpers instead of nested loops

Prefer the platform's set operations over hand-rolled `for` loops with inner `.find()`:

```javascript
// Keep only lines whose transaction id is NOT in the canceled set - one call, no inner loop
let expiredLines = list:excludeMultiple(getExpiryLines.data, 'transaction.id', cancelTransactionId);

// Keep only assignments whose parLocation.id is IN the caller's allowed set
let scoped = list:filterMultiple(getExpiryAssignment.data, 'parLocation.id', allowedParLocationIds);

// Newest-first, then take [0] - instead of a max-tracking loop
let lastCheckOut = list:sort(completedTransaction, 'checkOutTime', false)[0].checkOutTime;

// Flatten a list-of-lists before .distinct()
let allWorkers = list:flatten(getExpiryAssignment.data.map(x => {x.assignedWorkers})).distinct();
```

**Why better:** `list:filterMultiple`/`list:excludeMultiple` express an inner-join / anti-join in one line; the naive version is an outer `for` with an inner `.find()` (O(n/m) and much harder to read). `list:sort(..., false)[0]` replaces a running-max loop. These read as intent, not mechanics.

**Where it applies:** any "keep/drop rows whose key is in this other list", any "newest/oldest by field", any de-dupe across a nested collection.

---

## 4. Skip endpoint round-trips with `exclude` (conditional execution)

An endpoint can carry an `exclude` expression - when it evaluates true, the call is not made. Chain it to a precondition so dependent lookups only fire when they can succeed.

```jsonc
{
  "name": "getAssignmentForCost",
  "baseUrlType": "app",
  "url": "<% 'expiryAssignments/' + getExpiryTransaction.data.filter(x => {x.workdayID == queryParams.transactionId})[0].assignment.id %>",
  "authType": "sso",
  "exclude": "<% getExpiryTransaction.data.filter(x => {x.workdayID == queryParams.transactionId}).size() == 0 %>",
  "_comment": "Parent assignment (absent for ad-hoc). Skipped when there's no matching transaction."
},
{
  "name": "getParForCost",
  "baseUrlType": "workday-wql",
  "authType": "sso",
  "exclude": "<% empty getAssignmentForCost || empty getAssignmentForCost.parLocationId %>",
  "url": "..."
}
```

**Why better:** avoids a guaranteed-to-fail call (indexing `[0]` on an empty result, or a lookup with a null id) and saves a network round-trip on paths where the data isn't there (e.g., ad-hoc records with no parent). Cleaner than making the call and defensively null-guarding every downstream read of a response that was never going to come.

**Where it applies:** any dependent/secondary endpoint whose inputs come from a prior endpoint that may be empty; any lookup that only makes sense for a subset of entry states.

---

## 5. Reusable `.script` files exporting a helper map

Logic used by more than one handler lives in `presentation/scripts/*.script`, included via the page's `include[]`, and called by name - not copy-pasted into each `onChange`.

```javascript
// presentation/scripts/weeklyFilters.script
var applyFilters = function() {
  var rows = getExpiryAssignment.data;
  // ...reads every filter widget, builds `out`...
  weeklyGrid.setRows(out);
};

{ "applyFilters": applyFilters }   // export map - the file's public surface
```

```jsonc
// weeklyAssignments.pmd
"include": [ "weeklyFilters.script" ],
...
"onChange": "<% weeklyFilters.applyFilters(); %>"   // every filter widget calls the one function
```

**Why better:** five filter widgets share ONE filter routine instead of five near-identical inline copies that drift apart. The file is independently diffable, commentable, and carries the header/change-log block (see standards.md). Keep genuinely page-specific one-offs inline; externalize what repeats.

**Where it applies:** filter-bar -> grid refresh, any calculation invoked from multiple widgets, anything you'd otherwise paste twice.

---

## 6. Early-return guards over deep nesting

Small helpers resolve the empty/absent case first and return, so the happy path isn't buried in an `if` pyramid:

```javascript
let openTransaction = function(assignmentId) {
  let transaction = getExpiryTransaction.data.filter(x => {x.assignment.id == assignmentId
                      && (x.status == 'In Progress' || x.status == 'On Hold')});
  return empty transaction ? '' : transaction[0].workdayID;   // guard first, then index safely
};
```

Combined with the null-coalescing operator for field reads (`x.unitOfMeasure.descriptor ?? ''`) this keeps helpers to a couple of lines and prevents the "index [0] on empty" runtime error.

**Where it applies:** every helper that returns a value derived from a filtered list.

## 7. Treat flow count as a budget - param-driven pages over one-flow-per-action

The app-wide cap is **25 combined flowDefinitions + editWizards** (build fails at 26 - see
pmd.md for the error and the verified fix). On a CRUD app, one-flow-per-action spends that
budget fast: add/edit/cancel/restore/remove/confirm pages at one 2-step flow each.

Design the consolidation in from the FIRST page, not at flow 26:

- **One page per action FAMILY, parameterized** - a single confirm page whose
  `queryParams` carry the variation (`activeVal`, or `collection` + `recId` + `returnId`),
  driving both the write value and the on-screen copy. Callers differ only in
  `parameterBindings`. One flow serves the whole family, behavior-identical per action.
- Prefer `multiStepLayout` (one PMD, up to 10 steps, zero flowDefinitions) over
  page-per-step wizards - see pmd.md.
- At design time, count the planned flows on the wireframe set; if the CRUD surface x
  1-flow-per-action approaches ~20, consolidate BEFORE build (architecture review's
  limits-headroom row is where this gets checked).

**Where it applies:** any app with more than a handful of add/edit/confirm actions -
verified on a delivered build session, 2026-08-05 (26 flows -> 25 by merging cancel+restore
into one param-driven page).

**CLARIFY - two DIFFERENT caps, don't conflate them (per Workday App Catalog samples, sample-verified):**
- The **25-cap is PMD-side**: combined `flowDefinitions` + `editWizards` on PMD pages. That is the
  budget the consolidation above protects.
- **Orchestration decomposition is a SEPARATE budget** - the **150 flows/app** cap (warn 125, from
  orchestration.md limits). Suborchestrations (`.suborchestration` files) count against *that*, not
  the 25 PMD-flow cap. So **factoring one big flow into many small typed subflows does NOT spend
  page-flow budget** - decompose orchestrations aggressively for readability/reuse without touching
  the CRUD-page headroom. (The two only meet in the total 150-flows/app ceiling.)

**Suborchestration decomposition conventions (per Workday App Catalog sample capitalProjectPlanning, sample-verified):** the sample factors a large orchestration into many small subflows using a consistent shape worth copying -
- **`Verb+Entity` names** (`CreatePlan`, `ResolveTask`, `PostLines`) - read as intent.
- **suffix discipline: `*Stub`** (a not-yet-implemented placeholder subflow - the orchestration analog of the `IN_PROGRESS_` flow-name convention), **`*Base`** (a shared/base subflow other flows build on), **`*DNU`** ("Do Not Use" - retained but deprecated; never call from new work).
- **thin typed subflow interfaces** - each `StartSubflow` declares a small set of typed parameters and `EndSubflow` exports a small typed result, so a subflow is a clean function boundary rather than a grab-bag of loose data reads. Keep the interface narrow; pass ids/dates in, hand a typed result back.
