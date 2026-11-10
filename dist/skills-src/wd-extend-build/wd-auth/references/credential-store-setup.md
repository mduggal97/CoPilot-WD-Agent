# Credential store setup

Two storage mechanisms, each with a sweet spot. Use both - they're complementary.

---

## Option A: Windows environment variables

Best for: static credentials used by scripts and MCP server configs (the Smartsheet
pattern). Simple, works everywhere, no Python dependency.

### Setup (one-time, persistent across reboots)

The user runs these steps outside the Claude session:

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to **Advanced** tab, click **Environment Variables**
3. Under **User variables** (top section, not System), click **New** for each:

| Variable name | Value | Used by |
|---|---|---|
| `WD_IMPL_USER` | Implementer username (e.g., `impl-user@<tenant_alias>`) | SOAP/WWS Basic auth - LEGACY/transitional (see caveat below) |
| `WD_IMPL_PASSWORD` | Implementer password | SOAP/WWS Basic auth - LEGACY/transitional (see caveat below) |
| `WD_CLIENT_ID` | OAuth API Client ID | Refresh-token grant scripts |
| `WD_CLIENT_SECRET` | OAuth API Client secret | Refresh-token grant scripts |
| `WD_REFRESH_TOKEN` | OAuth refresh token | Refresh-token grant scripts |
| `SMARTSHEET_API_TOKEN` | Smartsheet API token (already set if using Smartsheet MCP) | Smartsheet MCP server |

4. Click OK on all dialogs
5. **Restart all terminals** (env vars only apply to terminals opened after the change)

> **LEGACY caveat - `WD_IMPL_USER` / `WD_IMPL_PASSWORD` (HTTP Basic):** HTTP Basic auth for
> Workday web services is being retired (~R2 2026); use the Mode 2 refresh-token bearer for
> SOAP/WWS. A tenant may still have Basic enabled transitionally - verify in-tenant - but
> do not design new work on it. Store `WD_CLIENT_ID` / `WD_CLIENT_SECRET` / `WD_REFRESH_TOKEN`
> (or a Credential Manager `refresh` profile) and take the Mode 2 path instead
> (auth-decision-tree.md Mode 2). Keep the Basic rows only for a tenant confirmed still on it.

### Multi-tenant env vars

When working across multiple tenants, suffix the variable name with the tenant:

| Variable | Example |
|---|---|
| `WD_IMPL_USER_FIRM` | `impl-user@<firm_tenant>_wcpdev2` |
| `WD_IMPL_USER_CLIENT` | `impl-user@<client_tenant>_wcpdev2` |
| `WD_CLIENT_ID_FIRM` | (client ID for the firm dev tenant) |
| `WD_CLIENT_ID_CLIENT` | (client ID for the client dev tenant) |

Scripts resolve the suffix from a `--tenant` or `--profile` flag.

### Verification (agent can run these)

```powershell
# Check that env vars are set (prints True/False, never the actual value)
[bool]$env:WD_IMPL_USER
[bool]$env:WD_IMPL_PASSWORD
[bool]$env:WD_CLIENT_ID
[bool]$env:WD_CLIENT_SECRET
[bool]$env:WD_REFRESH_TOKEN
```

### Security considerations

- **Never hardcode credentials in files that sync** (OneDrive, Git repos, `.env` files
  in synced project folders). Environment variables avoid this entirely.
- **Never echo/print the actual value** in chat or logs. Use the `[bool]` check above
  to verify presence without revealing the secret.
- Env vars are visible to every process running as your user. For higher isolation, use
  Option B (Credential Manager).
- If the project folder syncs to OneDrive (as this workspace does), `.env` files are
  NOT safe even if `.gitignore`d - OneDrive still syncs them. Use system env vars or
  Credential Manager instead.

---

## Option B: Windows Credential Manager (via tenant_toolkit.py)

Best for: multi-profile tenant credentials managed by the tenant toolkit. Stronger
isolation than env vars (per-app access control), and the toolkit's `set-creds` uses
hidden prompts so secrets never appear on screen.

### Setup (per tenant profile)

The user runs this outside the Claude session:

```powershell
python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py set-creds <profile-name>
```

The script prompts (hidden input - nothing displays while pasting):

| Prompt | What to enter |
|---|---|
| Base URL | For wdcli auth: `https://api.us.wcp.workday.com` / For refresh auth: the tenant's `tenantGwUrl` from `wdcli tenant list -f json --ci` |
| Tenant | The tenant alias (e.g., `<firm_tenant>_wcpdev2`) |
| Auth mode | `wdcli` (dev tenants, uses wdcli bearer) or `refresh` (API client, standing) |
| Client ID | (refresh mode only) The API Client ID |
| Client Secret | (refresh mode only) The API Client secret |
| Refresh Token | (refresh mode only) The non-expiring refresh token |
| Allow writes | `y` only for dev tenants you intend to write to |

### Where Credential Manager stores it

Windows Credential Manager (accessible via Control Panel > Credential Manager > Windows
Credentials). The toolkit stores entries under service name `workday_tenant_<profile>`.
Readable only by the current Windows user.

### Verification (agent can run)

```powershell
python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py check-tenant <profile-name>
```

This mints a bearer from the stored credentials, hits a harmless endpoint, and prints
the tenant identity. If it fails, the credentials are wrong or expired.

---

## Which store for which mode

| Auth mode | Recommended store | Why |
|---|---|---|
| wdcli OAuth (Mode 1) | N/A - wdcli manages its own | No user-managed credential |
| API Client refresh (Mode 2) | **Credential Manager** via toolkit | Multi-profile, hidden prompts, stronger isolation |
| HTTP Basic / ISU (Mode 3) - LEGACY/transitional | **Env vars** (`WD_IMPL_USER` / `WD_IMPL_PASSWORD`) | Basic for web services is being retired (~R2 2026) - verify in-tenant; for new work use Mode 2 (refresh bearer) instead |
| OAuth PKCE (Mode 4) | N/A - browser-session-based | No server-side credential |
| MCP server configs | **Env vars** (like Smartsheet pattern) | MCP headers reference `${VAR_NAME}` |

---

## MCP server credential pattern (extending the Smartsheet model)

If a Workday-connected MCP server becomes available (or you build one), register it the
same way as Smartsheet:

```json
{
  "mcpServers": {
    "workday-tenant": {
      "type": "http",
      "url": "https://your-workday-mcp-endpoint",
      "headers": {
        "Authorization": "Bearer ${WD_BEARER_TOKEN}"
      }
    }
  }
}
```

The `${VAR_NAME}` syntax in Claude Code's `settings.json` resolves against env vars at
connection time. The actual token never appears in the config file.

**Current limitation:** Workday does not host a public MCP server (unlike Smartsheet).
If you build a local MCP proxy, it would need to handle token refresh internally.

---

## Credential rotation checklist

When rotating credentials (password change, token revocation, client secret rotation):

1. **Identify which store holds the credential** (env var, Credential Manager, or wdcli)
2. **Update the store:**
   - Env var: `sysdm.cpl` > Environment Variables > edit the value > restart terminals
   - Credential Manager: re-run `set-creds <profile>` (overwrites the old entry)
   - wdcli: re-run `wdcli auth login` / `wdcli tenant login`
3. **Verify:** run the appropriate check (env var `[bool]` test, `check-tenant`, or
   `wdcli whoami`)
4. **If rotating an API Client secret:** the old secret is invalidated immediately.
   Update the store BEFORE any script needs it, or those scripts will fail with
   `invalid_client`.
