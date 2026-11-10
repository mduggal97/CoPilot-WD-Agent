# Topology Independence - repo layout is decoupled from runtime shape

Modeled on the reference architecture. Patterns only - every example below
is invented and generic.

## The principle in one sentence

**How your code is organized and how it is deployed are two independent axes.** A
monorepo does not mean one running container, and a single container does not mean
a monorepo. You decide "monolith vs. many services" at **deploy time**, by
choosing which modules a composition root mounts - **not** by moving code.

If the module contract holds (see `module-contract.md` - liftable units that never
import a sibling and never read another module's rows), then a module already IS a
deployable unit. Extracting it is a packaging decision, not a refactor.

```
   AXIS 1: repository organization   ->   one monorepo, N module packages
   AXIS 2: runtime topology          ->   1 container, or 2, or N

   These do not have to match. The only thing that varies between
   "all in one container" and "this module in its own container" is
   WHICH ROUTERS A COMPOSITION ROOT MOUNTS.
```

---

## The two moving parts

### 1. Liftable units (modules)

Each module is an independent package: its own router, its own `/health`, its own
Postgres schema, its own migration tree, no sibling imports. Because it depends
only on the shared foundation (never on another module), you can pick it up and
run it anywhere. That property is what "liftable" means.

### 2. Thin composition roots

A **composition root** is a tiny FastAPI app whose entire job is to wire the
cross-cutting stack (error handlers, request-id/access-log middleware, the
default-deny auth seam) and then **mount some set of module routers**. It contains
almost no logic of its own. The set of routers it mounts is the ONLY thing that
distinguishes one deployment shape from another.

- Mount **every** module -> that image is "the monolith" (one container serves the
  whole platform).
- Mount **one** module -> that image is an "extracted service" (that module runs by
  itself).

Same modules, same code on disk. Two different composition roots, two different
runtime topologies.

---

## Before and after: extracting module X, zero code movement

Take an invented module `reports`. It starts life inside the monolith and later
gets extracted - because, say, its jobs run for 30 minutes and a stalled job
should never take down the health check for the other modules.

### BEFORE - reports runs inside the monolith

The monolith composition root (`services/api`) mounts every module, `reports`
among them:

```python
# services/api/api_root/app.py  (the monolith - mounts ALL modules)
from fastapi import FastAPI
from widgets_app.api.router import router as widgets_router
from gallery_app.api.router import router as gallery_router
from reports_app.api.router import router as reports_router   # <- mounted here today
from shared_app.middleware import register_middleware
from shared_app.errors import register_error_handlers


def create_app(*, authenticator=None) -> FastAPI:
    app = FastAPI(title="Platform")
    register_error_handlers(app)
    register_middleware(app, authenticator=authenticator)   # default-deny auth seam

    @app.get("/health", include_in_schema=False)
    def health():
        return {"status": "ok"}

    app.include_router(widgets_router, prefix="/api/v1/widgets")
    app.include_router(gallery_router, prefix="/api/v1/gallery")
    app.include_router(reports_router, prefix="/api/v1/reports")   # <- one line
    return app
```

One process serves `/api/v1/widgets/*`, `/api/v1/gallery/*`, and
`/api/v1/reports/*`.

### AFTER - reports runs as its own service

Two edits, and **not one line of `reports_app` changes**:

**Edit 1 - a new, tiny composition root that mounts ONLY reports.** This is a new
file under `services/reports`, structurally identical to the monolith root but with
a single module:

```python
# services/reports/reports_svc/app.py  (extracted service - mounts ONE module)
from fastapi import FastAPI
from reports_app.api.router import router as reports_router   # SAME module package
from shared_app.middleware import register_middleware
from shared_app.errors import register_error_handlers


def create_app(*, authenticator=None) -> FastAPI:
    app = FastAPI(title="Platform - Reports")
    register_error_handlers(app)                 # SAME shared cross-cutting stack
    register_middleware(app, authenticator=authenticator)   # SAME default-deny seam

    @app.get("/health", include_in_schema=False)
    def health():
        return {"status": "ok"}

    # The ONLY module this service mounts. Note: SAME prefix the monolith used,
    # so the published /api/v1/reports contract is byte-for-byte unchanged -
    # only the process serving it moved.
    app.include_router(reports_router, prefix="/api/v1/reports")
    return app
```

**Edit 2 - the monolith stops mounting reports and reverse-proxies it instead**
(see next section for why a proxy, not a redirect):

```python
# services/api/api_root/app.py  (diff)
-   app.include_router(reports_router, prefix="/api/v1/reports")
+   # reports now runs as its own service (services/reports). The monolith
+   # reverse-proxies /api/v1/reports/* to it so the SPA stays same-origin.
+   app.include_router(reports_proxy_router)
```

That is the entire extraction. The module package `reports_app/` - its routers,
its `core/`, its `models`, its migrations, its schema - is **untouched**. It did
not know it was in a monolith and it does not know it is now standalone. The auth
seam is identical in both roots (the extracted service re-validates the bearer
itself - defense in depth, since the proxy in front forwards the token).

> Migrations move with the module, not the composition root. `reports_app` already
> owned its schema and its private `alembic_version_reports` table; extraction
> changes nothing about how its migrations run. That is the whole reason
> schema-per-module and per-module migration trees are in the module contract.

---

## Same-origin reverse proxy - so the SPA never notices

The single-page app calls its backend at same-origin paths: `/api/v1/reports/...`.
If extraction forced the browser to call a **different** origin (the reports
service's own URL), you would inherit CORS, a second auth surface, and a per-module
API base URL baked into the frontend. That leaks internal topology into the client
and is exactly what we want to avoid.

The fix: the monolith (which also serves the SPA bundle) keeps owning
`/api/v1/reports/*` as a route, but that route is now a **reverse proxy** that
forwards the request to the extracted service and streams the response back.

```python
# services/api/api_root/reports_proxy.py  (essence only)
import os, httpx
from fastapi import APIRouter, Request, Response

reports_proxy_router = APIRouter()

# Hop-by-hop headers describe one connection, not the end-to-end message - drop them.
_HOP_BY_HOP = {"connection", "keep-alive", "transfer-encoding", "upgrade",
               "host", "content-length", "proxy-authorization"}


@reports_proxy_router.api_route(
    "/api/v1/reports/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    include_in_schema=False,   # the typed contract is published by the extracted service
)
async def proxy_reports(path: str, request: Request) -> Response:
    base = os.environ["REPORTS_SERVICE_URL"].rstrip("/")   # internal base URL of the service
    fwd_headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in _HOP_BY_HOP}         # forward the bearer verbatim
    async with httpx.AsyncClient() as client:
        upstream = await client.request(
            request.method, f"{base}/api/v1/reports/{path}",
            params=request.query_params, headers=fwd_headers,
            content=await request.body() or None,
        )
    resp_headers = {k: v for k, v in upstream.headers.items()
                    if k.lower() not in _HOP_BY_HOP}
    return Response(content=upstream.content, status_code=upstream.status_code,
                    headers=resp_headers, media_type=upstream.headers.get("content-type"))
```

Key points:

- **Proxy, not redirect.** A redirect (302 to the service's URL) would expose the
  internal service origin to the browser and break same-origin auth/cookies. A
  reverse proxy keeps the browser talking to one origin; the hop to the extracted
  service happens server-side, invisibly.
- **The Authorization header is forwarded verbatim** and the extracted service
  **re-validates it** - defense in depth. The proxy adds no trust; it is pure
  transport.
- **The published contract is unchanged.** The extracted service mounts the module
  at the same `/api/v1/reports` prefix and publishes its own OpenAPI. Clients see
  the same paths and same schemas; only the serving process moved.
- Guard the forwarded path against `..` segments so a crafted path cannot escape
  the module prefix upstream. Fail clear (503) when the service URL is unset, so
  the rest of the platform still boots.

The SPA, meanwhile, is untouched: it still calls `/api/v1/reports/artifacts` and
still gets an answer from the same origin. It has no idea a hop happened.

---

## How to split a service later - the checklist

You are changing a composition root and infra, never module files.

1. **Confirm the module is actually liftable.** Run the independence contract - if
   `import-linter` says `reports_app` imports a sibling, fix that first; you cannot
   cleanly extract a module that reaches into another.
2. **Add a new composition root** (`services/reports/reports_svc/app.py`) that
   mounts only that module's router, with the *same prefix* and the *same shared
   cross-cutting/auth stack* as the monolith. Copy the monolith root's shape; swap
   the router set to one.
3. **Point the monolith's route at a proxy.** Replace the `include_router(reports_
   router, ...)` line with `include_router(reports_proxy_router)` and set
   `REPORTS_SERVICE_URL` on the monolith deployment.
4. **Deploy the module's migrations against its own schema** from the new service's
   image (its Alembic tree and private version table came along for free).
5. **Ship two images instead of one.** The module package is in both images'
   dependency closures; which router each image mounts is the only difference.

To **collapse** an extracted service back into the monolith, reverse it: mount the
module router directly again and delete the proxy line. Same zero-code-movement
property in the other direction.

---

## Why this is worth the discipline

- **Deferred, reversible decisions.** You do not have to guess your runtime
  topology on day one. Build everything in one container; extract the one module
  that outgrows it (heavy CPU, long jobs, a noisy dependency, an independent
  scaling or blast-radius need) exactly when the evidence appears - and only that
  module.
- **Blast-radius isolation on demand.** A module with a 30-minute job or a flaky
  external dependency can be moved to its own process so its failures cannot starve
  the shared health check, without rewriting it.
- **No frontend churn.** Because of the same-origin proxy, extraction and
  collapse are invisible to the SPA and to API clients. Topology changes never
  become client changes.
- **The repo stays simple.** One monorepo, one set of module packages, one place to
  read all the code - regardless of how many processes are running in production.

The mantra: **change a composition root, not files.** If an "extraction" is making
you move code between packages, the module contract was not being followed - go
fix the coupling first, then the extraction becomes a two-file change.
