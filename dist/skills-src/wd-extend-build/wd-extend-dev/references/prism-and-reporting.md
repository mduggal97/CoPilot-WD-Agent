# Prism & reporting - building the analytics side as a delivery workstream

Most Extend apps also have a *reporting* question: "where do users see the numbers, and how do we compute them?" Historically that surfaced only as a discovery item and an export target. This reference is the **build home** for it - deciding the surface, designing the Prism datasets, wiring Prism -> WQL -> Extend, and sizing the effort. Export/retention of finished data is a different job -> [wd-post-go-live/references/data-retention-export.md].

## Decision guide - where should the numbers live?

Pick the surface by who consumes it, how heavy the math is, and where the data already sits.

| Situation | Use |
|---|---|
| App's own screens need a small aggregate/rollup over the app's BOs (counts, totals, status tiles) | **In-app view** - WQL-backed grid/tiles computed on the page (see efficiency.md #2 compute-once) |
| Targeted filtered slice, joins across app BOs, automation-friendly | **WQL** query (externalize per efficiency.md #1) |
| Delivered, printable, scheduled, or exportable report that finance/ops already know how to run | **Delivered custom report / RaaS** (report-writer effort; promotes separately - wd-deployment) |
| Heavy transforms, multi-source joins/blends, thresholds, period-over-period math, large volumes | **Prism** - compute in a pipeline, then surface the result |
| BI-tool destination, SQL-shaped bulk/aggregate reads | **LDQ / Data Lake / Data Connect** (Early Access as of 2026-06-02; GA planned later 2026 - see release-impact.md; LDQ = SQL via JDBC/Python; Data Lake = curated unified view; Data Connect = Apache Iceberg zero-copy connectors to AWS/Snowflake/Databricks) |

Rule of thumb: **compute cheap, per-row, per-session logic in the page; compute expensive, cross-source, pre-aggregated logic in Prism** and let Extend read the result. Don't rebuild in PMD script what a Prism pipeline can materialize once for everyone. Don't stand up a Prism pipeline for a rollup a single WQL query already returns fast.

> *Example (client-neutral framing):* the Budget Variance app splits exactly this way - **Prism** ingests actuals + budget after close, computes variances and applies the company threshold and publishes them as a data source; **Extend** routes the result (inbox task -> dashboard), captures commentary/attestation, and serves the reporting view. Two platforms, two skill sets - see LOE below.

## Prism dataset design (the build)

A Prism deliverable is a **pipeline**, authored in Prism, not in Extend source:

1. **Sources** - where raw data lands: Workday data via a **Data Source** (report/WQL-backed) or Data Change Task; external data via **file load** (CSV/gzip) or, if enabled, **Data In** (Iceberg/Snowflake-landed external table joined without a physical copy - verify GA). Keep one source per feed; don't overload.
2. **Stages / transforms** - the transform graph: joins, unions, filters, group-by aggregations, and **derived fields** (calculated columns - variance, threshold flags, period labels). This is where the analytical math lives; name stages descriptively and comment intent, same KT bar as code (standards.md).
3. **Publish** - the output **Published Data Source (PDS)** that downstream consumers read. Decide grain (row level vs pre-aggregated to the reporting node) at design time - it drives everything downstream.
4. **Refresh** - how the pipeline re-runs (scheduled after close, event-driven, or on-demand) and whether it's full-refresh (TruncateAndInsert) or incremental (Insert). Snapshot vs real-time is a **design decision** - most finance pipelines are post-close snapshots, not live.

### Idempotent reloads + schema drift (pattern from a community data-sync skill - apply, not Workday-verified)

A dataset that reloads on a schedule has to survive both re-runs and a source that changes shape underneath it. Design for both up front:

- **Idempotency - a re-run must never double the data.** A full-refresh feed uses replace semantics (**TruncateAndInsert**, above) so re-running overwrites rather than appends. An incremental feed (**Insert**) must carry a **dedupe / business key** so a replayed or overlapping batch updates-or-ignores instead of inserting duplicate rows. This maps onto the already-verified `operation: Insert|TruncateAndInsert` choice - pick it deliberately per feed, don't default to Insert on a feed that can re-run.
- **Schema drift - catch a changed source before it lands.** When the source adds, renames, or drops a column between loads, fail loud rather than load silently: a **renamed** column loads as NULLs and a **dropped** one breaks a downstream derived field, and neither throws on its own. Bake a header / field-set check into the loader that compares the incoming shape to the expected schema and stops on mismatch - same bar as the reconciler (data-conversion.md #5).

### Canonical metrics - don't redefine the number (pattern from a community data-catalog skill)

Before adding a **derived field** or a report that computes net revenue, FTE, days-cash-on-hand, grant burn rate, and the like, check whether an **approved canonical definition already exists**. Maintain a small **certified-metric register** - name, plain-English definition, exact formula + grain, owner - and derive from it so five reports don't compute the same metric five different ways. A genuinely new metric gets **added to the register and reused**, not reinvented per report. This is the analytics twin of the design-doc open-items discipline: one agreed definition, referenced everywhere.

Publish/refresh mechanics (per Workday Admin Guide (Reporting & Analytics), Jul 2026):

- Two paths to a Prism Data Source: **dataset -> Publish** (Prism Datasets: Publish domain) or **table -> "Enable for Analysis"** checkbox. PDS name = display name.
- Refresh triggers: manual, recurring schedule, **dependent schedule** (fires on completion of another Prism process, optional delay - chain ingest->publish), and two BP services - **Publish Prism Dataset Service** and **Execute Prism Data Change Service** - runnable as Business Process steps with a cancel-on-failure option. An Extend Model BP can therefore synchronously refresh Prism before downstream steps read it. Restrictions: DCTs with direct file-upload sources can't run as BP steps (SFTP-source ones can); a dataset can't have overlapping publishes.
- The **last-successful-publish timestamp (UTC)** on publish status is the system-of-record for the "show the as-of date" rule below. Monitoring: Prism Management Console (rolling 180-day dashboard), Prism Activities Monitor, Data Catalog activity tabs.
- Naming: display names <=255 chars, unique case-insensitive, can't start with `WPA_`; **API names are immutable after creation** - pick deliberately (they key tenant-portable loads).
- Delivered DCT connections (Prism pulls directly - no middleware leg): S3, Redshift, Azure Blob/Synapse, BigQuery, GCS, Salesforce, Snowflake, SFTP.
- Tenant enablement requires a **Workday Tenant Management case + Setup Feature request** to provision Prism hardware - a lead-time item. Prism objects migrate via **Object Transporter (OX)**.

Load path INTO Prism from an orchestration: **Prism Tables Materialize API** - `POST /api/prismAnalytics/v3/tables/materialize` `{source, target, operation: Insert|TruncateAndInsert}`, keyed by apiName (tenant-portable, auto callback -> no timeout risk). Cleaner than the fileContainers + DCT bucket->gzip-CSV choreography. Both documented in orchestration.md ("Newer capabilities"); **verify GA/current before client use** (DevCon 2026 preview era). Note: the Jul 2026 Reporting & Analytics admin guide has **no mention** of Materialize, Data In/Iceberg, Export Prism Artifacts, or LDQ - its silence keeps these verify-GA flags in place (canonical operation names match what we recorded).

## Getting Prism data into an Extend app

Extend does not read Prism directly by default - you make the Prism output WQL-addressable, then query it like any other WQL source:

- **Publish/expose the dataset to WQL** (and/or bundle Prism tables/datasets/DCTs into the app via the **Export Prism Artifacts** task - "Prism artifacts in Extend"; **verify GA/current**). Once a PDS is WQL-queryable, an Extend endpoint reads it with `baseUrlType: "workday-wql"` exactly like a BO-backed query - externalize it per efficiency.md #1.
- **In the page**, treat the Prism result as a read-only data source: WQL-backed grids, tiles, and **chart widgets**; filter/aggregate further in `onLoad` with the compute-once pattern (efficiency.md #2). Prism owns the heavy math; the page owns presentation and light per-session filtering.
- **From an orchestration**, query the PDS via WQL for routing/branch logic (e.g., only create a task when a threshold flag is set), same POST `/wql/v1/data` pattern as orchestration.md.

### Sample-verified load & wiring details (per Workday App Catalog samples)

Official sample apps confirm the WQL read naming and the file-based load path (sample-verified - above doc-sourced, below build-verified):

- **WQL source naming for a Prism source:** a published / analysis-enabled Prism source is addressable in WQL as **`cds_<apiName>`**, and its row key projects as **`WPA_RowID as id`** - use that as the stable id when reading a PDS into an Extend grid/endpoint.
- **WQL inline BP subselect (confirmed 2026-08-07, `tuitionReimbursement/presentation/wqlQueries/requests.wqlquery`):** read a business-process's status and awaiting-action step straight off an app BO in ONE query with a nested subselect - `SELECT workdayID as requestId, businessProcesses{status, workdayID as id, businessProcessStepAwaitingAction}, ... FROM {{appId}}_<collection>`. Solves the common "show me the approval status/step in a grid" without a second call.
- **File-load DCT choreography (now DOUBLY sample-verified):** load into Prism from an orchestration via **fileContainers -> files (multipart, gzip'd CSV) -> dataChanges/activities** - create a file container, POST the gzipped CSV as a multipart `files` part, then drive a Data Change Task's dataChanges/activities to apply it. The **Prism Materialize API STAYS verify-GA** - it is absent from the entire sample catalog, so the file-bucket path is the sample-proven one today.
- **Fold helpers for the CSV body:** build the upload with **`FormattedCsvFoldValue`** (Aggregate/fold to formatted CSV) and compress with the **`.gzip()`** helper before POSTing to the file container (orchestration-side fold taxonomy in orchestration.md).
- **Single-threaded DCT governance lock:** a DCT cannot run concurrently with itself - samples gate the launch button on a status poll of the run: read **`$.state.descriptor`** and enable/lock the button on **`Success` / `Failed`** so a second run can't start mid-flight. Bake this into any user-launchable Prism load.
- **Self-provisioning via `install.orchestration`:** a sample stands up its own Prism target table at install time from a flow - **`POST /api/prismAnalytics/v3/tables`** with the schema JSON - so the app creates its table without manual Prism setup (distinct from the `/tables/materialize` load endpoint above).

## Extend analytics surface vs. Prism dashboard - pick the front end

| Want | Build |
|---|---|
| Numbers inside the app's workflow (a task, a request screen, a manager's action page), with app navigation and BP integration | **Extend page** - WQL/BO grids + chart widgets, actions wired to the BP |
| Standalone exploratory analytics, slice/dice, self-serve, no workflow | **Prism discovery board / dashboard** (Workday reporting surface - lives outside the Extend app) |
| Both | Prism computes + a discovery board for analysts; Extend surfaces the same PDS in-workflow for the actors who must act on it |

If the client just needs to *look at* analytics, a Prism discovery board may be the whole answer - don't build an Extend page for it. Extend earns its place when the numbers drive an **action** (comment, attest, approve, write back).

### Which metrics - and why they disagree (pattern from a community KPI-dashboard skill)

- **Decision-driving vs vanity.** Put a metric on a surface only if someone changes a decision based on it. "Total logins", "records created", running counts and the like look impressive but drive nothing - they cost pipeline + page real estate and dilute the numbers that matter. Filter the KPI list to what an actor will actually act on (the same "does it drive an action" test that decides whether analytics belong in Extend vs a discovery board, above).
- **Contradiction debugging.** When two tiles or reports that *should* agree don't, the cause is almost always **inconsistent calc methodology, not bad data** - different grain, different date basis (post vs effective date), different filter / null handling, or one reading a stale snapshot. Routine: pin both to the same **as-of date**, confirm both resolve the metric to the **same canonical definition** (register above), then compare grain and filters - suspect the source last, not first.

## Build workstream shape + LOE signal

**Flag for wd-estimate: Prism/reporting is a distinct skill set - two platforms, two estimates.** An Extend+Prism app is not one workstream sized by Extend hours. The Prism side (source config, transform graph, derived fields, publish, refresh scheduling, load integration) is separate design + build + test effort, typically a **Prism/reporting developer**, not the Extend developer. Common miss: sizing only the Extend pages and treating "and it reads from Prism" as a line item. Size the pipeline explicitly.

Workstream steps: reporting requirements in discovery (wd-discovery) -> dataset/grain decisions + surface choice in design (wd-design-doc; add the datasets and the reporting grain to the object model / a reporting tab) -> Prism pipeline build in parallel with Extend build -> publish to WQL -> wire Extend endpoints -> joint test. Calibrate wd-estimate to carry a Prism line whenever the app has a reporting/analytics ask.

## Testing, refresh, security

- **Test the pipeline as data, not as clicks:** validate transform output against a known source extract (row counts, aggregate totals, threshold/derived-field correctness) before wiring the front end. A wrong derived field is a silent, everyone-sees-it defect. Once the PDS is WQL-addressable, the counts/totals are machine-checkable live via tenant-ops WQL against the source extract (references/tenant-ops.md). For the full reconcile-and-verdict discipline on a Prism load (counts + control totals + sample-value check + pass/fail + variance explanation), reuse the reconciliation harness owned by data-conversion.md #5 - a Prism load reconciles the same way a BO conversion does.
- **Refresh coupling:** the Extend view is only as fresh as the last pipeline run - a snapshot app must show the "as of" date so users don't read stale numbers as live. Test the refresh cadence, not just a single load.
- **Security is layered - grant and test both sides:** Extend/BO data uses security domains (the S22 grant - model.md); the Prism side is **four-layer on the PDS** (per Workday Admin Guide (Reporting & Analytics), Jul 2026): data-source domains, row-level via **Securing Entities**, field-level domains, and field-value-level - if none configured, **Prism: Default to Dataset Access** applies (contextual on the underlying object). A user who can open the page can still get empty results if the PDS isn't granted to their group. Never put confidential figures in a surface whose Prism security is broader than intended.
- **Data Catalog access is unconstrained:** anyone who can view/edit a table/dataset sees ALL rows/fields, and creating a table/dataset from a Workday report **strips the source BOs' security domains** - security is only re-applied at the PDS (Edit Data Source Security). Never treat Catalog sharing as data security. DCTs have no direct ACL - access derives from target-table permissions compatible with the operation, plus view on the source. **Relax Sharing Rules** is the sanctioned pattern for a filtered dataset over a sensitive table (consumers don't need upstream-lineage permissions).
- **Domain inventory for design docs:** Prism: Tables Create / Manage / Owner Manage; Prism Datasets: Create / Manage / Owner Manage / Publish; Prism: Manage Data Source; Manage Relax Sharing; Manage File Containers; Manage Connection. Object sharing: Viewer/Editor/Owner + Can Insert/Update/Delete/Truncate Table Data.
- **Volumes:** large PDS reads still hit WQL paging limits (orchestration.md) - page appropriately; pre-aggregate in Prism to keep the Extend read small.

## Prism limits (per Workday Admin Guide (Reporting & Analytics), Jul 2026)

- **Ingest:** single file 256 MB compressed (bucket/REST/DCT; UI base-dataset upload 500 MB); 24,000 buckets and 24,000 DCT activities per rolling 24 h; 10 concurrent uploads; 50,000 files / 125 GB compressed per 24 h; 1,000 fields max per table and per published dataset; Text <=32,000 chars; row <=500,000 chars; DCT auto-retries 3x.
- **Report-as-source:** report must be advanced, web-service-enabled, and have the **"Enable for Prism"** checkbox; fails >30M rows; no business-view sources; **no effective dating** (current-time only); custom-object multi-instance fields land NULL; currency fields need Show Currency Column.
- **Consumption:** a PDS supports only advanced/composite/matrix/simple/transposed report types; background reports on a PDS <=1M rows; a PDS returns <=512 MB; a table >2B rows makes the PDS unusable in discovery-board vizzes/worklets; matrix on a PDS 40M rows background.
- **Reportable-rows entitlement:** Data Catalog > Prism Usage shows total reportable rows vs the purchase agreement - every physical row of a published dataset / analysis-enabled table counts. Pre-aggregating in the pipeline (already the recommendation here) also reduces entitlement consumption.

## Boundaries - what this reference does NOT own

- **Exporting/retaining finished Prism or BO data** (RaaS/WQL/LDQ/Materialize export paths, data-lake archival, purge design) -> [wd-post-go-live/references/data-retention-export.md]. This file is about *building/serving* analytics; that one is about *getting it out and aging it*.
- **LDQ / Data Cloud SQL details and GA status** -> reference_wd_data_cloud_ldq (and data-retention-export.md's LDQ entry). Cite it; don't restate.
- **WQL/RaaS call mechanics in orchestrations** -> orchestration.md ("Reading data at scale", Materialize).
- **Design-doc tab format** for the reporting/object-model content -> wd-design-doc.
- **Office/chart file mechanics** (a delivered .xlsx report artifact) -> xlsx skill.

## Prism administration facts (doc-sourced, Workday education manuals 2026-08)

doc-sourced - Workday Education course manuals (public), crawled 2026-08-25; cite: "Prism Analytics for
Administrators". Doc-tier facts: verify in-tenant before load-bearing use.

- **Prism Access Security Group requirement:** Prism domains accept only certain group types -
  all UNCONSTRAINED types, ROLE-BASED CONSTRAINED, aggregation-of-role-based, and
  intersection-of-role-based. NOT supported: job-based, segment-based, miscellaneous org-based,
  Manager's Manager. Plan the client's Prism admin/consumer groups around this before designing
  the security model - a job-based or segment-based group simply cannot hold Prism access.
- **Row-level security** on a published data source = **Securing Entities**: role-enabled instance
  fields in the dataset (e.g. a Company or Cost Center field) that Workday matches against the
  user's role assignments. Configure via **Edit Data Source Security**.
- **1,000 published fields max** per Prism data source (and 1,000 fields per table; WPA_* system
  fields excluded from the count).
- **Publish timeout: 24 hours**; a dataset cannot have overlapping publishes.
- **Republish required after schema OR security changes** - editing Securing Entities/domains or the
  dataset shape does nothing for consumers until the dataset is published again.
- **Data-acquisition basics:** file upload caps at 256 MB (CSV/TXT); custom-report ingestion requires
  advanced type + Enable as Web Service + Enable for Prism Analytics (2 GB cap, >24h tasks cancelled);
  sFTP connections support Delete After Retrieval / Gzip decompress / PGP decrypt with limits of
  <5,000 files, <5h transfer, <1 GB compressed / <10 GB uncompressed per file. A **Data Change Task**
  = source + parsing + pre-existing target table + operation (Insert / Truncate and Insert / Update /
  Upsert / Delete) + field mapping; ONE active schedule per DCT. With data present you can
  add/delete/rename table fields but NOT change types/constraints (truncate first).
- **Contextual publishing** lets a Dataset Owner/Editor publish for testing without holding
  unconstrained publish rights (Prism Datasets: Publish domain governs real publishing).

Pipeline-authoring additions (official-docs - Workday Education course manuals ("Prism Analytics for
Administrators"), crawled 2026-08-25; spot-verify load-bearing numbers in-tenant):

- **Stage catalog (7 types):** Filter, Group By, Join, Manage Fields, Union, Explode, Unpivot. There
  is NO Pivot stage - it is on the roadmap with no availability date; workaround = Join + calculated
  fields. Unpivot caps at 150 input fields per stage. Explode removes the multi-instance field AND
  its associated report field from later stages - add a follow-up Manage Fields stage to map the new
  single-instance field to a report field (that mapping is what restricts instance prompt values).
- **Function library:** Logical CASE / COALESCE; Conversion TO_DATE / TO_STRING / TO_INT; Text TRIM /
  SUBSTRING / LENGTH / CONCAT; Date DATE_ADD / TRUNC / TODAY; Window (11): ROW_NUMBER, SUM, AVG, MIN,
  MAX, LAG, LEAD, FIRST, LAST, COUNT, RANK - window functions keep the row count (vs Group By).
  Prism calculated fields evaluate at PUBLISH time (Workday report calc fields evaluate at report
  runtime) - prefer Prism calc fields for performance; keep report-side calc fields for percentages
  and lookup/rollup formats. (!) reconcile: the manual prints `PARTITIONED BY` in window syntax where
  standard SQL uses `PARTITION BY` - verify in a tenant expression editor before quoting syntax.
- **Join/union rules:** join keys are case-sensitive and must match type; EQUALITY ONLY (no >, <, !=,
  <>, BETWEEN); multiple matches DUPLICATE rows; unions do NOT dedupe. Group By output contains ONLY
  the group-by fields + summarizations (Average/Count/Max/Min/Sum) - to keep a field, group by it.
  Memory/UI aids: Join Stage Suggestions show distinct counts, null %, match %.
- **Capacity framing (corroborates the reportable-rows entitlement note above):** published ROWS are
  contractual ("limited based on your contractual agreement with Workday"); ingestion is unlimited.
  The manual never mentions DPU/compute-unit concepts - education-materials view, not billing mechanics.
- **Ingestion corroboration:** 256 MB file upload / 2 GB report source / 24 h data-change AND publish
  timeouts / sFTP <5,000 files, <5 h transfer, <1 GB compressed or <10 GB uncompressed per file - all
  matching the admin-guide numbers above. Edit-Transformations example data table samples max 20K rows.
