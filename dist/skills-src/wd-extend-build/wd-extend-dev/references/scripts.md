# Scripts this skill references - regenerate-on-demand build-specs

These live in the Workday Extend workspace, not inside the skill. If one isn't present, Claude
regenerates an equivalent from the build-spec below. All are cross-platform Python (stdlib +
`requests` for the REST client); setup in `wd-extend-lifecycle/references/prerequisites.md`.

- **`pmd_preflight.py`** - pre-upload gotcha linter for PMD/pod/script/BO/AMD source. SHIPS
  INSIDE this skill (`scripts/pmd_preflight.py`), unlike the workspace scripts below - no
  regeneration spec needed. Codifies every mechanically-detectable pmd-gotcha (~25 checks);
  run on the app root before every `wdcli app upload` (usage + rationale: wdcli-workflow.md
  build loop; enforcement rule: pmd-gotchas.md header).
- **`security_domain_discovery.py`** - SHIPS INSIDE this skill (`scripts/security_domain_discovery.py`).
  Given reports/web-services/BPs an app touches, discovers the security domains and BP
  permissions needed and checks a target ISSG against them (spec below).
- **`security_domain_apply.py`** - SHIPS INSIDE this skill (`scripts/security_domain_apply.py`).
  The guarded WRITE half of the above: plan a set of domain/BP grants, then apply them with
  a human confirming every write. READ `domain-apply-safety.md` before using `--execute`
  (spec below). Stdlib only; exit 1 = FAIL findings.
- **`validate.py`** - pre-upload structural linter for `.orchestration` flows (spec below).
- **`workday_rest.py`** - reusable Workday REST/OAuth client (spec below).
- **`generate_flow.py`** - the per-integration orchestration-JSON builder; its approach is
  documented in `orchestration.md` ("generate the JSON from a Python builder with small helper
  functions per node type; copy a proven template app, keep reusable subflows verbatim, emit a
  new main flow"). Rebuild it per that reference for the specific integration; there is no
  single generic version.

The traditional-integration template builders (`build_naming_standards_doc.py`,
`build_integration_checklist.py`, `build_security_segment_worksheet.py`) live in the
wd-integration-dev skill (`references/scripts.md` there).

---

### validate.py - pre-upload structural linter for Workday Orchestrate `.orchestration` flow files
- **Language / runtime:** Python 3 (`#!/usr/bin/env python3`), stdlib only.
- **Third-party deps:** none / stdlib only (`json, re, sys, collections.Counter`).
- **OS constraints:** Cross-platform.
- **Inputs:** CLI: one or more `.orchestration` file paths (`argv[1:]`). Each is a JSON typed-AST envelope `{ "_type":..., "_value":..., "flowVersion":... }`. No args -> print the docstring, exit 2.
- **Outputs:** Stdout only - per file `[OK]/[WARN]/[FAIL]` + `ERROR:`/`warning:` detail. Exit 0 if all pass (warnings allowed), 1 if any error, 2 if no args.
- **Method:**
  1. `walk_names(obj,names)` recurses dicts/lists; when a node's `_type` is in `NODE_KINDS` and `_value` is a dict, collect `_value.name._value`.
  2. `walk_kind(obj,kind)` yields the `_value` dict of every node of a `_type`; `count_kind` counts them.
  3. `validate_file(path)`: parse JSON (JSON/OS error -> single "invalid JSON" error). `flow = doc["_value"]`.
  4. Check - node-name uniqueness: `Counter` the names; any count >1 -> ERROR listing sorted dupes.
  5. Check - every `BranchOnConditions` `_value` must contain both `ifBranches` and `elseBranch`; any legacy key (`branches`, `Branch`, `defaultBranch`, `DefaultBranch`) -> ERROR.
  6. Check - count legacy `Http` nodes; any -> WARNING (prefer `SendHttpRequest`).
  7. Check - top-level `flowVersion`: missing -> warning; not `"3.3.0"` -> warning.
  8. Check - `flow["id"]["_value"]` must match a 32-char lowercase-hex regex, else warning.
  9. `main` iterates files, prints status, ORs any error into the exit code.
- **Key constants:** `HEX32 = ^[0-9a-f]{32}$`; recommended `flowVersion == "3.3.0"`; `NODE_KINDS` frozenset = {CreateValues, CreateTextTemplate, CreateJson, StoreDocument, Loop, BatchLoop, JoinLoop, SendWorkdayApiRequest, SendWorkdayRaasRequest, SendHttpRequest, Http, SendIntegrationMessage, BranchOnConditions, ContinueOnConditions, Validate, TriggerPdfGeneration, TriggerIntegration, CallSubflow, LogToFile, Log, Group, ImplicitGroup, ErrorHandler}; legacy branch-key list; exit codes 0/1/2. (`CreateJson`, `SendWorkdayRaasRequest`, `JoinLoop` verified in live app source, 2026-08-05.)
- **Gotchas:** structural lint only - NOT a compiler; `wdcli app upload` stays authoritative. `NODE_KINDS` deliberately EXCLUDES Parameter/ExprParameter, Flow name, WhenBranch labels, and Aggregate/FoldValue nameProps because those legitimately repeat in valid exports (including them -> false-positive dup-name errors). The duplicate-name check SILENTLY SKIPS any node kind missing from `NODE_KINDS` - an under-inclusive set means missed dupes, not errors, so keep the set current as new node types are verified. Names are compared flow-wide including auto-generated `_group_*`/`_else_*`. Warnings never fail the build; only errors set exit 1.
- **Regeneration confidence:** High - logic is simple and fully specified; the only rebuild risk is the exact `NODE_KINDS` membership (over/under-inclusion changes results).

---

### workday_rest.py - reusable Workday REST/OAuth client (refresh-token grant, cached bearer, paging, WQL, RaaS)
- **Language / runtime:** Python 3, importable module (`WorkdayREST` class).
- **Third-party deps:** `requests`. Stdlib: `time, json, logging, urllib.parse`.
- **OS constraints:** Cross-platform.
- **Inputs:** Constructor `base_url` (no trailing slash), `tenant`, `client_id`, `client_secret`, `refresh_token`, optional `version="v1"` (caller usually sources these from env vars). Method inputs: REST paths, WQL query strings.
- **Outputs:** raw verbs return `requests.Response`; `get_paged` -> `{"total","data"}`; `wql` -> list. No files. Errors logged via `logging`.
- **Method:**
  1. Constructor strips trailing slash and derives endpoints: token `{base}/ccx/oauth2/{tenant}/token`, REST `{base}/ccx/api/{version}/{tenant}`, Prism `{base}/api/prismAnalytics/v3/{tenant}`. Init `_bearer=None`, `_bearer_ts=None`.
  2. `_create_bearer()`: POST form-urlencoded `grant_type=refresh_token` + refresh_token + client_id + client_secret; on 200 store `access_token` + timestamp, else log + null.
  3. `bearer_token()`: refresh if missing OR older than 900 s; return token or "".
  4. `_auth_headers(extra)`: `Authorization: Bearer <token>` + extras.
  5. Raw `get/post/put/patch`: attach auth headers; `post` sets JSON content-type + `json.dumps` when `json_body` given (also supports `files`); log GET !=200 and write status >299; return Response.
  6. `_resolve(path,base)`: pass through absolute http(s) URLs; else join onto chosen base (default REST).
  7. `get_paged(path,base,params,page_size)`: `limit=min(page_size,100)` + `offset`; loop GET, extend `data`, stop on short page or non-200; never raises -> returns `{"total","data"}`.
  8. `wql(query)`: GET `https://api.us.wcp.workday.com/wql/v1/data?query=<url-encoded>`; return `body["data"]` on 200 else `[]`.
  9. `get_raas(url)`: reuse the cached bearer -> GET the caller-pasted RaaS URL **verbatim** (the full Related Actions -> Web Service -> View URLs value; classic tenanted host `/ccx/service/customreport2/{tenant}`, so this needs the **refresh** bearer, not a gateway token); on 200 branch on format - JSON body -> return `body["Report_Entry"]`, CSV body -> `csv.reader` parse into rows; non-200 -> log status + return the Response so the caller inspects it (do NOT silently return None). Caveat: `format=` must be the URL's **last** param. Derived from Workday/raas-python (official client, Apache-2.0).
- **Key constants:** `WQL_HOST="https://api.us.wcp.workday.com"`; `MAX_PAGE_SIZE=100` (hard Workday ceiling); bearer cache TTL `900` s; token endpoint `Content-Type: application/x-www-form-urlencoded`; write-error threshold `status_code > 299`; refresh-token grant (NOT client-credentials).
- **Gotchas:** token cached ~15 min then auto-refreshed - don't assume a fresh mint per call. Page size capped at 100 regardless of request; paging stops on a short page. WQL uses a region-direct host distinct from the tenant base. `get_paged` swallows errors by design - callers must check `total`. Many Workday 400s return valid JSON with an `error` attribute; raw verbs return the Response so callers can inspect the body. `get_raas` hits a **classic tenanted host** (not the WCP gateway WQL/REST hosts) and so requires the refresh grant - a gateway bearer 401s there; keep our status-checking discipline and deliberately do NOT copy the reference client's silent `Bearer None` / None-return anti-pattern (fail loud, return the Response). Distilled from Workday/prism-python (Apache-2.0); `get_raas` per Workday/raas-python (official client, Apache-2.0).
- **Regeneration confidence:** High - endpoints, auth flow, and constants are explicit; preserve the exact endpoint path templates and the 100/900 constants.

---

### security_domain_discovery.py - partner-tool-style security-domain/BP discovery via WQL + SOAP (no custom reports needed)
- **Status:** SHIPS inside this skill (`scripts/security_domain_discovery.py`). Live-verified
  against a dev tenant, 2026-09-04 - see `the security-domain-process notes (in memory)` memory and
  `<workspace>/security-domain-discovery/`.
- **Language / runtime:** Python 3, stdlib (`argparse, json, sys, xml.etree.ElementTree`) + `requests` + `keyring`.
- **OS constraints:** Cross-platform.
- **Origin:** reverse-mined from the partner tool, a Workday-delivered implementation-partner Studio
  integration that determines/provisions ISU/ISSG security by resolving what an integration
  touches (reports, web services, BPs) to the domains that secure them. This script replicates
  the DISCOVERY half (never the write/grant half) using plain WQL + a read-only SOAP call
  instead of the partner tool's runtime-built custom reports - proven to expose the same data.
- **Inputs:** CLI subcommands.
  - `discover --tenant <alias> [--reports "A,B"] [--outbound-ws "A,B"] [--inbound-ws "A,B"]
    [--view-all-bp "A,B"] [--initiate-bp "A,B"] [--issg "Name"] [--override-inheritance]
    [--out file.md] [--json-out file.json]`
  - `domain-info --tenant <alias> --domain "Domain Name"` - one-off single-domain lookup.
- **Outputs:** Markdown checklist (stdout or `--out`) in the same shape as
  `wd-deployment/security-setup-section.md` Part 3's domains-and-permissions table: per
  domain, the sources needing it, the access level, whether `--issg` already has it, and
  the current grantee list. Optional raw JSON via `--json-out`. Never writes to the tenant.
- **Method:**
  1. `load_credentials(tenant)` - tries the `tenant_toolkit.py` profile store first
     (`wd-tenant-ops:<profile>:<field>`), falls back to the simpler legacy per-tenant scheme
     (`keyring` service `wd-<tenant>`, fields `client_id`/`client_secret`/`refresh_token`,
     optional `base_host`) already in use for the dev-tenant family (see `the tenant OAuth+WQL recipe (in memory)`).
  2. `Tenant.__init__` mints a refresh-grant bearer against `{base_host}/ccx/oauth2/{tenant}/token`.
  3. **Reports -> domains:** WQL `allCustomReports` filtered by exact `reportName`, reading
     `domainsSecuringReportDefinitionBasedOnRDSAndSMD` + `domainsSecuringAlternateRDS`
     (both return arrays of `{descriptor,id}`) - level always "Get Only".
  4. **Web service operations -> domain:** WQL `allWebServiceOperations` filtered by exact
     `webServiceOperationName`, reading `domain2` (can be a single object OR a list - handle
     both). Outbound -> "Get Only"; inbound -> "Get and Put" (caller-supplied via the two
     separate CLI flags, matching the partner tool's own bucketing).
  5. `merge_required_domains` collapses hits by domain id, keeping every source label and the
     HIGHEST access level requested for that domain (`LEVEL_RANK` order).
  6. **Inheritance check:** WQL `allDomains` filtered by exact `domainName`, reading
     `usingParentPermissions`, `superDomain`, and all four access-level security-group list
     fields in one query. If inheriting and `--override-inheritance` is NOT set, redirect the
     target to `superDomain` and re-query ITS fields (the partner tool's redirect-to-parent behavior).
  7. **Already-granted check:** the access level's field name (`LEVEL_FIELD` map: Get Only ->
     `get_OnlySecurityGroups`, Get and Put -> `putSecurityGroups`, View and Modify ->
     `modifySecurityGroups`, View Only -> `view_OnlySecurityGroups`) is read off the (possibly
     redirected) domain row; `--issg` is matched by exact descriptor string against that list.
  8. **BP View All / Initiate:** one SOAP `Get_Business_Process_Security_Policies_Request`
     v23.2 against `Core_Implementation_Service` per BP name, filtered by
     `Business_Process_Type_Reference/ID[@type='Business_Process_Type']` = the BP name (exact
     element names taken from the partner tool's own request, NOT guessed). Parses
     `View_Event_Security_Policy_Permission_Data/Security_Group_Reference` (already-granted
     check against `--issg`) and every `Event_Action_Security_Policy_Data` (task name + its
     current groups) so a consultant can VISUALLY match the Initiate-permission task to their
     inbound web service - the script does NOT auto-match this (see Gotchas).
  9. `render_markdown` builds the final checklist; `cmd_discover` writes/prints it.
- **Key constants:** `TOOLKIT_SERVICE = "wd-tenant-ops"`; `DEFAULT_BASE_HOST =
  None` (no baked-in default; guards/errors if unset - set via a `base_host`
  keyring field for other gateways, e.g. a `_wcpdev2` host); `LEVEL_FIELD`/`LEVEL_RANK` map
  the four the partner tool access levels to `allDomains` fields, verified live.
- **Gotchas:** exact-name WHERE matching only (no fuzzy search) - report/web-service/BP names
  must match tenant text exactly, case-sensitive, or the row silently isn't found (a WARN is
  printed to stderr). `domain2` on `allWebServiceOperations` returns null for operations that
  aren't domain-gated (BP-security-only, or public/unsecured operations) - not a bug, just
  means that operation's access is governed elsewhere (check the BP side). BP
  Initiate-permission task matching is NOT automated - the child-element shape of
  `Event_Action_Security_Policy_Data` beyond `Task_Reference` + `Security_Group_Reference`
  wasn't exhaustively probed, and a wrong auto-match would recommend granting the wrong task;
  the script prints all tasks (including one observed case where `Task_Reference` carried no
  descriptor - shows as `?`) so a human confirms. This is READ-ONLY by design - executing the
  actual grant (`Put_Domain_Security_Policies_Request` / `Put_Business_Process_Security_Policy_Request`)
  is a deliberate unbuilt follow-up, to be gated the same way `tenant_toolkit.py` gates writes
  (`allow_writes` + explicit `--tenant-type`) once needed.
- **Regeneration confidence:** High - every WQL field name and the SOAP request shape were
  live-verified against a dev tenant (2026-09-04), not inferred from the partner tool's XSLT alone.

---

### security_domain_apply.py - GUARDED write path for domain/BP security grants (plan then apply)
- **Status:** SHIPS inside this skill (`scripts/security_domain_apply.py`). Every code path
  live-verified against a dev tenant (read-only: inspecting generated PUT bodies for well-formedness)
  and a dev tenant (one real `--execute` write, maintainer-approved: Get Only on "Custom Report
  Creation" to "SecurTest-ISSG", 2026-09-04 - succeeded, confirmed pending, not yet
  activated). See `domain-apply-safety.md` for the full guardrail list and the THREE real
  bugs live-testing caught (two before any write was attempted, one only visible after a
  real write - post-write verification was checking active policy instead of the
  pending-changes queue, now fixed).
- **Language / runtime:** Python 3, stdlib (`argparse, copy, datetime, hashlib, json, os,
  sys, xml.etree.ElementTree`) + `requests` + `keyring`. Imports `security_domain_discovery.py`
  from the same folder (credentials, WQL, SOAP-GET helpers, domain/report/WS resolution).
- **OS constraints:** Cross-platform.
- **Origin:** the write half of the the partner tool-mined process (see `security_domain_discovery.py`'s
  entry above) - `Put_Domain_Security_Policies_Request` / `Put_Business_Process_Security_Policy_Request`
  shapes taken VERBATIM from the partner tool's `PutChildDomainRequest.xsl` / `PutParentDomainRequest.xsl` /
  `PutViewAllBPRequest.xsl`, then corrected where live testing showed the mined shape was wrong
  (see Gotchas).
- **Inputs:** CLI subcommands.
  - `plan --tenant <alias> [--reports "A,B"] [--outbound-ws "A,B"] [--inbound-ws "A,B"]
    [--view-all-bp "A,B"] [--domain "Name" --domain-wid <WID> [--level "Get Only"|...]]
    --issg "Name" --issg-wid <WID> [--override-inheritance] [--out file.json]`
    - `--domain`/`--domain-wid` targets a domain directly (requires a WID you already
      have - no name-based lookup), for domains not reachable via a report/WS lookup
      (e.g. bootstrap-style domains like "Custom Report Creation" that a design doc's
      Security tab names directly).
    - Read-only. Resolves inputs the same way `security_domain_discovery.py discover` does,
      then for every NOT-already-granted domain/BP: fetches the current full policy
      document, builds the exact PUT body, and writes everything (snapshot + hash + PUT
      body + diff metadata) to a plan JSON file. `--override-inheritance` on `plan` causes
      inheriting domains to be SKIPPED with a message (override is not automated - see
      Gotchas), not silently applied a different way.
  - `apply --plan <file> --tenant-type {dev|impl|sandbox} [--execute] [--allow-modify-grants]`
    - Defaults to dry run (prints the itemized change list, calls nothing). `--execute`
      required to write for real; even then, re-validates the ISSG and every item's
      freshness, requires the operator to type the tenant alias to confirm, then processes
      ONE item at a time with a pre-write backup and a post-write verification re-fetch,
      stopping immediately on the first failure of any kind.
- **Outputs:** a plan JSON file (`plan` command); console progress + a backup file per
  successful write + one audit-log JSONL line per attempt, all under
  `scripts/security_domain_apply_runs/<tenant>/` (local to the skill folder, NOT under
  OneDrive - deliberate, since plan/backup files carry real tenant security-group names).
- **Method:**
  1. Domain resolution reuses `security_domain_discovery.py`'s `resolve_report_domains` /
     `resolve_ws_domains` / `merge_required_domains` / `domain_inheritance_info` - the read
     side is identical to `discover`.
  2. **Critical structural fact (live-verified, not assumed):** `Get_Domain_Security_Policy_Request`
     only resolves a TOP-LEVEL domain's own WID. A subdomain's own WID is REJECTED
     (`"does not meet the restrictions defined for this field"`). Every subdomain case -
     whether inheriting-and-redirecting or already carrying its own active policy - fetches
     via `superDomain`'s WID and locates the target inside that single document
     (`find_subpolicy`, matching `Subdomain_Reference/ID[@type='WID']`).
  3. `build_domain_put` deep-copies the fetched `Domain_Security_Policy_Data`, then either
     appends a new `Security_Policy_Permission_Data` at the top level (non-subdomain case) or
     finds the matching `Security_Subpolicy_Data` and appends a new
     `Security_Subpolicy_Permission_Data` inside it (subdomain case) - mirroring
     `PutChildDomainRequest.xsl`'s `AddToChild` / `PutParentDomainRequest.xsl` exactly, MINUS
     the ID-type bug (see Gotchas).
  4. `build_bp_view_all_put` deep-copies the fetched `Business_Process_Security_Policy_Data`,
     strips `BP_BLOCKS_TO_STRIP` (see Gotchas), and appends one `Security_Group_Reference` to
     `View_Event_Security_Policy_Permission_Data` only - every other permission-block type
     (`Approve_Event`, `Cancel_Event`, `Rescind_Event`, `Correct_Event`,
     `Event_Action_Security_Policy_Data` / Initiate tasks, etc.) is copied verbatim.
  5. `validate_issg` confirms `--issg-wid` actually names `--issg` via
     `SELECT securityGroup FROM allSecurityGroups WHERE securityGroup = '<wid>'` (WQL resolves
     a reference field by WID string, NOT by descriptor text - `WHERE securityGroup = 'Name'`
     errors `cannot resolve instance`). Runs once at `plan` time and again at `apply` time.
  5a. Post-write verification (`check_pending_domain_change` / `check_pending_bp_change`)
     queries `domainSecurityPoliciesWithPendingChanges` / `businessProcessSecurityPoliciesWithPendingChanges`
     and matches by DESCRIPTOR + a timestamp after the write - NOT by WID, because (live-verified)
     these sources carry their own internal WID for the same domain/BP, incompatible with the
     WID used to fetch/PUT the policy (see the WID-portability pattern in `domain-apply-safety.md`).
     Confirms a pending change now exists for the right object; does not independently confirm
     which exact group/level landed - the human's own pre-Activate review still owns that.
  6. `cmd_apply`: tenant-type gate -> strip View-and-Modify items unless
     `--allow-modify-grants` -> print the plan -> dry-run early-return unless `--execute` ->
     typed tenant-name confirmation -> re-validate ISSG -> per item: re-fetch + hash-compare
     (`_sha`) against the plan's snapshot, abort on mismatch; write timestamped backup; POST
     the pre-built PUT envelope via the shared `_request` (SSL-retry) helper; on any fault or
     non-200, log and STOP; on success, re-fetch and confirm the group appears in the right
     permission list before calling it verified; log every outcome to `audit_log.jsonl`.
- **Key constants:** `SECURITY_OPERATIONS` - the same four WID/ID pairs as
  `security_domain_discovery.py`'s `LEVEL_FIELD`, keyed the other direction (level name ->
  WID + Security_Operation_ID), verified byte-for-byte against the the partner tool XSLT.
  `VALID_TENANT_TYPES = {"dev","impl","sandbox"}` (argparse `choices=` - "prod" is a hard
  parse-time rejection, not a runtime check). `BP_BLOCKS_TO_STRIP` - the two response-only
  BP blocks that must NOT be echoed back on the PUT.
- **Gotchas:**
  - **ID-type bug in the partner tool's own templates:** `PutChildDomainRequest.xsl` /
    `PutParentDomainRequest.xsl` label the new `Security_Group_Reference`'s ID as
    `wd:type="Tenant_Security_Group_ID"` while populating it with a WID-formatted value (the
    launch parameter is WID-typed) - a type/value mismatch. This script uses `wd:type="WID"`
    instead, live-verified to resolve correctly. Don't "fix" this back to match the partner tool - the partner tool's
    version is the bug.
  - **Subdomain WIDs cannot be fetched directly** - see Method #2. If `superDomain` is
    missing/null from `allDomains` for a domain that IS a subdomain, this is an untested edge
    case - `plan` will fail the GET and skip the item with a printed reason rather than guess.
  - **`allDomains`'s own `domain` self-reference field is a red herring for this purpose** -
    its WID is NOT valid as a `Get_Domain_Security_Policy_Request` `Domain_Reference` target
    even for domains that otherwise work fine (confirmed by testing); this script never uses
    that field for fetching, only the WIDs embedded in report/web-service domain references
    and in `superDomain`.
  - **Override-inheritance is not automated** - `plan` skips these items outright with a
    message; the correct payload (mirroring the parent's grants into a fresh subpolicy) needs
    more verification before it's safe to generate unattended.
  - **BP Initiate-permission grants are not built** - only View All. Task-matching stays a
    human step (see `security_domain_discovery.py`'s Gotchas).
  - **No ISU/ISSG creation** - existing objects only.
  - Plan/backup/audit files land under the skill's own scripts folder (outside OneDrive) on
    purpose - they carry real tenant security-group names and WIDs.
- **Regeneration confidence:** Medium-High - every WQL field, every SOAP request/response
  shape, and both real bugs listed above were caught by live testing against a dev tenant, not
  inferred from the the partner tool source alone; the untested edges (override-inheritance,
  multi-level domain nesting beyond one parent/child level, BP Initiate automation) are
  explicitly called out rather than silently assumed to work.

---

### generate_flow.py - emit a Workday Orchestrate `.orchestration` (Maya) flow from a Python builder with per-node-type helpers
- **Status:** **NOT a single generic file** - it is rebuilt PER INTEGRATION (kept alongside the app in the Extend workspace). There is no one canonical version; `orchestration.md` documents the approach and this build-spec makes it reproducible. The reusable value is the **builder skeleton + the typed-AST envelope shape + the securityDomains rule**, not any one integration's flow.
- **Language / runtime:** Python 3, stdlib only (`json`, `sys`); no third-party deps. Cross-platform.
- **Inputs:** the target integration's shape (node sequence, expressions/XPaths, API versions, launch params) - supplied per integration, not via generic CLI args. Optionally the path of a proven template app copied via `wdcli app copy`.
- **Outputs:** one `<FlowName>.orchestration` JSON file (and, when copying a template, the retained reusable subflow files) written into the app's `orchestration/` folder; stdout confirmation. Feed the result to `validate.py` before `wdcli app upload`.
- **Approach (build-verified, per orchestration.md):**
  - **Copy a proven template app** (`wdcli app copy`), **keep its reusable subflows verbatim** (e.g. a SendSOAPRequest subflow + an EventSummary subflow), delete the subflow files you don't need, and have the builder **emit a new MAIN flow that calls the retained subflows** - do NOT hand-author net-new subflows from scratch. Prefer the visual Orchestration Builder for net-new flow LAYOUT; use this script for edits, generation of the main flow, review, and promotion.
  - Generate the JSON from **small helper functions, one per node type** (`create_values(...)`, `send_workday_api_request(...)`, `branch_on_conditions(...)`, `loop(...)`, `call_subflow(...)`, etc.), rather than hand-editing the verbose tree.
- **Method:**
  1. Define an envelope helper: **every value is a typed-AST envelope `{"_type": <TypeName>, "_value": <payload>}`.** All node builders return this shape; nesting composes envelopes.
  2. Root doc = `{"flowVersion": "<3.x>", "_type": "Flow", "_value": {...}}`. Match the template's `flowVersion` (3.1.0 omits `tlsConfigRef`; 3.3.0 carries `tlsConfigRef: _DEFAULT_TLS_CONFIG`).
  3. Start/end nodes keyed to flow type: `FlowSync -> StartBasic/EndSync` / `FlowAsync -> StartAsync/EndEmptyMaya` / `IntegrationFrameworkTrigger -> StartIntegrationFrameworkTrigger/EndEmptyMaya` / `FlowSubflow -> StartSubflow/EndSubflow`. Never emit a `MixedStart` at 3.x.
  4. Build the main flow's node list with the per-type helpers; wire launch params on `StartBasic` (`structuredRequest.ObjectRequestStructure.props`, read as `data.start.$_<name>`) as needed.
  5. **The launch gate `securityDomains` is a BARE string array at the FLOW ROOT** - a sibling of `"_type": "Flow"`, OUTSIDE `_value` (e.g. `"securityDomains": ["<Domain>"]`). Do NOT set the NESTED `securityDomains` envelope inside `_value` - leave that typed-null untouched (setting it to a bare list is a confirmed 3x build failure). A gating flow carries BOTH; a non-gating flow omits the root key.
  6. Ensure node-name uniqueness across the flow (the linter errors on dupes), keep names valid dotted identifiers, `json.dump` with stable formatting, write to `orchestration/<FlowName>.orchestration`.
  7. Run `python scripts/validate.py <FlowName>.orchestration` (regenerate it from the spec above if absent) - build-clean = linter accepts it - then `wdcli app upload`.
- **Key constants:** typed-AST envelope keys `_type`/`_value`; root keys `flowVersion` + `_type: "Flow"` + `_value` + optional bare-array `securityDomains`; recommended `flowVersion "3.3.0"` (match the template). Node kinds and their payload shapes: see `orchestration.md` section  Node vocabulary.
- **Gotchas:** hand-authoring a brand-new flow from scratch is (!) - copy a proven app and reuse subflows verbatim. The two look-alike `securityDomains` (bare root gate vs nested typed-null artifact) are the single easiest thing to get wrong - re-read `orchestration.md` before touching either. `SendWorkdayApiRequest` does NOT hard-fail on 4xx (silent data loss) - the builder should emit the response-status / XPath-fault guard (or reference a `retryConfig` with `successResponseCodeRanges`) rather than trusting a clean completion. Always lint before upload; `wdcli app upload` stays authoritative - this is a generator, not a compiler.
- **Regeneration confidence:** **Medium** - the builder skeleton, envelope shape, start/end pairing, and the securityDomains rule are fully specified and reproducible; the PER-INTEGRATION node graph, expressions, and which template app to copy are supplied fresh each time (there is deliberately no single generic version).
- **Cross-ref:** [orchestration.md](orchestration.md) (Maya format, node vocabulary, securityDomains rule, `/launch` bridge) and `validate.py` above (the pre-upload linter).
