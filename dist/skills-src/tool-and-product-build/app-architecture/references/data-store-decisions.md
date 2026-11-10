# Data Store Decisions - when NOT Postgres

Modeled on public AWS and PostgreSQL guidance. Patterns only - every example
below is invented and generic. No account ids, no client names, no real data.

## Why this file exists

Zero current portfolio demand for a non-Postgres store. This file is forward
coverage: the "do we need NoSQL / a cache / a search engine" question will
come up eventually, and the answer should be a deliberate, documented
decision, not a reflex either way. Read this BEFORE reaching for a new
store, not after one is already half-wired in.

> **Postgres is the default data store for every module, every time, until a
> named, measured reason says otherwise.** Adding a second store is an
> escalation, not a starting point.

---

## Table of contents

- [The default, stated hard](#the-default)
- [The questions that justify escalating](#questions)
- [DynamoDB](#dynamodb)
- [ElastiCache / Redis (or Valkey)](#cache)
- [S3 as a data store](#s3)
- [OpenSearch](#opensearch)
- [Decision table](#decision-table)
- [Pointers](#pointers)

---

<a name="the-default"></a>
## 1. The default, stated hard

`module-contract.md` gives every module its own Postgres schema. Most of
what teams reach for a specialty store to solve, Postgres already does, on
the instance the module already has:

| "We need a ___" | Postgres already has it |
|---|---|
| Document store for flexible/variable-shape records | `jsonb` column - typed, queryable (`->`, `->>`, `@>`), indexable (GIN) |
| Vector database for embeddings/RAG | `pgvector` extension - see app-agentic references/retrieval.md |
| A queue for background jobs | `LISTEN/NOTIFY` for wake-ups + `SELECT ... FOR UPDATE SKIP LOCKED` for a claim-one-row worker queue - no extra infra, transactional with the data it queues |
| Full-text search | built-in `tsvector`/`tsquery` + GIN index - no separate engine for typical in-app keyword search |
| A cache | often nothing - a well-indexed query at app scale is frequently fast enough that a cache solves a problem you do not have yet |

Most "we need NoSQL" conversations should end at this table. Before going
further, answer the questions below - if none clearly apply, stay on
Postgres and move on.

<a name="questions"></a>
## 2. The questions that justify escalating

Ask these in order. A "yes" is a real signal; a hunch that a document store
"feels more modern" is not.

1. **Access-pattern cardinality** - Are read/write patterns few, fixed, and
   known in advance ("get by id", "get all children of X"), not ad-hoc or
   still-being-discovered? Fixed patterns are what a single-table NoSQL
   design rewards; exploratory patterns are what it punishes.
2. **Single-digit-ms latency at scale** - Has a specific endpoint been
   PROFILED (not guessed) to miss a single-digit-ms p99 target at real
   volume, even well-indexed, even with a read replica?
3. **Write throughput** - Has a single Postgres primary's write path (WAL,
   autovacuum, index maintenance) been PROFILED as the bottleneck, not
   assumed to eventually become one?
4. **Item size/shape** - Is the data many small, independent, uniformly
   shaped items with no relational structure, rather than the joined,
   module-owned data every module already has?
5. **Fan-out** - Does the read path serve a genuinely high fan-out (a hot
   key read by very many callers) that rewards a purpose-built key-value
   engine's replication model?

If none clearly apply, the honest answer is "Postgres, with an index we
have not added yet." If one does, read the matching section below - each
names the gain, the cost, and what you give up, so escalating is a
documented trade, not a vibe.

---

<a name="dynamodb"></a>
## 3. DynamoDB

**Verify-current as of 2026-09-11** - on-demand pricing and table classes
move faster than this file will be re-read; re-check the AWS pricing page
before quoting a number.

**When it genuinely wins**: access patterns are known and few (question 1);
scale is massive (millions of items, very high request rates) and that
outweighs Postgres's flexibility; serverless ops matters (no instance to
size/patch/fail over, near-zero cost on `PAY_PER_REQUEST` for spiky loads).

**Single-table design in brief** - one table per bounded context, not one
per entity type:

```
PK               SK                  attributes
WIDGET#w-100     META                name, status, createdAt
WIDGET#w-100     ORDER#o-55          orderTotal, placedAt
USER#u-9         META                email, plan
```

PK groups everything about one "thing" so a single `Query` fetches it and
its children; SK encodes sub-type and sort order. GSIs add a second PK/SK
pair for a second access pattern - each is a full index copy, costing
storage and write capacity, not a free `CREATE INDEX`. The trade: data that
would be a Postgres join is denormalized onto one item at write time. A new
access pattern you did not design for means a new GSI or data-model change,
not a new `WHERE` clause.

**What you give up**: ad-hoc queries (no `WHERE name LIKE` without a
purpose-built GSI or export); joins (none - fetched as N calls or
denormalized in); transaction scope (`TransactWriteItems` caps at 100 items
/ 4 MB, one account/region, unlike an unbounded Postgres transaction); and,
the one that matters most here, **schema-per-module mapping** -
`module-contract.md` gives every module one Postgres schema on a SHARED
instance; DynamoDB has no schema concept to shard that way. **A DynamoDB
table maps to exactly ONE module's internal store, never a shared table
used by several modules** - the same "no module reads another module's
rows" rule, just paid for as a dedicated table+GSIs, not a free schema.

**On-demand vs provisioned**: on-demand (`PAY_PER_REQUEST`) needs no
capacity planning, best for new/spiky workloads; provisioned (optionally
auto-scaled) is cheaper at steady, well-understood volume. Cost scales with
request volume and item size, not an always-on instance - model it before
calling "serverless" automatically cheaper.

---

<a name="cache"></a>
## 4. ElastiCache / Redis (or Valkey)

**Verify-current as of 2026-09-11**: AWS ElastiCache offers a Redis
OSS-compatible engine and Valkey (the Linux Foundation fork created after
Redis Inc.'s 2024 license change); check the current engine picker and AWS
guidance before naming an engine in a design doc, since naming/licensing
here has kept moving and AWS has been steering new deployments to Valkey.

**What it is for**: cache-aside (check cache, miss falls to Postgres, write
back with a TTL - Postgres is always the system of record, a vanished cache
only makes the app slower, never wrong); sessions (TTL-native key-value at
volumes where a session table is a measurable Postgres load); rate limiting
(`INCR` + `EXPIRE` beats a locked counter row); lightweight queues (Redis
lists/streams when the queue does not need the transactional tie to its
data that Postgres `SKIP LOCKED` gives for free).

**When Postgres alone is fine**: at internal scale, plain Postgres
(maybe with a missing index added) usually IS the cache. Reach for
ElastiCache only once a specific, measured hot path shows repeated identical
reads a TTL'd cache would absorb - not as a day-one default. An unused
cache is not free: it is another moving part and another place staleness
bugs hide.

**Eviction and cold-start, honestly**: eviction under memory pressure
(`allkeys-lru`, `volatile-ttl`, etc.) is normal operation, not a corner case
- any code that treats a cache hit as guaranteed is wrong by construction. A
freshly deployed or failed-over node is EMPTY; the first traffic wave after
a deploy hits Postgres at full volume with zero absorption. Size Postgres to
survive a cold cache; the cache is a speed bonus, never load-bearing.

---

<a name="s3"></a>
## 5. S3 as a data store

**Large blobs/artifacts out of Postgres** - pointer row in Postgres, bytes
in S3:

```sql
-- widgets_app schema - the artifact's metadata and location, not its bytes
CREATE TABLE widgets.artifact (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_id     uuid NOT NULL REFERENCES widgets.widget(id),
    s3_key        text NOT NULL,   -- s3://bucket/widgets/<widget_id>/<artifact_id>.pdf
    content_type  text NOT NULL,
    byte_size     bigint NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);
```

Postgres stays small and fast to back up - it never carries megabyte-scale
blobs in a row. **Lifecycle tiers**: S3 lifecycle rules age an object from
Standard to Infrequent Access to Glacier with no application code involved;
set the policy at bucket creation, not after the bucket is full of
cold objects. **Presigned URLs**: the app hands the client a time-limited
presigned S3 URL for upload/download and never proxies large bytes through
its own compute; keep TTLs short and scoped to one object.

**When Postgres `bytea` is acceptable**: small, transactional blobs that
must roll back with their row (a thumbnail, a small form-attached snapshot)
are fine as `bytea` up to roughly the tens-of-KB range. Once a module's
`bytea` column dominates its schema's storage, that is the signal to move
to the pointer-row-plus-S3 pattern above.

---

<a name="opensearch"></a>
## 6. OpenSearch

**You probably do not need it.** Postgres full-text search (`tsvector`/
`tsquery` + GIN index) covers "find records containing these keywords"
inside one module's data for most in-app search boxes this suite builds.
Reach for OpenSearch only when the need is genuinely beyond that: real
relevance needs (fuzzy/typo-tolerant matching, faceted search, ranking
`ts_rank` does not satisfy, at a corpus size where the gap is user-visible);
or log analytics (aggregating high-volume structured logs/events across
time windows and dashboards - a different workload shape from transactional
application data, not a bigger version of it).

**The managed-service cost floor**: OpenSearch Service (or Serverless)
carries its own always-on cost floor (data nodes, or Serverless OCU
minimums) ON TOP OF the RDS Postgres instance every module already shares -
never a replacement, always a second store to operate and pay for. Size
that floor against real search/log volume before adding it; verify current
OpenSearch pricing at aws.amazon.com before quoting a number (checked
2026-09-11).

---

<a name="decision-table"></a>
## 7. Decision table

| Need | First reach (Postgres) | Escalate to | Module-contract note |
|---|---|---|---|
| Flexible/variable-shape records | `jsonb` + GIN index | - | stays in the module's own schema |
| Embeddings / RAG retrieval | `pgvector` | - | app-agentic references/retrieval.md; module's own schema |
| Background job queue | `LISTEN/NOTIFY` + `SKIP LOCKED` | managed queue (SQS) for cross-service fan-out | queue table in the owning module's schema |
| In-app keyword search | `tsvector`/`tsquery` + GIN | OpenSearch, past real relevance/scale limits | dedicated index still module-private |
| Known fixed-pattern lookups, massive scale | - (escalation case) | DynamoDB | one table per module, never shared |
| Hot-path latency / session / rate-limit | well-indexed query first | ElastiCache, cache-aside | keys namespaced per module; never system of record |
| Large blobs / artifacts / exports | `bytea` if small + transactional | S3, pointer row + object | pointer row in module's schema; bucket/prefix module-scoped |
| Log analytics / faceted search, real volume | - (escalation case) | OpenSearch | module-private index; others read via the owning module's API |

**The invariant, restated once** because it applies to every row above
regardless of store chosen: every store - Postgres schema, DynamoDB table,
cache namespace, S3 prefix, OpenSearch index - stays **module-private**.
Cross-module access is only ever through the owning module's API, never by
another module reading the store directly. Escalating off Postgres changes
WHERE a module's data lives; it never changes WHO is allowed to touch it.

---

<a name="pointers"></a>
## 8. Pointers

- **Multi-tenancy** - `multi-tenancy.md` in this folder. Row-Level Security
  is a Postgres-only mechanic; moving a module (or one tenant's slice of it)
  off Postgres means that file's Pool-model RLS story no longer applies and
  has to be re-derived for the new store (e.g. a DynamoDB table keys
  isolation into the PK, not a database-enforced policy) - re-verify the
  isolation guarantee by construction before shipping a non-Postgres store
  on a customer-sold multi-tenant module.
- **pgvector / RAG** - the app-agentic skill, references/retrieval.md, owns
  the embeddings/retrieval pattern this file only summarizes above.
- **Analytics warehouses (Snowflake/Databricks)** - the saas-integration
  skill, references/data-platforms.md, owns those as INTEGRATION targets
  (data flows OUT to them for analytics), not as an application data store a
  module reads from on the request path. "We send data to a warehouse for
  analytics" is not the same decision as "we escalated off Postgres."
