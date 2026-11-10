# Module Contract - the shape of one liftable unit

Modeled on the reference architecture. Patterns only - every example below
is invented and generic.

## What a "liftable unit" is

A module is a self-contained feature package that can run inside a shared
container today and be pulled out into its own service tomorrow **without moving
any code**. For that to be possible, every module has to look the same from the
outside: same router export, same `/health`, same data-isolation rules, same
migration shape, same layering. This file is that uniform shape.

The payoff of the uniformity is concrete:

- **Uniform mounting** - a composition root can mount any module with one line
  (`include_router(<name>_router, prefix="/api/v1/<name>")`) because every module
  exports the same thing. Nothing about mounting module B differs from module A.
- **Independent deploy and rollback** - because a module owns its own schema and
  its own migration tree, you can migrate, deploy, or roll back one module without
  touching another. A bad release in `widgets` never forces a `gallery` rollback.
- **Testability** - the pure logic has no I/O, so it tests in milliseconds with no
  database, and the parts that do have I/O are thin enough to test against a real
  Postgres in a small integration tier.

If you only remember one sentence: **a module is an independent Python package
that never imports a sibling module and never reads another module's rows.**

---

## 1. Directory layout (minimal, correct)

Here is the whole contract for an invented `widgets` module. Nothing here is
optional except where noted.

```
packages/modules/widgets/
  pyproject.toml                 # its own package; depends on shared, never a sibling
  alembic.ini                    # this module's migration config
  CLAUDE.md                      # the module's own contract card (see section 6)
  widgets_app/                   # the importable package (one per module)
    __init__.py
    py.typed
    schema.py                    # MODULE_SCHEMA = "widgets" - the ONE schema token
    models.py                    # ORM models, attached to the shared MetaData
    core/                        # FUNCTIONAL CORE - pure, no I/O
      __init__.py
      pagination.py              # e.g. limit validation, cursor math
      reconcile.py               # e.g. set-algebra "what to add / remove"
    api/                         # IMPERATIVE SHELL - routers, DB, side effects
      __init__.py
      router.py                  # required: exports `router: APIRouter`
      health.py                  # required: unauthenticated GET /health
      deps.py                    # schema-scoped DB session dependency
      contracts.py               # Pydantic request/response models (frozen)
      repository.py              # DB reads/writes + ORM->contract projection
      widgets.py                 # the actual endpoints
  migrations/
    env.py                       # Alembic env; PRIVATE version_table
    versions/
      0001_widgets_table.py      # this module's migration chain, starts at None
  tests/
    unit/                        # fast, hermetic - exercises core/ + pure shell
    integration/                 # needs Postgres - exercises api/ + migrations
```

Two rules people get wrong:

- `schema.py` sits at the **top level of the package**, not under `core/` or
  `api/`. Both the runtime (`api/deps.py`) and the migration tooling
  (`migrations/env.py`) import it, and neither layer should have to reach into the
  other's folder to get the schema name.
- Tests directories have **no `__init__.py`**. Every module ships a
  `tests/unit/test_health.py`; if the test packages were importable, two modules'
  identically-named test files would collide when collected from the repo root.
  Use pytest's `importlib` import mode at the root to key tests by path.

---

## 2. FCIS split - functional core, imperative shell

The single most important internal rule. Split every module into two layers:

| Layer | Folder | May contain | May NOT contain |
|-------|--------|-------------|-----------------|
| Functional core | `core/` | pure functions, dataclasses, set/string/number logic, validation | any I/O, any DB session, any network/S3/model call, any import of `api/` or `models` |
| Imperative shell | `api/` | routers, DB sessions, HTTP, side effects, ORM<->contract projection | pure business rules that belong in `core/` |

The dependency arrow points **one way**: `api/` may import `core/`; `core/` may
**never** import `api/` or `models`. This is what makes the core testable with no
database and no mocks - it is just functions over values.

### core/ example (pure - no I/O)

```python
# widgets_app/core/reconcile.py
"""Compute which widget ids to add and which to remove. Pure set algebra."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ReconcilePlan:
    to_add: tuple[str, ...]
    to_remove: tuple[str, ...]


def plan(incoming_ids: set[str], existing_ids: set[str]) -> ReconcilePlan:
    # Deterministic (sorted) so a unit test can assert exact output - no DB, no clock.
    return ReconcilePlan(
        to_add=tuple(sorted(incoming_ids - existing_ids)),
        to_remove=tuple(sorted(existing_ids - incoming_ids)),
    )
```

Notice: no session, no `await`, no import from `api/`. A test calls `plan({...},
{...})` and asserts on the result in microseconds.

### api/ example (imperative - the shell that does the I/O)

```python
# widgets_app/api/widgets.py
"""Widget read endpoint. The shell: it owns the DB session and calls core/ for logic."""
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from widgets_app.api import repository
from widgets_app.api.contracts import WidgetListResponse
from widgets_app.api.deps import get_widgets_session   # schema-scoped session
from widgets_app.core.pagination import resolve as resolve_page  # PURE

widgets_router = APIRouter()


@widgets_router.get("/widgets", response_model=WidgetListResponse)
async def list_widgets(
    session: Annotated[AsyncSession, Depends(get_widgets_session)],
    limit: int | None = None,
    cursor: str | None = None,
) -> WidgetListResponse:
    # Pure decision first (validate/interpret paging), then the impure DB read.
    page = resolve_page(limit, cursor)          # core/ - no I/O
    return await repository.list_widgets(session, page=page)   # api/ - the I/O
```

The endpoint is thin: it resolves paging with a pure function, then hands a
schema-scoped session to the repository. All the branching logic that is easy to
get wrong (limit bounds, cursor decode) lives in `core/` where it is trivially
testable.

> Pragmatic deviation: ORM->contract projection (`to_summary`, `to_detail`) lives
> in `api/repository.py`, not `core/`, because it must import the ORM models and
> the Pydantic contracts - both of which `core/` is forbidden to touch. That is
> the correct call: projection is shell work. Keep genuinely pure rules in `core/`.

---

## 3. Unauthenticated GET /health

Every module exports its own `/health` on its router, and it is the **one route
that is never authenticated**.

```python
# widgets_app/api/health.py
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get("/health", include_in_schema=False)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
```

Mounted under the module prefix, the effective path is
`/api/v1/widgets/health`. This is the MODULE's own liveness signal (and what it
serves once extracted into its own service). The container platform's health
check is a SEPARATE, root-level `GET /health` on the composition root (see
app-hosting/references/aws-architecture.md) - App Runner probes that, not each
module's path. Why the pattern matters:

- The container platform (App Runner or equivalent) polls a liveness URL. It must
  answer 200 whenever the process is up, **before** any token exists, or the
  platform kills a perfectly healthy container.
- Auth is enforced at the **edge**, once, by the composition root's default-deny
  middleware - not per route. So `/health` is the deliberate hole, and everything
  else is protected for free by being outside that exemption. Modules add **no**
  auth dependency to their own routes; they inherit default-deny.

---

## 4. Schema-per-module data isolation

Each module owns exactly one Postgres **schema** and reads only its own rows.

- `schema.py` holds a single constant: `MODULE_SCHEMA = "widgets"`.
- Every route depends on a **schema-scoped session** bound to that constant, never
  the schema-unaware default session (which resolves to `public`).
- **No cross-module row reads.** A module never runs a query against another
  module's tables. If `widgets` needs data that `gallery` owns, it calls
  `gallery`'s HTTP API - it does not reach into `gallery`'s schema. This is the
  database-level twin of "no sibling imports": isolation in code AND in data.

```python
# widgets_app/schema.py
from __future__ import annotations
MODULE_SCHEMA = "widgets"   # the single source of truth for this module's schema
```

```python
# widgets_app/api/deps.py
from __future__ import annotations
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from shared_app.db.session import get_session_for_schema   # the shared seam
from widgets_app.schema import MODULE_SCHEMA


async def get_widgets_session() -> AsyncGenerator[AsyncSession, None]:
    # Every widgets route depends on THIS, so the schema string is written once.
    async for session in get_session_for_schema(MODULE_SCHEMA):
        yield session
```

Why one constant, imported by both runtime and migrations: the schema a request
**writes into** and the schema a migration **creates** can then never drift apart.
If you hardcoded `"widgets"` in two places, a typo in one makes the app write to a
schema the migration never built - a silent, ugly failure. One token, two importers.

The session seam routes the schema via a client-side statement rewrite
(`schema_translate_map`), never `SET search_path` - so a connection pooler cannot
leak one request's schema into the next.

---

## 5. Per-module Alembic tree with a PRIVATE version table

Each module has its **own** `migrations/` tree, its **own** version chain, and -
critically - its **own** version table name.

```python
# widgets_app migrations/env.py  (essentials only)
from __future__ import annotations
import os
from alembic import context
from sqlalchemy import schema as sa_schema
import widgets_app.models  # noqa: F401 - registers this module's tables on the shared MetaData
from widgets_app.schema import MODULE_SCHEMA as BASE_SCHEMA
from shared_app.db import Base
from shared_app.db.autogenerate import owner_scoped_include_object
from shared_app.db.schema import validate_schema_name

target_metadata = Base.metadata

# PRIVATE version table - the whole point. Convention: alembic_version_<module>.
VERSION_TABLE = "alembic_version_widgets"

# Optional per-run prefix so parallel CI runs / test isolation never share tables.
_prefix = os.environ.get("SCHEMA_PREFIX", "")
MODULE_SCHEMA = validate_schema_name(
    f"{_prefix}_{BASE_SCHEMA}" if _prefix else BASE_SCHEMA,
    label="widgets schema",
)

# Autogenerate must only see THIS module's tables. The shared MetaData carries
# every module's tables, so without this filter an autogenerate run from the
# widgets tree would "see" gallery's tables reflected from the live DB and
# propose dropping them. Derive the owned set from this package's own mappers.
_OWNED = {
    m.class_.__tablename__
    for m in Base.registry.mappers
    if m.class_.__module__.startswith("widgets_app.")
}
INCLUDE_OBJECT = owner_scoped_include_object(_OWNED)
```

```python
# widgets_app migrations/versions/0001_widgets_table.py
revision = "0001"
down_revision = None          # first migration in THIS module's chain
```

Why the private version table matters:

- All modules share one physical database. Alembic's default version table is
  `alembic_version` - a single row that says "this DB is at revision X". If two
  modules shared it, module B's `upgrade head` would see module A's revision, not
  recognize it, and either error or clobber it. A **per-module** version table
  (`alembic_version_widgets`) means each module's migration history is completely
  independent: you can `upgrade`, `downgrade`, or `stamp` one module's schema
  without the other module's chain being involved at all.
- The version table lives **in the module's own schema** (`version_table_schema =
  MODULE_SCHEMA`), so even the bookkeeping row is isolated.
- `down_revision = None` on the first migration: each module's chain is its own
  root, not a continuation of another module's.

This is what makes **independent deploy/rollback** real rather than aspirational:
migration state is per module, so release state is per module.

---

## 6. Per-module CLAUDE.md (the contract card)

Every module ships a `CLAUDE.md` at its root that states its contract in prose so
the next engineer (or agent) does not have to reverse-engineer it. Keep it short
and factual. A good skeleton:

```markdown
# Widgets Module
Last verified: YYYY-MM-DD

## Purpose
One paragraph: what this module does and what it deliberately does NOT do.

## Contracts
- Exposes: each route, its method/path, its response model, its auth posture.
  (e.g. GET /api/v1/widgets/health -> {"status":"ok"} (unauthenticated))
- Guarantees: error body format, /health always unauthenticated, additive-only, etc.
- Expects: shared primitives it depends on; its own Postgres table + schema;
  any config keys it reads at runtime.

## Dependencies
- Uses: shared package, sqlalchemy, pydantic, ... (NEVER a sibling module).
- Used by: the monolith composition root; future: its own extracted service.
- Boundary: MUST NOT import sibling modules. Enforced by import-linter.

## Key Decisions / Invariants / Gotchas
- The load-bearing choices, the rules that must stay true, and the traps.
```

The value is that the contract is written down at the boundary, next to the code,
and dated - so drift is visible.

---

## 7. Import-linter enforcement of the layering

Prose rules rot. Encode them as import contracts that fail CI. Using
`import-linter` (`lint-imports`), the module contract becomes three machine-checked
guarantees in the root `pyproject.toml`:

```toml
[tool.importlinter]
root_packages = ["shared_app", "api_root", "widgets_app", "gallery_app"]

# (a) Modules are mutually independent - no module imports a sibling.
[[tool.importlinter.contracts]]
name = "Modules are mutually independent (no sibling imports)"
type = "independence"
modules = ["widgets_app", "gallery_app"]   # append every module here

# (b) FCIS per module - api (shell) may import core (pure); core may not import api.
#     NOTE: import-linter `layers` is OUTERMOST-FIRST. ["api", "core"] forbids
#     core -> api. Reversing the two lines silently enforces the OPPOSITE rule
#     while still passing, so lock the order with a unit test.
[[tool.importlinter.contracts]]
name = "FCIS layers in widgets_app"
type = "layers"
layers = ["api", "core"]
containers = ["widgets_app"]

# (c) Shared sits BELOW everything - it must not import a module or the root.
[[tool.importlinter.contracts]]
name = "Shared must not import the composition root or any module"
type = "forbidden"
source_modules = ["shared_app"]
forbidden_modules = ["api_root", "widgets_app", "gallery_app"]
```

Why each contract exists:

- **independence** - the moment `widgets_app` imports `gallery_app`, the two are no
  longer separately liftable; you could not extract one without dragging the other.
  The linter makes that regression fail the build instead of being discovered a
  year later during an extraction.
- **FCIS layers** - encodes "core has no I/O" structurally. If someone adds
  `from widgets_app.api.repository import ...` inside `core/`, CI goes red.
- **shared-below** - the shared foundation (auth, DB base, agent client) must never
  depend upward on a feature module, or the dependency graph becomes cyclic and
  nothing can be built or extracted in isolation.

Tip that pays off: derive the "list every module" contracts from the module
folders on disk in a unit test, so adding a module without registering it in the
contracts fails a test rather than silently escaping enforcement.

---

## 8. Scaffold, don't copy

**Never create a new module by cloning a sibling folder.** Generate it from a
scaffold instead.

Copying a sibling is how drift and hidden coupling enter:

- You inherit the sibling's `pyproject.toml` name, its schema token, its version
  table name, its CLAUDE.md - and you WILL miss renaming one of them. A missed
  `MODULE_SCHEMA` or `alembic_version_<name>` means the new module quietly shares
  the old module's schema or migration bookkeeping. That is a data-corruption bug,
  not a lint nit.
- You inherit whatever pragmatic exceptions the sibling accumulated, without the
  context that justified them.

A scaffold (a generator, even a simple templated one) produces a module that is
**correct by construction**: the package name, `MODULE_SCHEMA`, `VERSION_TABLE`,
the `/health` route, the `router` export, the FCIS folders, and the three
import-linter registrations are all filled from one input (the module name). The
scaffold's job is precisely to make the mechanical, easy-to-miss edits
unmissable.

Rule of thumb: if adding a module involves editing more than a couple of shared
files by hand (the composition root's mount line, the import-linter lists), those
edits should be **done by the scaffold**, and a disk-derived test should verify
none were forgotten.

---

## Checklist - a module is contract-complete when

- [ ] It is its own package (`pyproject.toml`) depending on shared, never a sibling.
- [ ] `core/` is pure (no I/O, no `api/` import); `api/` is the shell.
- [ ] It exports `router: APIRouter` and an unauthenticated `GET /health`.
- [ ] It owns one Postgres schema via a single `MODULE_SCHEMA` token, and reads no
      other module's rows.
- [ ] It has its own Alembic tree with a private `alembic_version_<name>` table in
      its own schema, chain rooted at `down_revision = None`.
- [ ] It ships a dated `CLAUDE.md` contract card.
- [ ] independence + FCIS + shared-below contracts are registered and green.
- [ ] It was generated from a scaffold, not copied from a sibling.
