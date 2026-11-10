# Module Contract - TypeScript/Node Parity Spec

Companion to [module-contract.md](module-contract.md). That file is the
contract; this file is a translation, not a second contract. Every rule
there still applies - FCIS split, unauthenticated `/health`,
schema-per-module, private migration history, a dated CLAUDE.md,
scaffold-don't-copy. This file only answers "what is the TS/Node shape."

verify-current: library claims below checked 2026-09-11 against each
project's own docs/npm page. Pin exact versions in the lockfile, not from
memory - this is a starting point, not a floor.

## Table of contents

1. [Decision gate - Python stays the default](#1-decision-gate)
2. [Parity table](#2-parity-table)
3. [The contract items, TS shape](#3-contract-items)
4. [Testing](#4-testing)
5. [What does not translate - honest deltas](#5-deltas)
6. [Deployment - unchanged](#6-deployment)

---

<a name="1-decision-gate"></a>
## 1. Decision gate - Python stays the default

Python/FastAPI is the default backend for every new module in this suite.
Choose TypeScript/Node ONLY for one of these named reasons:

- **Client team standard** - the client's engineers will own or co-maintain
  this code long-term and TS/Node is their house stack.
- **Existing Node estate** - the module extends or sits beside a Node
  service the client (or the firm) already runs.
- **JS-ecosystem dependency** - the module's core value depends on a
  library that only exists (or is well-maintained) in npm, with no
  acceptable Python equivalent.

"The developer prefers TS," "might be faster to write," and "not sure yet"
do not qualify - scaffold in Python per module-contract.md otherwise.

**Never mix Python and TS backend modules inside one app's module set.** A
composition root mounts modules of ONE language family. A need spanning
both is an argument for two composition roots (topology-independence.md) -
a Python monolith and a TS extracted service over HTTP - never one root
importing both a Python and an npm package side by side; mixing defeats
uniform mounting and doubles the toolchain per module.

---

<a name="2-parity-table"></a>
## 2. Parity table

| Python/FastAPI concern | TS/Node equivalent | Why |
|---|---|---|
| FastAPI | **Fastify** | vs Express/Hono - below. |
| Pydantic | **zod** + **fastify-type-provider-zod** | Schema-first validation that also drives route typing, same role Pydantic plays for FastAPI. |
| SQLAlchemy + Alembic | **Drizzle ORM** + **drizzle-kit** | vs Prisma - below. |
| import-linter | **eslint-plugin-boundaries** | vs dependency-cruiser - below. |
| pytest + testcontainers | **Vitest** + **testcontainers-node** | Same real-Postgres integration discipline, TS-native runner. |
| uvicorn | **node's built-in runtime** (`node --watch` in dev, plain `node` in prod) | No ASGI-server equivalent needed; `--watch` gives uvicorn's `--reload`. |

**Fastify over Express or Hono.** verify-current (2026-09-11): Fastify
sustains roughly 2-3x Express's JSON throughput and ships built-in
JSON-schema validation, exactly the seam `fastify-type-provider-zod` plugs
into. Express has the deepest middleware ecosystem but no built-in
validation. Hono targets edge/serverless cold-starts; these modules run in
a long-lived App Runner container behind the VPN (app-hosting), not at the
edge, and Hono's middleware/auth ecosystem is the least mature of the
three. Fastify's schema-driven-route design maps onto FastAPI's, so it wins.

**Drizzle over Prisma.** verify-current (2026-09-11): Drizzle is code-first
- tables are TS values, no schema DSL, no generation step - and
`drizzle-kit generate` emits plain timestamped SQL files into a folder you
point at per module, mapping directly onto Alembic's per-module
`migrations/versions/` chain: one config, one `out` folder, one migrations
table per module (section 3.4). Prisma is schema-first (one `.prisma` file
diffed against a shadow database); multi-file schema exists as of Prisma
6.x, but the history and shadow-db mechanics still assume ONE project
schema and history table - forking that into N per-module histories fights
the tool. Per-module migration independence is a hard requirement, so
Drizzle wins.

**eslint-plugin-boundaries over dependency-cruiser.** Pick ONE so every
module is checked the same way. boundaries runs inside the same ESLint
pass a TS module already needs, giving instant in-editor/CI feedback the
way `lint-imports` does - no second tool or config format.
dependency-cruiser is stronger for graph visualization and catches a few
things boundaries does not (orphaned files, precise cycles), but that is a
diagnostic strength, not a per-commit gate. See section 5 for where
boundaries' rigor falls short of import-linter's.

---

<a name="3-contract-items"></a>
## 3. The contract items, TS shape

### 3.1 Directory layout

```
packages/modules/widgets/
  package.json          # own package; depends on shared, never a sibling
  tsconfig.json          # extends the repo-root base config
  drizzle.config.ts       # migration config (3.4)
  CLAUDE.md                # dated contract card (module-contract.md s6)
  src/
    schema.ts               # MODULE_SCHEMA = "widgets" - the ONE schema token
    models.ts               # Drizzle table definitions, this module's pgSchema
    core/                    # FUNCTIONAL CORE - pure, no I/O
      pagination.ts, reconcile.ts
    api/                     # IMPERATIVE SHELL - Fastify plugin, DB, side effects
      plugin.ts               # required: exports a Fastify plugin (3.5)
      health.ts                # required: unauthenticated GET /health
      db.ts                      # schema-scoped Drizzle client factory
      contracts.ts                # zod request/response schemas
      repository.ts                # DB I/O + row->contract projection
      widgets.ts                    # the actual routes
  drizzle/0001_widgets_table.sql  # this module's chain, from drizzle-kit
  tests/unit/, tests/integration/   # integration needs Postgres (testcontainers-node)
```

### 3.2 FCIS split, health, and errors

`core/` imports nothing from `api/` or `models.ts`; `api/` may import
`core/`. Enforced by eslint-plugin-boundaries, same intent as
import-linter's `layers` contract - same "outermost-first" gotcha to watch
for (element-type order backwards silently enforces the opposite rule).

```ts
// widgets/src/api/widgets.ts - the shell: owns the DB call, delegates logic to core/
import { resolvePage } from '../core/pagination'   // PURE - lives in core/
import { listWidgets } from './repository'

export const widgetsRoutes: FastifyPluginAsync = async (app) => {
  app.get('/widgets', async (request) => {
    const page = resolvePage(request.query)   // core/ - no I/O
    return listWidgets(app.db, page)           // api/ - the I/O
  })
}

// widgets/src/api/health.ts - unauthenticated, mounted under the module prefix
export const healthRoute: FastifyPluginAsync = async (app) => {
  app.get('/health', { schema: { hide: true } }, async () => ({ status: 'ok' }))
}
```

Same posture as module-contract.md section 3: `/health` is the module's own
liveness signal; the platform's root-level `GET /health` lives on the
composition root regardless of backend language (app-hosting
aws-architecture.md). Auth is enforced once at the edge by a default-deny
hook on the root; module routes add no auth logic of their own.

```ts
// shared/node/src/errors/problem-details.ts - registered ONCE, on the composition root
export function registerProblemDetails(app: FastifyInstance) {
  app.setErrorHandler((error, request, reply) => {
    const status = (error as { statusCode?: number }).statusCode ?? 500
    reply.type('application/problem+json').status(status).send({
      type: 'about:blank', title: error.name || 'Internal Server Error',
      status, detail: error.message, instance: request.url,
    })
  })
}
```

One handler, on the composition root, the same way shared_app registers
RFC-9457 handlers on the Python side - a module never formats its own errors.

### 3.3 Schema-per-module

Drizzle's `pgSchema` is the TS analog of `MODULE_SCHEMA` plus Python's
`schema_translate_map` session seam:

```ts
// widgets/src/schema.ts
export const MODULE_SCHEMA = 'widgets' as const

// widgets/src/models.ts
import { pgSchema, uuid, text, timestamp } from 'drizzle-orm/pg-core'
import { MODULE_SCHEMA } from './schema'

const widgetsSchema = pgSchema(MODULE_SCHEMA)
export const widget = widgetsSchema.table('widget', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
})
```

The module's Drizzle client (`api/db.ts`) imports only its own `../models`
- same rule as Python: a module needing another module's data calls its
HTTP API, never its rows.

### 3.4 Per-module migrations

```ts
// widgets/drizzle.config.ts
import type { Config } from 'drizzle-kit'

export default {
  schema: './src/models.ts',
  out: './drizzle',                 // this module's OWN migration folder
  dialect: 'postgresql',
  dbCredentials: { url: process.env.DATABASE_URL! },
  // Private "version table" equivalent to alembic_version_widgets - keeps
  // this module's bookkeeping out of every other module's tracking table.
  migrations: { table: 'drizzle_migrations_widgets', schema: 'widgets' },
} satisfies Config
```

Run per module, never a repo-root config: `drizzle-kit generate --config
.../drizzle.config.ts`, then `migrate` the same way - each chain starts
empty and advances independently, the deploy/rollback independence
Alembic gives.

### 3.5 Composition root and runtime config

```ts
// services/api/src/app.ts - the TS monolith composition root (illustrative)
import Fastify from 'fastify'
import { widgetsRoutes } from '@modules/widgets/api/plugin'
import { registerProblemDetails } from '@shared/node/errors/problem-details'

export function createApp() {
  const app = Fastify()
  registerProblemDetails(app)
  app.register(widgetsRoutes, { prefix: '/api/v1/widgets' })  // one line per module
  return app
}
```

`services/<module>/` (an extracted-service root) registers exactly one
module's plugin at the same prefix - Fastify's `register` standing in for
`include_router`. Reach into a module via a path alias (`@modules/widgets`,
`@shared/node`) off a repo-root `baseUrl`, mirroring frontend-react-vite.md's
`@shared/*` convention - never a relative import climbing out of a folder.

Node has no bundle-baking step like a Vite SPA, but the principle holds:
read every per-environment value (`DATABASE_URL`, the Entra tenant id,
feature flags) from `process.env` at container **start**, never baked in
at build time - repo-layout.md's runtime-config-not-build-time rule.

---

<a name="4-testing"></a>
## 4. Testing

Three tiers, same shape as Python, TS-native tools:

- **Unit** - Vitest against `core/` only. No Postgres, no Fastify instance,
  runs in milliseconds - the analog of pytest's `tests/unit/`.
- **Integration** - Vitest + `@testcontainers/postgresql`
  (testcontainers-node). Each suite starts its own real Postgres container
  in `beforeAll`, runs that module's `drizzle-kit migrate` against it, then
  exercises `api/` end to end - the analog of pytest + testcontainers.
  verify-current (2026-09-11): testcontainers-node is the standard 2026
  approach per current framework docs; one container per suite.
- **Contract tests against the module's OpenAPI** - register
  `@fastify/swagger` with the zod type provider so the OpenAPI document
  generates FROM the `contracts.ts` zod schemas the routes already validate
  against (no hand-maintained second copy). A contract test asserts the
  document still contains the routes a consumer depends on - catches a
  breaking change the same way an explicit `contracts.py` does on Python.

---

<a name="5-deltas"></a>
## 5. What does not translate - honest deltas

- **import-linter rigor has no exact TS equivalent.** import-linter
  analyzes the real import graph regardless of file naming.
  eslint-plugin-boundaries approximates this with glob-matched "element
  types" - a folder rename or new file outside the configured glob
  silently stops being checked, where import-linter would still catch it
  wherever the file lives. Verify the boundaries config stays in sync with
  the module folders on disk via a disk-derived test (module-contract.md
  section 7's "derive from disk" tip).
- **Async model differs, not just syntax.** Python's ASGI workers are
  typically multiple OS processes, each one asyncio loop, so CPU-bound work
  in one request does not starve every other. Node is single-threaded per
  process by default; CPU-bound work (JSON transforms, crypto, image
  processing) blocks that thread and needs an explicit `worker_threads`
  pool, with no transparent multi-process fallback.
- **Packaging is unchanged.** One image per composition root, same
  Dockerfile pattern as Python (starter-kit.md item 7) - `node` instead of
  `python`/`uvicorn`. Extraction is still a new `services/<module>/` root
  with its own Dockerfile, not a code move - topology-independence.md
  holds regardless of language.

---

<a name="6-deployment"></a>
## 6. Deployment - unchanged

A TS/Node module deploys through the exact same pipeline and
infrastructure as a Python module: one container per composition root, AWS
App Runner behind the VPN, RDS Postgres, the same parameterized
CloudFormation, the same dev/prod two-account two-pass pipeline, config
fetched at runtime rather than baked at build. Nothing in app-hosting is
Python-specific - see app-hosting references/aws-architecture.md (hosting
shape) and references/cloudformation-pipeline.md (pipeline stages).
