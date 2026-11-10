# Workday from a hosted tool - unattended RaaS/WQL/REST calls

A hosted Track-2 tool (FastAPI backend on AWS App Runner, credentials in AWS
Secrets Manager) that reads a Workday tenant on a schedule - no human at the
keyboard, no browser, no MFA prompt at call time. This is the shape that falls
in the crack between wd-auth (built for an interactive Claude Code session)
and this skill (built for non-Workday SaaS). This file closes that gap: it is
the HOSTED-TOOL WIRING for calling Workday unattended. Query authoring (how to
write a WQL SELECT, how to build a RaaS report) stays owned by wd-extend-dev -
this file cross-links it rather than duplicating it.

KT note up front: everything below is a specialization of two skills you
already have open. The auth MODE is wd-auth's Mode 2 (API Client refresh-token
grant), described there for an interactive-session credential store (Windows
Credential Manager). Here the same mode's credential lands in AWS Secrets
Manager instead, because the caller is a container, not a terminal. The
platform-neutral SaaS craft (retry, backoff, rate limits, secret storage) is
`patterns.md` in this skill - Workday is just one more OAuth-server-to-server
integration by that reading, with its own host-style trap layered on top.

## Contents

- [1. When this applies vs when to use wd-auth](#1-when-this-applies)
- [2. Auth - the API Client refresh-token grant (Mode 2), run headless](#2-auth)
- [3. Where the credential lives - AWS Secrets Manager, not the image](#3-credential-storage)
- [4. The host-style gotcha - RaaS vs WQL/BO REST](#4-host-style-gotcha)
- [5. Calling Workday - RaaS, WQL, BO REST (wiring only)](#5-calling-workday)
- [6. Unattended discipline - rotation, retry, TLS, scheduling](#6-unattended-discipline)
- [7. Security - least-privilege ISU, measure-twice, synthetic first](#7-security)

---

## 1. When this applies

**Use this file when the caller is a hosted service calling Workday on its
own**, with nobody present to click through a browser MFA prompt: a FastAPI
backend on App Runner, a scheduled Lambda/Fargate job, a background worker -
anything that must mint or refresh a Workday bearer token from code, on a
timer or in response to an API request, with the credential resting in
Secrets Manager between calls.

**Use wd-auth instead when a human is in the loop at call time** - a Claude
Code session running `wdcli` commands, an interactive browser hitting a
Workday login page, or anyone typing a password/MFA code. wd-auth's Mode 1
(wdcli device-code) is explicitly interactive: "the user, in their own
terminal, never the agent" (`wd-auth/references/auth-decision-tree.md`). A
hosted tool cannot run Mode 1 at all - there is no browser session for a
container to hand a login page to, and no MFA prompt for a service to answer.

**The most likely internal accelerator shape this covers:** a tool that reads
a Workday tenant on a schedule (WQL data pulls, a RaaS security-posture
report) and generates a package from it - e.g. a security-request or
audit-drift artifact - with no human present at read time. That is squarely
this file's scope.

| Caller | Auth owner |
|---|---|
| Claude Code session running `wdcli` / browser-driven tenant setup | wd-auth (Modes 1, 3, 4, 5) |
| A person's own script, run interactively, prompted for credentials each session | wd-auth (Mode 2, interactive-session variant - credential-store-setup.md) |
| A hosted tool's backend, calling Workday unattended, on a schedule or per API request, credential in Secrets Manager | THIS FILE (Mode 2, headless variant) |

---

## 2. Auth - the API Client refresh-token grant (Mode 2), run headless

**Use the Workday API Client for Integrations + refresh-token grant - not
wdcli, not device-code, not interactive PKCE.** wdcli's device-code flow
(wd-auth Mode 1) opens a browser and waits for a human to sign in with SSO +
MFA; there is no way to run it from a container with no display and no user.
Auth-code + PKCE (wd-auth Mode 4) likewise needs a browser redirect and a
signed-in person - it is for an external UI acting AS that person, not a
backend acting as itself. The refresh-token grant is the one Workday auth mode
built to run with nobody watching: mint it once (interactively, by a human,
during setup), then let code refresh it indefinitely.

**What backs the credential.** An **API Client registered in-tenant**
(`Register API Client for Integrations`) bound to an **ISU (Integration
System User)** - a service identity, not a named person's login. The client
has a client ID, a client secret, and a per-user refresh token generated
against it. Registration and refresh-token generation are one-time,
human-driven setup steps in the Workday tenant UI - full click-level steps are
in `wd-auth/references/oauth-setup-guide.md` Part 1. Do not re-derive that
walkthrough here; what this file adds is what changes when the caller is a
service instead of a script run at a terminal.

**The exchange, at call time:**

1. **Token endpoint (classic tenanted host):**
   `https://<tenantGwUrl>/ccx/oauth2/<tenant>/token` - get `tenantGwUrl` from
   `wdcli tenant list -f json --ci` during setup, or from the tenant's known
   services host; do not guess it (`wd-auth/references/oauth-setup-guide.md`
   Part 3, "400 with no body" row).
2. **POST the refresh token, client ID, and client secret** (standard OAuth2
   refresh-token grant body) to that endpoint; the response is a short-lived
   access token.
3. **Cache the access token in memory with its expiry, and refresh proactively
   a skew window before it expires** (this skill's `patterns.md` section 1) -
   not reactively after a 401. A scheduled job that mints a token, does its
   run, and discards it is simplest and sidesteps most of this; a
   long-lived service process should refresh on a timer.

**Access-token TTL is short and configured per API Client - verify current in
the tenant, do not hardcode a number.** The registration screen's **"Enforce
60 Minute Access Token Expiry"** checkbox is **irreversible once enabled** and
forces a hard 60-minute cap; left unchecked, the default TTL is
tenant/release-specific (`wd-auth/references/oauth-setup-guide.md` Part 1).
Design the refresh logic to re-mint at call time rather than assume a fixed
lifetime survives a release upgrade.

**Refresh-token expiry - check "Non-Expiring Refresh Tokens" at registration.**
Without it, the refresh token itself expires on a configurable per-client
timeout (commonly 1-365 days) and an unattended job breaks silently once it
lapses with no human present to notice the browser-login prompt that never
comes. This is the single most important registration setting for a headless
caller - confirm it is checked before treating the credential as "standing."
(Same setting, same rationale, as wd-auth's interactive-session guidance -
the difference here is that a lapsed token on a schedule fails with nobody
watching, so the non-expiring setting stops being a convenience and becomes
a requirement.)

**Grant type name, for precision:** RFC 6749 section 6 refresh-token grant,
layered on Workday's tenant-scoped OAuth2 implementation - not the pure
client-credentials grant this skill's `patterns.md` section 1 describes as
the SaaS default, because Workday's classic-host services key off a
per-user refresh token bound to the ISU, not a bare client-credentials
exchange. Verify the exact grant parameter names against the live token
endpoint response if you hand-roll the exchange instead of reusing an
existing client.

---

## 3. Where the credential lives - AWS Secrets Manager, not the image

**Store the client ID, client secret, and refresh token in AWS Secrets
Manager, injected as a `RuntimeEnvironmentSecret` - never in the container
image, never as a plaintext environment variable, never in the repo.** This is
not a Workday-specific rule; it is the same rule this skill's `patterns.md`
section 1 states for every SaaS credential, and the same mechanism
`app-hosting/references/aws-architecture.md` section 3.4 documents for
`DATABASE_URL`. Do not re-teach Secrets Manager wiring here - cross-link
app-hosting for the how; this file's addition is Workday-specific:

- **Three secrets, one Workday profile**: client ID, client secret, refresh
  token travel together (unlike a single-API-key SaaS integration). Store them
  as one Secrets Manager secret with three keys, or three named secrets under
  a shared prefix - either way, rotate and reference them together so a
  partial update never leaves the triplet mismatched.
- **The token endpoint host and tenant alias are NOT secret** - they are
  per-environment configuration (which tenant, which host) and belong as a
  plain `RuntimeEnvironmentVariable`, same rule of thumb as
  `aws-architecture.md` section 5's config table: credentials are secrets,
  everything else per-environment is a plain runtime value.
- **Cache the minted access token in process memory only** - never write the
  short-lived access token itself back to Secrets Manager; it is disposable
  and re-minted from the refresh token on demand. Persisting it adds a
  rotation surface for no benefit.
- **One API Client per environment**, mirroring the Entra "one app
  registration per environment" pattern in `aws-architecture.md` section
  3.6 - dev's Workday API Client and prod's are different registrations
  against different tenants, with separate Secrets Manager entries. Never
  point a dev deployment at a prod tenant's credential to "save a step."

---

## 4. The host-style gotcha

**Get this wrong and every RaaS call 401s even though the token mint
succeeded.** Workday exposes two distinct host styles, and a bearer minted
for one does NOT work at the other (`wd-extend-dev/references/tenant-ops.md`):

| Surface | Host style | What it needs |
|---|---|---|
| **RaaS** (`/ccx/service/customreport2/{tenant}`) | Classic tenanted host | The refresh-grant bearer from section 2. A WCP-gateway bearer 401s here - tokens do not cross styles. |
| **WQL** (`/wql/v1/data`), **BO REST** (`/apps/<refId>/v1/...`, `customObject/v2`) | WCP gateway (`api.us.wcp.workday.com` / regional equivalent) | Also reachable with the same refresh-grant bearer if the API Client is scoped for it, or with a WCP-gateway-only bearer for lighter interactive use. |

The refresh-token grant described in section 2 reaches the classic tenanted
host by construction, and can ALSO reach the WCP gateway if the client's
scopes are configured for it - so a correctly-scoped Mode 2 client is the one
credential that covers both surfaces for a hosted tool. The trap is not "which
grant" (there is only one for headless use); it is "which BASE URL for which
API" - RaaS always goes to the classic tenanted host, full stop, regardless
of which token you are holding. Hardcode the host per surface in config, keyed
by tenant, not guessed at call time.

Cross-region calls fail with a plain 401 regardless of host style - the
region is fixed by where the tenant/API Client lives; always call the
matching regional gateway (`wd-auth/references/oauth-setup-guide.md` Part 2
official table). Verify current regional hostnames before hardcoding them.

---

## 5. Calling Workday - RaaS, WQL, BO REST (wiring only)

This section is deliberately thin - **wd-extend-dev owns query authoring**
(`references/rest-api-catalog.md`, `references/wql.md`,
`references/tenant-ops.md`). What follows is which surface to reach for from
a hosted tool, and the one or two facts a headless caller needs that an
interactive session does not.

**RaaS - "anything a report can show."** The universal escape hatch: any
tenant fact exposed in a custom report becomes API-readable
(`wd-extend-dev/references/tenant-ops.md`). Build the report in-tenant
(one-time human setup), own it by the ISU, web-service-enable it, then GET it
from the hosted tool. Two headless-specific facts:

- **Pass the full "Related Actions -> Web Service -> View URLs" value
  verbatim** - do not hand-assemble the URL from owner/report name; Workday's
  own generated URL is the contract (per Workday/raas-python, official
  client, Apache-2.0 - `wd-extend-dev/references/tenant-ops.md`).
- **The `format=` query parameter must be last** in the URL, same source.
- RaaS auth is per section 2/4 above - refresh-grant bearer, classic host.
  Nothing about calling it from a scheduled job changes the report-building
  side; that stays wd-extend-dev's lane.

**WQL - structured, tabular reads.** `GET /wql/v1/data?query=...` for queries
under 2,048 characters, `POST /wql/v1/data` with `{"query": "..."}` for
longer ones (up to ~16,000 chars) - official limits, verify current
(`wd-extend-dev/references/wql.md`). For a hosted tool's scheduled pull:

- **Page with `offset`**, not by re-running from zero each time (10,000
  rows/page, ~1M-row query cap, official - verify current).
- **Results are cached roughly 30 minutes** server-side; a re-query with
  `offset=0` inside that window can return stale data if the tenant changed
  underneath it - relevant for a "read the current state" scheduled job, not
  just paging.
- Query GRAMMAR (SELECT/FROM/WHERE shapes, data-source discovery,
  parameter binding in `.wqlquery` files) is entirely `wql.md`'s job - this
  file does not restate it.

**BO REST - the app's own business-object data.** `/apps/<refId>/v1/<collection>`
for an Extend app's own BOs (bulk cap 100/request, build-verified), or
`customObject/v2` for custom objects on standard BOs (official ceiling 200,
100 is the build-verified-safe batch size -
`wd-extend-dev/references/rest-api-catalog.md`). Reached at the WCP gateway
per section 4. Use this when the hosted tool is reading or writing an
Extend app's own data rather than tenant/report data.

**Do not duplicate query text here.** If a hosted tool's WQL queries or RaaS
report definitions need documenting, that documentation belongs in
wd-extend-dev's authoring references or in the tool's own repo - this skill
owns the fact that the hosted tool CAN reach these surfaces and how its
credential gets there, not the SQL/report content itself.

---

## 6. Unattended discipline

Everything in this skill's `patterns.md` sections 3-6 (idempotency, retry,
rate limits, pagination, dead-letter) applies to a Workday integration exactly
as to any other SaaS - Workday is not a special case for that craft. Three
points are Workday-specific enough to call out here:

**Refresh-token rotation and expiry handling.** A refresh token generated
without "Non-Expiring" (section 2) will eventually stop working with an
`invalid_grant` error and no advance warning - there is no expiry-approaching
signal from Workday, it just fails on first use past the timeout
(`wd-auth/references/oauth-setup-guide.md` Part 3 debugging table). For a
scheduled job with nobody watching:

- Alert on `invalid_grant` distinctly from other failures - it means the
  refresh token itself is dead, not a transient auth blip, and retrying will
  not help; someone has to regenerate it in the tenant UI
  (`Manage Refresh Tokens for Integrations`).
- Prefer the non-expiring setting for any credential a hosted tool depends on
  continuously; reserve time-boxed refresh tokens for credentials you
  deliberately want to lapse.

**Retry/backoff and 429s.** Workday's REST/WQL/RaaS surfaces are ordinary
HTTP APIs for this purpose - apply this skill's section 4 rules unchanged:
retry transient failures (429, 5xx, timeout) with exponential backoff +
jitter, do NOT retry deterministic failures (400, 401, 403), and honor a
`Retry-After` header if Workday returns one. `wql.md` calls out WQL-specific
timeouts (30 min query, 5 min page) as a related but distinct concern from
rate limiting - a timeout means the query itself is too broad, not that you
are being throttled; narrow the query rather than just retrying it.

**Corporate TLS.** `myworkday.com` classic-tenanted hosts sit behind
corporate SSL inspection that can trip Python's certificate validation for a
script calling them directly (`wd-extend-dev/references/tenant-ops.md`) - the
WCP gateway is typically NOT intercepted. This is a DIFFERENT mechanism from,
but the same shape as, the boto3-vs-httpx corporate-TLS split
`app-agentic/references/provider-seam.md` documents for Bedrock vs the
Anthropic SDK: a corporate root CA is trusted by some HTTP clients and not
others on the same machine, and the symptom is `SSL: CERTIFICATE_VERIFY_FAILED`
on the client that does not see the corporate root. Whichever HTTP client the
hosted tool uses for Workday calls (`httpx`, `requests`, `boto3` is not
applicable here since Workday is not an AWS service), confirm it resolves the
corporate root the same way the rest of the container's egress does - point
it at the corporate CA bundle (`REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`) rather
than assuming `verify=False` is an acceptable production fix; that flag is a
diagnostic escape hatch, not a shipped setting.

**Scheduling the read - App Runner is request-gated, not cron-native.** App
Runner throttles a container's CPU to near-zero between HTTP requests
(`app-hosting/references/operations.md` section 5) and has no built-in
scheduler - there is no "run this WQL pull every night" primitive on the App
Runner service itself. A scheduled Workday read needs an external trigger:

- An EventBridge-scheduled call to a route on the App Runner service (keeps
  the read inside the request/response model App Runner is built for) -
  fine for a read that completes within one request.
- Offload to a separate Fargate/Batch task or Step Functions execution for a
  longer pull, per the same file's guidance on background agent work - a
  multi-page WQL pull or a wide RaaS report generation can run past what a
  single request should hold open.

Either way, do not assume a "nightly job" quietly runs on its own inside the
App Runner container with nothing external driving it - the request-gated
constraint means something has to knock on the door on schedule.
`app-agentic/references/durable-runs.md` covers the durable-run/heartbeat
pattern if the read is long enough to need resumability across a restart.

---

## 7. Security

**The ISU is least-privilege, by design, not by afterthought.** The
Integration System User backing the API Client should hold exactly the
security domains the hosted tool's reads (and any writes) require - no more.
A tool that only runs WQL reads against a handful of data sources does not
need broad Integration or Implementation scopes; scope both the OAuth client
(section 3 of `wd-auth/references/oauth-setup-guide.md`) and the ISU's
security-group domain grants to the actual query/report set.

**Enumerate the required domains BEFORE building, not after the first S22.**
This is the suite's standing pre-build gate: **"MEASURE TWICE - THE PRE-BUILD
REQUIREMENTS GATE"** (`wd-extend-lifecycle/references/quality-gates.md`) makes
a blank or unresolved SECURITY section a hard stop on any build - Extend app,
integration, OR hosted tool, explicitly. For this shape, work the list before
the first line of the scheduler/client code:

- Every WQL data source the tool queries, every RaaS report it will call,
  every BO REST collection it touches - each maps to a security domain (or a
  report-security requirement) the ISU needs, per
  `wd-extend-dev/references/security-setup.md`.
- WQL's `allWebServiceOperations` data source (op -> `domain2` /
  `securityGroupsNeeded`) is the programmatic way to resolve exactly which
  domain a given service operation needs, rather than guessing
  (`wd-extend-dev/references/tenant-ops.md`).
- Batch the whole list into one written security request to the tenant's
  security admin, same convention as an Extend app's Security tab
  (`wd-extend-dev/references/security-setup.md`) - not five separate asks
  as gaps are discovered mid-build.

**Synthetic / non-production first.** Build and test the unattended
integration against a dev or sandbox tenant with synthetic data before
pointing it at anything with real person-level data, same standing rule as
every other build in this suite (no production extracts as seed data, no
customer data in shared dev tenants). A scheduled job that silently pulls
production person-level rows into a hosted tool's database or into an LLM
context is a data-governance violation independent of whether the auth and
host-style wiring are correct - get the wiring right in a synthetic tenant
first, then promote the credential (a NEW API Client + refresh token
registered in the target tenant, per section 3's "one client per
environment") rather than repointing a dev credential at prod.

---

Sources cited inline; the load-bearing ones collected here for convenience -
verify anything version-sensitive against the current page before relying on
an exact number:

- Workday auth modes and the refresh-token grant (Mode 2) -
  `wd-auth/references/auth-decision-tree.md`,
  `wd-auth/references/oauth-setup-guide.md` (developer.workday.com, dated
  citations inline in that file).
- Host styles, RaaS/WQL/BO-REST mechanics -
  `wd-extend-dev/references/tenant-ops.md`,
  `wd-extend-dev/references/rest-api-catalog.md`,
  `wd-extend-dev/references/wql.md`.
- Secrets Manager / RuntimeEnvironmentSecret, App Runner request-gating -
  `app-hosting/references/aws-architecture.md`,
  `app-hosting/references/operations.md`.
- Corporate-TLS client-trust split (analogous mechanism) -
  `app-agentic/references/provider-seam.md`.
- Platform-neutral auth/retry/secret-storage craft this file specializes -
  `references/patterns.md` (this skill).
- The pre-build security gate - `wd-extend-lifecycle/references/quality-gates.md`.
