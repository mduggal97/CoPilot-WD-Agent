# Data Platform Integration (Snowflake, Databricks, generic warehouse/lakehouse)

How a hosted tool integrates WITH a cloud data platform - connect + authenticate,
load data in bulk, read it out, keep it incremental, and the one architecture
decision that matters most: **materialize in the tool's own Postgres, or query
the warehouse live?** Practitioner overview + load-bearing gotchas. Read
patterns.md first; this specializes those patterns to Snowflake and Databricks,
with the generic principles called out so they carry to Redshift, BigQuery,
Synapse, etc.

**Version-sensitive:** connector/driver versions, auth options, and streaming
mechanisms move quickly on both platforms (e.g. Snowpipe Streaming, Databricks
OAuth M2M minimum connector versions). Pin driver versions and confirm auth
options against the current docs.

## Contents

- [1. The architecture decision - materialize vs query live](#1-the-decision)
- [Workday Data Connect - zero-copy via Iceberg (the third path)](#workday-data-connect)
- [2. Snowflake - connect and auth](#2-snowflake-auth)
- [3. Snowflake - load data in](#3-snowflake-load)
- [4. Databricks - connect and auth](#4-databricks-auth)
- [5. Databricks - load data in](#5-databricks-load)
- [6. Reading out, and reverse ETL](#6-reading-out-reverse-etl)
- [7. Incremental patterns](#7-incremental)
- [8. Generic warehouse/lakehouse principles](#8-generic)

---

## 1. The decision - materialize vs query live

Before any connection code, decide how the tool relates to the warehouse. This
is the load-bearing decision; get it wrong and you either burn warehouse compute
on every page load or serve stale data.

**Materialize into the tool's Postgres (ELT/sync, then read local).** On a
schedule (or via change feed), pull the slice the tool needs into its own RDS
Postgres (app-hosting owns that Postgres); the app reads local.

- **Choose this when:** the tool needs low-latency, high-frequency reads of a
  BOUNDED slice; the UI cannot tolerate multi-second warehouse query latency;
  you want to be insulated from warehouse availability and cost spikes; the data
  volume the tool actually touches is small relative to the warehouse.
- This is the DEFAULT for an interactive hosted tool. Postgres is already in the
  stack, sub-millisecond, and free of per-query warehouse cost.

**Query the warehouse live (federate).** The tool issues queries to Snowflake /
Databricks at request time.

- **Choose this when:** the data is too big to copy; it must be real-time-fresh;
  queries are ad-hoc/analytical over the FULL data set; or governance requires
  the data stay in the warehouse and never land in the app's Postgres.
- Cost/latency caveat: every live query spins warehouse compute (a Snowflake
  virtual warehouse, a Databricks SQL warehouse) - that is real money and
  seconds of latency PER query. Never put a live warehouse query on a hot
  interactive path without caching. Auto-suspend the compute so it does not idle
  billably.

Rule of thumb: **materialize a bounded, hot slice into Postgres for the app to
read; query live only for big, fresh, or ad-hoc analytical needs - and cache
even then.** Many tools do both: nightly materialize for the dashboard, live
query for a drill-down. Decide deliberately per data set.

A THIRD option exists when Workday is the source and the target platform pair is
covered: Workday Data Connect zero-copy sharing - see the next section before
building either path above for Workday-sourced data.

---

## Workday Data Connect - zero-copy via Iceberg (the third path)

The extract patterns in sections 2-8 below assume a hosted tool builds the
pipeline: stage files, COPY INTO, watermark-poll. When the source is Workday
itself and the target is Snowflake or Databricks, Workday's own product does
the sharing instead - no extract job, no staged files, no pipeline for the
tool to build or maintain.

**What it is.** Workday Data Cloud has three parts: **Data Lake** (Workday's
own data materialized as Apache Iceberg / Parquet tables), **Data Connect**
(the two-way zero-copy SHARING protocol on top of those Iceberg tables), and
**Live Data Query (LDQ)** (a separate always-live SQL surface over Trino/JDBC,
not Iceberg-table-based - do not conflate the two). Data Connect is the piece
that matters for this file. CONFIRMED, Workday newsroom, 2025-09-16
(https://newsroom.workday.com/2025-09-16-Workday-Introduces-Workday-Data-Cloud-to-Unlock-the-Power-of-People-and-Money-Data-and-Accelerate-AI-Powered-Innovation).

**Mechanism, inbound (Databricks/Snowflake -> Workday, "Data In").** Confirmed
via a live Workday admin guide: the customer registers an **External Catalog**
in Prism Data Catalog pointing at the source platform's **Iceberg REST catalog
endpoint** (for Databricks, literally Unity Catalog's
`/api/2.1/unity-catalog/iceberg-rest`), authenticates with **OAuth2 token
exchange** (a Databricks service principal plus a JWK certificate Workday
generates that the admin registers on the service principal's federation
policy), then Workday runs a **Schema Sync** that registers the source tables
as External Tables "without moving or copying data." CONFIRMED, doc.workday.com,
"Set Up Zero-Copy Data In with Databricks," fetched 2026-09-10
(https://doc.workday.com/admin-guide/en-us/workday-data-cloud/data-in/set-up-zero-copy-data-in-with-databricks-2.html).

**Mechanism, outbound (Workday -> Snowflake/Databricks, Data Connect proper).**
On the receiving side, Workday's Iceberg tables surface as an externally
managed table in the target's own catalog - Snowflake calls this a
**Catalog-Linked Database** under **Horizon** governance: "on the Snowflake
side, it's always an externally managed Iceberg table." CONFIRMED, Snowflake
zero-copy integrations page, fetched 2026-09-10
(https://www.snowflake.com/en/product/features/zero-copy-integrations/).
GATED - a Workday-published outbound setup guide (the mirror of the Data In
doc above) was not found in this pass; the mechanism is documented from the
receiving platform's side, not Workday's.

**Partners and dates (announcement order), all CONFIRMED via Workday newsroom.**
- Databricks, Salesforce Data Cloud, Snowflake - 2025-09-16, Rising 2025.
- Google BigQuery - 2025-11-19.
- AWS - 2026-06-02, DevCon 2026: "bi-directional, zero-copy access ... without
  shadow databases or brittle pipelines"
  (https://newsroom.workday.com/2026-06-02-Workday-Announces-Workday-Data-Cloud-Integration-with-AWS,-Giving-Developers-Direct-Access-to-Workdays-Governed-Data-Layer).

**Status as of 2026-09-10.** Early access, platform by platform - no blanket
GA yet. Snowflake: private preview, "GA planned for later in 2026" (Snowflake's
own FAQ, no quarter given) - REPORTED. AWS: "available... in early access soon"
per the 2026-06-02 release - CONFIRMED as EA-not-GA. Rising 2026 (2026-10-12 to
10-15) is the next likely GA/pricing checkpoint. Verify current status
in-tenant before committing to a client timeline.

**Enabling it - licensing signal.** Requires **Workday Data Cloud** as a
product prerequisite plus **Prism Data Catalog** access to build the
connection (CONFIRMED, same admin guide). That guide never mentions Extend -
do not assume Extend Pro gates Data Connect; Extend Pro gates a DIFFERENT
Data-Cloud-adjacent surface (agent actions / Agent-Ready Tools). UNVERIFIED
either way - confirm with the client's Workday account team at contract time.
Data Cloud draws from Workday's fungible **Flex Credits** pool alongside
agents (REPORTED, Workday usage-based-pricing materials); no published
per-call/per-GB rate for Data Connect - verify in the tenant's Platform
Consumption Console before quoting a client a cost. GATED.

**Operationally, what "zero-copy" changes.**
- **Freshness** - Iceberg tables are periodically MATERIALIZED, not streamed;
  this is a weaker guarantee than LDQ's always-live Trino reads. Cadence is not
  published - GATED, confirm in-tenant before promising near-real-time.
- **Governance** - the receiving platform's own RBAC/column security/audit
  wraps the shared table (Snowflake: "the same way they apply to native
  Snowflake tables") - but whether Workday's own security-domain-level access
  propagates into the target platform's grants is undocumented. GATED, do not
  assume it does; verify per tenant.
- **Compute** - zero-copy means the CONSUMING platform's own compute (a
  Snowflake warehouse, a Databricks SQL warehouse) reads the shared files -
  section 1's live-query compute caveat still applies, now to Workday-sourced
  data too. REPORTED/inferred from the Iceberg REST catalog architecture, not
  an explicit Workday billing statement - verify at contract time.
- **Schema evolution** - not documented anywhere surfaced in this research.
  GATED.

**The consulting decision rule.** Before proposing an extract pipeline (this
file's sections 2-7) for Workday-sourced data landing in Snowflake or
Databricks:
- Target is Snowflake, Databricks, Salesforce Data Cloud, BigQuery, or AWS,
  the needed objects are in Workday's exposed Data Lake catalog, and EA timing
  fits the engagement -> recommend Data Connect first. No pipeline to build or
  re-run; governance stays native to the target platform.
- Otherwise (unsupported platform, object not yet exposed, EA timing does not
  fit the go-live date, or the client needs true streaming/CDC freshness
  beyond periodic materialization) -> fall back to this file's extract
  patterns (COPY INTO / Snowpipe / Auto Loader, section 1's materialize-vs-
  query-live decision).
- Either way, verify current EA/GA status and the exposed-object catalog
  in-tenant before committing to a client timeline - this space moves fast
  and REPORTED dates lag what a given tenant actually has enabled.

---

## 2. Snowflake - connect and auth

Connect via the Snowflake driver/connector for your language (e.g. the Python
connector, or Snowpark). Auth options, in order of preference for an unattended
hosted tool:

- **Key-pair authentication (JWT)** - you generate an RSA key pair, register the
  PUBLIC key on the Snowflake user, and the connector signs a JWT with the
  PRIVATE key (held in Secrets Manager - patterns.md section 1). No password.
  This is the recommended mechanism for service/integration accounts, and it is
  what the Snowpipe REST endpoints require.
- **OAuth** (Snowflake OAuth or External OAuth via the corporate IdP) - for
  flows where an external authorization server issues tokens.
- **Username/password** - avoid for automation; and note Snowflake has been
  moving to REQUIRE MFA for password sign-in, which breaks unattended
  password-based connections. Key-pair sidesteps this entirely.

Gotchas: a Snowflake connection carries a **role, warehouse, database, and
schema** context - set them explicitly, do not rely on user defaults, or a query
runs with the wrong compute or privileges. The **virtual warehouse** is the
compute; size it for the workload and set **auto-suspend** so an idle integration
warehouse stops billing. Source: key-pair auth
(https://docs.snowflake.com/en/user-guide/key-pair-auth); authentication
overview (https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-overview).

---

## 3. Snowflake - load data in

Two load models - pick by latency and continuity:

- **Bulk load with `COPY INTO <table>` from a stage.** Land files (CSV/JSON/
  Parquet) in a **stage** - internal (Snowflake-managed) or external (an S3 /
  Azure / GCS bucket you own) - then `COPY INTO` the table. This is the batch
  path (patterns.md section 2) - use it for periodic large loads. You provide and
  size the warehouse that runs the COPY.
- **Snowpipe - continuous micro-batch.** Loads files as soon as they land in a
  stage, within minutes, without you scheduling COPYs. Triggered either
  automatically by cloud storage events (S3 event notifications) or by calling
  the **Snowpipe REST API** (which requires key-pair JWT auth). Use when you want
  near-real-time landing instead of scheduled batches.
- **Snowpipe Streaming** - a newer, lower-latency row-level streaming ingest
  (no files) for true streaming sources - confirm current availability/API in the
  docs, it has evolved.

Gotchas: **COPY INTO is idempotent by load history** - Snowflake tracks which
staged files it has already loaded and skips them on re-run (patterns.md section
3), which is why file-based loads replay safely. Match the FILE FORMAT to the
data and use `VALIDATION_MODE` / `ON_ERROR` to handle bad rows instead of failing
the whole load. Sources: data loading overview
(https://docs.snowflake.com/en/user-guide/data-load-overview); Snowpipe
(https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro); COPY INTO
(https://docs.snowflake.com/en/sql-reference/sql/copy-into-table).

---

## 4. Databricks - connect and auth

Connect to a **SQL warehouse** (Databricks SQL) via the Databricks SQL Connector
(Python and others) or the ODBC/JDBC driver. Governance is through **Unity
Catalog** (catalog.schema.table three-level namespace). Auth for a hosted tool:

- **OAuth machine-to-machine (M2M) with a service principal** - the recommended
  unattended path. Create a service principal, give it an OAuth secret, set
  `DATABRICKS_CLIENT_ID` + `DATABRICKS_CLIENT_SECRET` (the secret in Secrets
  Manager - patterns.md section 1); the connector mints and auto-refreshes tokens,
  including for long-running (>1h) jobs. Requires a recent connector version
  (the Python SQL connector added M2M in the 2.5.x line) - pin it.
- **Personal access token (PAT)** - a long-lived bearer token. Simpler but it is
  a durable secret with a coarse scope; OAuth M2M is preferred. If used, store
  and rotate it like any secret.

Gotchas: the tool connects to a **SQL warehouse** endpoint (HTTP path + host);
set **auto-stop** on the warehouse so it does not idle billably, and expect a
cold-start delay on the first query after it stops. Unity Catalog grants govern
what the service principal can see - a missing grant looks like an empty result.
Source: OAuth M2M
(https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m); Python SQL
connector (https://docs.databricks.com/aws/en/dev-tools/python-sql-connector).

---

## 5. Databricks - load data in

- **`COPY INTO <delta_table>` from cloud object storage.** SQL bulk load into a
  Delta table from files in S3/ADLS/GCS. **Retriable and idempotent** - files
  already loaded are skipped on re-run (patterns.md section 3), so replay is
  safe. Supports CSV/JSON/Parquet/Avro/ORC/XML/text/binary. Runs on a SQL
  warehouse or cluster.
- **Auto Loader (`cloudFiles`)** - incrementally and efficiently ingests new
  files as they arrive in storage (the continuous counterpart, akin to Snowpipe).
  Use for streaming/continuous file ingestion at scale.
- For writing a modest result set FROM the tool INTO Databricks, INSERTs over the
  SQL connector are fine; for anything bulk, stage files and `COPY INTO`.

Gotcha: prefer landing files in object storage + `COPY INTO`/Auto Loader over
row-by-row INSERT for volume - same bulk-over-single-row rule as everywhere
(patterns.md section 2). Source: COPY INTO
(https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into); load
data with COPY INTO
(https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/).

---

## 6. Reading out, and reverse ETL

**Query out.** Both platforms are ANSI-SQL-ish - the tool runs a SELECT over the
SQL connector against a warehouse. Always: parameterize (no SQL injection),
LIMIT/paginate large result sets (patterns.md section 5), and cache results - a
warehouse query is expensive compute, do not re-run it per request.

**Reverse ETL** - moving warehouse/lakehouse data BACK OUT into an operational
system (a SaaS, or the tool's Postgres) so it is usable in an application
context. This is exactly the "materialize a slice into Postgres" path (section
1) generalized. Do not conflate it with Workday Data Connect's inbound "Data
In" (section above): reverse ETL physically COPIES rows; Data In registers a
zero-copy external-table pointer and moves nothing. Do it incrementally (section 7), idempotently (upsert on a
natural key), and only for the slice the operational system needs - do not mirror
the whole warehouse into Postgres.

---

## 7. Incremental patterns

Never re-pull the whole table on every sync - it wastes warehouse compute and
does not scale. Pull only what changed since last time (the incremental-poll
high-water mark, patterns.md section 2):

- **Watermark column** - a monotonically increasing `updated_at` / load
  timestamp / sequence. Persist the last value processed; next run selects
  `WHERE watermark > :last`. Simple and portable across every warehouse.
- **Change tracking** - Snowflake **Streams** expose row-level change (CDC)
  on a table/view; Databricks **Change Data Feed** (CDF) exposes row changes on a
  Delta table. Use these when you need true insert/update/delete deltas, not just
  "rows touched since T."
- **Boundary discipline** - use `>=` on the watermark and dedupe idempotently,
  or you drop rows that share the boundary timestamp. Store watermark values in
  the warehouse's own time/UTC to avoid skew.

---

## 8. Generic warehouse/lakehouse principles

The specifics above are Snowflake/Databricks, but the shape carries to Amazon
Redshift, Google BigQuery, Azure Synapse/Fabric, and others:

- **Auth = key-pair/JWT or OAuth service identity, secret in Secrets Manager.**
  Not a password, not a token in the repo.
- **Bulk-load via staged files + a COPY-style command**, not row-by-row inserts.
  Every warehouse has a bulk loader; use it.
- **Compute is metered per query** - a warehouse/slot/DWU spins up and bills.
  Cache, auto-suspend, and do not put live warehouse queries on hot interactive
  paths.
- **Incremental by watermark or a native change feed** - never full-table
  re-pulls.
- **Materialize-vs-query-live is the first decision** (section 1) and it is the
  same on every platform.

---

Sources are linked inline; all are official `docs.snowflake.com` /
`docs.databricks.com`. Connector versions, auth options, and streaming ingest
mechanisms are actively evolving on both platforms - pin versions and confirm
against the current docs before relying on anything here.
