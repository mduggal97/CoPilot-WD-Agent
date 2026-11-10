# Multi-Tenancy - the per-CUSTOMER data-isolation model

Modeled on public AWS and PostgreSQL guidance. Patterns only - every example
below is invented and generic. No account ids, no client names, no real data.

## Why this file exists (the gap it closes)

`module-contract.md` gives every module its own Postgres **schema**. That
isolates **features** from each other inside one internal tool used by one
org's own users - `widgets` cannot read `gallery`'s rows, by construction. It
says nothing about **customers**, because an internal tool has none: there is
one tenant (the firm) and many users, not many paying organizations sharing the
app.

The practice is now building the CUSTOMER-SOLD hosted-product path (next-year
roadmap, starting now): the same app, sold to and shared by multiple paying
customers, where **customer A's data must never be visible to customer B** -
not through a bug, not through a missing filter, not through an admin screen.
That is a second, orthogonal axis of isolation this suite has not yet owned.
This file owns it: the **data-layer** model for isolating customers.

**Companion, not duplicate.** `app-hosting/references/customer-hosting.md`
(authored in parallel) owns the rest of the customer-sold path - public
ingress, external identity (customer SSO / Cognito / Auth0), and tenant
provisioning workflow. THIS file owns what happens once a request is
authenticated and lands in the database: which rows it is allowed to touch.
Read both; do not expect either to repeat the other. Where the two meet (how
a resolved tenant id gets from an authenticated request into the isolation
mechanics below), that mechanic lives here; how the tenant was authenticated
in the first place lives there.

Relevant flag already on record in this suite:
`app-hosting/references/aws-architecture.md` section 3.2 marks the current
AWS shape as **internal-only** and explicitly calls out that "there is no
per-customer multi-tenancy here (schema-per-MODULE isolates features, not
customers)" as a gap to design before attempting a customer-sold product.
This file is that design.

---

## Table of contents

- [Per-module vs per-customer - two orthogonal axes](#two-axes)
- [The three canonical isolation models](#three-models)
- [Tradeoffs at a glance](#tradeoffs)
- [How to choose](#how-to-choose)
- [Mixing models in one product](#mixing)
- [Row-Level Security for the Pool model](#rls)
- [The fatal failure mode - a cross-tenant leak](#fatal-failure)
- [Testing the isolation - prove tenant A cannot read tenant B](#testing)
- [Migrations, noisy neighbors, and tenant lifecycle](#lifecycle)
- [The cross-tenant-leak invariant](#invariant)
- [Checklist](#checklist)

---

<a name="two-axes"></a>
## Per-module vs per-customer - two orthogonal axes

Keep these mentally separate; conflating them is how designs get muddled.

| Axis | Question it answers | Owned by | Mechanism |
|---|---|---|---|
| Per-module | "which FEATURE owns this table?" | `module-contract.md` | one Postgres schema per module |
| Per-customer (tenancy) | "which CUSTOMER owns this row?" | this file | Pool / Bridge / Silo (below) |

**Per-module != per-customer.** A schema-per-module boundary that is rock
solid inside one customer's data does nothing to stop customer A's request
from reading customer B's row in the SAME module's SAME schema - because
tenancy was never modeled as a boundary at all. Do not assume schema-per-
module gives you customer isolation for free; it does not, and treating it as
if it does is exactly how a leak ships. See
[How this composes with schema-per-module](#mixing) for how the two axes
combine correctly.

---

<a name="three-models"></a>
## The three canonical isolation models

These are the AWS SaaS Lens / "Multi-Tenant SaaS Architecture on AWS" terms
(AWS Well-Architected SaaS Lens; AWS SaaS Factory guidance) - inspiration for
the naming and tradeoffs below, not copied text; every code sketch is
invented for this suite.

### Pool - shared schema, `tenant_id` column + Row-Level Security

Every tenant's rows live in the SAME tables, in the SAME schema, in the SAME
database. Every tenant-owned table carries a `tenant_id` column, and Postgres
Row-Level Security (RLS) enforces - at the database engine, not just in
application code - that a connection can only see rows matching its current
tenant context. Full mechanics in [RLS for the Pool model](#rls).

```
tenants share:  database  ->  schema  ->  table  ->  (rows filtered by tenant_id via RLS)
```

### Bridge - schema-per-tenant in a shared database

Every tenant gets its OWN Postgres schema (e.g. `tenant_acme`, `tenant_globex`)
inside one shared database instance. Tables are identical across schemas; a
connection is routed to the right schema per request (the same
`schema_translate_map` seam `module-contract.md` uses for modules - now keyed
by tenant instead of by module).

```
tenants share:  database
tenants own:    schema  ->  table  ->  rows (no tenant_id column needed - the schema IS the boundary)
```

### Silo - database or stack per tenant

Every tenant gets its own database (or, at the extreme, its own full
application stack: its own RDS instance, its own container, sometimes its own
VPC). Nothing is shared below the compute layer that provisions silos.

```
tenants own:  database  (or the entire stack, one deployment per tenant)
```

---

<a name="tradeoffs"></a>
## Tradeoffs at a glance

| Dimension | Pool | Bridge | Silo |
|---|---|---|---|
| Isolation strength | Logical only - one bug in a `WHERE` clause or a missing RLS policy crosses tenants | Stronger - a stray query without a schema qualifier fails loudly (relation not found) rather than returning another tenant's rows | Strongest - physically separate database/stack; a bug in tenant A's queries cannot even connect to tenant B's data |
| Cost / density | Cheapest - thousands of tenants share one small database | Medium - one database, but N schemas means N x the catalog objects, connections, and vacuum/autovacuum overhead | Most expensive - N databases or N full stacks, each with its own baseline cost floor |
| Noisy-neighbor risk | Highest - one tenant's heavy query load or lock contention is felt by everyone sharing the instance | Medium - separate schemas reduce lock contention but still share the instance's CPU/IO/connections | Lowest - a noisy tenant's load stays inside its own database/stack |
| Blast radius of an outage/bug | Whole product, all tenants, at once | Usually one tenant's schema, but a shared-instance outage still takes everyone down | One tenant, unless the shared provisioning layer itself breaks |
| Per-tenant customization (custom fields, custom retention, custom backup schedule) | Hard - one schema, one shape, for everyone | Possible per-schema (e.g. one tenant's schema gets an extra column) but awkward to keep track of across many schemas | Easy - each tenant's database can genuinely differ |
| Operational complexity | Lowest - one migration run, one backup job, one connection pool | Medium - migrations and backups loop over N schemas | Highest - migrations, backups, monitoring, and cost tracking are all N times over, or need a fleet-management layer |
| Onboarding a new tenant | Fastest - insert a tenant row, no schema/DDL work | Medium - run the schema-creation + migration script for the new schema | Slowest - provision a new database/stack, wire secrets, wire monitoring |
| Typical scale | Hundreds to tens of thousands of small-to-medium tenants | Tens to low hundreds of tenants (catalog/connection overhead caps this) | A handful to low dozens of large or regulated tenants |

---

<a name="how-to-choose"></a>
## How to choose

Answer these in order; the first "yes" usually decides it for that tenant
tier.

1. **Does this tenant carry a regulatory or contractual isolation demand**
   (data residency, a dedicated-infrastructure clause, HIPAA/FedRAMP-style
   segregation, a security questionnaire that requires no shared compute)?
   -> **Silo.** No amount of RLS discipline satisfies a contract that requires
   physically separate infrastructure; do not try to argue engineering
   controls into a contractual requirement.
2. **How many tenants, and how large is each?** A few large, high-value
   enterprise tenants -> Bridge or Silo is affordable per-tenant overhead.
   Hundreds to tens of thousands of small tenants -> Pool is the only model
   whose cost per tenant stays low enough to be viable; Silo's fixed cost
   floor per tenant does not scale down.
3. **What is the cost target?** If margin depends on serving many tenants off
   one small database, Pool. If the product's price point already assumes
   dedicated infrastructure per customer (common in enterprise/regulated
   deals), Silo's cost is already priced in.
4. **How much per-tenant customization is promised?** Heavy schema
   customization, custom retention windows, or a bespoke backup/restore SLA
   per tenant push toward Bridge or Silo, where a tenant's schema/database can
   diverge. A product with one fixed shape for every tenant has no need for
   that flexibility - stay in Pool.
5. **What is acceptable blast radius?** If a single bad migration or a noisy
   tenant must never be able to affect anyone else, Bridge or Silo bound that
   risk structurally; Pool depends entirely on the RLS policy and query
   discipline holding.

<a name="mixing"></a>
### A product can MIX models - this is normal, not an anti-pattern

Most tenants do not need Silo-grade isolation, and a handful of tenants
(a large enterprise account, a regulated customer with a residency
requirement) will need more than the default tier gives everyone else. Do
not force one model on every tenant:

- Default new tenants into **Pool** - it is the cheapest and fastest to
  onboard, and it is where the product should optimize its operational
  tooling (one migration path, one backup job, one connection pool).
- Offer **Silo** as an explicit, priced tier for tenants whose contract or
  regulatory posture demands it. That tenant's row in the tenant-registry
  table records `isolation_model = "silo"` and a pointer to its dedicated
  database DSN; the application's tenant-resolution layer routes that
  tenant's connections there instead of into the shared pool. The
  application code above the connection layer does not need to know or care
  which model backs a given tenant - it asks "give me a session scoped to
  tenant X" and the routing layer decides Pool-with-RLS or Silo-connection
  underneath.
- **Bridge is a reasonable middle tier** if a cohort of tenants wants schema-
  level separation without full Silo cost - but recognize it does not scale
  to thousands of tenants (Postgres catalog and connection overhead per
  schema becomes the limiting factor well before Pool would).

The design point that makes mixing tractable: keep a **tenant registry**
(one row per tenant: id, isolation_model, connection/DSN pointer or schema
name, lifecycle status) as the single source of truth the routing layer
consults. Nothing else in the codebase should hardcode "all tenants are
Pool."

---

<a name="rls"></a>
## Row-Level Security for the Pool model - the load-bearing mechanic

Pool is the default tier for most tenants, and its entire safety case rests
on Postgres Row-Level Security (RLS) being correctly enabled, correctly
policied, and correctly fed a tenant context on every connection. Official
reference: PostgreSQL documentation, "Row Security Policies"
(postgresql.org/docs, `CREATE POLICY` / `ALTER TABLE ... ENABLE ROW LEVEL
SECURITY`) - read it before deviating from the pattern below.

### Step 1 - every tenant-owned table gets a `tenant_id` column

```sql
-- widgets_app tenant-owned table (Pool model) - invented, generic
CREATE TABLE widgets.widget (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   uuid NOT NULL,              -- the tenancy column, on EVERY tenant-owned table
    name        text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Index it - every tenant-scoped query filters on this, and RLS adds it to every plan.
CREATE INDEX widget_tenant_id_idx ON widgets.widget (tenant_id);
```

### Step 2 - enable RLS and FORCE it (including for the table owner)

```sql
ALTER TABLE widgets.widget ENABLE ROW LEVEL SECURITY;
-- FORCE matters: without it, the table owner (often the app's own DB role,
-- if it was used to run migrations) bypasses RLS by default. FORCE closes
-- that hole so even the owning role is subject to the policy.
ALTER TABLE widgets.widget FORCE ROW LEVEL SECURITY;
```

### Step 3 - one policy per table, keyed to a session-local setting

```sql
-- The policy: a row is visible/writable only if its tenant_id matches the
-- tenant_id the CURRENT connection has declared via SET (step 4).
CREATE POLICY tenant_isolation ON widgets.widget
    USING (tenant_id = current_setting('app.current_tenant')::uuid)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid);
    -- USING governs SELECT/UPDATE/DELETE visibility.
    -- WITH CHECK governs INSERT/UPDATE - blocks writing a row into a tenant
    -- you are not scoped to, not just reading one.
```

Do this for every tenant-owned table. A scaffold or migration helper should
generate the `ENABLE`/`FORCE`/`CREATE POLICY` triple automatically whenever a
table declares a `tenant_id` column, the same way `module-contract.md`'s
scaffold generates `MODULE_SCHEMA` correctly by construction - a manually
remembered RLS policy per new table is exactly the kind of mechanical step
that eventually gets forgotten.

### Step 4 - set the tenant context once per request/connection

RLS reads `current_setting('app.current_tenant')` - something has to set
that GUC before any query runs, on every request, without exception.

```python
# shared_app/db/tenant_session.py (illustrative, Pool model)
"""Resolve a tenant-scoped session. The ONE place tenant context is set -
every tenant-owned query in the app goes through this, never a raw session."""
from __future__ import annotations
from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from shared_app.db.session import get_raw_session  # schema-unaware pooled session


async def get_tenant_session(tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_raw_session():
        # set_config(..., is_local=True) scopes the setting to THIS transaction
        # only - it cannot leak into the next request that reuses this pooled
        # connection. Never use a bare `SET` here (that is session-scoped and
        # WILL leak across pooled connections - see the fatal failure mode below).
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": tenant_id},
        )
        yield session
```

```python
# widgets_app/api/deps.py (illustrative) - the tenant id comes from the
# AUTHENTICATED request context (resolved by customer-hosting.md's identity
# layer), never from a client-supplied header or query param.
from __future__ import annotations
from typing import Annotated
from fastapi import Depends, Request
from shared_app.db.tenant_session import get_tenant_session


async def get_widgets_tenant_session(request: Request):
    tenant_id = request.state.tenant_id  # set by auth middleware after token validation
    async for session in get_tenant_session(tenant_id):
        yield session
```

Why `is_local=True` (transaction-scoped `SET`) and not a plain `SET`, and why
the setting is applied via `set_config` rather than string-formatted into a
`SET` statement: a plain `SET` persists for the life of the pooled physical
connection, so the NEXT request that borrows that connection from the pool
inherits the PREVIOUS request's tenant context if it forgets to set its own -
a silent cross-tenant leak with no error at all. Transaction-scoped
`set_config` resets automatically at transaction end regardless of what the
next borrower does. `module-contract.md`'s schema-scoped session makes the
identical argument for `schema_translate_map` over `SET search_path`; RLS's
tenant context has the same pooled-connection hazard and the same fix.

### Why RLS and not "just filter every query in application code"

Filtering in application code (`WHERE tenant_id = :tid` hand-added to every
query) is not wrong in principle, but it puts the ENTIRE isolation guarantee
on every engineer remembering to add that clause to every query, forever,
including ad-hoc reporting queries, background jobs, and a future ORM
relationship that joins without it. RLS moves the guarantee to the database
engine: even a query that forgets the filter, a raw SQL debugging session, or
a future engineer who does not know the convention still cannot see another
tenant's rows, because Postgres itself refuses to return them. Defense in
depth: keep explicit tenant filters in application code too (cheaper query
plans, clearer intent) - RLS is the backstop, not a reason to skip them.

---

<a name="fatal-failure"></a>
## The fatal failure mode - a cross-tenant leak

State this plainly, because it is the one bug class in this whole file that
matters more than any other: **a query path that bypasses RLS, or a table
that never got RLS enabled, or a request that runs with the wrong tenant
context - is a cross-tenant data leak. That is the single worst bug a
multi-tenant SaaS product can ship:** it is a breach, not a defect; it is
disclosed to customers and regulators, not filed as a bug ticket; and it can
end the product's ability to sell to security-conscious customers at all.

Concrete ways it happens, all of them mundane:

- A new table is added and someone forgets `ENABLE ROW LEVEL SECURITY` (it is
  OFF by default in Postgres - the safe-by-default direction is backwards
  here, so this must be enforced mechanically, not by memory).
- A table's owner role runs a migration or an ad-hoc fix without `FORCE ROW
  LEVEL SECURITY` set, and the owner role is also the role the app connects
  as - RLS silently does not apply to it.
- A background job, a reporting query, or an admin tool opens a connection
  through a path that never calls `get_tenant_session` - it uses the raw
  pooled session directly and never sets `app.current_tenant` at all. Some
  Postgres RLS configurations treat an unset session variable permissively
  rather than denying, so this can return ALL tenants' rows, not zero.
- A pooled connection's tenant context from a previous request leaks into
  the next one because the code used a session-scoped `SET` instead of
  transaction-scoped `set_config(..., true)` (see step 4 above).
- A join or a subquery reaches into a table that has RLS, but does so via a
  `SECURITY DEFINER` function or a superuser-ish role that bypasses RLS by
  design, without the author realizing that role bypasses it.

None of these throw an error. They all look, at a glance, like the feature
works. That is what makes this the worst bug class: it fails silently and is
usually found by a customer, an auditor, or a penetration test - not by a
stack trace.

---

<a name="testing"></a>
## Testing the isolation - prove tenant A cannot read tenant B

Do not settle for "the policy looks right on inspection." Write an
integration test that actually tries to breach isolation and asserts it
fails. This test belongs in EVERY module's `tests/integration/` (see
`module-contract.md` section 1) that owns a tenant-scoped table, and it
should run against a real Postgres, not a mock - RLS is a database-engine
feature; mocking the session defeats the entire point of the test.

```python
# widgets_app/tests/integration/test_tenant_isolation.py (illustrative)
"""The single most important test in a Pool-model module: prove that a
session scoped to tenant A cannot read, update, or delete tenant B's rows -
even when it knows B's row id."""
import pytest
from shared_app.db.tenant_session import get_tenant_session
from widgets_app.api import repository

TENANT_A = "11111111-1111-1111-1111-111111111111"
TENANT_B = "22222222-2222-2222-2222-222222222222"


@pytest.mark.asyncio
async def test_tenant_a_cannot_read_tenant_b_row(db_engine):
    # Seed one row owned by tenant B.
    async for session_b in get_tenant_session(TENANT_B):
        row = await repository.create_widget(session_b, name="B's widget")
        await session_b.commit()

    # A session scoped to tenant A, given tenant B's exact row id, must see nothing.
    async for session_a in get_tenant_session(TENANT_A):
        found = await repository.get_widget(session_a, widget_id=row.id)
        assert found is None, "CROSS-TENANT LEAK: tenant A read tenant B's row"

        # Also prove the write path is blocked (WITH CHECK), not just SELECT.
        with pytest.raises(Exception):  # the DB rejects the tenant_id mismatch
            await repository.force_update_tenant_id(session_a, widget_id=row.id, new_tenant=TENANT_A)
            await session_a.commit()


@pytest.mark.asyncio
async def test_every_tenant_table_has_rls_enabled(db_engine):
    # A disk/catalog-derived guard, same spirit as module-contract.md's
    # disk-derived "every module is registered" test: query pg_tables /
    # pg_class.relrowsecurity for every table with a tenant_id column and
    # fail the build if ANY of them do not have RLS enabled AND forced.
    rows = await db_engine.fetch_all(
        """
        SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity
        FROM pg_class c
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'tenant_id'
        WHERE c.relkind = 'r'
        """
    )
    offenders = [r for r in rows if not (r.relrowsecurity and r.relforcerowsecurity)]
    assert not offenders, f"Tables with tenant_id but RLS not enabled+forced: {offenders}"
```

The second test matters as much as the first: the leak test proves the
policy works where it exists; the catalog-derived test proves NO tenant-
owned table was ever added without the policy in the first place. Run both
in CI, against a real Postgres, on every change - this is not optional
coverage, it is the mechanical guard for the [invariant](#invariant) below.

---

<a name="lifecycle"></a>
## Migrations, noisy neighbors, and tenant lifecycle

### Migrations

- **Pool** - one schema, one migration run, same as any module (see
  `module-contract.md` section 5 / `local-dev.md`'s per-module Alembic loop).
  Tenancy adds no extra migration surface: a new column ships once and every
  tenant's rows get it simultaneously.
- **Bridge** - migrations must run once PER TENANT SCHEMA. Loop the same way
  `local-dev.md`'s `tools/migrate-local.sh` loops over module trees, but keyed
  by tenant schema instead of module name. A migration that fails halfway
  through the loop leaves SOME tenants upgraded and others not - track
  per-tenant migration state (a row in the tenant registry) so a retry is
  idempotent and resumable, not a guess.
- **Silo** - migrations must run once PER TENANT DATABASE, typically via a
  fan-out job (one migration task per tenant database DSN). This is the
  clearest cost of Silo: N databases means N migration runs, N chances for one
  to fail independently of the others, and a fleet-management layer to track
  which tenants are on which schema version.

### Noisy-neighbor mitigation

- **Pool** is where noisy-neighbor risk is highest, because tenants share
  connections, CPU, and IO on one instance. Mitigate with per-tenant
  connection-pool caps (never let one tenant hold every connection in the
  pool), statement timeouts, and query-plan monitoring keyed by
  `app.current_tenant` so a runaway tenant is identifiable, not just "the DB
  is slow." A large, disproportionately heavy tenant is itself a strong
  signal that tenant should be moved to Bridge or Silo (see
  [how to choose](#how-to-choose)) rather than tuned around indefinitely.
- **Bridge** reduces contention somewhat (separate schemas mean separate
  table/index working sets) but the instance's CPU/IO/connection ceiling is
  still shared - a truly noisy tenant still affects everyone.
- **Silo** removes the shared-instance risk entirely for tenants who need
  that guarantee; the tradeoff is paying for dedicated capacity even when
  that tenant is idle.

### Tenant lifecycle - onboard, suspend, export, delete (GDPR-style erasure)

Keep these as explicit, tested operations against the tenant registry - not
ad-hoc scripts run once and forgotten.

- **Onboard.** Insert a tenant registry row (id, isolation_model, status =
  `active`). Pool: no DDL needed, first request just works once the row
  exists. Bridge: run the schema-creation + migration script for the new
  schema. Silo: provision the dedicated database/stack, run its migrations,
  wire its secret.
- **Suspend.** Flip the registry row's status to `suspended` and have the
  auth/routing layer refuse to resolve a tenant session for that id - do NOT
  delete or move data on suspend; it should be a fully reversible, one-flag
  operation.
- **Export.** A tenant-scoped export must use the SAME tenant-scoped session
  path as normal application traffic (`get_tenant_session` for Pool, the
  schema/database connection for Bridge/Silo) - never a superuser dump
  filtered after the fact by application code, which reintroduces exactly the
  bypass risk described in [the fatal failure mode](#fatal-failure). For Pool,
  this means the export tool authenticates as a real tenant-scoped session
  and lets RLS itself guarantee it only ever sees that tenant's rows.
- **Delete / GDPR-style erasure.** Pool: `DELETE FROM ... WHERE tenant_id =
  :tid` run through the tenant-scoped session (RLS both guarantees you cannot
  delete another tenant's rows by mistake, and confirms the delete touched
  the tenant you meant). Bridge: `DROP SCHEMA tenant_x CASCADE` - clean and
  total, no `tenant_id` accounting needed. Silo: drop the database / decommission
  the stack. In all three cases, log the deletion with a timestamp and row/
  object count in an audit trail that itself lives OUTSIDE the deleted
  tenant's data, and confirm backups are also subject to the same retention/
  erasure policy - a satisfied deletion request that still lives on in a
  30-day-old backup is not actually satisfied.

---

<a name="invariant"></a>
## The cross-tenant-leak invariant

If this file is reduced to one rule, it is this:

> **No request, job, query, or export - authenticated or not, application
> code or ad-hoc - may ever return or mutate a row belonging to a tenant
> other than the one the request is scoped to. There are no exceptions for
> "just this one admin query" or "just this one background job."**

The mechanical guard that keeps this true, restated from
[Testing the isolation](#testing):

1. Every tenant-owned table has `ENABLE ROW LEVEL SECURITY` AND `FORCE ROW
   LEVEL SECURITY` - verified by a catalog-derived test that fails CI the
   moment a new table with a `tenant_id` column ships without both.
2. Every tenant-scoped code path sets `app.current_tenant` via transaction-
   scoped `set_config(..., true)`, never a bare `SET`, and never skips it -
   verified by the leak test that seeds tenant B's row and asserts tenant A's
   session cannot see or mutate it.
3. Any "admin" or "cross-tenant reporting" need is served by a SEPARATE,
   explicitly-audited path that is itself tenant-aware (e.g. it iterates
   tenants one at a time through normal tenant-scoped sessions, or reads from
   a purpose-built aggregate table populated by a job that respects the same
   RLS boundary) - never by a superuser connection that happens to bypass RLS
   because it was convenient.

Sources for the underlying mechanics (inspiration, not copied text): AWS
Well-Architected SaaS Lens and the "Multi-Tenant SaaS Architecture on AWS"
guidance for the Pool/Bridge/Silo terminology and tradeoffs; PostgreSQL
official documentation ("Row Security Policies", `CREATE POLICY`) for the
RLS mechanics themselves.

---

<a name="checklist"></a>
## Checklist - a Pool-model tenant-owned table is isolation-complete when

- [ ] It has a `tenant_id` column, NOT NULL, indexed.
- [ ] `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY` are both set.
- [ ] It has a policy with both `USING` and `WITH CHECK` keyed to
      `current_setting('app.current_tenant')`.
- [ ] Every route/job that touches it resolves its session via the shared
      tenant-session seam (transaction-scoped `set_config`), never a raw
      pooled session.
- [ ] A leak test proves tenant A cannot read/write tenant B's row, and a
      catalog-derived test proves no tenant-owned table escaped RLS.
- [ ] The tenant registry records this tenant's isolation model, so a future
      move to Bridge/Silo for this one tenant is a routing change, not a
      rewrite.
- [ ] Onboard/suspend/export/delete are each implemented through the same
      tenant-scoped path as normal traffic - none of them is a superuser
      script that bypasses RLS "just this once."
