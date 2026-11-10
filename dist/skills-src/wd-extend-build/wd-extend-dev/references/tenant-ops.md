# Live tenant operations - check, verify, load

The suite's artifacts (design docs, security grants, test scenarios, migration checklists) name tenant facts. This reference is how we **check those facts against the live tenant and load data/config directly** instead of asking a human to eyeball Workday. Mechanics live here; each consuming skill (wd-testing, wd-deployment, wd-demo, wd-post-go-live) points at the relevant recipe.

Auth + transport: `scripts/tenant_toolkit.py` (**read-side VERIFIED live 2026-08-06 against a dev tenant**: check-tenant, wql, rest get). Endpoint shapes and per-op security domains come from the local schema snapshot ([rest-api-catalog.md](rest-api-catalog.md)). Credentials: Windows Credential Manager profiles via `set-creds` (hidden prompts) - never chat/files/env.

> **Auth is owned by wd-auth.** This reference covers the toolkit's *transport and read/write mechanics*; how you obtain each credential (mode selection, wdcli login, API-client + refresh-token registration, PKCE/SPA, expiry recovery) is owned by the **wd-auth** skill - see `wd-auth/references/auth-decision-tree.md`. Pointers below name the exact wd-auth page for each path.

**Host facts (all verified 2026-08-06):**
- `wdcli tenant list -f json --ci` returns **both hosts for every tenant** - `tenantBaseUrl` (UI) and `tenantGwUrl` (the tenanted services host, e.g. `https://wcpdev-services1.wd101.myworkday.com` for a dev tenant, `https://impl-services1.wd12.myworkday.com` for an impl tenant). Never guess hosts again - read them here.
- **Two host styles:** WCP gateway (`https://api.us.wcp.workday.com` - Extend BO REST `/apps/<ref>/v1/...`, WQL `/wql/v1/data`, NO tenant segment) vs classic tenanted host (token `/ccx/oauth2/{tenant}/token`, REST `/ccx/api/...`, SOAP `/ccx/service/{tenant}/...`).
- **Tokens don't cross styles:** a `wdcli tenant token` bearer works ONLY at the WCP gateway (tenanted host returns 401 "Invalid access token"); classic-host calls need the API-client refresh grant (or ISU auth).
- **Two auth modes in the toolkit:** `wdcli` (dev tenants; zero setup; ~1h TTL; requires `account switch` to the right org + `tenant login <alias>` - alias POSITIONAL) and `refresh` (API client; standing/unattended; classic hosts). These map to wd-auth Modes 1 and 2; the mode-selection logic and full facts are owned there - see `wd-auth/references/auth-decision-tree.md`.
- **User-context SPA / auth-code+PKCE (for external UIs over Extend, not the toolkit)** is **wd-auth Mode 4** - owned by `wd-auth/references/auth-decision-tree.md` (Mode 4) with the console/PKCE setup in `wd-auth/references/oauth-setup-guide.md`. Reach for it only when building an external user-facing UI over Extend (external-apis-and-genai.md "reverse direction"); NOT for headless tooling - that's the two toolkit modes above.
- **WSDL fetch is ANONYMOUS:** `{gwUrl}/ccx/service/{tenant}/<Service>/v46.2?wsdl` returns the full WSDL with no auth (verified: Human_Resources 4 MB, Integrations 1.1 MB) - schema acquisition for envelope generation needs no credentials. `/ccx/service/{tenant}/` itself is 404 (no index) - enumerate services via the in-tenant Public Web Services report.
- **Corporate network:** `myworkday.com` hosts sit behind corporate SSL inspection that trips CPython cert validation - the toolkit auto-retries `verify=False` with a visible note (house-known; same as the Smartsheet client). The WCP gateway is not intercepted.

## First-time setup runbook (the suite's model USER-ACTION block - fence user steps exactly like this)

Every step below happens **outside the Claude session**, in the user's own terminal or the Workday UI. Present it verbatim (adjusted per tenant); don't interleave it with steps Claude runs.

**Path A - dev tenant, wdcli auth (5 min, no tenant admin work):**

*Your steps (outside this session):*
1. **Your terminal:** `wdcli whoami` - confirm the org shown is the one that owns the target tenant (account state is machine-global; e.g. a client dev tenant belongs to the client org, not the firm's own org). If not: `wdcli account switch <shortId>`.
2. **Your terminal:** `wdcli tenant login <alias>` - alias is POSITIONAL (there is no `-t` flag here; that belongs to `app deploy`). A browser opens; sign in. Note: only one tenant token exists at a time - this displaces any other tenant's token.
3. **Your terminal:** `python <skills>\wd-extend-dev\scripts\tenant_toolkit.py set-creds <profile>` - answers: base_url `https://api.us.wcp.workday.com`, tenant `<alias>`, auth `wdcli`, allow writes `y` only for dev.
4. **Tell Claude "done"** - Claude runs `check-tenant <profile>` and reads the result.

**Path B - API client, refresh auth (standing/unattended; also unlocks SOAP + classic-host REST):**

The API-client registration itself (OAuth 2.0 Clients Enabled, Register API Client for
Integrations, scopes, Non-Expiring Refresh Tokens, Manage Refresh Tokens, the display-once
Client ID/Secret + refresh token, the `invalid_grant` recovery) is **owned by wd-auth** - walk
`wd-auth/references/oauth-setup-guide.md` **Part 1** for the click-level steps and the exact
values. This reference owns only the toolkit wiring on top of it:

*Your steps (outside this session):*
1. Complete the API-client + refresh-token registration per `wd-auth/references/oauth-setup-guide.md` Part 1, keeping the display-once Client ID, Client Secret, and refresh token to hand.
2. **Your terminal:** `python ...\tenant_toolkit.py set-creds <profile>` - per-prompt values: base_url = the tenant's **`tenantGwUrl`** from `wdcli tenant list -f json --ci` (NOT the UI URL); tenant = `<alias>`; auth = `refresh`; then the three secrets. The secret prompts are **hidden - pasting shows nothing on screen**; paste and press Enter.
3. **Tell Claude "done"** - Claude runs `check-tenant <profile>` and verifies the mint + probe.

Nothing secret ever goes in chat; everything lands in Windows Credential Manager.

## AUTOMATE-FIRST - do it yourself; prompt only for the disallowed (STANDING, owner-set 2026-09-10)

**Default posture for ALL build / configuration / test work: automate it** - via private/public Workday
APIs, `wdcli`, or in-app browser actions (`mcp__Claude_Browser__*`) - to build AND test the solution. Do
NOT hand a step to the user just because prompting is easier. The tools to do most of it ourselves exist;
use them. (The WRITE GATE below governs HOW to write safely; this governs WHETHER to automate at all - the
answer is yes, by default.)

**Prompt the user ONLY for the strictly-disallowed set** - the actions Workday or the safety rules genuinely
require a human for. This is the entire handoff list; everything else is automated + verified:

1. **Security policy ACTIVATION and any security/system-settings change** - `Activate Pending Security
   Policy Changes` (and `Activate Previous Security Timestamp`). We may CREATE the ISU/ISSG/domain grants
   up to the activate step ONLY via the guarded SOAP path (`scripts/security_domain_apply.py` - dev/sandbox,
   confirm-each-write, never activates); **creating or editing any security object in the BROWSER is a user
   handoff** (per wd-tenant-config Tier 3 - the agent never makes the committing click on a security write),
   and the **activation itself is always the required handoff** (a BO call returns S22 until the user activates).
2. **Credential / token / password / MFA / SSO** entry - never typed by the agent; secure hidden prompt or
   the user's password manager (see wd-auth).
3. **Production** changes of any kind.
4. **CAPTCHAs / bot-detection**, accepting **terms / OAuth consent**, account creation, irreversible
   **financial** actions, and **permanent / hard deletion** (emptying trash, hard-deleting records/files).

Everything else - create ISU/ISSG/domains/API-clients/app-attributes, BP config, schedules, test data, deploy
to DEV, run the app to test - **automate** under the WRITE GATE (plan-first, confirm-each-write, dev tenants
only). When a step IS on the disallowed list, present it as a crisp USER-ACTION block (the First-time setup
runbook above is the model), not a vague ask.

## THE WRITE GATE (read before any tenant write)

1. **Never production.** Writes are allowed only in dev / implementation / sandbox tenants, against a session-start **tenant allowlist** the user confirms explicitly. First call of any write session = an identity check (e.g., WQL `SELECT` on a known-tiny data source, or GET a known instance) that proves which tenant the token actually hits - the wdcli account-flip incident applies to REST creds too.
2. **Synthetic data only** - the demo/UAT synthetic-data policy (wd-deployment security posture) applies to API loads exactly as to manual entry. No production extracts as seed data without the ai-data-governance gate.
3. **Every load ships with its cleanup plan** - the un-load (delete/inactivate list, or a wipe-by-marker convention: seed records carry a recognizable marker in a text field so `WQL WHERE field CONTAINS marker` finds them all later). No cleanup plan -> the load is BLOCKED, same rule as ownerless runbooks.
4. **Soft-delete landmine applies** (model.md checklist #3 / pmd-gotchas #45): bulk loads must set boolean flags explicitly or records vanish from filtered lists.
5. Respect platform behavior: 429 -> exponential back-off (standards.md); no loads during the Weekly Service Update window (auto-restart double-load risk - per Workday Admin Guide (Integrations), Jul 2026).
6. **Reads are gated too where data is sensitive:** metadata/config/count reads are fine anywhere you're authorized; pulling production person-level rows into AI context violates the ai-data-governance floor - aggregate or synthesize instead.

## Read-side catalog - checks the suite can run itself

| Check | API | Feeds |
|---|---|---|
| Reference-ID liveness - does every RefID cited in the design doc's data/config tabs exist in this tenant? **VERIFIED**: `tenant_toolkit.py refs <profile> <Reference_ID_Type>` (SOAP Get_References; e.g. `Cost_Center_Reference_ID` -> 81 CCs w/ WID + RefID + descriptor in a dev tenant) | SOAP `Get_References` (Integrations service) by type; REST prompt-`/values/...` endpoints where a service has them | Design-doc QA gate; migration verification |
| Worktag combination validity before building FIN transactions | `worktag POST /validateWorktags` (read-only) | Design validation; unit-test data prep |
| Budget impact pre-check | `budgets POST /runBudgetCheck` (read-only) | FIN app design; UAT scenario sanity |
| Account-posting-rule resolution (which ledger account will this hit?) | `coreAccounting /evaluateAccountPostingRules` | FIN design docs; defect triage |
| App/BO data state - counts, orphans, field distributions | WQL `/data` (+ `/dataSources` discovery); app BO REST GET | Migration verification (counts match across tenants); UAT reset checks |
| **Anything a custom report can show** - ISU inventory, domain grants, signons, integration events, BP config | **RaaS**: build the report, ISU-own it, web-service-enable -> GET. *The universal escape hatch: any tenant fact exposed in a report becomes API-readable.* **Host + auth (per Workday/raas-python, official client, Apache-2.0):** RaaS lives at `/ccx/service/customreport2/{tenant}` = a **classic tenanted-host** service (NOT `/ccx/api/`, NOT the WCP gateway), so `raas` **hard-requires a `refresh`-auth profile** (a wdcli/gateway bearer 401s here). Input = the full **Related Actions -> Web Service -> View URLs** value pasted **verbatim** (no owner/name assembly); the `format=` param must be the **last** URL param. | Security audits vs security-setup conventions; drift detection; evidence capture |
| In-flight BP events before a version swap or cutover | `businessProcess /events` (+ eventSteps) | The version-swap/in-flight-BP (!) - CHECK it instead of guessing; go/no-go evidence |
| Existing custom-object inventory (collision check before designing new ones) | `customObjectDefinition /definitions` | Discovery; architecture review |
| Which security domain does this WS op need? (op->domain mapping, per op) | WQL `allWebServiceOperations` - `webServiceOperationName, webService1, public, domain2, securityGroupsNeeded` | security-setup ISSG grant tables; design-doc Security tab; integration discovery |
| Live perf/health baseline (queued/running tasks, sessions) | `systemMetrics` (System Monitor domains) | Perf-testing evidence; hypercare monitoring |
| Who touched what (UAT forensics, incident timeline) | `privacy /activityLogging` (needs Enable User Activity Logging; `limit=1000&instancesReturned=1` iteration) | UAT defect triage; security-incident recipes |
| Cross-tenant drift (dev vs impl vs sandbox) | Run the same read-set per tenant, diff | migration-checklist verification; promotion evidence |
| **THE TENANT-READINESS READ-SET** (named recipe - four gates share it): (1) BO data call returns data, not S22 -> grants activated; (2) `refs` on every RefID the design doc cites -> reference data present; (3) WQL on App-Attribute values -> this tenant's WIDs, not another tenant's; (4) `raas` under the ISU -> reports promoted + owned. Run it per tenant hop; the pass/fail set IS the gate evidence | tenant_toolkit: rest get + refs + wql + raas | Go/no-go prod prerequisites (wd-deployment SKILL); security grant verification (security-setup); tenant-setup guide section 5; UAT entry criteria (wd-testing) |

## Write-side catalog - what we can load

| Load | Mechanism | Status |
|---|---|---|
| Extend app BO test data (incl. parent/child with dates) | BO REST `?bulk=true` + the two-pass dated-import pattern (orchestration.md) | **Build+runtime verified** (a build session) |
| Custom-object data on standard BOs (worker stock grants etc.) | `customObject v2` - `bulk=true` (<=100/req), `updateIfExists=true` upsert, `{WID};{refIdAlias}={value}` addressing | Doc-sourced; shapes in local schemas |
| Standard-BO transactions (job changes, payments, requisitions...) | Per-service REST POSTs (staffing, studentFinance, procurement...) - check each op's `x-workday-secured-by-domains` first | Doc-sourced; verify per service |
| Foundation/config objects (integration systems, sequence generators, and the wide SOAP Put_* surface) | SOAP `Put_*` ops - generate request envelopes from the local/tenant WSDL instead of round-tripping EIB spreadsheets | (!) untested as a generated-envelope flow; ops themselves are the same ones EIB/iLoad use |
| Demo seeding (dev-tenant cast: app data staged for a demo script) | Per-app seed pack = scenario JSON + loader run + reset (cleanup plan is the reset) | Pattern; first pack to be built with wd-demo |
| UAT cycle reset | Snapshot via GET-all -> wipe-by-marker -> reload seed pack | Pattern |
| Scenario-driven test data | wd-testing unit scenarios declare their data preconditions -> each scenario's precondition block IS its seed-pack spec | Pattern; wire at scenario-derivation time |

EIB remains the right tool when the *client* will own recurring loads; direct API loads win for repeatable engineering seed packs (versionable, diffable, no spreadsheet drift).

## Implementer / private web services (partner-account surface) - discovery plan

**ALL DISCOVERY EXPERIMENTS RESOLVED (2026-08-06, a dev tenant, implementer account's API client).** The implementer surface is real, enumerable, schema'd, and callable:

- **Enumeration is a WQL query, not a UI report.** Two data sources: `publicWebServices` (e.g. 56 services w/ WSDL file names in a dev tenant) and the prize, **`allWebServiceOperations`** - every op in the tenant with `webServiceOperationName`, `webService1` (owning service), **`public` flag**, and **`domain2`/`securityGroupsNeeded`** (the op->security-domain mapping, programmatically!). One dev tenant measured: **7,221 ops = 3,102 public + 4,119 non-public**, the non-public bulk being the Implementation Services (HCM 708 ops, Financials 594, Core 403, Payroll 348, + Student/FinAid/Time Tracking impl services; also UI Server/unit-test internals - ignore those). Save the full dumps next to the REST schemas in your Extend workspace: `rest-api-schemas\<tenant>_{public_web_services,all_ws_operations}_<date>.json`.
- **Implementation-service WSDLs fetch anonymously** like public ones: `{gw}/ccx/service/{tenant}/Core_Implementation_Service/v46.2?wsdl` (5.5 MB; HCM 9.9 MB). Service URL name = descriptor with underscores.
- **Implementer ops are CALLABLE with the same bearer** - verified: `Get_Organization_Subtype` on Core_Implementation_Service returned live data. Namespace is plain `urn:com.workday/bsvc`; **element names come from the WSDL, not the op display name** (display "Get Organization Subtypes" -> element `Get_Organization_Subtype_Request`, singular - a wrong guess 500s with "Element not found", which is a validation error, not auth). Always extract the element from the WSDL before calling.
- `/ccx/service/{tenant}/` has no index (404) - enumeration is the WQL query above.
- **The iLoad-grade `Put_*` implementer ops are the config-load write surface** (Put Organization Subtype, AddUpdate Time Profile, ...) - they fall under THE WRITE GATE like every other write; per-op access is still security-policy-dependent (check `domain2`/`securityGroupsNeeded` on the op's row first).

### Custom reports + calculated fields load END-TO-END VERIFIED (2026-09-01, a dev tenant)

The backend of Workday's "Calculated Fields" / "Custom Reports" advanced-load spreadsheets is the private **`Report_Metadata`** service (62 ops). A full write round-trip is proven: `Put_Calculated_Field` x2 (Lookup Single Instance fields) + `Put_Tenanted_Report_Definition` created a web-service-enabled Advanced report that then RAN via gateway RaaS with correct prompt filtering. Working client + envelope examples: the author's Extend workspace `advanced-load-analysis\` (report_metadata_client.py + report2_bodies\). Hard-won facts:

- **BASIC AUTH FOR WEB SERVICES IS RETIRED (~R2 2026).** Worked 2026-08-11; by 2026-09-01 every SOAP call returns "invalid username or password" while the same account logs into the UI fine, and the opt-out checkbox is gone from Tenant Setup - Security. The ONLY path now = API-client refresh grant -> `Authorization: Bearer` at the classic host (Path B setup). (wws_inventory.py was updated accordingly - bearer-only, keychain service `wd-wws-inventory`.)
- **`Report_Metadata` is an UNVERSIONED service**: call the versionless URL (`{gw}/ccx/service/{tenant}/Report_Metadata`) with NO `wd:version` attribute on the request element - any version segment or attribute gets "The web service or version is invalid for the requested operation". Versioned services (Core_Implementation_Service, Integrations) behave normally. `?wsdl` still wants a version segment (schema download only).
- **Reports are addressable by name**: `wd:ID wd:type="Custom_Report_ID" wd:parent_type="System_User_ID" wd:parent_id="<owner>"` - and `Put_Tenanted_Report_Definition` can create the report OWNED BY THE ISU directly (skips the transfer-ownership post-step).
- **`Put_Calculated_Field` creates TENANT-level fields only.** Report-SPECIFIC calc fields resolve as references (`Calculated_Field_ID` = "<BO> - <name> - <hash>") but `Get_Calculated_Fields` returns no data for them and Put cannot create them - if a design requires report-specific fields (config-package portability), those stay manual/UI.
- **Field-WID discovery**: `Get_Integration_External_Fields` (private `Integration_Metadata` service, also callable) takes `Field_Name` + `Work_Data=true` criteria and returns class-report-field WIDs by NAME - the missing link for authoring (e.g. "Company for Organization" on Cost Center). Global fields reuse one WID everywhere ("Workday ID", "Name").
- **Authoring recipe**: Get a hand-built sibling report as the serialization template (12 KB of exact XML beats any doc), swap references, Put, Get back and diff, then execute via RaaS to prove the contract. Get-all corpora (77 pages of calc fields, 39 pages of report defs at Count=100) grep-mine well for donor shapes + WIDs.

## tenant_toolkit.py - build-spec (read side live-verified; write verbs deliberately absent)

**Lives at `wd-extend-dev/scripts/tenant_toolkit.py` - read side LIVE-VERIFIED 2026-08-06 (a dev tenant, both auth modes):** `check-tenant`, `wql`, `rest get`, `soap` (envelope or bare op XML, auto-wrapped), `refs` (Get_References by Reference_ID_Type). `raas` - **URL grammar + classic-host auth confirmed per Workday/raas-python (official client, Apache-2.0); still un-run live** (promoted from "implemented, unexercised"). Write verbs deliberately absent until designed behind the WRITE GATE. Spec for regeneration:

Thin CLI over the `workday_rest.py` core, adding: `set-creds` (hidden prompt -> Windows Credential Manager: base URL, tenant, client id/secret, refresh token - per named tenant profile); `check-tenant <profile>` (mint bearer, hit a harmless known endpoint, print tenant identity + REFUSE writes if profile isn't on the allowlist); `wql <profile> <query>`; `raas <profile> <report-url>` (classic tenanted host `/ccx/service/customreport2/{tenant}` -> **`refresh`-auth profile required**; pass the full **View URLs** value verbatim with `format=` last - per Workday/raas-python, official client, Apache-2.0); `rest <profile> get|post|put|patch <path> [--body file.json] [--bulk]`; `refs <profile> <type>` (Get_References wrapper once SOAP auth is verified); `soap <profile> <envelope.xml>` (send raw envelope, print response). Write subcommands hard-require `--tenant-type dev|impl|sandbox` AND the profile's allowlist flag - refuse otherwise. Log every write (timestamp, endpoint, row count, marker) to a session load-log the cleanup plan can replay in reverse.

First verification pass: run read-side checks against a dev tenant with a purpose-made API client, then promote each recipe from (!) to verified.
