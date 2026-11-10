# Starter Kit - the worked example this family lacked

Every other file in this skill (module-contract.md, repo-layout.md,
local-dev.md) is prose describing a shape. Nothing in the app-* family ships
a runnable artifact you can point at and say "start from this." This file
and its companion script close that gap:

- [scripts/scaffold_module.py](../scripts/scaffold_module.py) - a stdlib-only
  Python generator that produces one contract-complete module skeleton per
  run. Section 1 below documents what it emits and how to run it.
- This file documents the rest of the picture: the one-time repo assembly a
  scaffolded module drops into, and the clone-then-scaffold workflow that
  ties the two together.

Nothing here is a new pattern. It is the existing module-contract.md,
repo-layout.md, local-dev.md, and app-hosting patterns, arranged as a
checklist and a script instead of prose alone.

## Table of contents

- [1. The scaffold generator](#1-the-scaffold-generator)
- [2. The minimal starter repo](#2-the-minimal-starter-repo)
- [3. The clone-then-scaffold-modules workflow](#3-the-clone-then-scaffold-modules-workflow)
- [4. Where to read next](#4-where-to-read-next)

---

## 1. The scaffold generator

`scripts/scaffold_module.py` generates one new module, correct by
construction, matching [module-contract.md](module-contract.md) exactly.
Stdlib only - no install step, no network call, runs on Windows, macOS, and
Linux.

### Run it

```bash
python scripts/scaffold_module.py widgets
python scripts/scaffold_module.py time_tracking --dest packages/modules
python scripts/scaffold_module.py --help
```

Run it from your repo root so the default `--dest` (`packages/modules`)
lands where repo-layout.md expects it, or point `--dest` anywhere.

### What it produces

```
packages/modules/widgets/
  pyproject.toml            # depends on shared-app, never a sibling module
  alembic.ini                # script_location = migrations
  CLAUDE.md                  # dated contract card (module-contract.md s6)
  widgets_app/
    __init__.py, py.typed
    schema.py                 # MODULE_SCHEMA = "widgets"
    models.py                 # stub; imports MODULE_SCHEMA
    core/
      __init__.py
      example.py               # pure function - no I/O, no api/ import
    api/
      __init__.py
      router.py                # exports `router: APIRouter`
      health.py                 # unauthenticated GET /health
      deps.py                    # schema-scoped session dependency
      contracts.py               # frozen Pydantic request/response models
      repository.py              # DB I/O + ORM->contract projection
      widgets.py                 # the example endpoint
  migrations/
    env.py                     # private alembic_version_widgets version table
    versions/0001_widgets_table.py   # down_revision = None, no-op body
  tests/
    unit/test_example_core.py, test_health.py
    integration/test_widgets_api.py
```

Every mechanical, easy-to-miss edit module-contract.md section 8 warns about
- the package name, `MODULE_SCHEMA`, `VERSION_TABLE`, the `/health` route,
the `router` export - is filled from the one input you gave it: the module
name.

### What it prints (and does NOT write)

The generator only ever writes inside the new module's own directory. It
never edits a shared repo file, so after it runs it prints the three
registrations module-contract.md section 7 and local-dev.md's scaffold
section call out as easy to forget:

- The import-linter contract lines to paste into the root `pyproject.toml`
  (a new per-module FCIS layers contract, plus the module's name added to
  the existing `root_packages`, independence, and shared-below lists).
- The composition root's mount line
  (`app.include_router(widgets_app.api.router.router, prefix="/api/v1/widgets")`).
- The reminder to add an entry to `apps/web/src/registry/registry.tsx` if
  the module has a UI.

It then prints the "close the local loop" commands from local-dev.md:
`alembic upgrade head` for the new module, `lint-imports`, and
`pytest <module>/tests`.

### Failure modes (by design)

- **Module directory already exists** - refuses to run, exit code 1. It
  never merges into or overwrites a module (module-contract.md section 8:
  generate, don't clone-and-rename). Delete the directory yourself first if
  you really mean to regenerate it.
- **Invalid module name** - must be lowercase snake_case starting with a
  letter (`widgets`, `time_tracking`). Rejects Python keywords and names
  that collide with a reserved top-level or layer name (`core`, `api`,
  `shared`, `tests`, and similar).
- **Long path on Windows** - a module scaffolded several directories deep
  under a long repo checkout path can approach Windows' ~260-character
  `MAX_PATH`. The generator writes through the `\\?\` extended-length
  prefix internally so this does not surface as a confusing
  `FileNotFoundError`; it is called out here because the failure mode is
  easy to misdiagnose if you hit it anywhere else in the toolchain (git,
  editors, CI runners on Windows agents).

### What it deliberately does not do

The generated `api/` and `core/` files import `fastapi`, `sqlalchemy`,
`pydantic`, and `shared_app` - none of which the generator itself imports
or needs installed. Those files are meant to compile and run once the
module lands in a repo that already has those on its dependency path. This
tool scaffolds **one module**, not a whole repo; section 2 covers the repo
shape it expects to drop into.

---

## 2. The minimal starter repo

The scaffold generator assumes a repo already shaped like
[repo-layout.md](repo-layout.md). That repo shape is not itself generated by
any script in this skill - it is a one-time assembly a builder does when
standing up a brand-new hosted tool, then never repeats. Treat the list
below as the checklist for that one-time assembly. Nothing here duplicates
the full detail already written elsewhere; each item cross-links the file
that owns it.

```
repo-root/
  pyproject.toml              # workspace root - see checklist item 1
  compose.yaml                 # local Postgres - see checklist item 2
  apps/web/                     # SPA shell - see checklist item 3
  services/api/                  # composition root - see checklist item 4
  packages/shared/python/         # shared_app foundation - see checklist item 5
  packages/modules/                # EMPTY at first - scaffold_module.py fills this
  infra/cloudformation/             # parameterized stacks - see checklist item 6
  infra/buildspecs/                  # CI stage scripts - see checklist item 6
  services/api/Dockerfile             # one image - see checklist item 7
```

### Checklist

1. **Workspace root `pyproject.toml`.** Declares workspace members by glob
   (`packages/shared/python`, `packages/modules/*`, `services/*`, `tools/*`)
   and holds the `import-linter` contracts (independence, FCIS layers per
   module, shared-below). Starts with just the `shared_app` member and the
   two structural contracts; the scaffold generator prints the lines to add
   per module from here on. Full shape: repo-layout.md, "The workspace root
   ties it together."

2. **`compose.yaml` for local Postgres.** One `postgres:16` service, a
   throwaway `app`/`app`/`app` user/password/db, port 5432 exposed to the
   host, a named volume, a healthcheck. This is the ONE piece of
   infrastructure-as-code that runs on a laptop - everything else in this
   checklist is cloud-only. Full file and the `docker compose up -d db` /
   reset workflow: local-dev.md, "Local Postgres in Docker."

3. **`apps/web/` - the SPA shell.** A single React/Vite app with a
   registry-driven router (`src/registry/registry.tsx` exports
   `MODULE_REGISTRY`; `src/App.tsx` builds routes from it, one entry per
   module that has a UI). Starts with an empty registry and a landing page;
   each scaffolded module with a UI adds one entry, never a new router file.
   Full shape and the runtime-config-fetch pattern (`/api/v1/auth/config`,
   never baked in at build time): repo-layout.md, "apps/web - the SPA shell,
   and it is registry-driven"; aws-architecture.md section 4 for why config
   is fetched at runtime.

4. **`services/api/` - the monolith composition root.** A thin FastAPI
   `create_app()` factory that wires the shared cross-cutting stack (error
   handlers, request-id/access-log middleware), the auth seam
   (real Entra validator in the cloud, a dev-stub principal locally), serves
   the built SPA with an SPA-aware static handler, and mounts every module's
   `router` at `/api/v1/<module>`. Starts with zero modules mounted; each
   scaffold run adds one `include_router` line here (the generator prints
   the exact line - see section 1). Root-level `GET /health` (unauthenticated,
   distinct from each module's own `/health`) lives here too - see
   module-contract.md section 3 and aws-architecture.md section 3.1 for why
   App Runner probes THIS one. Full shape: repo-layout.md, "services/ - thin
   composition roots"; local-dev.md, "Running the backend."

5. **`packages/shared/python/` - the `shared_app` foundation.** The
   cross-cutting primitives every module builds on and may never build
   upward from: the JWT-validating/dev-stub auth seam, the SQLAlchemy
   `Base`/`MetaData` plus the schema-scoped session helper
   (`get_session_for_schema`) every module's `api/deps.py` imports, typed
   config, and the RFC-9457 error handlers. This is the one package that
   must exist BEFORE the first module is scaffolded, because every
   generated `api/deps.py` and `migrations/env.py` imports from it
   unconditionally. Full shape: repo-layout.md, "packages/shared/ - the
   cross-module foundation."

6. **`infra/` - the parameterized CloudFormation the pipeline expects.**
   This skill does not own infrastructure-as-code; it only needs the repo
   to have the two places the pipeline reads from:
   `infra/cloudformation/` (the two reusable, parameterized stack templates
   - a per-service pipeline and a generalized app-layer stack - instantiated
   per service by supplying parameters, never by hand-writing new YAML) and
   `infra/buildspecs/` (the Source -> Test -> Build -> Migrate -> DeployDev
   -> ScanGate -> ApproveProd -> PushProdImage -> MigrateProd -> DeployProd
   stage scripts). Do not author these from scratch - the full pattern,
   parameter tables, the two-account model, and the two-pass ECR-gated
   bootstrap are in **app-hosting**: `references/cloudformation-pipeline.md`
   and `references/aws-architecture.md`. Genericize-before-adopt scrub list:
   `references/deploy-runbook.md` in that same skill.

7. **One `Dockerfile` per composition root.** `services/api/Dockerfile`
   builds the SPA and the FastAPI backend into ONE image (see
   aws-architecture.md section 4, "the one image principle" - nothing
   environment-specific baked in; the same bytes run in dev and prod). It
   copies in `packages/shared/` plus every module under `packages/modules/`
   that this composition root mounts. When a module is later extracted into
   its own service (`services/<module>/`), that service gets its own
   Dockerfile copying only `packages/shared/` and that one module - see
   `topology-independence.md`. Binds `0.0.0.0:${PORT:-8080}`; answers
   `GET /health` before any auth is wired.

The result of doing this checklist once: an empty-but-real platform with no
product modules yet, ready for `scaffold_module.py` to fill
`packages/modules/` one module at a time.

---

## 3. The clone-then-scaffold-modules workflow

The point of sections 1 and 2 together: assemble the starter repo shape
ONCE, then every feature after that is "clone (or you already have the
repo), scaffold a module, wire it in, migrate, test" - never "hand-copy a
sibling module." In order:

1. **Clone the repo** (or, for the very first module ever, finish the
   section 2 checklist first). `git clone <repo> && cd <repo>`.
2. **Install the workspace.** `uv sync` (installs `shared_app` + every
   existing module + every service); `cd apps/web && npm install`.
3. **Start local Postgres.** `docker compose up -d db`, wait for
   `pg_isready`. See local-dev.md, "Local Postgres in Docker."
4. **Scaffold the module.**
   `python scripts/scaffold_module.py <name>`. See section 1 above.
5. **Wire it in** - the three registrations the generator printed:
   - Add the import-linter contract lines to the root `pyproject.toml`.
   - Add the `include_router(...)` line to `services/api`'s `create_app()`.
   - If it has a UI, add one entry to `apps/web/src/registry/registry.tsx`.
6. **Migrate.**
   `uv run alembic -c packages/modules/<name>/alembic.ini upgrade head` -
   creates the module's schema and applies its (initially no-op) first
   revision.
7. **Verify.** `uv run lint-imports` (independence + FCIS + shared-below all
   green); `uv run pytest packages/modules/<name>/tests` (the shipped
   `test_health.py` and the example unit test both pass out of the box).
8. **Build the real feature** - replace the example `core/`, `api/`,
   `models.py`, and tests with the module's actual logic. The scaffold's job
   ends here; module-contract.md is the reference for everything you add.
9. **Run the whole stack** to see it end to end: start `services/api` and
   `apps/web` per local-dev.md's "Running the backend and the SPA," and
   confirm the new module's route answers through the SPA proxy.
10. **Ship it** through the pipeline described in app-hosting's
    `cloudformation-pipeline.md` - no new infrastructure per module, only
    new `SourceFilePaths` entries pointing at it.

Repeat from step 4 for the next module. The repo only grows by module
directories and by the small, mechanical wiring edits in step 5 - never by
copying a sibling.

---

## 4. Where to read next

| Question | Read |
|---|---|
| The exact shape a scaffolded module must have | [module-contract.md](module-contract.md) |
| Why repo layout and runtime topology are independent axes | [topology-independence.md](topology-independence.md) |
| Where every top-level folder lives and why | [repo-layout.md](repo-layout.md) |
| Running the whole stack on a laptop, step by step | [local-dev.md](local-dev.md) |
| The two reusable CloudFormation templates and the pipeline stages | app-hosting `references/cloudformation-pipeline.md` |
| App Runner, private ingress, RDS, Bedrock, Entra - the hosting shape | app-hosting `references/aws-architecture.md` |
| Genericize-before-adopt scrub list, step-by-step deploy | app-hosting `references/deploy-runbook.md` |
| Deciding whether to build a hosted tool at all, first-cut module list | [discovery-and-design-brief.md](discovery-and-design-brief.md) |
