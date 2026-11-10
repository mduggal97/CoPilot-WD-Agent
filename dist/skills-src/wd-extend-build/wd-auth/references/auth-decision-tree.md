# Auth decision tree - which mode for which task

Five auth modes exist in Workday. Each has a different token lifetime, setup cost, and
capability surface. Pick the lightest mode that covers the task.

---

## Mode 1: wdcli OAuth (device-code flow)

**What it is:** `wdcli auth login` opens a browser, the user signs in with SSO + MFA,
and wdcli stores an OAuth token on disk. Subsequent wdcli commands use the stored token
silently.

**Use when:**
- Building, uploading, deploying, downloading, or promoting Extend apps
- Running `wdcli tenant token` to get a short-lived bearer for REST testing
- Any `wdcli app *` or `wdcli tenant *` command

**Setup cost:** Zero config. wdcli manages its own token store.

**Token lifetime:** Three separate expirations (see auth-troubleshooting.md):
- Developer session (full org auth) - longest, expires after extended inactivity
- Tenant auth (per-tenant deploy) - medium, per `wdcli tenant login <alias>`
- REST bearer (`wdcli tenant token`) - ~1 hour, request-scoped. (official-docs - developer.workday.com, 2026-08-25: "All Workday Extend access tokens expire after 60 minutes" - corroborates the ~1 hr observation. Mode 2's classic tenanted-host access token is a separate surface with its own configured TTL - see Mode 2.)

**Surface reached:** WCP gateway (`api.us.wcp.workday.com`) only. Does NOT reach
classic tenanted hosts (`*-services1.wd*.myworkday.com`) - those need Mode 2 or 3.

**Who runs it:** The user, in their own terminal. Never the agent.

**Cross-ref:** wd-extend-dev `references/wdcli-setup.md` (install + sign-in steps),
`references/wdcli-workflow.md` (build loop commands).

---

## Mode 2: API Client refresh-token grant (OAuth client_credentials / refresh)

**What it is:** An API Client registered in-tenant with a client ID, client secret, and
a per-user refresh token (commonly configured non-expiring). Scripts exchange the refresh
token for a short-lived access token, then use that bearer for REST, WQL, SOAP, and RaaS
calls.

**Use when:**
- Calling REST/WQL/RaaS/SOAP from scripts or the tenant_toolkit (standing, unattended)
- Any classic-tenanted-host call (RaaS, SOAP, older REST endpoints)
- Automated/scheduled integration runs
- Any scenario where wdcli's ~1-hour bearer is too short or too manual

**Setup cost:** Medium. Requires tenant admin work (register client, generate refresh
token). Full walkthrough in oauth-setup-guide.md.

**Token lifetime:** Access-token TTL and refresh-token timeout are configured per API
Client and vary by tenant and release (refresh-token timeout is commonly configurable
1-365 days; the client can also be set to a non-expiring refresh token). Confirm the live
values in the tenant's API Client / OAuth config rather than relying on a fixed number -
see the verify-in-tenant rule in
`wd-extend-lifecycle/references/verify-in-tenant.md`. Treat any specific number as a starting
point to verify.
- Refresh token: per-client timeout (commonly non-expiring if configured; revocable by admin)
- Access token: short-lived, auto-refreshed by scripts (confirm the tenant's value)

**Surface reached:** Classic tenanted host (REST `/ccx/api/...`, SOAP `/ccx/service/...`,
RaaS `/ccx/service/customreport2/...`). Also WCP gateway if the client is configured
for it.

**Credential store:** Windows Credential Manager via `tenant_toolkit.py set-creds`
(recommended) or environment variables (credential-store-setup.md).

**Cross-ref:** wd-extend-dev `references/tenant-ops.md` (Path B setup runbook),
`references/security-setup.md` (API client security model).

---

## Mode 3: HTTP Basic (implementer / ISU account) - BEING RETIRED FOR WEB SERVICES (~R2 2026)

**One-voice statement:** HTTP Basic auth for Workday web services is being retired
(~R2 2026); use the Mode 2 refresh-token bearer for SOAP/WWS. A tenant may still have
Basic enabled transitionally - verify in-tenant - but do not design new work on it.

**Status (observed 2026-09-01, dev tenant):** Basic was already dead for web services in
this tenant. The symptom is unmistakable: the SAME account logs into the tenant UI fine,
but every SOAP/WWS Basic call returns HTTP 500 "invalid username or password" - on
every service, both `user@tenant` and plain `user` forms - and the opt-out checkbox
("Disable Basic Authentication for Web Services") is GONE from Tenant Setup - Security.
Calls that worked in August 2026 died in the R2 window with no tenant-side change.

**Do this instead:** Mode 2 (API client + refresh grant -> `Authorization: Bearer` at
the classic host). Setup walkthrough: the USER-ACTION runbook in wd-extend-dev
`references/tenant-ops.md` Path B; loading workflow: wd-extend-dev
`references/private-ws-loading.md`.

**Diagnosis rule:** "UI login works + WS Basic fails tenant-wide" = this retirement,
NOT a wrong password. Do not burn attempts re-typing credentials; go straight to the
API-client path. Any script still coding Basic auth for WWS is broken and needs the
bearer conversion.

**Security note (still true):** Implementer accounts are powerful - they can modify
tenant config. Never expose credentials in chat, docs, or committed files.

---

## Mode 4: OAuth auth-code + PKCE (user-context SPA)

**What it is:** A PUBLIC WCP API Client (no secret) registered on developer.workday.com.
A browser-based app redirects the user to Workday's auth endpoint, the user signs in,
and the app gets a JWT bearer that executes API calls AS that user.

**Use when:**
- Building an external web application that reads/writes Workday data on behalf of
  individual users
- The app needs user-level security (each user sees only what their Workday permissions
  allow)

**Setup cost:** High. Requires developer portal access, API Client registration with
CORS domains and scopes, and PKCE implementation in the frontend.

**Token lifetime:** Short (no refresh token in this flow). Expiry = re-login. (official-docs - developer.workday.com, 2026-08-25: Extend access tokens officially expire after 60 minutes.)

**Surface reached:** WCP gateway (`api.workday.com`) only, executing as the signed-in
user. `/me` aliases work.

**Credential store:** None server-side. The client ID is public. The auth flow is
browser-session-based.

**Cross-ref:** wd-extend-dev `references/external-apis-and-genai.md` (reverse-direction
section), `references/tenant-ops.md` (PKCE notes - it maps to Mode 4 here).

---

## Mode 5: Anonymous (WSDL fetch only)

**What it is:** WSDL endpoints are publicly accessible with no auth.

**Use when:**
- Downloading WSDL schemas for envelope generation or documentation
- `{gwUrl}/ccx/service/{tenant}/<Service>/<vNN.N>?wsdl` - returns full WSDL, no auth
  (use your tenant's current Web Services version)

**Setup cost:** Zero.

**Cross-ref:** wd-extend-dev `references/tenant-ops.md` (implementer/private WS section).

---

## Decision flowchart

```
START
  |
  v
Is this a wdcli command? --yes--> Mode 1 (wdcli OAuth)
  |no
  v
Is this a browser-based user-facing app? --yes--> Mode 4 (PKCE)
  |no
  v
Do you need classic-host access (RaaS/SOAP)? --yes--> Is an API Client registered?
  |no                                                     |yes           |no
  v                                                       v              v
Is a wdcli bearer sufficient (~1hr)?                Mode 2 (refresh)  Mode 2 (register API Client)
  |yes        |no
  v            v
Mode 1 token  Mode 2 (register API Client)
```

Note: Mode 3 (HTTP Basic) is NOT a branch here - it is being retired for web services
(~R2 2026). Use Mode 2 (refresh-token bearer) for all SOAP/WWS/RaaS work; only fall back
to Basic if a tenant still has it enabled transitionally, verified in-tenant.

## Multi-org reality

Workday auth is **per-org** for wdcli and **per-tenant** for API clients:
- wdcli `account switch` changes the active org machine-globally (any parallel session
  can flip it)
- API Client credentials are tenant-scoped (a client registered in tenant A doesn't
  work in tenant B)
- Implementer accounts are tenant-scoped (different password per tenant)
- When working across orgs (e.g., your firm's org + a client org), ALWAYS verify
  which org/tenant is active before any operation (see auth-preflight.md)
