# Repo Layout - where everything lives and why

Modeled on the reference architecture. Patterns only - the tree below is an
invented, generic illustration.

## The shape

One monorepo, four top-level homes: the SPA, the composition roots, the packages
(modules + shared foundation), and the operational scaffolding (infra + tools).
The organizing idea is the one from `topology-independence.md`: **modules are the
liftable units, composition roots decide the runtime shape, and the two are
independent.** The layout exists to keep that separation obvious.

```
repo-root/
  README.md
  pyproject.toml                 # workspace root: members glob + import-linter contracts
  apps/
    web/                         # the SPA shell (React/Vite) - ONE front door
      src/
        App.tsx                  # builds <Routes> from the module registry (no per-module edit)
        registry/
          registry.tsx           # MODULE_REGISTRY - the one place a module plugs into the SPA
          types.ts               # ModuleRegistryEntry shape (id, label, routePrefix, element)
        <module>/                # each module's UI, lazy-loaded (e.g. widgets/, gallery/)
      dist/                      # build output; served by the composition root as static files
  services/                      # THIN composition roots - each mounts some set of module routers
    api/                         # mounts ALL module routers -> the single-container "monolith"
      api_root/app.py            # create_app(): wires shared stack + auth seam, mounts routers, serves SPA
    <module>/                    # mounts ONE module -> an extracted service (e.g. reports/)
      <module>_svc/app.py        # same shape as api/, one router
  packages/
    modules/                     # THE LIFTABLE UNITS - one independent package per feature
      widgets/                   # (see module-contract.md for the full internal shape)
      gallery/
      reports/
    shared/                      # cross-module FOUNDATIONS every module may depend on
      python/                    # -> shared_app: auth, db base/session, agent, model client, config, errors
      ui/                        # shared React components + design tokens (npm-only, no .py)
  infra/
    cloudformation/              # infrastructure-as-code (roles, DB bootstrap, per-service deploy)
    buildspecs/                  # CI build/migrate specs
  tools/                         # platform-owned CLIs and standalone helper services (e.g. mcp-broker)
  docs/
    standards/                   # module contract, testing, house style
    issues/                      # per-issue design notes
```

---

## apps/web - the SPA shell, and it is registry-driven

There is exactly **one** frontend for the whole platform - a single React/Vite SPA
served from one origin. The important pattern is that the SPA does not hardcode
which modules exist. It reads a **module registry**.

`registry.tsx` exports one array. Each entry declares a module's id, its label, the
route prefix it owns, and the React element to render there. Everything else - the
router, the nav drawer, the landing tiles - **derives** from that array:

```tsx
// apps/web/src/registry/registry.tsx  (illustrative)
import { WidgetsModule } from '../widgets/WidgetsModule'
import { GalleryModule } from '../gallery/GalleryModule'
import type { ModuleRegistryEntry } from './types'

export const MODULE_REGISTRY: readonly ModuleRegistryEntry[] = [
  { id: 'widgets', label: 'Widgets', routePrefix: '/widgets', element: <WidgetsModule /> },
  { id: 'gallery', label: 'Gallery', routePrefix: '/gallery', element: <GalleryModule /> },
]
```

```tsx
// apps/web/src/App.tsx  (illustrative) - routes are BUILT from the registry
import { Route, Routes } from 'react-router-dom'
import { MODULE_REGISTRY } from './registry/registry'

export function App() {
  return (
    <Routes>
      {MODULE_REGISTRY.map((entry) => (
        // The module owns its whole subtree: <prefix>/*, resolved client-side.
        <Route key={entry.id} path={`${entry.routePrefix}/*`} element={entry.element} />
      ))}
    </Routes>
  )
}
```

Why this matters:

- **Adding a module to the UI is a single registry entry.** The router, nav, and
  landing page all read the same array, so no other frontend file changes. This is
  the SPA-side mirror of the backend's "mount one router" - both sides add a module
  by touching exactly one wiring point.
- **Route-split + lazy load.** Each module's UI is its own bundle, loaded only when
  its route is visited. The module's element can be `React.lazy`-loaded so the
  initial shell stays small.
- **Backend-only modules are absent by design.** A module that has an API but no UI
  simply has no registry entry - it contributes no nav item and no route. Belonging
  in the registry means "has a UI," not merely "has a router."

### Serving the SPA and deep links

The composition root serves the built SPA (`apps/web/dist`) as static files, and
uses an SPA-aware static handler that **falls back to `index.html` for unmatched
route-like paths**. That is what makes a hard refresh on a deep link (e.g.
`/gallery/123`) work: the server has no such file, but instead of 404 it returns
the shell, and the client-side router resolves the path. Real asset misses
(`/assets/x.js`) and API paths keep their 404 so a typo never silently becomes an
HTML 200. Content-hashed assets are cached immutably; the shell is `no-cache` so a
new deploy is picked up on the next navigation.

### Auth and config are fetched at RUNTIME, not baked in

The SPA bundle ships with **no** tenant id, client id, or API base compiled into
it. On boot it calls an unauthenticated config endpoint (e.g.
`/api/v1/auth/config`) to learn its identity-provider settings, then signs in and
attaches the token to subsequent `/api/v1/*` calls. That config route is exempt
from auth alongside `/health` - the browser must reach it before it can hold any
token. The benefit: the **same** built bundle runs in dev, staging, and prod
unchanged; environment differences live in runtime config, not in N rebuilds.

---

## services/ - thin composition roots

Everything about `services/` is in `topology-independence.md`; the layout point is
just this: **a service is a thin app that mounts module routers, and the folder is
deliberately small.**

- `services/api/` is the **monolith** root: it mounts every module router, wires the
  shared cross-cutting stack (error handlers, request-id/access-log middleware) and
  the default-deny auth seam, serves the SPA, and (for any module that has been
  extracted) reverse-proxies that module's paths. Its `create_app()` is a factory so
  tests build a fresh app in isolation; the deployed `app` fills the auth seam.
- `services/<module>/` is an **extracted-service** root: same shape, but it mounts
  exactly one module's router at the same prefix. It exists only when a module has
  been pulled out into its own process.

The rule of thumb: if you find yourself writing business logic in a `services/`
app, it is in the wrong place - that logic belongs in a module's `core/` or `api/`.
Composition roots wire; they do not compute.

---

## packages/modules/ - the liftable units

One folder per feature module, each an independent Python package. This is where
the actual product lives. The full internal contract (FCIS split, `/health`,
schema-per-module, private migration tree, per-module CLAUDE.md) is in
`module-contract.md`. The layout-level facts:

- A module is a workspace member with its own `pyproject.toml`, discovered by a
  glob (`packages/modules/*`) so a new module auto-joins the workspace.
- A module depends on `packages/shared`, **never** on a sibling module - enforced by
  an `import-linter` independence contract in the root `pyproject.toml`.
- A module owns its own Postgres schema and its own Alembic tree, so it can be
  migrated, deployed, and rolled back independently.

---

## packages/shared/ - the cross-module foundation

Everything a module is allowed to build on that is not itself a module. It sits
**below** every module in the dependency graph (shared may never import a module or
a composition root - an `import-linter` forbidden contract enforces this).

- `packages/shared/python/` -> the `shared_app` package. The cross-cutting Python
  foundations, typically:
  - **auth** - identity-provider JWT validation, the default-deny authenticator
    seam, the runtime auth-config route the SPA fetches on boot.
  - **db** - the SQLAlchemy `Base`/`MetaData` every module's models attach to, and
    the schema-scoped session seam (`get_session_for_schema`) that routes each
    request into the calling module's schema.
  - **agent / model client** - the shared client for the model provider (e.g. a
    Bedrock/Anthropic seam), spend metering, tool-loop plumbing. (See the agentic
    skill for depth.)
  - **config, errors, middleware** - typed settings, the RFC-9457 problem+json
    error handlers, request-id/access-log middleware.
- `packages/shared/ui/` -> shared React components and design tokens. npm-only (no
  Python), so it is listed/handled separately from the Python packages.

Why a shared package instead of copy-pasting primitives into each module: auth, DB
base, and the model client are genuinely cross-cutting - one correct
implementation, imported everywhere, with the dependency arrow pointing strictly
downward. That keeps modules thin and keeps a security-relevant fix (say, in JWT
validation) in one place.

---

## infra/ and tools/

- `infra/cloudformation/` - infrastructure-as-code: IAM roles, database bootstrap,
  and a **per-service** deploy definition. Because each composition root is its own
  deployable image, extracting a module adds one more small stack here (the new
  service + its config) and nothing structural changes.
- `infra/buildspecs/` - the CI build and migration specs (e.g. a migrate step that
  runs each module's `upgrade head` against its own schema).
- `tools/` - platform-owned CLIs and small standalone services that support the
  platform but are not product modules: e.g. an `mcp-broker` (hosts an MCP server
  for agent tool access), catalog/validation CLIs, cost/reporting jobs. Each is its
  own workspace member with its own tests and CI gate, kept out of the module graph
  on purpose - they are operational, not product surface.

---

## The workspace root ties it together

The root `pyproject.toml` declares the workspace members by glob and holds the
`import-linter` contracts that keep the whole layout honest:

```toml
[tool.uv.workspace]
# Globs so a new module/service/tool auto-joins once it has a pyproject.toml.
members = ["packages/shared/python", "packages/modules/*", "services/*", "tools/*"]

[tool.importlinter]
root_packages = ["shared_app", "api_root", "widgets_app", "gallery_app", "reports_app"]
# Contracts (full detail in module-contract.md):
#   - modules are mutually independent (no sibling imports)
#   - FCIS layers per module (api may import core; core may not import api)
#   - shared_app must not import a module or a composition root
```

Read the layout top-down and the architecture reads itself: **one SPA front door
(registry-driven), thin composition roots that choose the runtime shape, liftable
module packages that hold the product, a shared foundation strictly below them, and
infra/tools around the edges.** Repo organization and runtime topology stay
independent because the layout keeps the modules liftable and the composition roots
thin.
