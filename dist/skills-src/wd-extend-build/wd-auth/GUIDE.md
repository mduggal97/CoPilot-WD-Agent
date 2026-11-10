---
name: wd-auth
description: >-
  Workday authentication, credentials, and OAuth setup across all surfaces - wdcli,
  REST/SOAP/WQL/RaaS APIs, tenant UI, and the developer portal. PREFLIGHT GATE: consult BEFORE the
  first wdcli command in a session, BEFORE opening any Workday URL in the in-app browser (no SSO
  session there, so a login handoff is needed), and BEFORE any API call - to catch expired tokens
  and wrong-org state early. TRIGGERS: storing credentials, API tokens or secrets, configuring
  OAuth API Clients, auth failures (401, 403, token expiry, invalid_grant, invalid_client, "not
  logged in", "tenant not found or is not a development tenant", S22 permission denied), choosing
  an auth mode (wdcli vs refresh vs basic vs PKCE), rotating or revoking credentials, multi-org
  switching (wdcli account switch, wdcli whoami), MFA/SSO constraints, or "why can't the agent log
  in for me" / "how do I connect Claude to the tenant". Owns the auth DECISION; wdcli install, the
  build loop, and ISU/ISSG grants live in wd-extend-dev.
---

# Workday Authentication & Credential Management

This skill is the cross-suite authority on Workday auth. It answers "which auth mode do I
use," "how do I set up credentials," and "why is auth failing" before handing off to the
skill that owns the specific surface (wd-extend-dev for wdcli/tenant ops, wd-deployment
for promotion auth, wd-integration-dev for integration auth).

## Quick decision - which auth mode?

| You need to | Auth mode | Credential store | Details |
|---|---|---|---|
| Build/deploy Extend apps (wdcli) | wdcli OAuth (device code) | wdcli manages its own token | [auth-decision-tree.md](references/auth-decision-tree.md) |
| Call REST/WQL from the toolkit or scripts | wdcli bearer OR refresh-token grant | Windows Credential Manager (toolkit profile) | [auth-decision-tree.md](references/auth-decision-tree.md) |
| Call SOAP/WWS or RaaS | Refresh-token grant (Mode 2 bearer); HTTP Basic is being retired ~R2 2026 - legacy/transitional only, verify in-tenant | Credential Manager (Basic: env vars, legacy) | [credential-store-setup.md](references/credential-store-setup.md) |
| Build a user-facing SPA over Extend data | OAuth auth-code + PKCE (public WCP client) | Browser session (no stored secret) | [oauth-setup-guide.md](references/oauth-setup-guide.md) |
| Automate unattended integration runs | API Client refresh-token grant | Credential Manager profile | [oauth-setup-guide.md](references/oauth-setup-guide.md) |
| Log into tenant UI or developer portal | SSO + MFA (human only) | N/A - agent cannot do this | [mfa-and-browser-auth.md](references/mfa-and-browser-auth.md) |

## Reference map - read what you need

| You need to | Read |
|---|---|
| **Choose the right auth mode** for the task at hand | [references/auth-decision-tree.md](references/auth-decision-tree.md) |
| **Set up credential storage** (env vars, Credential Manager, security guidance) | [references/credential-store-setup.md](references/credential-store-setup.md) |
| **Set up an OAuth API Client** in a Workday tenant from scratch, or debug token flows (invalid_grant, scope errors, CORS, PKCE) | [references/oauth-setup-guide.md](references/oauth-setup-guide.md) |
| **Run the auth preflight check** before a build/deploy/API session (wdcli whoami, token validity, org verification) | [references/auth-preflight.md](references/auth-preflight.md) |
| **Diagnose an auth failure** (consolidated error -> cause -> fix table across all surfaces) | [references/auth-troubleshooting.md](references/auth-troubleshooting.md) |
| **Understand MFA/SSO constraints** and what the agent can vs cannot do in a browser | [references/mfa-and-browser-auth.md](references/mfa-and-browser-auth.md) |

## Boundaries

- **wdcli install, build loop, app commands:** wd-extend-dev `references/wdcli-setup.md` and `wdcli-workflow.md`
- **Tenant ops, toolkit profiles, WRITE GATE:** wd-extend-dev `references/tenant-ops.md`
- **ISU, security domains, API client grants:** wd-extend-dev `references/security-setup.md`
- **Promotion auth, per-tenant re-setup:** wd-deployment `references/promotion-and-environments.md`
- **Smartsheet API token (generation + secure storage):** wd-smartsheet `references/token-setup.md` (the in-suite owner)

## Lifecycle neighbors

This skill runs BEFORE every other wd-* skill that touches Workday - if auth isn't working, nothing else works; the preflight check (auth-preflight.md) is the gate. Consulted BY: wd-extend-dev + wd-integration-dev (before wdcli/API/SOAP work), wd-test-execution + wd-tenant-config (the browser login handoff), wd-deployment (per-tenant credential setup). This skill owns the auth DECISION + login handoff; the ISU/ISSG/domain grants themselves live in wd-extend-dev security-setup.md + wd-deployment.

**Quality-gate rule (suite-wide):** the auth preflight (auth-preflight.md) is a named check in wd-extend-lifecycle references/quality-gates.md - run it before the first wdcli/API/browser-tenant action and report the result.
