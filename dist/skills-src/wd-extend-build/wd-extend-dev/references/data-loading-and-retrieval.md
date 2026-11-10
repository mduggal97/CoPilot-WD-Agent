# Data loading and retrieval - the load-in / read-out hub

The single map for getting data INTO an Extend app and reading it back OUT, at each scale,
with the landmines and the decision points. This file LINKS the detailed rules that live in
their home references (pmd-gotchas.md #N, model.md, wql.md, orchestration.md, efficiency.md,
and the wd-integration-dev / wd-tenant-config / wd-post-go-live skills) - it does not
duplicate them. It OWNS the native-Workday seed-via-EIB story (Section 2), which had no home.

Provenance: build-verified unless marked. New items carry their session date.

## 0. Decision map (start here)

**Loading IN - pick by scale and channel:**

- One record from a page -> a normal page create (outbound `onSend` POST).
- A few dozen APP-BO rows a user enters -> grid `outboundFields` (framework POSTs once per
  user-entered row; pmd.md outbound + pmd-gotchas #52/#56/#57).
- Hundreds of APP-BO rows from a page -> the VIEW-page bulk-create pattern (Section 1) +
  `?bulk=true` batches of <=100 (model.md; pmd-gotchas #6 cascading-forEach).
- Hundreds+ of APP-BO rows from a flow -> orchestration `BatchLoop` -> `?bulk=true` POST
  (orchestration.md; iterator chunk size 100).
- NATIVE Workday reference/master data (Locations, Purchase Items, Par Locations, workers,
  orgs) -> **EIB Put_* web services, NOT the app** (Section 2). The app reads this data; it
  does not create it.
- A client file in a variable format -> a DT pre-formatter -> the canonical layout an O4I
  template reads (wd-integration-dev document-transformation.md).

**Reading OUT - pick by source:**

- Your OWN app BO -> **BO REST collection GET** (WQL does NOT reliably index app BOs - A6
  below; model.md). Respect the 100-row cap.
- NATIVE Workday data into the app -> a **delivered WQL data source + a reference-field
  filter** (Section 3, N6). Empty in dev usually means missing tenant data, not a broken
  query (N5).
- More than ~100 rows / analytics / an extract -> RaaS or Prism, never an unbounded page
  read (wql.md; prism-and-reporting.md; wd-post-go-live export).

## 1. Loading IN - app BO writes (links; owns the two named patterns)

- **Grid `outboundFields` = framework POST per USER-entered row** - the reliable page-side
  create path. Pre-populated rows (via `rows`) and standalone `values`-only endpoints do NOT
  fire. See pmd.md outbound + pmd-gotchas #52.
- **Script-side `.invoke()` POSTs in `onSubmit` are TRANSACTIONAL on EDIT pages - they roll
  back when the page closes** (pmd-gotchas #52). Do NOT build imports on them.
- **PROVEN page-side BULK-create pattern (resolved 2026-08-26):** a **VIEW page** + a deferred
  POST endpoint + a source `button` carrying `commandHttpMethod: "POST"`. VIEW pages have no
  edit transaction, so deferred `.invoke()` POSTs in `onLoad` PERSIST (unlike EDIT pages).
  Full mechanics + the "POST inbound endpoint couldn't be loaded" fix: pmd-gotchas #56/#57.
  - The payload rides the endpoint's own `values` + `outboundPath` (`[{"outboundPath":"data",
    "value":"<% pageVariables.payload %>"}]`), set BEFORE `.invoke()`, called with NO argument -
    passing the body as an `.invoke()` argument is SILENTLY DROPPED (pmd-gotchas #59).
  - EDIT-grid `outboundFields` is NOT a guaranteed alternative: it has been seen to silently
    create 0 instances for a simple BO (pmd-gotchas #60) - prefer the VIEW-page pattern for a
    reliable bulk create.
- **Bulk POST** `?bulk=true` with the `{"data":[...]}` wrapper; hard cap 100/call (error
  **S25** above that). Batch from a page with the **cascading-forEach** recipe - closures
  cannot reassign an outer counter (pmd-gotchas #6; model.md bulk section).
- **Descriptor-snapshot-as-TEXT (N4, verified in two apps, 2026-08-26) - the recommended way
  to persist a reference.** Instead of a `SINGLE_INSTANCE` field, capture the referenced
  instance's WID/descriptor into a TEXT field at write time. Two wins: (a) one clean POST -
  no two-step parent/child create; (b) it sidesteps the null-SINGLE_INSTANCE-crashes-GET
  landmine (model.md / pmd-gotchas #12). Use this whenever you only need the id/label of the
  reference, not a live BO link. The parent WID snapshot then drives child reads (N6).
- **Upsert (N7, design-intent, NOT yet build-verified):** GET-before-PUT against the native
  object, with effective dating and a reactivate-if-inactive path. Treat as the intended
  idempotent-load shape for writes back to native Workday objects; build-verify before relying.
- **Active-boolean on load** - set the `active`/gate boolean explicitly on every create, or a
  filtered read hides the row with no error (model.md field-change checklist; pmd-gotchas #45).
- **Deploy CAN WIPE dev BO data** (suspected trigger: a new app version) - check, and re-seed,
  after every `wdcli app deploy` (wdcli-workflow.md).

## 2. Loading IN - native Workday seed via EIB (owns this content, NEW 2026-08-26)

A bare shared dev tenant has no native reference data, so the app's delivered-WQL reads
return empty (N5). Seed the native objects the app reads via **EIB Put_* web services** before
expecting the app to show anything.

- **Auth (N3, verified):** the Extend/wdcli **tenant token is Extend-platform-scoped and the
  general WQL/REST API rejects it** ("Invalid access token"). Seed loads and out-of-app
  reads/writes need a SEPARATELY-scoped ISU / API client, not the Extend token (wd-auth).
- **Per-object gotchas (N1, verified working smoke test):**
  - **Put_Location** - par-usage locations REQUIRE an address AND exactly ONE usage marked
    Primary=Y; do NOT send an Effective Date on create.
  - **Put_Purchase_Item** - inventory items need Base UoM `EA` + Conversion Factor `1` + a
    Stocking usage (not just Ordering), because the spend categories are stocking categories.
  - **Put_Inventory_Par_Location** - set the Item column's row-4 reference type to
    `Purchase_Item_ID` (it defaults to `Catalog_Item_ID`) and the Worktag column's row-4 to
    `Cost_Center_Reference_ID`; Par Company required; Source Inventory Site optional - omit it
    (there is no Create Inventory Site task). Layout: header fields on the first line row, then
    one row per item line (line Row ID 1..30, same Spreadsheet Key).
- **KNOWN WALL (N2, verified failure, root cause SUSPECTED, OPEN):** after the FIRST
  par-location load succeeds, every subsequent create - bulk, small batch, even a byte-identical
  single - fails with `Attempt to process an immutable Instance Data ... on: 16460$21`, and the
  collision instance is CONSTANT across runs regardless of payload. This points to a
  tenant-level locked instance, not the payload. Consequence: you can seed ONE rich par location
  and build against it, but you cannot bulk-populate this shared dev tenant. Delivered fallback:
  load large native volumes via EIB in the CLIENT tenant (once/quarter), keep the Extend UI for
  changes/exceptions - do not bulk-load native inventory through the app. Unflag if a later run
  isolates the cause.
- EIB template mechanics: wd-integration-dev eib.md. The O4I / WWS-import-framework variant of
  "load a file in" (submit -> poll Get_Import_Processes -> harvest Get_Import_Process_Messages):
  orchestration.md + the payroll-input template.
- Synthetic data only in a shared dev tenant (the no-customer-data rule) - use synthetic
  locations/items. Bulk/repeatable loads and test data: wd-tenant-config test-data.md.

## 3. Reading OUT

- **Your OWN app BO -> BO REST collection GET.** WQL is NOT guaranteed to index app-BO
  instances (A6, verified: WQL returned 0 while REST returned every row) - default to REST for
  own-BO reads. The collection `limit` is 1-100 and **silently truncates** past 100; filter
  server-side by a REFERENCE field (`?<refField>=<WID>` works) - a TEXT-field query param is
  silently ignored (model.md; pmd-gotchas #15).
- **Native Workday data -> a delivered WQL data source + a workdayID filter (N6, verified in
  production reads).** E.g. read par locations via `parLocationForMassMaintainParLocations`
  (SSO, `filterIsRequired=false`), then read that location's expected items via
  `parLocationLineForMassMaintainParItems` with `filter WHERE parLocation = <workdayID>`. The
  parent WID comes from the TEXT snapshot (N4) - a reference-field filter, so it works.
- **Empty native read != broken query (N5, verified).** Delivered-WQL pickers are
  tenant-dependent: a dev tenant may lack whole FDM dimensions (Balancing Unit / Function /
  `organizations` absent where they are client-specific) and inventory sources can be empty
  (dev `itemLot`). Verify each delivered source per tenant; seed (Section 2) or expect empty in
  dev - do not chase it as a bug. (Distinct from A6, which is about your OWN app BOs.)
- **WQL grammar / paging / functions:** wql.md (the owner). WQL returns descriptor + WID, NOT
  textual reference IDs - resolve those separately via SOAP Get_References when a downstream
  consumer needs `<Object>_ID`.
- **`instanceList` + `onSearch` still needs a seed value (N8):** a picker with `onSearch`
  fails the build unless it also carries one of `instanceList` / `values` /
  `instanceListLoopTag`; seed an empty `"values": "<% [] %>"` to satisfy it (pmd-gotchas #58).
- **At scale / export:** RaaS for large structured extracts, Prism for volume/blend
  (prism-and-reporting.md); the retention/export-out path is owned by wd-post-go-live.

## 4. Cross-cutting landmines index (one line each, links home)

- Deploy can wipe dev BO data -> check and re-seed before any read/test (wdcli-workflow.md).
- Stored-null SINGLE_INSTANCE crashes the collection GET serializer (model.md; prefer N4).
- Removing a reference field strands zombie records - use a fresh collection (model.md).
- No `.keySet()` / `.length` at runtime (pmd-gotchas #53; use `.size()`).
- `authType` must be consistent across a flow's pages; an ISU-authed read the ISU cannot see
  returns EMPTY, not an error (pmd.md; pmd-gotchas).
- Deploy flakiness -> retry then bisect (wdcli-workflow.md).
- **After a load (or before trusting "the data isn't there"), verify programmatically** - a browser "No Items" is often async or security-gated, not a true empty; confirm the native data / your BO instances with the read recipes in [tenant-state-verification.md](tenant-state-verification.md).

## 5. Where this is used across the lifecycle

- Design / data-conversion (wd-design-doc, wd-discovery): Section 0 decision map + Section 2 -
  which load channel at which scale, and will the tenant even HAVE the native data.
- Build (wd-extend-dev): Sections 1 and 3 (home).
- Testing (wd-testing, wd-test-execution): Section 2 seed + the deploy-wipes-data trap - seed
  before every test pass.
- Deployment / data-conversion (wd-deployment): Section 2 EIB seed + the N2 immutable-instance
  risk + the Extend-token-not-API-token auth trap (N3).
- Post-go-live (wd-post-go-live): Section 3 read-out at scale (RaaS/Prism/BO REST export;
  100-row cap -> offload to reporting).
- Auth preflight (wd-auth): the N3 token-scope note.
