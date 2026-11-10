# MFA, SSO, and browser auth - what the agent can and cannot do

This reference documents the hard constraints on browser-based Workday authentication
and the patterns for working around them.

---

## The constraint

Three independent factors make browser-based Workday auth impossible for an AI agent:

1. **Credential entry is prohibited.** The agent cannot type passwords, API keys, or
   tokens into any field - this is a safety boundary, not a technical limitation.

2. **MFA requires a human with a physical device.** Duo push notifications,
   authenticator TOTP codes, and hardware keys all require the user's phone or token
   generator. No credential storage or automation can bypass this step.

3. **The in-app browser is isolated.** Claude Code's built-in browser is a fresh
   Chromium instance with no cookies, no SSO sessions, and no saved credentials. Even
   if the user is logged into Workday in their real browser, the in-app browser has no
   access to that session. The Claude in Chrome extension (which could bridge to the
   real browser) is blocked by corporate IT policy.

**Result:** The agent cannot log into:
- Workday tenant UI (e.g., `wcpdev.wd101.myworkday.com`)
- Workday Developer Portal (`developer.workday.com`)
- Workday Community (`community.workday.com`)
- Any SSO-protected Workday surface

---

## What the agent CAN do (no browser/MFA needed)

| Task | How | Auth mode |
|---|---|---|
| Build/deploy Extend apps | `wdcli` commands in PowerShell (user pre-authenticates) | wdcli OAuth - stored token |
| Query tenant data (WQL, REST) | `tenant_toolkit.py` or direct HTTP calls | Refresh-token bearer or wdcli bearer |
| Call SOAP/WWS operations | HTTP requests with the Mode 2 refresh-token bearer | Refresh-token bearer via Credential Manager (HTTP Basic for web services is being retired ~R2 2026 - verify in-tenant, do not design new work on it; see auth-decision-tree.md Mode 2) |
| Fetch WSDL schemas | Anonymous HTTP GET | None needed |
| Read RaaS custom reports | `tenant_toolkit.py raas` | Refresh-token bearer |
| Download/upload Extend app source | `wdcli app download/upload` | wdcli OAuth - stored token |

All of these work because the auth token is **pre-established** by the user (via
browser login + MFA) and then **reused** by the agent via stored token or env var.

---

## The handoff pattern - USER-ACTION blocks

When the agent needs something that requires browser/MFA auth, it surfaces a
USER-ACTION block: a fenced, numbered checklist the user follows in their own
terminal or browser. The agent waits for the user to signal completion, then continues.

### Standard USER-ACTION block format

```
YOUR STEPS (outside this session):
1. [WHERE to go / what to open]
2. [EXACT thing to type or click]
3. [What you'll see when it works]
4. Tell me "done" (or paste the result if I asked for one).
```

Rules for writing USER-ACTION blocks:
- **Every step names the exact location** (which app, which menu, which field)
- **Every step names the exact value** to enter (not "your credentials" but "your
  Workday email")
- **Include what success looks like** ("The terminal prints 'Login successful'")
- **End with a signal** ("Tell me done" or "Paste the output here")
- **Never ask the user to paste secrets** into chat (passwords, tokens, keys)

### Common handoff scenarios

**wdcli re-auth** (most frequent - tokens expire during a work session) and **tenant login**
(needed before first deploy to a tenant): the canonical USER-ACTION blocks for both are OWNED by
[auth-preflight.md](auth-preflight.md) "USER-ACTION blocks" (Developer session expired / Tenant auth
expired) - surface those verbatim; do not restate them here.

**API Client registration** (first-time setup):

```
YOUR STEPS (in the Workday tenant UI):
1. Search: "Register API Client for Integrations"
2. Client Name: TenantOps - <tenantAlias>
3. Check: Non-Expiring Refresh Tokens
4. Leave UNCHECKED: Enforce 60 Minute Access Token Expiry
5. Scopes: System, Tenant Non-Configurable, Integration, Implementation, Custom Objects
6. Click OK
7. COPY the Client ID and Client Secret shown (they appear ONCE)
8. DO NOT paste them here - hold them for the next step
```

**Developer portal task** (e.g., WCP API Client for PKCE):

```
YOUR STEPS (on developer.workday.com):
1. Sign in to the Workday Developer Portal
2. Navigate to: [exact path I'll provide]
3. [Exact configuration steps]
4. Note the Client ID (this one is public - you CAN paste it here)
5. Tell me "done" and paste the Client ID
```

---

## MFA types and their impact

| MFA method | How it works | Agent impact |
|---|---|---|
| **Duo Push** | Notification to the Duo Mobile app; user taps Approve | Agent waits; user signals "done" after approving |
| **Duo Passcode** | 6-digit code from Duo Mobile app | User enters it in the browser; agent cannot |
| **Authenticator app (TOTP)** | 6-digit rotating code from Microsoft/Google Authenticator | Same as Duo Passcode |
| **Hardware token (YubiKey, etc.)** | Physical key tap or USB insert | User performs it; agent cannot |
| **SMS code** | 6-digit code sent via text message | User enters it; agent cannot |

All MFA methods require the user at the keyboard with their physical device. None can
be automated or delegated to the agent.

---

## What about session persistence?

Once the user completes MFA and signs in:
- **wdcli tokens** persist on disk and survive terminal restarts. They do NOT require
  re-authentication for every command - only when the token expires (hours to days
  depending on the token type).
- **API Client refresh tokens** are non-expiring (if configured). Once stored in
  Credential Manager, they work indefinitely until revoked by a tenant admin.
- **Browser sessions** (tenant UI, developer portal) have their own session cookies.
  These do not help the agent since the agent uses API tokens, not browser sessions.

**Practical impact:** The user typically authenticates once at the start of a work
session. The agent then works uninterrupted until a token expires (usually hours later).
Re-auth is infrequent.

---

## Future possibilities (not available today)

- **Workday MCP server:** If Workday publishes a hosted MCP server (like Smartsheet
  did), it could use a stored API token without browser auth. Not available as of
  Aug 2026.
- **Claude in Chrome on corporate-managed machines:** If IT policy changes to allow the extension,
  the agent could potentially drive the user's real browser (with its existing SSO
  session) for read-only tenant browsing. Still could not bypass MFA for new sessions.
- **Passkey/WebAuthn support in wdcli:** If Workday adds non-browser auth flows
  (device attestation, passkeys), wdcli might authenticate without opening a browser.
  Speculative.

---

## Boundary - login handoff vs driving mechanics

This skill owns only the LOGIN HANDOFF (getting a human through SSO + MFA so a session
exists). It does NOT own the mechanics of DRIVING the in-app browser once you are in -
dropdown-search prompts, grids, async pickers, and the rest. Those live with their owner:
`wd-test-execution/references/browser-mechanics.md`.

## Cross-ref

- Browser-automation policy: check your firm's policy on driving an SSO browser session before automating any login (on the author's environment this lives in local memory; it is not part of the suite)
- Auth preflight (detect expired tokens early): auth-preflight.md (this skill)
- Credential storage: credential-store-setup.md (this skill)
- In-app browser DRIVING mechanics (not login): `wd-test-execution/references/browser-mechanics.md`
