# WQL (Workday Query Language) - language and invocation reference

WQL is the default read path for Extend pages and O4I flows: SQL-like SELECT syntax over
Workday "data sources" (delivered tenant sources, app BOs, calculated fields, Prism PDS),
returning JSON. This file owns the grammar and the invocation mechanics. Evidence tiers:
build-verified (ran in a delivered app/tenant) > sample-verified (official Workday App
Catalog samples) > official-docs (public Workday docs) > (!) verify in-tenant.

## Where WQL runs - the invocation forms

| Surface | Form | Tier |
|---|---|---|
| Page endpoint, URL-encoded | `baseUrlType: "workday-wql"`, `url: "<% 'data?query=' + string:pathEncode('SELECT ...') %>"` (`string:urlEncode` also works) | build-verified |
| Page endpoint, externalized | `wqlQuery: {queryId: "<id>", parameters: {...}}` referencing `presentation/wqlQueries/<id>.wqlquery` | build-verified |
| Page endpoint, POST | `httpMethod: "POST"`, `url: "data"`, `onSend` returns `{query: <string>}` - the query travels in the body, no encoding needed | sample-verified (wql, generateWQL catalog apps) |
| Orchestration flow | GET `/wql/v1/data` with the query in a `queryParams` entry (build-verified), or CreateTextTemplate + POST; iterate `.asJSON().iterator("$.data[*]")` - see orchestration.md "Reading data at scale" | build-verified |
| External REST | `GET https://api.us.wcp.workday.com/wql/v1/data?query=<urlencoded>` or POST `{"query": "..."}` with a bearer token (wdcli tenant token for ad-hoc testing; API client + refresh grant for production - see the wd-auth skill) | build-verified |

**RULE - externalize into a `.wqlquery` component; do not string-build a SELECT into an endpoint `url` [feedback 2026-09-04].** The "Page endpoint, externalized" row is the DEFAULT for any reused/non-trivial read: define the query once in `presentation/wqlQueries/<id>.wqlquery` and reference it with `wqlQuery:{queryId, parameters}`. Maintenance then lives in ONE place and the platform handles binding/escaping. A `SELECT` string-built into an endpoint `url` (the "URL-encoded" row) is reserved for a genuine one-off; putting a WQL query in the url of a REST/app endpoint (any `baseUrlType` other than `workday-wql`/`wql`) is the wrong endpoint TYPE (pmd-gotchas #78, caught by pmd_preflight). If sibling endpoints in the same app already use the component form and one does not, fix the outlier - do not propagate the inline shortcut.

**Gotcha - the inline `wqlQuery: {query: "SELECT ..."}` block FAILS at runtime** ("Property
Error found: .data") even though it builds clean (delivered build session, 2026-08-05).
Use the URL-encoded form or the `queryId` form. Full page wiring, the deferred type-ahead
pattern, and this gotcha's context: pmd.md in this skill.

**Gotcha - external / ad-hoc WQL: `limit`/`offset` ride the QUERY STRING, not the JSON
body [BV].** On a tenant-specific WQL endpoint (`.../wql/v1/<tenant>/data`), putting
`limit`/`offset` in the POST body throws S5 "unrecognized field: limit"; pass them as query
params (`data?limit=100&offset=0`) with the body carrying only `{"query": "..."}`. The
tenant-specific endpoint caps the page at 100 rows (the WCP universal gateway accepts body
params and larger pages) - page with `offset`. Adjacent tooling gotcha: a Windows cp1252
console mangles non-ASCII when printing API output (a non-ASCII char -> UnicodeEncodeError
under `python x.py > log.txt` or any captured run) - print ASCII markers (`[OK]`/`FAIL`) or
force utf-8 for output that gets redirected/captured. [BV]

Auth: page endpoints run as the signed-in user (`authType: "sso"`) - results respect that
user's security. In a flow, WQL is auto-authenticated via the integration system's ISU.

## Discovering data sources and fields

The WQL provider exposes its own metadata endpoints (sample-verified, wql/generateWQL
catalog apps; also usable from external REST):

- `dataSources?limit=100` and `dataSources?searchString=<text>&limit=100` - list/search sources (each row: `id`, `descriptor`, `alias`).
- `dataSources/{id}/fields?limit=100` (+ `offset=`, + `searchString=`) - field catalog. Wide sources exceed one page (a par-location line source has 256 fields) - page through. **REQUIRES the source ID (the hash), NOT the alias** - passing the alias returns 404 (S21 not found); look the ID up from the `dataSources` list first. [BV]
- **A source's human descriptor is NOT its WQL alias - discover, do not guess [BV].** The display name in the UI often differs from the alias used in FROM (e.g. a "custom worktag values" concept can resolve to a custom-organizations source keyed by subtype; an "integration systems" concept can resolve to an "all integration systems (audited)" source). When you only know the business name, search `dataSources?searchString=<text>` and read the real `alias`/`descriptor` rather than assuming the obvious name.
- **SELECT/WHERE field names are NEVER a guess either - and a wrong one fails at RUNTIME, not build [feedback 2026-09-04].** A field name not on the source passes the build and compiles the page, then 400s at render (`RestRequestException: Inbound endpoint request failed (400): .../wql/v1/data`). MDR review example: `SELECT programObject ... referenceIDValue` when the source's real fields are `program` and `referenceID1`. Confirm every projected/filtered field against `dataSources/{id}/fields` (or by running the query live with a `wdcli tenant token`) BEFORE ship, and never carry a field list over from a copied sibling query - a Program is not a Cost Center, its fields differ. (Runtime failure, not caught by pmd_preflight - smoke-run each touched `.wqlquery`.)
- `dataSources/{id}/dataSourceFilters` - filters defined on the source. Non-empty here often means the source REQUIRES a filter (see FROM below).
- On the raw REST surface `/wql/v1/dataSources` is paged; its `search` query param was ignored in one tenant test - use `searchString`. (build-verified tenant fact)

## Grammar

### SELECT projection

- Field list with optional aliases: `SELECT workdayID, name, ledgerName AS ledger FROM companies` (sample-verified). `as`/`AS` and even `SELECT`/`select` are case-insensitive in samples.
- **House convention:** alias to `workdayID as id` + a display field `as descriptor` so results drop straight into instanceList pickers (build-verified everywhere).
- **Nested / related-object projection** with `{ }`: `locationOfBusinessAsset { workdayID as locationId, locationName }` (sample-verified). Multi-level nesting works: `primaryJob { jobProfile { descriptor }, position { workdayID, descriptor }, supervisoryOrganization { manager { descriptor } } }` (build-verified in a delivered app).
- **Business-process subselect on an app BO** (sample-verified, confirmed 2026-08-07): `businessProcesses{status, workdayID as id, businessProcessStepAwaitingAction}` - approval status/step in one query, no second call. Cross-ref: prism-and-reporting.md documents this same construct.
- **Tenant calculated fields** `cf_<name>` project like any field, including against an Extend BO's WQL data source - `cf_` fields never appear in the `.businessobject`, only in WQL (build-verified; see pmd.md).
- **Aggregation:** `SELECT crisisEvent, count() as count, followUpNeeded FROM ... GROUP BY crisisEvent, followUpNeeded` (sample-verified, crisisCheckin). Official function surface (official-docs, developer.workday.com, verified 2026-08-25) is EXACTLY six: `AVG`, `COUNT()`, `COUNT(DISTINCT)`, `MIN`, `MAX`, `SUM` - there are no other functions in WQL at all (percentile is RaaS-only).

### FROM - data sources

- Delivered sources by alias: `companies`, `costCenters`, `allWorkers`, `allActiveEmployees`, `supplierInvoices`, `purchaseOrders`, `purchaseItemsIndexed`, `allSecurityGroups`, `allCustomReports`, `countries`, `myDirectReports`, `itemLot`, etc. (build- and sample-verified).
- **App BO source name = `<appReferenceId>_<collectionName>`** (e.g. `myApp_abcdef_expenseRequests`). In a page, keep it portable with `site.applicationId` (inline expressions) or an `applicationId` parameter in a `.wqlquery` file - never hardcode the reference ID. (build-verified)
- **(!) App BO instances are NOT guaranteed to be WQL-indexed** (build-verified 2026-08-25): in one delivered app, `SELECT ... FROM <app>_<collection>` returned 0 rows while the BO REST collection GET returned every instance - all pages had to switch to REST. Verify WQL-on-your-own-BO returns data in the target tenant BEFORE building pages on it; default to BO REST for own-BO reads (model.md has the full rule).
- **Data-source arguments in parens after the source name** (sample-verified):
  - `dataSourceFilter = <filterName>`: `workersForHCMReporting (dataSourceFilter = allActiveWorkers)`, `allActiveJobProfiles(dataSourceFilter=defaultFilter)`.
  - Filter entry parameters alongside it: `businessAssets (dataSourceFilter = businessAssetsFilterByCompanySpendCategoriesAndItems, company='<wid>')`, `allCases (dataSourceFilter = casesOpenedWithinDateRangeFilter, startingCaseCreationDate='...', endingCaseCreationDate='...')`.
  - Source-level entry parameters without a named filter: `bonusAndOne_TimePayments (startDate='...', endDate='...')`, and a company-hierarchy + fiscal-period-range form on a ledger source.
- **Some sources REQUIRE a filter** - querying one bare returns 400 "Specify a data source filter" (build-verified: a par-location source required it while its MassMaintain sibling did not). Check `dataSourceFilters` on the source first.
- **Prism:** a published/analysis-enabled Prism source is addressable as `cds_<apiName>`; project `WPA_RowID as id` as the stable key (sample-verified) - full wiring in prism-and-reporting.md.

### WHERE - operator surface seen in source

All sample- or build-verified unless tagged:

- Comparison: `=`, `!=`, `<=`, `>=` (date range: `fiscalPeriodStartDate <= '<d>' AND fiscalPeriodEndDate >= '<d>'`). Bare `<`/`>` are OFFICIAL - all four inequality operators, Date and Numeric types only (official-docs, 2026-08-25).
- Boolean: `inactive = false`, `active = true` - bare `true`/`false` literals.
- Sets: `in (<wid>, ...)` (WIDs unquoted), `not in ('REVIEWED','SUBMITTED')` (strings quoted).
- Text search: `contains` / `not contains`, `startswith`, `endswith` - ALL official (official-docs, 2026-08-25): lowercase keywords, Text fields only, value matching case-insensitive. That is the ENTIRE pattern surface - there is officially NO `LIKE`.
- Null checks: `is empty` / `is not empty` - official, valid on all five field types including Instance (sample-verified locally as `IS NOT EMPTY`; keywords case-insensitive).
- Combination: `AND` / `OR` with parentheses; official docs: AND binds tighter than OR (official-docs) - parenthesize anyway.
- **`WHERE ON <relatedField> <condition>` - filter on a related object's fields**, chainable with a plain WHERE: `WHERE ON crisisEvent active = true WHERE crisisEvent IS NOT EMPTY` (sample-verified, crisisCheckin).
- Instance-field equality takes a WID: `WHERE supplier = <wid>` or `WHERE worker = ('<wid>')` - both bare and quoted/parenthesized forms appear in working samples.
- **(!) `WHERE <selfReferencingInstanceField> IN (<wids>)` on an instance data source can return ZERO rows with a 200** (build-verified) - silently empty, no error. Filter on **`workdayID`** instead (`WHERE workdayID IN (...)`), the universal per-row WID field. A 200-with-zero-rows on an instance-field filter is a query-SHAPE bug, not missing data - swap to `workdayID` before concluding the data is absent.

### ORDER BY / LIMIT / paging

- `ORDER BY <field> [ASC|DESC]` (sample-verified; default ascending). Multi-key comma list IS official (`ORDER BY f1 ASC, f2 DESC`); official caveat: it "sorts alphabetically, not logically" (official-docs, 2026-08-25).
- In-query `LIMIT n` (sample-verified via generateWQL's builder); official max is 999,999 - and LIMIT does NOT improve performance (the full result set is retrieved first, then truncated; official-docs 2026-08-25).
- REST paging on `/wql/v1/data`: 10,000 rows/page, 1M-row query cap, page with `offset`. Official REST specifics (2026-08-25): GET `/data` for queries under 2,048 chars; POST `/data` for 2,048-16,000 chars; results are CACHED ~30 minutes - re-query with `offset=0` to bust the cache; timeouts 30 min (query) / 5 min (page).
- `.wqlquery` files take top-level `"limit"` and `"offset"` - static strings (`"limit": "100"`) or expressions (`"limit": "<% limitParam %>"`, build-verified) - so the page can drive paging without touching the SQL.
- **WQL hierarchy/hop expansion cap: 500 hops** (build-verified 2026-09-01, UAP Role Pairing). When a data source traverses a hierarchy (e.g. security role assignments per worker), WQL silently returns an EMPTY result (no error) when the expansion exceeds 500 nodes/hops. A worker with 500+ role assignments hits this cap and their data comes back blank. Detection: guard the WQL result with `countItemsAtJsonPath("$.data[*]")` - 0 rows on a worker you know has data = cap blown. Workaround: fall back to SOAP (e.g. `Get_Roles` / `Assign_Roles`) for those workers. Flag this in the design when reading role assignments, security group memberships, or deep org hierarchies for users with large footprints.

### Dates and functions

Dates pass as ISO `'yyyy-MM-dd'` string literals in comparisons and entry parameters
(build- and sample-verified). CONFIRMED official (2026-08-25): WQL has NO date or string
functions at all - the six aggregates above are the entire function surface; dates ride
literals and FROM temporal entry parameters. Do date math in the page/flow expression
layer before binding the literal.

## Parameter binding in .wqlquery files

Two authored shapes (both detailed with full JSON in efficiency.md - the externalization
house pattern lives THERE; this is the language view):

1. **Plain-string query + `<% name %>` placeholders**, `"parameters": ["name", ...]` declared; the endpoint binds them: `wqlQuery: {queryId: "x", parameters: {name: "<% expr %>"}}`. The platform does the substitution - no `string:pathEncode`, no quote-escaping.
2. **Expression-body query** - the whole `query` is a `<% ... %>` expression whose value is a backtick template with `{{param}}` interpolation. Because the body is an expression, even FROM can be parameterized (`FROM {{appId}}_requests`) - impossible in form 1. (sample-verified across the catalog)

Also seen working: inline expression splices inside a plain-string query
(`FROM <% applicationId + '_excelFiles' %>`), and an entire WHERE clause passed as one
parameter (`<% queryWhereClause %>`) so the page assembles the predicate (build-verified).

**Injection safety:** parameter binding is TEXTUAL substitution, not typed SQL binding.
Anything user-typed that lands inside quotes (a CONTAINS search string) can break out of
the literal. Low-stakes in practice - the query still runs AS the signed-in user, so it
cannot read anything the user could not query anyway - but it can 400 the endpoint or
return the wrong rows. Sanitize search text (strip quotes) before binding, and never
splice user input into a WID-list or FROM position.

## Result shape and reference-ID gotchas

- Response: `{"total": n, "data": [ {row}, ... ]}`; a page endpoint reads `<name>.data`.
- **Instance fields return `{descriptor, id}` OBJECTS, not strings** (build-verified; pmd-gotchas #17). Storing one into a TEXT BO field 400s - use `.descriptor`. SINGLE_INSTANCE writes accept `{"id": <wid>}`.
- **WQL returns descriptor + WID, NOT textual reference IDs** (build-verified). If a downstream consumer (SOAP payload, external system) needs `Cost_Center_ID`-style reference IDs, resolve them separately (SOAP Get_References) - WQL cannot give you them.
- **In a flow, `.descriptor` on an instance field does NOT resolve via `stringAtJsonPath`** even though the raw JSON shows it - alias a flat scalar column instead (build-verified; orchestration.md).
- **(!) Subselect rows OMIT absent fields entirely - a field with no value is MISSING from the JSON, not null** (build-verified). A nested subselect (`parentField{ a, b, c }`) drops any unvalued field on that row, so a null-normalizing concat like `'' + row.b` throws `JexlArithmetic.NullOperand` and 500s the page at runtime (builds do NOT catch it - only a live read does). Elvis FIRST, operate after: `(row.b ?: '')` / `('' + (row.b ?: ''))`. Treat EVERY field read off a WQL response (top level and subselect) as possibly-absent.
- **Booleans come back as `0`/`1` in subselects** (build-verified) - normalize before comparing: `('' + (row.flag ?: '')) == '1'`.
- Aggregate/GROUP BY rows contain only the grouped fields + the aggregate alias.

## Errors and failure modes

- The endpoint response carries an `errors` array alongside `data` - the catalog wql app surfaces `<endpoint>.errors` directly (sample-verified). Many Workday 400s are valid JSON with an `error`/`errors` attribute: inspect the body.
- On a page, a failed WQL endpoint surfaces as **"Property Error found: .data"** on whatever widget reads it - that message means the CALL failed, not that your expression is wrong (build-verified).
- Common causes: missing required dataSourceFilter (400 "Specify a data source filter"); a field name not on the source; unbalanced quotes from string-spliced user input; querying a source the user lacks security for (empty or error, per the SSO auth model).
- **A large `IN (<wid>, ...)` list on a GET can blow the URL/gateway limit and return an HTML error page** (build-verified), which a downstream `.asJSON()` reader then hits as `Unexpected character '<'` - the error surfaces at the READER node, not the failed call. Send volume-scaling IN-lists via `POST /wql/v1/data` with `{"query": "..."}` in the body instead.
- Slow/huge queries: cap with LIMIT during development; the tenant logs WQL performance (WQL Performance Logs task, official-docs).

## Verified examples

All paths under `workday-extend\_reference\app-catalog\` in the Extend dev workspace
(official Workday samples - sample-verified). Construct -> source file:

1. Simple projection + ORDER BY: `SELECT workdayID, name, currency, ledgerName AS ledger, fiscalSchedule, accountSet FROM companies ORDER BY name ASC` - `createAccountingJournal\presentation\wqlQueries\companies.wqlquery`
2. Parameterized date-range predicate: `... FROM fiscalPeriods WHERE fiscalSchedule = '<%fiscalSchedule%>' AND (fiscalPeriodStartDate <= '<%fiscalPeriodDate%>' AND fiscalPeriodEndDate >= '<%fiscalPeriodDate%>')` - `createAccountingJournal\...\fiscalPeriods.wqlquery`
3. dataSourceFilter + entry parameter + nested projection: `FROM businessAssets (dataSourceFilter = businessAssetsFilterByCompanySpendCategoriesAndItems, company='<% searchCompany %>') WHERE locationOfBusinessAsset = <% searchLocation %>` - `assetBarcoding\...\getAssetsAtLocationEP.wqlquery`
4. count() + GROUP BY + WHERE ON: `SELECT crisisEvent, count() as count, followUpNeeded FROM {{applicationId}}_crisisCheckInSurveys WHERE ON crisisEvent active = true GROUP BY crisisEvent, followUpNeeded` - `crisisCheckin\...\responsesByEvent.wqlquery`
5. BP-status subselect on an app BO + ORDER BY DESC: `SELECT workdayID as requestId, businessProcesses{status, workdayID as id, businessProcessStepAwaitingAction}, ... FROM {{appId}}_tuitionReimbursementRequests WHERE worker = {{workerID}} ORDER BY creationDate DESC` - `tuitionReimbursement\...\requests.wqlquery`
6. Picker-feed aliasing + in (param) + filtered HCM source: `SELECT fullLegalName AS descriptor, workdayID AS id FROM workersForHCMReporting (dataSourceFilter = allActiveWorkers) WHERE (activeStatus = true AND manager_Level01 in (<% manager %>))` - `employeeRecognition\...\employeeSearch.wqlquery`
7. Multi-level nested projection (build-verified, first-party): `SELECT workdayID, fullName, employeeID, primaryJob { jobProfile { descriptor }, position { workdayID, descriptor }, supervisoryOrganization { manager { descriptor } } } FROM allActiveWorkers WHERE workdayID = '<wid>'` - `User Access Provisioning\v2\app_source\presentation\accessStore.pmd`
8. Worker type-ahead CONTAINS (build-verified house snippet): `SELECT workdayID AS id, preferredNameInGeneralDisplayFormat AS descriptor FROM allWorkers WHERE fullName contains '<q>'` - used in delivered apps via a deferred endpoint (pmd.md).

The `wql` and `generateWQL` catalog apps are the reference implementations for
DYNAMIC query building from a page: dataSources/fields/dataSourceFilters discovery
endpoints feeding instanceLists, a script that assembles the SELECT, and the POST-body
`{query}` execution form with an `errors`-aware results grid.

## Domain-organized data source catalog (Part B deep pass - 2026-08-27)

A domain-organized index of KNOWN WQL data source aliases drawn from build-verified
and sample-verified sources. The full tenant catalog is only accessible via
`/wql/v1/dataSources?limit=100` - this index is a starting point, not a replacement for
the live discovery API. Tiers: BV = build-verified, SV = sample-verified (App Catalog),
OD = official-docs, IT = in-tenant verified.

**Workforce / HCM:**

| Alias | Notes | Tier |
|---|---|---|
| allWorkers | All workers; type-ahead with `fullName contains` | BV |
| allActiveEmployees | Active employees only | BV |
| allActiveWorkers | Active workers (may alias allActiveEmployees in some tenants; verify) | BV |
| workersForHCMReporting | Indexed for volume reads; use with `dataSourceFilter = allActiveWorkers` | BV |
| myDirectReports | Scoped to the signed-in manager | BV |
| allActiveJobProfiles | Job profile catalog; use `dataSourceFilter = defaultFilter` | SV |

**Finance / FDM:**

| Alias | Notes | Tier |
|---|---|---|
| companies | Companies/legal entities; fields: workdayID, name, currency, ledgerName, fiscalSchedule, accountSet | SV |
| costCenters | Cost center worktag reference data | BV |
| countries | Country reference data | BV |
| fiscalPeriods | Requires entry params: fiscalSchedule + date range; use `<=` / `>=` on fiscalPeriodStartDate / fiscalPeriodEndDate | SV |
| bonusAndOne_TimePayments | Requires entry params: startDate + endDate | SV |

**Procurement / Supply Chain / Assets:**

| Alias | Notes | Tier |
|---|---|---|
| supplierInvoices | Supplier invoices | BV |
| purchaseOrders | Purchase orders | BV |
| purchaseItemsIndexed | Purchase items (indexed for performance) | BV |
| businessAssets | Fixed/business assets; requires dataSourceFilter + company entry param | SV |
| itemLot | Inventory item lots | BV |

**Support / Cases:**

| Alias | Notes | Tier |
|---|---|---|
| allCases | Help/support cases; use `dataSourceFilter = casesOpenedWithinDateRangeFilter` with startingCaseCreationDate + endingCaseCreationDate | SV |

**Security / Admin / Reporting:**

| Alias | Notes | Tier |
|---|---|---|
| allSecurityGroups | Security group reference data | BV |
| allCustomReports | Custom reports in tenant | BV |
| allWebServiceOperations | 7,221 ops in a full tenant (3,102 public / 4,119 non-public); fields include public flag, domain2, securityGroupsNeeded - use for op-to-domain mapping | IT |
| indexedReportRunHistory | Report run history (who ran what when) | SV |
| customReportsICanRun | Reports the current user has access to run | SV |
| roleBasedSecurityAuditLogLite | Role assignment delta events (grants + revokes); useful for delta-scan reconciliation flows - query with a timestamp window to detect only NEW changes since last run; yields workerId, roleId, orgId, effectiveDate, action; build-verified 2026-09-01 (UAP Role Pairing, pulled 1,000 audit rows in one call from a dev tenant) | BV |

**Prism / Analytics:**

| Alias | Notes | Tier |
|---|---|---|
| cds_<apiName> | Any published/analysis-enabled Prism dataset; project WPA_RowID as the stable key | SV |

**App BOs:**

| Alias | Notes | Tier |
|---|---|---|
| <appRefId>_<collection> | Each app's BO collections; use site.applicationId in pages / applicationId param in .wqlquery files to avoid hardcoding the ref ID | BV |

**Gotcha: App BO WQL indexing** - an app's own BO instances are NOT guaranteed to be WQL-indexed (build-verified 2026-08-25): one delivered app returned 0 WQL rows while BO REST returned all instances. Verify WQL-on-own-BO works in the target tenant before building; default to BO REST for own-BO reads (model.md).

## Cross-references

- efficiency.md (this skill) - the externalized `.wqlquery` + `queryId` house pattern, both file shapes, when to leave a query inline.
- pmd.md (this skill) - page endpoint wiring, the inline-block runtime failure, deferred WQL fetch, `cf_` fields, i18n deferred-fetch chain.
- pmd-gotchas.md (this skill) - #15 (BO REST limit vs WQL), #17 (instance fields are objects).
- orchestration.md (this skill) - WQL from flows: GET/POST forms, iterator idiom, paging components, the flow-side `.descriptor` caveat, RaaS-vs-WQL decision.
- prism-and-reporting.md (this skill) - Prism datasets as WQL sources (`cds_<apiName>`), the BP subselect, reporting-surface decisions.
- The wd-post-go-live skill owns WQL as an EXPORT path (retention/archival); the wd-auth skill owns API-client/bearer setup for external WQL calls.

## Securing domains of ANY data source - queryable, no UI needed (verified 2026-09-04)

The `allDataSources` WQL source (alias also `dataSources`) is a data source ABOUT data sources, and it
carries `domain2` = the securing domains plus `WQLAlias` to filter by the exact alias you code against:

```sql
SELECT label, dataSourceType, domain2 FROM allDataSources WHERE WQLAlias = 'learningEnrollments'
```

This replaces hunting the View Data Source task in-tenant when building an ISSG grant list - one query per
source names the delivered domains (access requires at least ONE listed domain; field-level security can
still gate individual fields, e.g. allWorkers.workdayAccount). Verified names worth keeping (a dev tenant, 2026-09):
workersFromID -> Worker Data: Current Staffing Information; allSecurityGroups -> Security Configuration (+
Security Activation); learningEnrollments -> Reports: Learning Record / Person Data: Learning / Self-Service:
Learning [NOTE: `latestSuccessfulEnrollmentFlag = true` is a PORTABLE completion filter -- no tenant-specific
status WIDs required; build-verified 2026-09-04. Gotcha: `learningContent` returns MULTIPLE rows per course
title (offerings/versions) -- store the course WID + title snapshot in your admin picker, never just the title];
learningContent -> Learning Access (+ Manage/Set Up variants); allBudgetDimensionByType (Plan
Dimensions) -> Set Up: Adaptive Planning; allJobProfiles -> Job Information; supervisoryOrganizations ->
Manage: Supervisory Organization; costCenters -> Manage: Cost Center; companies -> Manage: Company;
customOrganizations -> Manage: Custom Organization. Also on allDataSources: `securityGroupsNeeded`,
`reportFields`, `isIndexedDataSource`, `built_InPrompts` - a full metadata surface.
