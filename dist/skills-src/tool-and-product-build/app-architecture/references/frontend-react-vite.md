# Frontend React/Vite - UI craft for a module SPA

Companion to [repo-layout.md](repo-layout.md) (the SPA shell, the module
registry, deep-link fallback) and [starter-kit.md](starter-kit.md) (the
one-time `apps/web` assembly). Those files cover the SHELL - how a module's
UI plugs into the ONE registry-driven SPA. This file covers the CRAFT - the
screen behind a registry entry: conventions, data fetching, forms, testing,
and the build gotchas.

Read this AFTER repo-layout.md's "apps/web" section. It does not restate the
registry pattern, the SPA-static-fallback rule, or the runtime auth-config
fetch - it assumes those exist and shows what goes inside `<module>/`.

verify-current: versions below checked 2026-09-10 against each project's own
release notes/npm page. Pin exact versions in the repo's lockfile, not from
memory - this is a starting point, not a floor.

## Table of contents

1. [Scaffold](#1-scaffold)
2. [TypeScript config](#2-typescript-config)
3. [Data layer - TanStack Query](#3-data-layer)
4. [State: server vs UI, no Redux by default](#4-state)
5. [Forms - react-hook-form + zod](#5-forms)
6. [Routing inside a module](#6-routing)
7. [Error boundaries and loading](#7-errors-and-loading)
8. [Auth wiring](#8-auth)
9. [Testing - Vitest, Testing Library, Playwright, MSW](#9-testing)
10. [Production build](#10-build)
11. [Accessibility baseline](#11-a11y)

---

<a name="1-scaffold"></a>
## 1. Scaffold

`apps/web` is scaffolded ONCE per repo (starter-kit.md checklist item 3),
never per module. A module adds a folder and a registry entry - it does not
run its own `npm create vite`.

```bash
npm create vite@latest apps/web -- --template react-ts
```

verify-current (2026-09-10): Vite 8.x current (Vite 7 shipped June 2025,
8.0 March 2026, per vite.dev/releases); React 19.x current (19.3.0, Sep
2026, per react.dev/versions). Confirm the `react-ts` template name is still
current before running.

Module UI folder convention (mirrors `packages/modules/<name>/` on the
backend so the two sit side by side):

```
apps/web/src/
  App.tsx               # shell-owned - no module logic here
  registry/             # shell-owned
  <module>/              # e.g. widgets/ - what YOU own
    WidgetsModule.tsx      # element wired into registry.tsx
    routes/                 # react-router sub-routes (section 6)
    components/              # module-local presentational components
    hooks/                    # useWidgets, useCreateWidget, etc.
    api/
      client.ts                # typed fetch wrapper, this module only
      types.ts                  # mirrors this module's contracts.py by hand
    schemas.ts                  # zod schemas for this module's forms (section 5)
    __tests__/                  # co-located tests (section 9)
```

Rule of thumb: a module's UI folder should be deletable on its own, same as
the backend's independence rule in [module-contract.md](module-contract.md)
- no module imports another module's folder. Shared presentational
components live in `packages/shared/ui/` (repo-layout.md), never copied
between modules.

---

<a name="2-typescript-config"></a>
## 2. TypeScript config essentials

**Strict mode, non-negotiable** - the Vite template ships `strict: true`;
keep it. A module's `api/types.ts` mirrors a frozen, strict Pydantic
contract; a loose TS config lets that mirror drift silently.

```json
// apps/web/tsconfig.json (essentials)
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "moduleResolution": "bundler",
    "baseUrl": "<repo-root>",
    "paths": { "@shared/*": ["packages/shared/ui/src/*"] }
  }
}
```

Path aliases should mirror the module boundary, not convenience: alias
`@shared/*` for the one thing every module may import; never alias into
ANOTHER module's folder - that defeats the independence rule it should
reinforce. Mirror the same paths in `vite.config.ts` (`resolve.alias`) since
Vite does not read `tsconfig.json` paths itself.

---

<a name="3-data-layer"></a>
## 3. Data layer - TanStack Query against the module contract

**Recommendation: TanStack Query (`@tanstack/react-query`) for all server
state.** verify-current (2026-09-10): v5.x current (5.102.x per npm); no v6
yet.

A module's API surface is exactly its FastAPI router's `contracts.py`
(module-contract.md) - one Pydantic model per endpoint. Mirror that shape by
hand in `api/types.ts`, and wrap every call in a typed function, never a raw
`fetch()` scattered through components:

```ts
// apps/web/src/widgets/api/client.ts
class ApiError extends Error {
  constructor(public status: number, public problem: unknown) { super(`API error ${status}`) }
}

// Normalizes the backend's RFC-9457 problem+json (module-contract.md's shared
// error handlers) into one exception shape every caller catches the same way.
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api/v1/widgets${path}`, { ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers } })
  if (!res.ok) throw new ApiError(res.status, await res.json().catch(() => null))
  return res.json() as Promise<T>
}

export const widgetsApi = {
  list: () => request<Widget[]>('/'),
  create: (body: CreateWidgetRequest) =>
    request<Widget>('/', { method: 'POST', body: JSON.stringify(body) }),
}
```

```ts
// apps/web/src/widgets/hooks/useWidgets.ts
export const widgetsKeys = { all: ['widgets'] as const }

export function useWidgets() {
  return useQuery({ queryKey: widgetsKeys.all, queryFn: widgetsApi.list })
}
export function useCreateWidget() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: widgetsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: widgetsKeys.all }) })
}
```

Why a wrapper instead of inline `fetch` per component: one place to attach
the auth token (section 8), one place to normalize errors for the error
boundary (section 7) to read, one place to update if the module's base path
changes. The relative `/api/v1/widgets` path (not an absolute URL) is
deliberate - same-origin through the Vite dev proxy locally
([local-dev.md](local-dev.md)) and through the composition root in the
cloud, no CORS config either place.

---

<a name="4-state"></a>
## 4. State: server state = Query, UI state = useState/context, no Redux by default

Two kinds of state, two tools - conflating them is the most common React
state mistake:

- **Server state** (anything from Postgres via `/api/v1/*`) - TanStack Query
  owns caching, refetch, loading/error status, invalidation. Never copy a
  query result into `useState` "to make it editable" - mutate through
  `useMutation` and let cache invalidation flow the update back.
- **UI state** (a modal's open flag, a selected tab, an in-progress draft) -
  plain `useState`, lifted to the nearest common ancestor, or a small
  `useContext` if it crosses more than a couple components inside ONE
  module. It never survives a reload and never needs dedup - that is the
  tell it is not server state.

**No Redux/Zustand/Jotai by default**, for reasons specific to this stack:
(1) the hard problem Redux solves - cross-component server-data caching - is
already TanStack Query's job here; (2) what is left over is almost always
local to one module's folder; (3) a global client store is a structural
coupling point across modules that the whole architecture is designed to
avoid (mirrors the backend's no-sibling-imports rule). Escalate past
`useState`/`useContext` only inside one module's own folder, and only after
`useReducer` proves insufficient.

---

<a name="5-forms"></a>
## 5. Forms - react-hook-form + zod, mirroring the Pydantic side

**Recommendation: `react-hook-form` + `zod` via `@hookform/resolvers`.**
verify-current (2026-09-10): `@hookform/resolvers` 5.x auto-detects Zod v3
vs v4 through the same `zodResolver` import, per the resolvers package docs.

The frontend's zod schema should be a hand-kept mirror of the backend's
`contracts.py` request model (module-contract.md) so a required field, max
length, or enum is enforced identically on both sides:

```ts
// apps/web/src/widgets/schemas.ts - mirrors CreateWidgetRequest in contracts.py
export const createWidgetSchema = z.object({
  name: z.string().min(1, 'Name is required').max(120),
  quantity: z.number().int().nonnegative(),
})
export type CreateWidgetForm = z.infer<typeof createWidgetSchema>
```

```tsx
// apps/web/src/widgets/components/CreateWidgetForm.tsx
export function CreateWidgetFormView() {
  const { register, handleSubmit, formState: { errors } } =
    useForm<CreateWidgetForm>({ resolver: zodResolver(createWidgetSchema) })
  const createWidget = useCreateWidget()
  return (
    <form onSubmit={handleSubmit((data) => createWidget.mutate(data))}>
      <label htmlFor="name">Name</label>
      <input id="name" {...register('name')} aria-invalid={!!errors.name} />
      {errors.name && <p role="alert">{errors.name.message}</p>}
      <button type="submit" disabled={createWidget.isPending}>Create</button>
    </form>
  )
}
```

If `contracts.py` and `schemas.ts` drift, the symptom is a form that submits
client-side and then 422s from FastAPI - or worse, one that silently accepts
a value FastAPI would reject. Where a repo can afford it, generate the zod
schema (or field list) from FastAPI's own OpenAPI output instead of hand-
copying twice; that is a repo-level tooling decision this file does not
prescribe by default.

---

<a name="6-routing"></a>
## 6. Routing inside a module

The shell owns the TOP-level route: `registry.tsx` maps one module to one
`routePrefix`, `App.tsx` mounts `<Route path="${routePrefix}/*">`
(repo-layout.md). Everything under that `/*` is the module's own
`react-router-dom` business - the shell never looks inside it:

```tsx
// apps/web/src/widgets/WidgetsModule.tsx - the element registry.tsx points at
export function WidgetsModule() {
  return (
    <Routes>
      <Route index element={<WidgetList />} />
      <Route path=":widgetId" element={<WidgetDetail />} />
    </Routes>
  )
}
```

This inherits two shell-level guarantees for free: deep links resolve
because the composition root's SPA-static fallback serves `index.html` for
unmatched route-like paths (repo-layout.md, "Serving the SPA and deep
links"), and the module's bundle loads lazily if `registry.tsx` wraps the
element in `React.lazy` - that boundary is the shell's job, not repeated per
module.

---

<a name="7-errors-and-loading"></a>
## 7. Error boundaries and loading/suspense

Two failure axes, both handled deliberately per module:

- **A component throws.** Wrap each module's top-level element in an error
  boundary (`react-error-boundary` or a hand-rolled class component) so one
  module's bug cannot blank the whole shell - the nav and other modules stay
  usable.
- **A query is loading or failed.** Use TanStack Query's `isPending`/
  `isError`/`error` explicitly at the point of use, rather than reaching for
  `<Suspense>`, unless the repo has deliberately adopted `useSuspenseQuery`
  for that module. Do not mix both styles in one component tree.

```tsx
export function WidgetList() {
  const { data, isPending, isError, error } = useWidgets()
  if (isPending) return <p>Loading widgets...</p>
  if (isError) return <p role="alert">Could not load widgets: {error.message}</p>
  return <ul>{data.map((w) => <li key={w.id}>{w.name}</li>)}</ul>
}
```

Normalize the "could not load" message from the `ApiError` shape in section
3 so every module reports backend errors the same way.

---

<a name="8-auth"></a>
## 8. Auth wiring

Full runtime-config + MSAL pattern: [repo-layout.md](repo-layout.md) ("Auth
and config are fetched at RUNTIME") and app-hosting `aws-architecture.md`
section 4 (the "one image" principle, never bake `VITE_ENTRA_*`) and
section 3.6 (the Entra app-registration/JWT shape). Do not restate that
wiring inside a module.

What a module DOES own: attaching the acquired token to its own calls - one
`Authorization: Bearer <token>` header added in the `request()` wrapper
(section 3), sourced from whatever auth context the shell exposes (MSAL
`useMsal()`/`acquireTokenSilent`, or the dev-stub principal locally per
[local-dev.md](local-dev.md)). A module never fetches `/api/v1/auth/config`
itself or constructs its own MSAL instance - that is shell-owned,
platform-wide state.

---

<a name="9-testing"></a>
## 9. Testing - Vitest, Testing Library, Playwright, MSW

verify-current (2026-09-10): Vitest (unit/component) + Testing Library
(component queries) + MSW (network-boundary mocking) + Playwright (E2E) is
the standard 2026 combination per current framework docs checked this date;
install latest of each and pin the lockfile.

```ts
// apps/web/vite.config.ts (test block, alongside the dev proxy in local-dev.md)
export default defineConfig({
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], globals: true },
})
```

```ts
// apps/web/src/test/setup.ts
import { server } from './msw/server'
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

**Mock at the network boundary, not the function level** - mock the `fetch`
call to `/api/v1/widgets`, not the `widgetsApi` module, so the test still
exercises the real typed wrapper and its error normalization:

```ts
// apps/web/src/test/msw/handlers.ts
export const handlers = [
  http.get('/api/v1/widgets', () => HttpResponse.json([{ id: '1', name: 'Acme Widget' }])),
]
// server.ts (Node, for Vitest): setupServer(...handlers) from 'msw/node'
```

The same `handlers.ts` reuses in a browser MSW worker for local dev and in
Playwright - do not maintain a second fixture set for E2E.

```tsx
// apps/web/src/widgets/__tests__/WidgetList.test.tsx
test('renders widgets from the API', async () => {
  const qc = new QueryClient()
  render(<QueryClientProvider client={qc}><WidgetList /></QueryClientProvider>)
  expect(await screen.findByText('Acme Widget')).toBeInTheDocument()
})
```

**E2E - Playwright**, run against the real backend
([local-dev.md](local-dev.md)) rather than MSW, so at least one layer
exercises the actual FastAPI module end to end:

```ts
// e2e/widgets.spec.ts
test('create a widget end to end', async ({ page }) => {
  await page.goto('/widgets')
  await page.getByLabel('Name').fill('Acme Widget')
  await page.getByRole('button', { name: 'Create' }).click()
  await expect(page.getByText('Acme Widget')).toBeVisible()
})
```

Test placement mirrors the backend: unit/component tests co-located under
`<module>/__tests__/` ([module-contract.md](module-contract.md)); Playwright
specs in a top-level `e2e/` since they exercise the whole stack, not one
module.

---

<a name="10-build"></a>
## 10. Production build

**Chunking.** Vite/Rollup code-splits at dynamic `import()` boundaries -
exactly what `React.lazy(() => import('./widgets/...'))` in `registry.tsx`
produces (repo-layout.md). Each module ships as its own chunk, loaded only
when visited. Skip hand-rolled `manualChunks` unless a specific module's
bundle is measured as too large on its own.

**Source maps.** Enable for production (`build.sourcemap: true`) so error
reports resolve to real source - but do not ship them publicly on the
customer-sold/public-ingress path (app-hosting `customer-hosting.md`);
upload to an error-tracking service and exclude `.map` files from what the
container serves.

**The env-baking gotcha - do not restate it, obey it.** Full rationale in
app-hosting `references/aws-architecture.md` section 4: never bake
`VITE_ENTRA_*` (or any per-environment value) into the bundle via
`import.meta.env.VITE_*` at build time - it produces different bytes per
environment and breaks the "build once, promote the same image" pipeline.
Anything that differs between dev and prod is fetched from a runtime config
endpoint the way `/api/v1/auth/config` already is (section 8).

`npm run build` output (`apps/web/dist`) is copied into the ONE
composition-root image (starter-kit.md item 7) - there is no separate
per-environment frontend build.

---

<a name="11-a11y"></a>
## 11. Accessibility baseline

Minimum bar for every module screen:

- **Every input has a `<label htmlFor>`** (or `aria-label`) - a placeholder
  is never a substitute (see section 5's form example).
- **Every interactive element is keyboard-reachable** - use `<button>`/`<a>`,
  not a clickable `<div>`, so focus and activation come free.
- **Focus moves deliberately** - a modal traps focus and returns it to the
  trigger on close; a route change resets focus to the page's main heading.
- **Validation errors are announced** - `role="alert"` or `aria-live` on the
  error message, as in section 5.
- **Color is never the only signal** - pair a color change with text/icon.

Testing Library's queries (`getByRole`, `getByLabelText`) double as an
accessibility check by construction - a component hard to query by role or
label is usually hard to use with a screen reader too; treat a test that
resorts to `getByTestId` as a signal to fix the markup, not just the test.

---

> Read [repo-layout.md](repo-layout.md) first for the shell shape this file
> assumes, [starter-kit.md](starter-kit.md) for the one-time `apps/web`
> assembly, [module-contract.md](module-contract.md) for the backend
> contract this file's data layer mirrors, and app-hosting
> `references/aws-architecture.md` section 4 for the runtime-config rule
> behind section 10's build gotcha.
