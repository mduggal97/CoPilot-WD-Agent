# Auth troubleshooting - consolidated error table

One table across all auth surfaces. When an auth-related error appears, find it here
first. Each entry names the surface it applies to and the exact fix.

---

## Error -> cause -> fix

### wdcli errors

| Error message | Cause | Fix |
|---|---|---|
| `Not logged in. Run "wdcli auth login"` | Developer session token expired (the full org-level auth) | User runs `wdcli auth login` in their terminal (browser OAuth + MFA) |
| `The command requires tenant authentication to proceed... wdcli tenant login` | Tenant-specific deploy token expired (separate from developer session) | User runs `wdcli tenant login <alias>` (alias is positional, no `-t` flag) |
| `The tenant <name> was not found or is not a development tenant` | **Wrong org is active** (machine-global state flipped by a parallel session or the user). The tenant exists - wdcli is just looking in the wrong org | `wdcli whoami` to see which org is active, then `wdcli account switch <correctOrgShortId> --ci`, then retry |
| `Nonexistent flag: -t` on `tenant login` | `-t` belongs to `app deploy`, NOT `tenant login`. The alias is positional | `wdcli tenant login <alias>` (no flag) |
| `A version is required` | Missing `--latest-version` on download/promote | Add `--latest-version` (or `--version` / `--version-id`) |
| `'C:\Program' is not recognized` on `app create` | Git-Bash mangled the unquoted wdcli install path | Run `app create` from **PowerShell**, not Git-Bash |
| `app deploy` hangs on tenant picker | Deploy always prompts for a tenant unless specified | Pass `-t <alias>` explicitly: `wdcli app deploy <refId> -t <alias> --latest-version` |
| `Cannot read properties of undefined (reading 'success')` | Usually a masked **Error 10: duplicate metadata** from a non-additive BO change | Check App Builder UI for the real error. Fix the model (append-only fields). Do NOT delete/recreate the app |
| Instant build failure, no compile output | Log lag (errors populate ~5s after failure) OR infra transient | Wait 5s, re-fetch build log. No compile lines at all = transient, re-upload. Compile lines present = real error, fix code |

### REST / WQL / toolkit errors

| Error / symptom | Cause | Fix |
|---|---|---|
| 401 `Invalid access token` | Token from one host style used at the other (wdcli bearer at classic host, or refresh bearer at WCP gateway) | Tokens don't cross styles. Use the right auth mode for the host. See auth-decision-tree.md |
| 401 `Invalid access token` on a WQL/REST seed load using the wdcli tenant token | The **`wdcli tenant token` is Extend-platform-scoped** - the general WQL/REST API rejects it (verified 2026-08-26) | Seed loads and out-of-app data reads/writes need a SEPARATELY-scoped ISU / API client + refresh grant, NOT the Extend token. See wd-extend-dev data-loading-and-retrieval.md Section 2 |
| 401 on previously-working call | Access token expired (refresh-grant token is short-lived - per-client TTL, confirm in-tenant; wdcli ~1 hr) | For toolkit: it auto-refreshes. For manual: re-mint (`wdcli tenant token` or re-run the script) |
| 403 `Insufficient permissions` | User/ISU missing the security domain for this operation | Not an auth issue - it's a security grant issue. See wd-extend-dev security-setup.md |
| S22 permission denied (Extend BO) | App's security domains not granted in this tenant | Same as above - tenant admin grants the domains |
| `invalid_client` (token exchange) | Client ID or secret is wrong | Re-check. If secret lost, register a new API Client |
| `invalid_grant` (token exchange) | Refresh token wrong, expired, or never generated for this user | In tenant: View API Client > Related Actions > Manage Refresh Tokens > check/regenerate for your user |
| `unauthorized_client` | OAuth 2.0 not enabled in the tenant | Tenant admin: `Edit Tenant Setup - Security` > check OAuth 2.0 Clients Enabled |
| `invalid_scope` | Scope not configured on the API Client | Edit the client registration to add the needed scope |
| 400 empty body on token exchange | Token endpoint URL is wrong | Must be `https://<tenantGwUrl>/ccx/oauth2/<tenant>/token`. Get `tenantGwUrl` from `wdcli tenant list -f json --ci` |
| `ConnectionError` / `SSLError` | Corporate SSL inspection breaking cert validation | Use `truststore` package, or set `REQUESTS_CA_BUNDLE`. The toolkit auto-retries with verify=False. WCP gateway is typically not intercepted |
| CORS error in browser | CORS domain not on the WCP API Client | Add origin to Authorized CORS Domains on developer.workday.com |

### SOAP / WWS errors

| Error / symptom | Cause | Fix |
|---|---|---|
| 401 on SOAP call | Wrong auth mode or bad credentials | SOAP needs the API-client refresh bearer (Basic auth retired ~R2 2026). wdcli bearer does NOT work for SOAP |
| SOAP Basic fails tenant-wide ("invalid username or password") while UI login works | Workday retired Basic auth for web services (~R2 2026); the Tenant Setup opt-out checkbox is gone | Not a password problem - switch to an API client + refresh grant (auth-decision-tree.md Mode 2; setup runbook in wd-extend-dev tenant-ops.md Path B) |
| Refresh token stored but token mint gets 400 "Invalid request" | A JWT (starts `eyJ`, ~1,000 chars, 2 dots) was pasted instead of the refresh token | The real refresh token from "Manage Refresh Tokens for Integrations" is a plain ~100-char string, no dots. Check length/shape without printing the value; regenerate and re-store |
| 500 `Element not found in envelope` | Wrong XML element name (used the display name instead of the WSDL element) | Element names come from the WSDL, not the op display name (e.g., display "Get Organization Subtypes" -> element `Get_Organization_Subtype_Request`, singular) |
| 404 on `/ccx/service/<tenant>/` | Service directory index is disabled (expected) | Enumerate services via in-tenant Public Web Services report or WQL `publicWebServices` |
| Timeout connecting to SOAP host | Wrong host URL. SOAP uses the gateway services host, not the UI host | Use `tenantGwUrl` (e.g., `wcpdev-services1.wd101.myworkday.com`), not the base URL |

### Browser / SSO / MFA errors

| Situation | Reality | What to do |
|---|---|---|
| Agent needs to log into tenant UI | **Cannot be automated** - SSO + MFA requires a human | Surface a USER-ACTION block with the URL and what to do once logged in |
| Agent needs developer portal access | **Cannot be automated** - SSO-gated | Same as above |
| MFA prompt during `wdcli auth login` | Expected - part of the OAuth flow | User completes MFA on their phone/authenticator |
| `wdcli auth login` browser doesn't open | Proxy/firewall blocking the OAuth redirect | User checks proxy settings, tries a different browser, or uses the URL manually |
| In-app browser has no SSO session | **Expected** - it's a fresh browser, separate from the user's real browser | Cannot piggyback on SSO sessions. Claude in Chrome extension is blocked by corporate IT policy |

---

## Triage sequence (when you hit an auth error)

1. **Read the error message literally.** Workday errors usually name the exact fix
   (e.g., "Run wdcli auth login" or "invalid_grant").
2. **Check which surface failed.** wdcli error? REST 401? SOAP 401? Browser? Different
   surfaces have different auth modes.
3. **Check if the org is correct** (`wdcli whoami`). The wrong-org issue is the #1
   misleading auth error in multi-org environments.
4. **Check token age.** If the call worked earlier in the session, the token likely
   expired. Re-mint rather than re-checking credentials.
5. **Don't chase code bugs first.** If a previously-working flow suddenly fails with
   auth errors, it's almost always a token/session expiry, not a code change.

---

## Cross-ref

- wdcli-specific errors with deeper context: wd-extend-dev `references/wdcli-setup.md` section 3
- Tenant toolkit errors: wd-extend-dev `references/tenant-ops.md`
- Security domain / permission errors: wd-extend-dev `references/security-setup.md`
