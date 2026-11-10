# OAuth API Client setup & debugging - end-to-end guide

This is the full walkthrough for setting up an OAuth API Client in a Workday tenant. Two
flows: **refresh-token grant** (for scripts/automation) and **auth-code + PKCE** (for
browser-based user-facing apps). If you just need wdcli to work, you don't need an API
Client - see auth-decision-tree.md Mode 1.

---

## Part 1: Refresh-token grant (scripts, automation, tenant toolkit)

This is the most common setup. It gives scripts a standing credential that can call
REST, WQL, SOAP, and RaaS without human interaction.

### Step 1: Verify OAuth is enabled in the tenant

*User does this in the Workday tenant UI:*

1. **Search:** `Edit Tenant Setup - Security`
2. **Confirm** that **OAuth 2.0 Clients Enabled** is checked
3. If unchecked, check it and submit (requires tenant admin / Security Administrator)

If this is unchecked, all OAuth flows fail silently (the token endpoint returns
`unauthorized_client` with no helpful message).

### Step 2: Register the API Client

> Cross-ref: the tenant-admin click-recipe for registering this API Client also exists as
> recipe R6 in `wd-deployment/references/tenant-task-recipes.md` (same task, two lenses:
> wd-auth owns the auth-mode/why, wd-deployment owns the click-steps) - keep them in sync
> so they cannot silently diverge.

*User does this in the Workday tenant UI:*

1. **Search:** `Register API Client for Integrations`
2. Fill in:

| Field | Value | Notes |
|---|---|---|
| Client Name | `TenantOps - <tenant_alias>` | Self-documenting. One client per purpose is cleaner than one shared client. |
| Non-Expiring Refresh Tokens | **Checked** | Without this, the refresh token expires on the client's configured timeout (commonly configurable 1-365 days) and scripts break silently once it lapses. Checking this removes that timeout. |
| Enforce 60 Minute Access Token Expiry | **Leave UNCHECKED** | This setting is **IRREVERSIBLE** once enabled. It forces all access tokens to 60 min max. The default access-token TTL is configured per API Client and varies by tenant and release - confirm the live value rather than assuming a fixed number (see the verify-in-tenant rule in `wd-extend-lifecycle/references/verify-in-tenant.md`). |
| Scopes | See scope guide below | Determines what the client can access. Editable later. |

3. Click **OK**
4. **CRITICAL:** The **Client ID** and **Client Secret** display on the confirmation
   page. **This is the only time the secret is shown.** Copy both immediately. If you
   lose the secret, you must create a new client.

### Step 3: Choose scopes

Scopes control what API surface the client can reach. For a general-purpose toolkit
client, select generously (you can always narrow later):

| Scope | What it unlocks |
|---|---|
| **System** | Core platform operations, tenant config reads |
| **Tenant Non-Configurable** | Read tenant metadata, public reports |
| **Integration** | Integration-related APIs (ISU, integration events) |
| **Implementation** | Implementation services (private web services - Get/Put ops) |
| **Custom Objects** | Extend BO REST API, custom object CRUD |
| **Organizations** | Org hierarchy reads |
| **Staffing** | Worker/position data (if needed) |
| **Human Resources** | HR-specific operations (if needed) |

For a scope-minimal automation client (just config/data checks), start with **System +
Tenant Non-Configurable + Custom Objects**.

### Step 4: Generate a refresh token

*User does this in the Workday tenant UI:*

1. After registering (or later: **Search** `View API Client` > find your client)
2. Click the **Related Actions** menu on the API Client
3. Select **API Client > Manage Refresh Tokens for Integrations**
4. Select **your Workday user account** from the picker
5. Click **Generate**
6. **CRITICAL:** The refresh token displays once. Copy it immediately.

The refresh token is **per user per client**. If multiple people need automation access,
each generates their own token under the same client.

### Step 5: Store the credentials

Two options (see credential-store-setup.md for full detail):

**Option A - Credential Manager (recommended):**
```powershell
python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py set-creds <profile>
```
Enter: base URL (the tenant's `tenantGwUrl`), tenant alias, auth mode `refresh`,
client ID, client secret, refresh token. All prompts are hidden.

**Option B - Environment variables:**
Set `WD_CLIENT_ID`, `WD_CLIENT_SECRET`, `WD_REFRESH_TOKEN` as Windows user env vars
(see credential-store-setup.md).

### Step 6: Test it

```powershell
python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py check-tenant <profile>
```

Success prints the tenant identity (tenant name, user display name). Failure shows the
HTTP error (see Part 3 for debugging).

---

## Part 2: Auth-code + PKCE (user-facing browser app)

This is for building an external web application where individual users sign in with
their own Workday accounts.

### Step 1: Register a WCP API Client (developer portal)

*User does this on developer.workday.com:*

1. Sign in to the **Workday Developer Portal** (developer.workday.com)
2. Navigate to your app's configuration
3. Register a **Public** WCP API Client (no secret - public clients use PKCE instead)
4. Configure:

| Setting | Value |
|---|---|
| Redirect URIs | Your app's callback URL(s) (e.g., `http://localhost:3000/callback` for dev, `https://app.example.com/callback` for prod) |
| Scopes | Set ON the client (NOT passed as a URL parameter) |
| Authorized CORS Domains | Your app's origin(s) (e.g., `http://localhost:3000`, `https://app.example.com`) - this solves browser CORS errors |

5. Note the **Client ID** (public - safe to include in frontend code)

### Step 2: Implement the auth flow

The authorization endpoint: `https://auth.api.workday.com/v1/authorize`
The token endpoint: `https://auth.api.workday.com/v1/token`

**Key differences from standard OAuth:**
- Token exchange uses `Authorization: ID <base64(client_id)>` (NOT `Basic`)
- No `scope` parameter in the authorize URL - scopes come from the client registration
- Optional `tenantAlias` parameter in the authorize URL skips the tenant picker
- No refresh token - on expiry, the user re-authenticates

### Step 3: Use the token

The JWT bearer works at the `api.workday.com` gateway, executing as the signed-in user.
`/me` URL aliases resolve to the current user's worker record.

**Cross-ref:** wd-extend-dev `references/external-apis-and-genai.md` (reverse-direction
section) for the full PKCE implementation pattern with code examples.

### Official OAuth facts (official-docs - developer.workday.com, 2026-08-25)

- **Four grant types officially listed** (Concept: Authorization Flows): Implicit (browser apps), Authorization Code (server web apps, optional refresh token), Authorization Code + PKCE (public clients), Client Credentials (no-user integrations). Bearer tokens only.
- **"All Workday Extend access tokens expire after 60 minutes"** (official statement). RECONCILIATION with Part 1: this covers the Extend/WCP-gateway token surface (it corroborates the ~1 hr wdcli bearer in auth-decision-tree.md Mode 1). The in-tenant API Client / CLASSIC tenanted-host access token in Part 1 is a SEPARATE surface whose default TTL is configured per API Client and varies by tenant and release - treat any specific number as a starting point to verify (see the verify-in-tenant rule in `wd-extend-lifecycle/references/verify-in-tenant.md`). The irreversible "Enforce 60 Minute Access Token Expiry" checkbox is the one hard cap: once enabled it forces that surface to 60 min max.
- **Cross-region API calls fail with 401 Unauthorized** - the region is fixed by the Developer Site profile; always call the matching regional gateway.
- **Regional gateway / auth base URLs:**

| Region | API gateway | Auth base |
|---|---|---|
| Personal dev accounts | `https://api.odp.wcp.workday.com` | gateway + `/auth` |
| US | `https://api.workday.com` or `https://api.us.wcp.workday.com` | gateway + `/auth` (also `https://auth.api.workday.com`) |
| Germany/EU | `https://api.eu.wcp.workday.com` | gateway + `/auth` |
| Singapore | `https://api.sg.wcp.workday.com` | gateway + `/auth` |
| UK | `https://api.uk.wcp.workday.com` | gateway + `/auth` |

SP Entity / Audience URI = auth base + `/sp`.

---

## Part 3: Debugging OAuth issues

### Token exchange errors

| Error | Cause | Fix |
|---|---|---|
| `invalid_client` | Client ID or secret is wrong | Re-check the client ID. If the secret was lost, register a new client. |
| `invalid_grant` | Refresh token is wrong, expired, or was never generated for this user | Go to **Manage Refresh Tokens for Integrations** on the API Client. Check if a token exists for your user. If not, generate one. If stale, regenerate. |
| `unauthorized_client` | OAuth not enabled in tenant, or the client's grant type isn't permitted | Check `Edit Tenant Setup - Security` > OAuth 2.0 Clients Enabled. Check the client's allowed grant types. |
| `invalid_scope` | Requested scope not configured on the client | Edit the API Client registration to add the needed scope. For PKCE: scopes are set on the client, not in the URL. |
| `access_denied` | The user's security policy doesn't allow this client | Check that the API Client's functional areas align with the user's security groups. |
| 400 with no body | Token endpoint URL is wrong (e.g., using the UI host instead of the gateway host, or wrong tenant in the URL) | Token URL for refresh grant: `https://<tenantGwUrl>/ccx/oauth2/<tenant>/token`. Get the `tenantGwUrl` from `wdcli tenant list -f json --ci`. |

### Bearer usage errors

| Error | Cause | Fix |
|---|---|---|
| 401 `Invalid access token` | Using a wdcli bearer at a classic tenanted host (or vice versa) | Tokens don't cross host styles. wdcli bearer = WCP gateway only. Refresh bearer = classic host only. See auth-decision-tree.md. |
| 401 on a previously-working call | Access token expired (short-lived for refresh grant - per-client TTL, confirm in-tenant; ~1 hr for wdcli) | Re-mint: `tenant_toolkit.py` auto-refreshes; for manual testing, re-run `wdcli tenant token <alias> --ci`. |
| 403 `Insufficient permissions` | The user/ISU lacks the security domain for this operation | Not an OAuth issue - this is a security grant issue. See wd-extend-dev `references/security-setup.md`. |
| 403 but only for some operations | Scopes on the API Client don't include this service area | Edit the API Client registration to add the needed scope. |
| CORS error in browser | CORS domain not registered on the WCP API Client | Add your app's origin to the client's **Authorized CORS Domains** on developer.workday.com. |
| S22 permission denied (Extend BO calls) | App's security domains not granted in this tenant | Not OAuth - this is tenant security setup. See wd-extend-dev `references/security-setup.md`. |

### Token introspection (debugging what a token can do)

There is no standard Workday token-introspection endpoint. To verify what a token
reaches:

1. **For wdcli bearer:** `wdcli whoami` shows the identity. Test an API call:
   ```powershell
   wdcli tenant token <alias> --ci
   # Copy the token, then test with curl or the toolkit
   ```
2. **For refresh bearer:** `tenant_toolkit.py check-tenant <profile>` mints and tests.
3. **For either:** Try a lightweight read (e.g., WQL `SELECT workdayID FROM workers
   LIMIT 1`) - success proves the token is valid and has at least basic read access.

### Corporate network issues

- Corporate SSL inspection (TLS-intercepting proxy) can break certificate validation
  for Python scripts calling `myworkday.com` hosts. The tenant toolkit handles this
  automatically (retry with `verify=False` and a visible warning). For custom scripts,
  use the `truststore` package or set `REQUESTS_CA_BUNDLE` to the corporate CA cert.
- The WCP gateway (`api.us.wcp.workday.com`) is typically NOT intercepted.
- If `wdcli auth login` fails to open a browser, check proxy settings. wdcli uses the
  system browser - if the proxy blocks the OAuth redirect, auth cannot complete.

### Scope reference (common Workday OAuth scopes)

Scopes are coarse-grained categories, not per-endpoint controls. Granting a scope does
not bypass security domain checks (those are separate):

| Scope | Category |
|---|---|
| System | Core platform, tenant config |
| Tenant Non-Configurable | Metadata, public info |
| Integration | Integration services |
| Implementation | Private implementation services |
| Custom Objects | Extend BO REST API |
| Staffing | Worker, position, job |
| Human Resources | HR-specific operations |
| Organizations | Org hierarchies |
| Financial Management | FIN transactions |
| Payroll | Payroll data |
| Benefits | Benefits administration |
| Recruiting | Recruiting/talent |
| Student | Student (Higher Ed) |
| Time Tracking | Time entry/approval |
