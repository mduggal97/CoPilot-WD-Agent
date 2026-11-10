# Local Dev - run the whole stack on a laptop

Modeled on the reference hosted-app architecture. Patterns only - every command,
name, and value below is invented and generic. No account ids, no real hostnames.

The goal of this file: get a new engineer (or an agent) from a fresh clone to a
running platform - SPA in a browser, FastAPI backend answering, Postgres holding
data, a module or two mounted - with **no AWS access, no corporate proxy
dependency, and no Entra tenant**. The cloud shape (App Runner + Bedrock + RDS +
Entra) is in `app-hosting`; this is the laptop shape that mirrors it closely
enough that code written locally runs unchanged in the cloud.

## Table of contents

- [The one idea: local differs only by CONFIG](#the-one-idea)
- [Prerequisites](#prerequisites)
- [0 to running - the ordered checklist](#zero-to-running)
- [Local Postgres in Docker](#local-postgres)
- [Per-module Alembic migrations, locally](#local-migrations)
- [Seed data](#seed-data)
- [The provider seam: anthropic-direct locally, Bedrock in cloud](#provider-seam-local)
- [Stubbing the Entra auth-config endpoint](#auth-stub)
- [Running the backend (composition root) and the SPA](#running)
- [The scaffold generator - create a new module](#scaffold)
- [Common local-dev failure modes](#failure-modes)

---

<a name="the-one-idea"></a>
## The one idea: local differs only by CONFIG, never by code

The whole platform is built so that **nothing environment-specific is baked into
the code** (see `topology-independence.md` and the hosting skill's "one image"
principle). Local dev is just the extreme case of that: the same module packages,
the same composition root, the same SPA bundle - pointed by environment variables
at a laptop-local Postgres, at the Anthropic API direct instead of Bedrock, and at
a stubbed auth-config instead of a real Entra tenant.

If you ever find yourself editing a module's Python to make it run locally, stop:
that is a config seam that is missing, not a local-only code path. Add the seam.
The three seams that make laptop-dev work are already in the architecture:

| Seam | Cloud | Local |
|---|---|---|
| Model provider (`provider-seam.md` in app-agentic) | `MODEL_PROVIDER=bedrock` | `MODEL_PROVIDER=anthropic` |
| Database URL | RDS DSN from Secrets Manager | `postgresql+asyncpg://.../app` to the Docker container |
| Auth config (`/api/v1/auth/config`) | real Entra tenant/client ids | a dev stub the SPA falls back to |

Everything else is identical.

---

<a name="prerequisites"></a>
## Prerequisites

- **Python** (the version in the repo's `.python-version` / `pyproject.toml`) and
  **uv** for the workspace (the repo is a uv workspace - see `repo-layout.md`).
- **Node + npm** for the SPA (`apps/web`).
- **Docker** (or Podman) for local Postgres. Nothing else needs a container
  locally - the backend and SPA run as plain host processes so you get fast
  reload and normal debuggers.
- An **Anthropic API key** for the model calls, IF you are exercising the agentic
  layer locally. A tool with no agent features needs no key. Never commit it -
  it goes in a gitignored `.env` (the secrets guard in app-harness will bark
  if you try to read it into context).
- You do **not** need: AWS credentials, VPN, the corporate proxy, or an Entra app
  registration. That is the point of this file.

---

<a name="zero-to-running"></a>
## 0 to running - the ordered checklist

Do these in order. Each step is expanded in its own section below.

1. **Clone and install.**
   ```bash
   git clone <repo> && cd <repo>
   uv sync                       # installs the workspace: shared + every module + services
   (cd apps/web && npm install)  # SPA deps
   ```

2. **Write a local `.env`** at the repo root (gitignored). Minimum viable:
   ```bash
   # --- database (points at the Docker Postgres from step 3) ---
   DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/app
   # --- model provider: anthropic-direct locally (off the corporate proxy) ---
   MODEL_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...          # only if using the agentic layer
   # --- auth: run the API with the auth gate in dev-stub mode ---
   AUTH_MODE=dev_stub                    # see the auth-stub section
   # --- spend cap so a runaway local loop cannot burn your key ---
   WEEKLY_BUDGET_MICROS=2000000          # $2.00; tune down for local
   ```
   Keep this file out of git and out of the model's context (do not `cat` it in a
   prompt). Use `.env.example` (committed, values blanked) as the template.

3. **Start local Postgres in Docker** (next section). Wait for it to accept
   connections.

4. **Create each module's schema and run its migrations** (migrations section).
   Every module owns its own schema and its own Alembic tree, so this is a loop
   over modules, not one global `upgrade head`.

5. **Load seed data** (seed section) - a small, obviously-fake dataset so the UI
   has something to render and integration tests have fixtures.

6. **Start the backend** - the monolith composition root, which mounts every
   module and serves the auth-config stub:
   ```bash
   uv run uvicorn api_root.app:app --reload --host 127.0.0.1 --port 8080
   ```
   Confirm `GET http://127.0.0.1:8080/health` returns `{"status":"ok"}` and
   `GET http://127.0.0.1:8080/api/v1/auth/config` returns the dev stub.

7. **Start the SPA dev server** (Vite), proxying `/api` to the backend:
   ```bash
   cd apps/web && npm run dev        # serves the SPA on http://localhost:5173
   ```
   Open the printed URL. The SPA fetches `/api/v1/auth/config`, sees the dev stub,
   and renders without a real sign-in.

8. **(Optional) Scaffold a new module** when you are adding a feature - use the
   generator, never a copy (scaffold section).

At this point the whole stack is on your laptop: browser -> SPA (Vite) -> `/api`
proxy -> FastAPI monolith -> Postgres (Docker), with model calls going to the
Anthropic API direct. You are ready to build.

---

<a name="local-postgres"></a>
## Local Postgres in Docker

One throwaway Postgres container is all local dev needs. A `compose.yaml` at the
repo root keeps it reproducible:

```yaml
# compose.yaml  (local dev only - never a deployment artifact)
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app        # local-only throwaway credential, matches DATABASE_URL
      POSTGRES_DB: app
    ports:
      - "5432:5432"                 # exposed to the host so the backend (a host process) can reach it
    volumes:
      - pgdata:/var/lib/postgresql/data   # persists across restarts; delete the volume to reset
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 3s
      timeout: 3s
      retries: 10
volumes:
  pgdata:
```

```bash
docker compose up -d db                    # start it detached
docker compose exec db pg_isready -U app   # wait until it says "accepting connections"
```

Why one shared database with schema-per-module (not one database per module),
even locally: it mirrors the cloud shape exactly (RDS is one shared instance, one
schema per module - see the hosting skill), so a migration or a cross-schema
assumption that breaks in the cloud also breaks locally. A different local
topology would hide exactly the bugs local dev exists to catch.

To **reset to empty**: `docker compose down -v` (the `-v` drops the `pgdata`
volume), then re-run migrations and seed. Fast and total.

---

<a name="local-migrations"></a>
## Per-module Alembic migrations, locally

Each module owns its own Alembic tree and its own private version table
(`alembic_version_<module>`) in its own schema - see `module-contract.md`
section 5. So "migrate the database" locally is **a loop over modules**, each
run from its own tree, not a single global command.

The schema itself is created by the migration chain's first revision (or by a
tiny bootstrap the shared db layer exposes) - a module never assumes its schema
pre-exists. A generic driver script:

```bash
# tools/migrate-local.sh  (illustrative) - upgrade every module against local Postgres
set -euo pipefail
export DATABASE_URL="${DATABASE_URL:?set DATABASE_URL first}"

for mod in packages/modules/*/ ; do
  name="$(basename "$mod")"
  if [ -f "${mod}alembic.ini" ]; then
    echo "== migrating ${name} =="
    # -c points at THIS module's alembic.ini; its env.py knows its own schema
    # and its private version table, so modules never collide.
    uv run alembic -c "${mod}alembic.ini" upgrade head
  fi
done
```

```bash
bash tools/migrate-local.sh
```

Working on **one** module? Just run that one tree:

```bash
uv run alembic -c packages/modules/widgets/alembic.ini upgrade head
```

Authoring a **new** migration for a module (autogenerate against the live local
DB, scoped to that module's tables only - the `owner_scoped_include_object`
filter in `env.py` keeps autogenerate from "seeing" other modules' tables):

```bash
uv run alembic -c packages/modules/widgets/alembic.ini revision \
  --autogenerate -m "add widget archived flag"
# THEN read the generated file before applying it - autogenerate is a draft, not a decision.
uv run alembic -c packages/modules/widgets/alembic.ini upgrade head
```

KT note: because each module's chain is rooted at `down_revision = None` and uses
its own version table, you can `downgrade`/`stamp`/`upgrade` one module locally
without touching another - the same independent-rollback property the cloud
relies on. If a global `alembic upgrade head` is the only way you can migrate, the
per-module trees have been merged by mistake; fix that, not the symptom.

---

<a name="seed-data"></a>
## Seed data

Local dev needs a small, **obviously fake** dataset so the SPA renders real-looking
screens and integration tests have fixtures. Keep it:

- **Generic and synthetic.** Never a client's real data, never a tenant extract,
  never PII - not even locally (see the suite's "no customer data in dev tenants"
  standing rule; it applies to laptops too). Names like `Acme Widget`, ids like
  `widget-0001`, dates that are clearly placeholders.
- **Per-module and idempotent.** Each module ships its own seed routine that
  writes only into its own schema and is safe to run twice (upsert, or
  delete-then-insert within the module's schema). A module never seeds another
  module's tables - same isolation rule as everything else.
- **Off the default path in the cloud.** Seeding is a local/dev convenience; gate
  it behind an explicit flag or a dedicated CLI so it can never run against a
  real environment by accident.

A generic entry point:

```bash
# tools/seed-local.sh (illustrative) - each module contributes its own seed step
set -euo pipefail
export DATABASE_URL="${DATABASE_URL:?}"
export ALLOW_SEED=1                    # explicit opt-in; the seed refuses to run without it
for mod in packages/modules/*/ ; do
  name="$(basename "$mod")"
  # convention: a module exposes `python -m <name>_app.seed` when it has seed data
  uv run python -m "${name}_app.seed" 2>/dev/null || echo "(${name}: no seed, skipping)"
done
```

The `ALLOW_SEED` gate is the important part: a seed routine that can silently run
anywhere is a data-integrity hazard. Make writing test data a conscious act.

---

<a name="provider-seam-local"></a>
## The provider seam: anthropic-direct locally, Bedrock in cloud

The agentic layer calls the model through one seam with two backends
(`provider-seam.md` in app-agentic). Which backend answers is chosen by the
`MODEL_PROVIDER` config value - **never** by a code change.

**Locally, use `MODEL_PROVIDER=anthropic`.** Two reasons:

1. **No AWS.** Bedrock needs AWS credentials, a region, and (in the reference
   architecture) the VPC egress path. A laptop off the VPN has none of that. The
   Anthropic API direct needs only an API key.
2. **The corporate-proxy TLS problem does not apply off-network.** The reason
   Bedrock/boto3 is the *cloud* default is that the Anthropic SDK's httpx/certifi
   stack fails certificate verification behind the corporate TLS-inspection proxy,
   while boto3 trusts the corporate root. On a laptop that is **off** that proxy
   (home network, or a machine where the corporate root is not intercepting), the
   Anthropic SDK verifies cleanly against the public CA and just works. So local =
   anthropic-direct, cloud = Bedrock, and the seam swaps between them by config.

   Caveat worth stating: if you are running local dev **on** the corporate network
   through the inspection proxy, the Anthropic SDK may still hit
   `CERTIFICATE_VERIFY_FAILED`. Do **not** disable verification to "fix" it (that
   trades a working default for a silently insecure one). Either point
   `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` at the corporate root bundle IT provides,
   or set `MODEL_PROVIDER=bedrock` and use real AWS credentials. The seam supports
   both; the code does not change.

Set the key and provider in `.env` (above). A tool with no agentic features needs
neither and can leave `MODEL_PROVIDER` unset.

---

<a name="auth-stub"></a>
## Stubbing the Entra auth-config endpoint

In the cloud the SPA fetches `GET /api/v1/auth/config` (unauthenticated, no
prefix - the one route besides `/health` that skips the identity gate) to learn
its Entra tenant/client ids at runtime, then signs in via MSAL. Locally you have
no Entra tenant, so you stub that endpoint and let the SPA skip real sign-in.

There are two cooperating halves - the backend serves a dev stub, and the SPA
tolerates it.

### Backend: serve a dev stub from the same route

The auth-config route reads its values from config. In `AUTH_MODE=dev_stub`, it
returns obvious-fake values and the auth middleware installs a **no-op / dev
principal** authenticator instead of the real Entra JWT validator - the same
swappable authenticator seam described in `topology-independence.md` and the MCP
auth seam in app-agentic, just selected to its dev setting.

```python
# shared_app/auth/config_route.py  (illustrative)
from fastapi import APIRouter
from shared_app.config import get_settings

auth_config_router = APIRouter()   # mounted with NO prefix, exempt from the auth gate

@auth_config_router.get("/api/v1/auth/config", include_in_schema=False)
def auth_config() -> dict:
    s = get_settings()
    if s.auth_mode == "dev_stub":
        # Obvious-fake values; the SPA recognizes dev mode and does not attempt MSAL.
        return {
            "mode": "dev_stub",
            "tenant_id": "dev-tenant-0000",
            "client_id": "dev-client-0000",
            "api_scope": "api://dev-client-0000/access_as_user",
        }
    # Real environment: values come from ENTRA_* runtime env vars (see hosting skill).
    return {
        "mode": "entra",
        "tenant_id": s.entra_tenant_id,
        "client_id": s.entra_client_id,
        "api_scope": f"api://{s.entra_client_id}/access_as_user",
    }
```

And the authenticator selection, at the one wiring point (never per route):

```python
# shared_app/auth/seam.py  (illustrative) - default-deny in real envs, dev principal locally
def build_authenticator(settings):
    if settings.auth_mode == "dev_stub":
        # Returns a fixed dev user for every request. LOCAL ONLY - this is opt-in
        # via AUTH_MODE and must never be the default in a deployed image.
        return DevPrincipalAuthenticator(user_id="dev-user", scopes=["access_as_user"])
    return EntraJwtAuthenticator(tenant_id=settings.entra_tenant_id,
                                 client_id=settings.entra_client_id)
```

Two guardrails that keep this from becoming a security hole:

- **Fail closed on the default.** `dev_stub` is opt-in via `AUTH_MODE`. An
  unconfigured or misconfigured deployed image must resolve to the real Entra
  validator (or refuse to start), never silently to the dev principal. Same
  "refuse to boot ungated" posture the MCP auth seam takes.
- **The stub still exercises the real code path.** The SPA still fetches the
  config route, still constructs its auth context from the response, and the
  backend still runs its middleware - you are swapping the *authenticator*, not
  bypassing the *plumbing*. So a bug in how auth wires up is still caught locally.

### SPA: fall back gracefully

The SPA already fetches `/api/v1/auth/config` on boot. In dev mode it reads
`"mode": "dev_stub"` and skips the MSAL redirect, attaching a placeholder identity
so protected calls carry the dev principal. The hosting skill notes the SPA also
falls back to obvious-fake stub values if the fetch fails entirely (no backend
running) - so the shell renders even before the API is up.

---

<a name="running"></a>
## Running the backend (composition root) and the SPA

**Backend** - run the monolith composition root (`services/api`), which mounts
every module, wires the shared cross-cutting stack + the (dev-mode) auth seam, and
serves the auth-config stub:

```bash
uv run uvicorn api_root.app:app --reload --host 127.0.0.1 --port 8080
```

`--reload` restarts on file change - the fast inner loop. Port 8080 mirrors the
container's port in the cloud, so nothing else has to change. Confirm two routes
answer before moving on:

```bash
curl -s http://127.0.0.1:8080/health                 # {"status":"ok"}
curl -s http://127.0.0.1:8080/api/v1/auth/config     # the dev stub JSON
```

Want to run just **one extracted service** instead of the whole monolith (e.g. to
debug the `reports` module in isolation)? Run its composition root instead - same
shape, one module mounted:

```bash
uv run uvicorn reports_svc.app:app --reload --host 127.0.0.1 --port 8081
```

That is the topology-independence property (`topology-independence.md`) paying off
locally: monolith or single-service is a choice of which `app` you launch, not a
code change.

**SPA** - the Vite dev server, proxying `/api` to the backend so the browser stays
same-origin (mirroring the same-origin reverse-proxy shape in the cloud):

```bash
cd apps/web && npm run dev        # http://localhost:5173
```

```ts
// apps/web/vite.config.ts  (the local proxy - illustrative)
export default defineConfig({
  server: {
    proxy: {
      // Browser calls same-origin /api/*; Vite forwards to the local backend.
      '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    },
  },
})
```

Open the printed URL. The registry-driven shell (see `repo-layout.md`) renders a
nav item and route per module in `MODULE_REGISTRY`; each module's UI lazy-loads
when you visit its route.

---

<a name="scaffold"></a>
## The scaffold generator - create a new module

**Never create a module by copying a sibling folder** (`module-contract.md`
section 8 - a missed `MODULE_SCHEMA` or version-table rename is a data-corruption
bug, not a lint nit). Generate it from the scaffold, which fills every
mechanical, easy-to-miss edit from one input (the module name):

```bash
# tools/new-module.py <name>  (illustrative) - correct-by-construction, not copy-and-rename
uv run python tools/new-module.py gadgets
```

What the generator produces so the contract is correct by construction:

- The package `packages/modules/gadgets/` with its own `pyproject.toml`
  (depends on `shared`, never a sibling), `alembic.ini`, and dated `CLAUDE.md`.
- `gadgets_app/schema.py` with `MODULE_SCHEMA = "gadgets"` - the one schema token.
- `core/` (pure) and `api/` (shell) folders, a `router` export, and an
  unauthenticated `GET /health`.
- `migrations/` with `env.py` carrying a **private** `alembic_version_gadgets`
  table and a first revision rooted at `down_revision = None`.
- The three registrations that are easy to forget by hand: the module added to the
  monolith composition root's mount list, to the SPA `MODULE_REGISTRY` (if it has
  UI), and to the `import-linter` independence contract in the root
  `pyproject.toml`.

After generating, close the local loop:

```bash
uv run alembic -c packages/modules/gadgets/alembic.ini upgrade head   # create its schema + tables
uv run lint-imports                                                    # independence/FCIS/shared-below all green
uv run pytest packages/modules/gadgets                                 # its shipped test_health passes
```

A disk-derived test (see `module-contract.md` section 8) should verify no module
was added without its contract registrations - so a hand-edit that skips the
scaffold fails a test rather than silently escaping enforcement.

---

<a name="failure-modes"></a>
## Common local-dev failure modes

- **`CERTIFICATE_VERIFY_FAILED` on the first model call.** You are on the
  corporate TLS-inspection proxy with `MODEL_PROVIDER=anthropic`. Point
  `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` at the corporate root, or switch to
  `MODEL_PROVIDER=bedrock` with AWS creds. Never disable verification.
- **`connection refused` to Postgres.** The container is not up yet - wait for
  `pg_isready` to report accepting, and confirm `DATABASE_URL` points at
  `localhost:5432`.
- **`relation ... does not exist` / empty screens.** Migrations or seed did not
  run for that module. Re-run the per-module migrate loop and the seed; remember
  each module migrates from its own tree.
- **SPA loads but every `/api` call 404s or CORS-errors.** The Vite `/api` proxy
  is not pointed at the backend, or the backend is on a different port than the
  proxy target. Same-origin proxy is what keeps the browser from needing CORS.
- **A module runs locally but breaks in CI/cloud.** Almost always a config seam
  that was hardcoded for local. Find the value that differs (DB, provider, auth)
  and route it through env/config - never a local-only code branch.
- **Autogenerate proposes dropping another module's tables.** The module's
  `env.py` `owner_scoped_include_object` filter is missing or wrong - autogenerate
  is seeing the shared MetaData's other tables. Fix the filter; do not accept the
  drop.

> Local dev is the cloud shape with three config values flipped - Postgres URL,
> `MODEL_PROVIDER=anthropic`, `AUTH_MODE=dev_stub`. If getting something to run
> locally needs a code change, a config seam is missing. Add the seam, not the
> branch.
