# Analytics / Reporting / Prism: the delivery-surface design bridge - solution playbook

Analytics is not a config DOMAIN like HCM or Financials - it is the DELIVERY SURFACE that
reports on every other domain's data. This playbook is the DOMAIN DESIGN bridge: given an
analytics/reporting need, which surface fits it, which data source feeds it, and the config
spine + gotchas that break a naive design. It does NOT own BUILD CRAFT - authoring a
`.report`, a Prism pipeline, a calculated field, or a WQL query is owned by wd-extend-dev
(`prism-and-reporting.md`, `report-writer-admin.md`, `wql.md`); this file CITES those, it
does not re-document them. Config facts below are doc-sourced [DS] (Workday Education course
manuals + Workday Admin Guide (Reporting & Analytics), 2026-08; verify in-tenant);
build-verified [BV] and sample-verified items are tagged where the suite confirms them.

## 1. Configuration spine

### Reporting (Report Writer surface)

- Object model: **PBO** (Primary Business Object; instances = rows) + **RBO** (Related BO,
  1:1 or 1:M) + **CRF** (Class Report Fields) + **Report Data Source (RDS)** = a view/filter
  onto a PBO. [DS] Full model in wd-extend-dev `report-writer-admin.md` - do not restate.
- **The PBO is LOCKED once chosen** - you can swap data sources only WITHIN the same PBO;
  wrong PBO = rebuild. This is the day-one reporting decision (mirror of the "staffing model
  is one-way" class of landmine). [DS]
- Report types drive the surface: **Advanced** (RBOs, filters, charts, shareable, and the
  ONLY type exposable as RaaS - the default workhorse) | Matrix (group/summarize/drill) |
  Composite (multiple matrix subreports) | Search (facets) | Simple (NOT shareable) | nBox /
  Trending / Transposed. Pick the type from what the consumer must DO with it. [DS]
- **Calculated fields** are the computed-column layer for reports and Extend BOs alike; the
  calc-field TYPE SELECTOR for Extend BOs is wd-extend-dev `model.md`, tenant authoring is
  `report-writer-admin.md`. Design decision only: WHICH number needs a calc field, and where
  it should evaluate (see the Prism-vs-report evaluation-time gotcha in section 4).
- **Custom Report Data Sources**: Standard | Indexed (Workers for HCM Reporting, Journal
  Lines for Financial Reporting, etc. - optimized for volume filter/group/facet) | Business
  View (blends component sources) | Prism (user-created, blends non-Workday data). The
  manual's rule: choose the source returning the SMALLEST dataset that still holds all needed
  data. [DS]
- **RaaS exposure (report-as-a-service)**: an Advanced report + "Enable As Web Service"
  becomes a callable JSON/CSV/XML endpoint - the outbound reporting workhorse. Mind the
  ~2083-char report-URL guard (wd-extend-dev `orchestration.md`). [BV guard]

### Prism (datasets, pipelines, published data sources)

- A Prism deliverable is a **pipeline** authored in Prism, not in Extend source: **Sources**
  (Workday Data Source / DCT / file load / Data In) -> **Stages/transforms** (the 7-stage
  catalog: Filter, Group By, Join, Manage Fields, Union, Explode, Unpivot - there is NO
  Pivot stage) + **derived fields** (calculated columns; evaluate at PUBLISH time) ->
  **Publish** to a **Published Data Source (PDS)** -> **Refresh** (manual / schedule /
  dependent schedule / BP service). [DS] Full build workstream in wd-extend-dev
  `prism-and-reporting.md`.
- **Data-change tasks (DCT)** = source + parsing + a PRE-EXISTING target table + operation
  (Insert / Truncate and Insert / Update / Upsert / Delete) + field mapping; ONE active
  schedule per DCT; a DCT cannot run concurrently with itself. Pick Insert vs Truncate-and-
  Insert deliberately per feed for idempotent reloads. [DS/BV lock]
- **Accounting Center** is Prism-based external accounting (ingest -> enrich -> detailed
  accounting -> summarize -> post journals). It is a FINANCIALS config surface, not an
  analytics build - see `financials.md` (section on Accounting Center) for its spine and hard
  limits; this playbook only notes it as the canonical "Prism table feeds a domain process"
  case.
- **Data blending**: Prism is the sanctioned place to join Workday data with external data
  (Business View blends inside Report Writer; Prism blends non-Workday sources). Blend in the
  pipeline, publish once, read the result everywhere - do not re-blend per report/page.
- **API names are immutable after creation** (they key tenant-portable loads); display names
  <=255 chars, unique case-insensitive, cannot start with `WPA_`. A day-one naming decision. [DS]

### Data-source choice - RaaS vs WQL vs LDQ (the design fork)

The single most load-bearing analytics DESIGN decision is which read path feeds the surface:

| Need | Source | Note |
|---|---|---|
| Delivered, printable, scheduled, exportable report finance/ops already run; outbound extract | **RaaS** (Advanced report + Enable As Web Service) | the outbound workhorse; ~2083-char URL guard |
| Targeted filtered slice, joins across BOs/app data, automation-friendly, in-page grids/tiles | **WQL** | auto-authenticated in a flow via the ISU; SSO-scoped from a page |
| BI-tool destination, SQL-shaped bulk/aggregate reads, external analytics stack | **LDQ / Data Cloud** (Legacy Data Query = SQL via JDBC/Python; Data Lake/Data Connect) | Early Access as of 2026-06-02, GA later 2026 - **verify GA before client use** |
| Heavy transforms, multi-source blends, thresholds, period math, large volumes | **Prism** pipeline, then surface the PDS | compute once for everyone |

- **Auto-published / delivered WQL sources** exist for most domains and are the fast read
  path: `allWorkers`, `allActiveEmployees`, `workersForHCMReporting` (indexed;
  `dataSourceFilter = allActiveWorkers`), `companies`, `costCenters`, `supplierInvoices`,
  `purchaseOrders`, `purchaseItemsIndexed`, `allCustomReports`, `allSecurityGroups`,
  `indexedReportRunHistory`, etc. [BV/SV - full catalog in wd-extend-dev `wql.md`]. A
  published/analysis-enabled Prism source is addressable as **`cds_<apiName>`** with
  **`WPA_RowID as id`** as the stable key. [SV]
- **Rule of thumb**: compute cheap per-row/per-session logic in the page (WQL); compute
  expensive cross-source pre-aggregated logic in Prism; use RaaS for the scheduled/printable/
  outbound artifact; reach for LDQ/Data Cloud only for a SQL/BI-tool destination (and only
  once GA is confirmed). Do NOT stand up a Prism pipeline for a rollup a single WQL query
  returns fast; do NOT rebuild in PMD script what a Prism pipeline materializes once.

### Delivery surfaces (where the numbers land)

- **In-app Extend view** - WQL/BO-backed grids, tiles, and chart widgets on a PMD page: use
  when the numbers drive an ACTION in the workflow (comment, attest, approve, write back).
- **Prism discovery board / dashboard / worksheets** - standalone exploratory analytics,
  slice/dice, self-serve, no workflow: use when the client just needs to LOOK. If that is the
  whole ask, do not build an Extend page for it.
- **Report / RaaS output** - the scheduled, bursted, printable, or integration-consumed
  artifact.
- Both: Prism computes + a discovery board for analysts WHILE Extend surfaces the same PDS
  in-workflow for the actors who must act. Two front ends, one PDS.

## 2. Technical surface

Ground the build surface in the suite's OWN references (cite, do not re-document):

- **Reporting / calc fields / dashboards / worklets / RaaS authoring** -> wd-extend-dev
  `report-writer-admin.md` (PBO/RBO/CRF/RDS model, report types, filters/subfilters/prompts,
  the HARD LIMITS table, calc-field authoring, scheduling/bursting/dashboards). [DS]
- **Prism pipelines, PDS, DCT, load-in/read-back wiring, Prism limits, Prism security** ->
  wd-extend-dev `prism-and-reporting.md` - the BUILD OWNER for the analytics workstream
  (decision guide, dataset design, `cds_<apiName>` WQL read, fileContainers -> DCT write,
  Materialize API, LOE-flag "two platforms, two estimates", four-layer PDS security). [DS +
  sample-verified]
- **WQL call mechanics, delivered-source catalog, `dataSources`/`fields`/`dataSourceFilters`
  discovery, `cds_<apiName>` naming** -> wd-extend-dev `wql.md`. [BV]
- **REST surface** -> wd-extend-dev `rest-api-catalog.md`: **prismAnalytics v3** (Tables,
  Buckets, Data Changes; the classic wBucket flow, ~21 ops) and **wql v1** (`data`,
  `dataSources`; ~8 ops). Gateway split: bulk/long Prism/WQL work goes to the tenanted host,
  never `api.workday.com`. [BV snapshot 2026-07-27]
- **Load-in / read-out decision map** -> wd-extend-dev `data-loading-and-retrieval.md`: own-app
  BO reads default to BO REST (WQL does not reliably index app BOs); >~100 rows / analytics /
  extract -> RaaS or Prism, never an unbounded page read. [BV]
- **WD Data Cloud / LDQ (Legacy Data Query) facts** - the suite records these under the memory
  reference `reference_wd_data_cloud_ldq` and in `prism-and-reporting.md`'s decision guide
  (LDQ = SQL via JDBC/Python; Data Lake = curated unified view; Data Connect = Apache Iceberg
  zero-copy to AWS/Snowflake/Databricks). Early Access as of 2026-06-02, GA planned later
  2026 - **confirm GA and in-tenant availability before any load-bearing design.** [DS,
  verify-GA]

Load/refresh hooks worth knowing at design time (detail lives in `prism-and-reporting.md`):

- Two BP services - **Publish Prism Dataset Service** and **Execute Prism Data Change
  Service** - run as Business Process steps, so an Extend Model BP can synchronously refresh
  Prism before a downstream step reads it. DCTs with direct file-upload sources CANNOT run as
  BP steps (SFTP-source ones can). [DS]
- Load INTO Prism from an orchestration: fileContainers -> files (multipart, gzip'd CSV) ->
  dataChanges/activities (sample-proven today) OR the Prism Tables Materialize API (absent
  from the sample catalog - **verify GA**). [SV / verify-GA]

## 3. Solution patterns + donors

**Donor honesty (mirror recruiting.md).** The suite has build-verified donors for the
Prism-in-Extend WIRING, but NOT for pure Report Writer / calc-field / RaaS authoring - that is
tenant configuration, not liftable app source. Where no build-verified donor exists, this
section says so rather than inventing one.

- **Prism result read into an Extend app** (the surface-the-numbers pattern) - publish/
  analysis-enable the PDS, read it in WQL as `cds_<apiName>` (project `WPA_RowID as id`), bind
  to a grid/tile/chart widget. Build-verified donors: `prismAndExtendDesignPatterns` (cds_
  table reads, single-threaded DCT status lock, `install.orchestration` self-provisioning) and
  `salesCommission` (DCT execution via the typed SendPrismRequest node). [BV - both cited in
  `financials.md` and `prism-and-reporting.md`.]
- **Extend writes INTO Prism** (feed a dataset from an app/orchestration) - fileContainers ->
  gzip'd CSV files -> DCT choreography; gate any user-launchable load on a DCT status poll
  (read `$.state.descriptor`, enable on `Success`/`Failed`) so a second run cannot start
  mid-flight. Same donors as above (sample-verified choreography in `prism-and-reporting.md`). [SV]
- **Prism computes + Extend routes the result** (the split-platform reporting app) - Prism
  ingests + computes + applies thresholds + publishes a PDS; Extend routes the result (inbox
  task -> dashboard), captures commentary/attestation, serves the reporting view. This is a
  TWO-platform, TWO-estimate shape - size the Prism pipeline separately (LOE flag in
  `prism-and-reporting.md`). No single lift-and-reuse donor covers both halves; assemble from
  the Prism-wiring donors above + the relevant domain playbook for the source data. [pattern]
- **RaaS-driven outbound extract** (delivered/custom report -> file out) - the generic shape
  is RaaS -> CsvFormat -> sequenced filename; the build-verified O4I donor for the OUTBOUND
  file mechanics is `employeeDemographicOutbound` (cited in `hcm-core.md`) - NOT an analytics-
  specific donor, but the RaaS-to-file shape transfers directly. No reporting-specific
  build-verified donor is on disk. [BV mechanics, no domain-specific donor]
- **Report/calc-field authoring itself** - NO reusable app donor; this is tenant config authored
  per wd-extend-dev `report-writer-admin.md`. Do not present a "reporting donor" - there isn't
  one; the reusable IP is the method, not a file. [honest gap]
- **Accounting Center / Prism external accounting feed** - AC is configuration, not custom
  build; the custom surface is the FEED. See `financials.md` (Accounting Center) for the spine
  and the same `prismAndExtendDesignPatterns` / `salesCommission` donors. [cross-domain]

## 4. Design gotchas

- **Analytics is a surface, not a domain** - there is no "analytics data" to load; you report
  ON another domain's data. Always pair this playbook with the SOURCE domain's playbook to know
  what the numbers actually mean and where they live.
- **PBO locks once chosen** (reporting) and **Prism API names are immutable after creation** -
  both are day-one decisions that force a rebuild if wrong. Decide the PBO and the PDS grain
  before authoring.
- **Prism calc fields evaluate at PUBLISH time; Workday report calc fields evaluate at report
  RUNTIME.** Prefer Prism calc fields for performance; keep report-side calc fields for
  percentages and lookup/rollup formats. Putting the same number in both places at different
  evaluation times is a classic disagreement source. [DS]
- **Two tiles that should agree but do not = inconsistent calc methodology, not bad data** -
  different grain, date basis (post vs effective date), filter/null handling, or one reading a
  stale snapshot. Pin both to the same as-of date and the same canonical metric definition
  before suspecting the source. Maintain a certified-metric register so five reports do not
  compute net revenue / FTE / burn rate five different ways. [pattern]
- **The Extend view is only as fresh as the last pipeline run** - a snapshot app MUST show the
  "as of" date (the last-successful-publish UTC timestamp) so users do not read stale numbers
  as live. Test the refresh cadence, not just a single load. [DS]
- **Prism security is layered and separate from Extend/BO security** - a user who can open the
  page can still get EMPTY results if the PDS is not granted to their group (four-layer PDS
  security: data-source domains, row-level Securing Entities, field-level, field-value-level).
  Data Catalog access is UNCONSTRAINED (viewer/editor sees ALL rows), and creating a
  table/dataset from a Workday report STRIPS the source BOs' security - re-apply at the PDS.
  Never treat Catalog sharing as data security. Route the end-user model to wd-deployment. [DS]
- **App BOs are NOT guaranteed WQL-indexed** - if the analytics surface reads an Extend app's
  own BO, verify WQL returns rows in the target tenant BEFORE building on it; default to BO
  REST for own-BO reads (wd-extend-dev `wql.md` / `model.md`). [BV]
- **RaaS report URLs hit the ~2083-char guard**; large PDS/WQL reads hit paging limits -
  pre-aggregate in Prism to keep the Extend read small, and page appropriately. Do not build an
  unbounded page read for an extract. [BV]
- **LDQ / Data Cloud is Early Access, not GA (as of 2026-06-02)** - do not design a client
  solution on it without confirming GA and in-tenant provisioning; the Jul 2026 Reporting &
  Analytics admin guide is silent on Materialize / Data In / LDQ, which keeps these verify-GA
  flags in place. [DS, verify-GA]
- **Prism enablement is a lead-time item** - it needs a Workday Tenant Management case + Setup
  Feature request to provision hardware, and objects migrate via Object Transporter (OX). Flag
  it in the estimate; it is not a same-sprint switch. [DS]
- **Verify the tenant actually HOLDS the source data before designing on it** - a bare dev
  tenant will not, and an empty WQL/RaaS/Prism result usually means missing tenant data, not a
  broken query. Trust-but-verify (wd-extend-lifecycle/references/verify-in-tenant.md).

Cross-refs: wd-extend-dev is the BUILD OWNER for everything technical here -
`prism-and-reporting.md` (Prism pipelines + Prism-in-Extend wiring + Prism limits/security),
`report-writer-admin.md` (report/calc-field/dashboard authoring), `wql.md` (WQL + delivered
source catalog + `cds_<apiName>`), `rest-api-catalog.md` (prismAnalytics v3 / wql v1),
`data-loading-and-retrieval.md` (load-in/read-out map); `reference_wd_data_cloud_ldq` (LDQ /
Data Cloud facts, verify-GA). Domain source data: pair with the relevant playbook in this skill
(e.g. `financials.md` for Accounting Center + journal reporting, `hcm-core.md` for worker
reporting). wd-deployment owns the end-user Prism/report security model.

Functional literacy (what a report / calc field / Prism dataset / discovery board IS, the
reporting vocabulary) lives in wd-discovery `functional-analytics.md` - this playbook assumes it.
