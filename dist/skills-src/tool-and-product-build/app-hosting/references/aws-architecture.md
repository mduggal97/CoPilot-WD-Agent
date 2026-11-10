# AWS Hosting Architecture (reference-architecture pattern)

This is the hosting SHAPE for an internally built web app or agentic tool: how the
container runs, how it is reached, where it gets its data and its model calls,
and how it is authenticated. It is modeled on the reference architecture
but described as a reusable pattern - none of the reference architecture's real account numbers,
endpoint IDs, or URLs appear here (see `deploy-runbook.md` for the scrub list
you MUST apply before adopting any real infra file).

Placeholders used throughout: `<APP_NAME>`, `<REGION>` (default `us-east-2`),
`<DEV_ACCOUNT_ID>`, `<PROD_ACCOUNT_ID>`, `<INGRESS_VPCE_ID>` (a `vpce-*` id),
`<VPC_CONNECTOR_ARN>`, `<ENTRA_TENANT_ID>`, `<ENTRA_CLIENT_ID>`.

---

## 1. The one-paragraph summary

A single container image (React/Vite SPA served by a FastAPI backend) runs on
**AWS App Runner** with **private ingress** (`IsPubliclyAccessible: false`),
reachable only from behind the corporate VPN. It listens on **port 8080** and
answers an **unauthenticated `GET /health`** for App Runner's liveness probe.
It talks to **RDS Postgres** (one shared instance, one schema per module) over
the VPC, and to **Amazon Bedrock** in `<REGION>` for model calls. Users are
authenticated by **Microsoft Entra** through a **single app registration per
environment**. The SPA does not bake its Entra settings at build time - it
fetches them at RUNTIME from an unauthenticated `GET /api/v1/auth/config`, so
**one image serves both dev and prod** unchanged.

---

## 2. Text architecture diagram

```
                         Corporate VPN / internal network perimeter
                         (owned by IT - this is the NETWORK boundary)
  +-------------------------------------------------------------------------+
  |                                                                         |
  |   Browser (on VPN)                                                      |
  |      |                                                                  |
  |      |  1. GET /  (SPA static bundle)                                   |
  |      |  2. GET /api/v1/auth/config   <-- unauthenticated, runtime cfg   |
  |      |  3. redirect to Entra, sign in, get token  ------------------+   |
  |      v                                                              |   |
  |   +--------------------------------------------------+             |   |
  |   |  Private VPC Ingress Endpoint (vpce-*)           |             |   |
  |   |  <INGRESS_VPCE_ID>  (SHARED, pre-existing)       |             |   |
  |   +-----------------------+--------------------------+             |   |
  |                           |                                        |   |
  |                           v  (PrivateLink; no public URL)          |   |
  |   +--------------------------------------------------+             |   |
  |   |  AWS App Runner service  <APP_NAME>-<env>        |             |   |
  |   |  IsPubliclyAccessible: false                     |             |   |
  |   |  Port 8080  |  Health: GET /health (200, no auth)|             |   |
  |   |                                                  |             |   |
  |   |  FastAPI backend + built SPA in ONE image        |             |   |
  |   |    - validates Entra JWT on protected routes <---+-------------+   |
  |   |    - reads ENTRA_TENANT_ID / ENTRA_CLIENT_ID     |                 |
  |   |      from RuntimeEnvironmentVariables            |                 |
  |   +------+----------------------------+--------------+                 |
  |          | egress via VPC connector   |  egress via VPC connector      |
  |          v  <VPC_CONNECTOR_ARN>       v                                |
  |   +--------------+          +----------------------+                   |
  |   | RDS Postgres |          | Amazon Bedrock       |                   |
  |   | shared inst. |          | <REGION> (us-east-2) |                   |
  |   | schema-per-  |          | model calls          |                   |
  |   | module       |          +----------------------+                   |
  |   +--------------+                                                     |
  |                                                                         |
  +-------------------------------------------------------------------------+

  Identity boundary  = Microsoft Entra (SSO, per-environment app registration)
  Network boundary   = the VPN / private ingress endpoint (owned by IT)
```

The two boundaries are independent and BOTH always on: a request must arrive
over the VPN (network) AND carry a valid Entra token on protected routes
(identity). `/health` and `/api/v1/auth/config` are the only two routes that
skip the identity check, and they are still only reachable over the VPN.

---

## 3. Component-by-component

### 3.1 AWS App Runner (the runtime)

- **Why App Runner, not ECS/EKS/Lambda:** it runs a long-lived container from
  an ECR image with almost no orchestration to own - no task definitions, no
  load balancer to wire, no node pool to patch. For a small productized tool
  that is one service (or a handful), that is the right amount of platform.
- **Port 8080, health `/health`.** App Runner probes `GET /health` over HTTP;
  the app answers `200 {"status":"ok"}` with NO auth check (it must return
  before any token exists). Bind the server to `0.0.0.0:8080`. App Runner
  injects `$PORT` (defaults to 8080); the container's start command should
  expand it at runtime rather than hardcode, e.g.
  `uvicorn app:app --host 0.0.0.0 --port ${PORT}`.
- **`AutoDeploymentsEnabled: false`.** Deploys are driven explicitly by the
  pipeline (see `cloudformation-pipeline.md`), never by App Runner watching ECR.
- **Sizing** is modest by default (for example `1 vCPU` / `2 GB`); raise per
  workload.

### 3.2 PRIVATE ingress behind the VPN (the load-bearing network decision)

- `NetworkConfiguration.IngressConfiguration.IsPubliclyAccessible: false`. The
  service has NO public `*.awsapprunner.com` URL that resolves off-VPN.
- Ingress is via a **shared, pre-existing VPC Ingress Endpoint**
  (`<INGRESS_VPCE_ID>`, a `vpce-*` PrivateLink endpoint). A
  `AWS::AppRunner::VpcIngressConnection` registers THIS service as a consumer of
  that endpoint. **Never create the endpoint in your stack** - it is a shared
  IT-owned resource; multiple services register additional consumers against
  the same one.
- **WHY private-behind-VPN and not public + WAF:** the decision is that the
  corporate VPN / network perimeter (owned by IT) IS the network boundary and
  Entra IS the identity boundary. There is deliberately no "private now, flip to
  public + WAF later" roadmap - `IsPubliclyAccessible: false` is the permanent
  end state. Reasons:
  - The tool is internal (firm staff / engagement teams), so a public front
    door would only add attack surface and a WAF to own for zero reach benefit.
  - Defense in depth: even a leaked Entra token or an auth bug cannot be
    exploited from the public internet, because the service is unreachable
    without first being on the VPN.
  - It removes an entire class of work (public DMZ, WAF rules, DDoS posture)
    from the project's scope and hands the network perimeter to the team that
    already owns it.
  - **(!) SCOPE FLAG (2026-09-10) - this architecture is INTERNAL-ONLY.** A
    customer-SOLD product cannot use it: a paying customer is not on the firm's VPN
    and is not in the firm's Entra tenant, so the service is unreachable for them,
    and there is no per-customer multi-tenancy here (schema-per-MODULE isolates
    features, not customers). The **customer-facing variant** - public ingress
    (ALB/CloudFront + WAF), an external identity provider (customer SSO / Cognito),
    and per-customer provisioning - is now designed in
    [customer-hosting.md](customer-hosting.md), and the per-customer data-isolation
    model in app-architecture `references/multi-tenancy.md`. Use those when the
    disposition (product-strategy) is CUSTOMER-SOLD; keep THIS internal architecture
    for internal practice tools. (Customer products are a next-year roadmap item;
    the pattern is designed, but the public-hosting security architecture still
    needs real IT/security sign-off before a customer-sold launch.)
- **DNS caveat:** App Runner's built-in custom-domain feature is public-only, so
  a friendly internal hostname (e.g. `<APP_NAME>.internal.example.com`) needs a
  private DNS record + corporate DNS forwarding, OR you accept the raw
  `*.awsapprunner.com` host over the VPN. This is an IT request, not something
  the app stack provisions.

### 3.3 Egress (outbound to RDS and Bedrock)

- Outbound traffic leaves through a **shared, pre-existing App Runner VPC
  connector** (`<VPC_CONNECTOR_ARN>`), `EgressType: VPC`. AWS enforces one
  connector per (VPC, subnets, security-group) tuple, so you **reuse** the
  connector, never create one.
- This is what lets the container reach RDS (private) and reach Bedrock /
  Entra's JWKS endpoint.

### 3.4 RDS Postgres (schema-per-module)

- One shared Postgres instance per environment. Each module confines itself to
  its **own schema** in the shared database - no separate database and no
  separate Postgres role per module. This keeps data isolated at the schema
  boundary while a single instance is cheap to run and back up.
- Each module owns its **own migration tree** with an isolated Alembic version
  table (e.g. `alembic_version_<module>`) so migrations for one module never
  collide with another's. See `app-architecture` for the module contract.
- `DATABASE_URL` is injected into the service as a **RuntimeEnvironmentSecret**
  (from Secrets Manager), never as a plaintext env var. The DB is not reachable
  from a laptop - `psql` for bootstrap/migrations runs from an in-VPC shell
  (CloudShell in the VPC or a VPC-attached CodeBuild), with TLS required.
- Optional hardening: IAM database auth (a password-free DSN + an
  `rds-db:connect` grant on a specific DB user) with `sslmode=verify-full` and
  the RDS CA bundle baked into the image. Off by default (`password` mode);
  turn it on per environment when required.

### 3.5 Amazon Bedrock (the model calls)

- Model calls go to **Bedrock, entered via `<REGION>` (`us-east-2`)** through the
  instance role - no long-lived API key in the container. A per-service
  `EnableBedrock` toggle turns the Bedrock policy on only for services that need
  it.
- **IAM gotcha - cross-region inference profiles need multi-region grants.**
  `app-agentic` uses `us.`-prefixed **cross-region inference profiles**, which
  route a single logical call to several US regions (us-east-1 / us-east-2 /
  us-west-2). An invoke policy scoped only to `us-east-2` model ARNs will
  `AccessDenied` when the profile routes elsewhere. The grant must allow
  `bedrock:InvokeModel*` on BOTH the inference-profile ARN AND the underlying
  foundation-model ARN **in every region the profile can route to** - not just
  us-east-2. (A data-residency note: "Bedrock in us-east-2" describes the entry
  region, not where every token is processed - cross-region profiles may execute
  in another US region. Confirm this is acceptable for the data class.)
- The agentic layer (provider seam, model registry, spend governance) is owned
  by `app-agentic`; this file only covers WHERE Bedrock sits in the hosting
  shape.

### 3.6 Microsoft Entra (identity)

- **A single Entra app registration per environment** (one for dev, one for
  prod). The backend validates the incoming JWT's signature against Entra's
  JWKS, and checks `aud`/`iss` against its configured `ENTRA_CLIENT_ID` /
  `ENTRA_TENANT_ID`.
- The API scope is DERIVED, not separately configured:
  `api://<ENTRA_CLIENT_ID>/access_as_user`. One convention, no extra setting to
  drift.

---

## 4. Runtime-not-build-time config (the "one image" principle)

This is the single most important idea in the hosting shape, so it gets its own
section.

**The problem it solves.** The SPA needs the Entra tenant id and client id to
build its MSAL sign-in config. The naive approach bakes those into the
JavaScript bundle at `npm run build` time (e.g. `VITE_ENTRA_CLIENT_ID`). But
dev and prod have DIFFERENT Entra client ids. If you bake them in, dev's image
and prod's image are different bytes - and worse, promoting "the tested image"
from dev to prod is impossible, because the dev image points every user at
dev's Entra app registration. You would have to rebuild for prod, which means
prod runs bytes that were never tested in dev.

**The pattern.** Nothing environment-specific is baked into the image. Instead:

1. The **backend** reads `ENTRA_TENANT_ID` and `ENTRA_CLIENT_ID` from App Runner
   `RuntimeEnvironmentVariables` (set per environment by the CloudFormation
   stack at deploy time).
2. The **SPA**, on load, fetches those same values at RUNTIME from a
   platform-wide, unauthenticated route:

   ```
   GET /api/v1/auth/config
   -> 200
   {
     "tenant_id": "<ENTRA_TENANT_ID>",
     "client_id": "<ENTRA_CLIENT_ID>",
     "api_scope": "api://<ENTRA_CLIENT_ID>/access_as_user"
   }
   ```

   The SPA constructs its MSAL config from the response - never from a
   build-time env var.
3. This route is unauthenticated by necessity: the SPA calls it BEFORE it can
   acquire any token, so it cannot itself sit behind the auth gate. It is
   mounted with no prefix (like `/health`), because it is platform-wide, not
   owned by any one module.
4. A fetch failure in local dev (no backend running) falls back to obvious-fake
   stub values, so the SPA still renders.

**The payoff.** ONE built image is promoted byte-for-byte from dev to prod. The
same bytes resolve dev's client id in the dev account and prod's client id in
the prod account, purely from the App Runner env vars each environment sets.
That is what makes the "build once, test in dev, promote the exact image to
prod" pipeline in `cloudformation-pipeline.md` sound.

**Generalize the pattern.** The same runtime-config technique applies to any
per-environment value the frontend needs (a sandbox iframe origin, a submit URL
that embeds a token, a downstream service URL). Serve it from a small
`/config`-style endpoint at runtime; never bake it into the bundle. A token that
must not ship in client JavaScript is an especially strong reason - keep it
server-side and hand out only what the browser strictly needs.

---

## 5. Config injection summary

| Value                         | How it reaches the container      | Why |
|-------------------------------|-----------------------------------|-----|
| `DATABASE_URL`                | RuntimeEnvironmentSecret (SM)      | it is a credential |
| `ENTRA_TENANT_ID` / `_CLIENT_ID` | RuntimeEnvironmentVariable      | not secret; per-env; also served to SPA at runtime |
| `BEDROCK_REGION`              | RuntimeEnvironmentVariable         | not secret |
| `<MODULE>_SERVICE_URL`        | RuntimeEnvironmentVariable (dflt "")| per-env downstream address; empty = fail-clear |
| API scope                     | derived in code from client id     | one convention, nothing to set |
| SPA Entra config              | fetched at runtime via `/api/v1/auth/config` | one image, two environments |

Rule of thumb: **credentials are secrets; everything else per-environment is a
plain runtime env var or a runtime-served config value - and NOTHING
environment-specific is baked into the image at build time.**

---

## 6. What this file deliberately does not cover

- The pipeline / IaC shape (two-account, two-pass, dev-immutable vs
  prod-mutable): see `cloudformation-pipeline.md`.
- Step-by-step deploy and the genericize-before-adopt scrub list: see
  `deploy-runbook.md`.
- How the module is structured internally (FCIS, module contract, migrations):
  see the `app-architecture` skill.
- The agent runtime (Bedrock/Anthropic provider seam, spend caps): see the
  `app-agentic` skill.
