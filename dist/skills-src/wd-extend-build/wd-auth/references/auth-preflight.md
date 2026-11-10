# Auth preflight check - run before every build/deploy/API session

This is the agent's auth-readiness gate. Run it at the start of any session that will
touch a Workday tenant. It catches expired tokens, wrong-org state, and missing
credentials BEFORE a build/deploy fails with a misleading error.

---

## The preflight sequence

Run these checks in order. Stop at the first failure and surface the USER-ACTION block.

### Check 1: wdcli auth (if the session will use wdcli)

```powershell
wdcli whoami --ci -f json
```

**Pass:** Returns JSON with the user's email and org short ID.
**Verify:** The org short ID matches the target app's org. If not, the user needs to
switch (Check 1b).

**Fail patterns:**
- `Not logged in. Run "wdcli auth login"` -> developer session expired
- Any other auth error -> developer session expired or corrupted
- Command not recognized -> wdcli not installed or not on PATH

### Check 1b: Org verification (multi-org environments)

Compare the org from `whoami` against the intended target:

| Target | Expected org |
|---|---|
| Firm apps (e.g., `<app>_<firm-org>`) | `<firm-org>` |
| Client apps (e.g., a client tenant) | The client's org short ID (e.g., `client01`) |

If wrong:

```powershell
wdcli account switch <correct-shortId> --ci
```

Then re-run `whoami` to confirm.

### Check 2: Tenant auth (if the session will deploy)

```powershell
wdcli tenant list -f json --ci
```

**Pass:** Returns a list of tenants with their promotion levels.
**Verify:** The target tenant appears in the list and shows the expected promotion level.

**Fail:** `The command requires tenant authentication` -> the user needs to run
`wdcli tenant login <alias>`.

### Check 3: Environment variables (if the session will use REST/SOAP directly)

```powershell
# Check presence without revealing values
[bool]$env:WD_IMPL_USER
[bool]$env:WD_IMPL_PASSWORD
```

Or for OAuth client credentials:
```powershell
[bool]$env:WD_CLIENT_ID
[bool]$env:WD_CLIENT_SECRET
[bool]$env:WD_REFRESH_TOKEN
```

**Pass:** All relevant vars return `True`.
**Fail:** Any return `False` -> the user needs to set them (credential-store-setup.md).

### Check 4: Credential Manager profile (if the session will use tenant_toolkit)

```powershell
python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py check-tenant <profile>
```

**Pass:** Prints tenant identity (tenant name, user display name).
**Fail:** Prints the error (invalid_grant, connection error, etc.) -> see
auth-troubleshooting.md.

---

## USER-ACTION blocks (surface these verbatim when a check fails)

### Developer session expired

```
YOUR STEPS (outside this session):
1. In your terminal, run:  wdcli auth login
2. A browser opens. Sign in with your Workday SSO credentials.
3. Complete MFA (Duo / Authenticator) if prompted.
4. The terminal prints "Login successful" (or similar).
5. Tell me "done" when you see the success message.
```

### Tenant auth expired

```
YOUR STEPS (outside this session):
1. In your terminal, run:  wdcli account switch <orgShortId>
   (skip if the org is already correct - I'll tell you which org)
2. Then run:  wdcli tenant login <tenantAlias>
   (the alias is positional - no -t flag here)
3. A browser opens. Sign in and complete MFA if prompted.
4. Tell me "done."
```

### Wrong org active

```
YOUR STEPS (outside this session):
1. In your terminal, run:  wdcli account switch <correctOrgShortId>
   For example:  wdcli account switch <firm-org>     (for your firm)
                 wdcli account switch client01   (for a client)
2. Tell me "done."
```

### Environment variables not set

```
YOUR STEPS (outside this session):
1. Press Win + R, type sysdm.cpl, press Enter.
2. Go to Advanced > Environment Variables.
3. Under User Variables, click New and add:
   - Variable name:  <VAR_NAME>
   - Variable value:  <paste the credential>
4. Click OK on all dialogs.
5. RESTART this Claude Code session (env vars only load on session start).
6. Tell me "restarted."
```

### Credential Manager profile missing or invalid

```
YOUR STEPS (outside this session):
1. In your terminal, run:
   python <skills-path>\wd-extend-dev\scripts\tenant_toolkit.py set-creds <profile>
2. Answer each prompt (input is hidden - paste and press Enter):
   - Base URL:       <I'll provide this>
   - Tenant:         <alias>
   - Auth mode:      refresh
   - Client ID:      <paste your client ID>
   - Client Secret:  <paste your client secret>
   - Refresh token:  <paste your refresh token>
   - Allow writes:   y  (if this is a dev tenant you'll write to)
3. Tell me "done."
```

---

## Preflight as a reusable pattern

The agent should run the preflight at these points:

1. **Start of any Extend build/deploy session** (Checks 1, 1b, 2)
2. **Before any REST/SOAP API call** (Check 3 or 4, depending on auth mode)
3. **After any "tenant not found" or auth error** (re-run all checks - don't chase
   phantom bugs before confirming auth state)
4. **After the user says "done"** following a USER-ACTION block (re-run the failed
   check to confirm it's fixed)

The check sequence is fast (~5 seconds total for checks 1-3). Run it early, catch
failures early, don't waste time debugging code that's actually fine.

---

## Cross-ref

- wdcli install + common errors: wd-extend-dev `references/wdcli-setup.md`
- Build loop with auth integration: wd-extend-dev `references/wdcli-workflow.md`
- Consolidated error table: auth-troubleshooting.md (this skill)
