# Traditional integration build - per-type guidance + build gates

Extend work often ships alongside traditional integrations (EIB, Studio, Core Connector, DT). This reference distills the firm integration build checklist (generic items). For the checklist workbook itself - the integration design/build checklist - **regenerate via `scripts/build_integration_checklist.py`** (spec in `scripts.md`; emits the design + per-type build sheets, the Status picklist, and generic API-client / key / SFTP-MFT reference sheets), or obtain the firm's branded master per engagement (environment memory). The builder produces a vendor-neutral template - client-specific SFTP/MFT, division-tag, and tenant details are genericized and filled in per engagement. Design gates live in wd-design-doc's IDD reference; naming in integration-naming.md. For Studio specifically, [studio.md](studio.md) covers project anatomy / assembly vocabulary / MVEL / when-Studio-vs-O4I, and [studio-patterns.md](studio-patterns.md) the named reusable designs (boomerang, chained multi-Studio, DIS compare, EIB launcher, WWS import framework, shared-library CLAR).

## Generic build gates (all integration types)

- Reports: share with the security group AND the ISU, transfer ownership to the ISU; population logic via calculated fields, not raw report filters; object prompts for test instances; population/filter parity between report filters and connector Population Eligibility.
- All names + Reference IDs per the naming standard (integration system, ISSG, EIB template, XSLT attachment, file utilities per environment, sequence generators).
- Output/log filenames include date-time (e.g. `..._Log_File_2023-11-16T17_45.html`).
- Document retention set (house default 180 days - Workday ships connectors at 30; documented override values are 60/90/120/180, so 180 is the documented MAX, not out-of-the-box; per Workday Admin Guide (Integrations), Jul 2026). Audit files auto-delete at end of retention; an event's consolidated report becomes unavailable once expired or over 10 MB.
- SFTP/delivery BPs use **Environment Restrictions with at least 2 endpoints (PROD + non-PROD)** - this is what stops a sandbox run delivering to a production vendor endpoint. Official corroboration (per Workday Admin Guide (Integrations), Jul 2026): exactly one transport per environment, each Restricted To its environment - an EMPTY Restricted To applies the transport to EVERY environment, and each environment holds only one transport; restrict attributes and maps by environment too.
- Tenant-level gates (Edit Tenant Setup - Integrations): can **require Studio integrations to include source code** (the tenant-enforced version of the Git-as-source gate - recommend clients enable it) and can disable integration subscription notifications tenant-wide.
- Default notifications on every integration system using the standard `CF CT Integration Notification Message Content - Subject/Body` calc fields (Trigger Status -> Conditions -> Recipient -> Message Content).
- XSLT: header comment block (integration name, developer, description, data population, frequency, dated dev log - mirrors this skill's change-log standard); no `//` selectors; decimals not doubles. **STUDIO only:** XSLT 3.0 with streaming; store xsl in `ws/WSAR-INF`. (EIB and Document Transformation are historically XSLT 2.0-only - see eib.md / xslt3.md; do not apply the 3.0 gate to them.)
- Code in source control: Git URL for XSLT/Studio code recorded in the IDD Overview links; keep Git current across tenant migrations.
- Unit tests complete with a successful event in the dev tenant; test-event links recorded; IDD tabs updated (Question, Overview, Requirements Added-to-Test, Report, File, WD Solution, Unit Testing, Examples, Flow, Open Issues); run DART and fix findings.

## Per-type highlights

- **EIB Inbound**: retrieval config (endpoint, SSH key pair, retention, sequence generator, compression, encryption key), data format, web-service op; ISSG (domains + ref ID) -> ISU (in ISSG, assigned to the integration) -> notifications.
- **EIB Outbound**: data source (report vs API), XSLT via Create XSLT Attachment Transformation (ref ID per standard), SSH/PGP keys created BEFORE delivery config, delivery endpoint details, ISSG/ISU chain, 4-part notification config.
- **Studio (both directions)**: import the Studio Starter Kit and refactor-rename project + collection (collection name ends `_Collection`); import the firm's shared Studio utilities; keep 'AMS' in the renamed Attribute Map service; common services = Report Service, Attribute Map Service, Listener Service (prefer API Client + attributes over custom-object service for config); a **boolean debug launch parameter** is standard; error handling = local handlers + mandatory global error handler + cloud logs with custom columns (not CSV); always XSLT+ component with streaming; document labels on files stored to the event.
- **Core Connector**: research/select the CC template on Community; enable optional services; transaction log service for change detection; attributes; maps (preconfigured vs new); delivery service vs BP; ISSG/ISU chain.
- **Connector + DT**: 'Document Transformation' template; input/output document tags; output encoding attribute (overrides the XSLT's); Audit Validation Messages; retention; Integration Attachment Service for the XSLT; add DT as a subprocess on the source integration's BP.
- **O4I as an INT**: app created per naming standards; orchestration (integration-system or BP-triggered); integration system from the Orchestrate Integration Template; debug boolean launch param; deploy/install/launch via the Developer Site Promotions tab; error handling writes Workday API error text to custom columns/messages. (Flow authoring: orchestration.md in the wd-extend-dev skill.)

## `Put_Integration_System` is a FULL REPLACE - send all three references every time
> Provenance: hard-won on an O4I integration-system setup script (2026-09-01). Vendor-neutral; WIDs are placeholders.

`Put_Integration_System` with `Add_Only="false"` is a full replace of `Integration_System_Data`. If you send only the field you intend to change (e.g. only `Custom_Launch_Parameter_Data`) and omit the others, Workday SILENTLY CLEARS them. So on every call include all three even when you are only changing one:

- `Integration_Template_Reference` - omitting it removes the Orchestrate Integration Template binding (kills the Template section, Integration Services, and the Integration Attributes tab in the UI).
- `Integration_System_User_Reference` - omitting it removes the ISU / Workday Account.
- `Integration_Service_Data` - omitting it removes the service registration.

**Symptom of the trap:** View Integration System shows only Basic Details + Launch Parameters - no Template section, no Workday Account, no Integration Services, and the "Launch Integration System" related action disappears.

**Fix - always include all three:**
```xml
<wd:Integration_Template_Reference>
  <wd:ID wd:type="WID">{ORCHESTRATE_TEMPLATE_WID}</wd:ID>
</wd:Integration_Template_Reference>
<wd:Integration_System_User_Reference>
  <wd:ID wd:type="WID">{ISU_WID}</wd:ID>
</wd:Integration_System_User_Reference>
<wd:Integration_Service_Data wd:Enabled="1">
  <wd:Integration_Service_Reference>
    <wd:ID wd:type="WID">{ORCH_SERVICE_WID}</wd:ID>
  </wd:Integration_Service_Reference>
</wd:Integration_Service_Data>
```

Get the template and service WIDs by running `Get_Integration_Systems` against a correctly-configured O4I integration in the same tenant and copying them out; the ISU WID is integration-specific, so read it from that same GET response for the system you are editing.

## Transport & delivery quirks (per Workday Admin Guide (Integrations), Jul 2026)

- SFTP: retry count configurable via Delivery Attempts; default block size 32K - tune via Test Transport.
- HTTPS delivery auto-retries up to 5x (3 s back-off) **on 302 responses only**; GCS gets exponential back-off (1/2/4/8/16 s) on 5xx.
- **Email and FTP transports require PGP encryption** - an unencrypted email EIB needs a security-admin override on every edit.
- WWS paging: SOAP responses default **100 records/page, max 999** via Response_Filter Count. DIS data-gathering time does not count toward the Studio processing time limit.
- Integration subscriptions (external endpoint notifications): delivery is NOT guaranteed (no WS-ReliableMessaging - out-of-order/duplicate/missing all possible); **2 consecutive failures disable the endpoint** - re-enable via Integration System > Edit Subscriptions -> clear Disable Endpoint; the message carries no event data - pull details via Get_Event_Detail.

## Keys & API clients (migration matters)

- x509 private key pair (SFTP SSH auth): WD developer creates, shares the RSA-SSH public portion. **Create in Production** - a key pair created in a non-Production tenant cannot be migrated to Production (Sandbox inherits from Prod via the weekly refresh); per Workday Admin Guide (Integrations), Jul 2026. This corrects the earlier firm-checklist "migratable, available in any IMPL tenant" claim - flag for review.
- PGP public key (encrypt outbound): vendor supplies - migratable. PGP private key pair (decrypt inbound): WD developer creates, gives public half to sender - **NOT migratable**; same create-in-Production guidance applies (refreshes carry it down).
- API Clients (OAuth 2.0): **not migratable** - created in the master tenant, available in lower tenants after refresh. Grant types: Authorization Code, PKCE, JWT Bearer, SAML Bearer (Implicit and MAC = do not use); token lifetimes are configured per API Client - **wd-auth owns the TTL guidance** (oauth-setup-guide.md; verify in the tenant rather than assuming a default - the Jul 2026 admin guide's defaults were 4h access / 30-day refresh, but they are tenant-configurable); scope by functional area; optional IP range and CORS origins.
- More OAuth/API-client facts (same guide):
  - Tenant prerequisite: **OAuth 2.0 Clients Enabled** checkbox on Edit Tenant Setup - Security - else the token endpoint rejects with "OAuth 2.0 is disabled for this tenant".
  - Refresh tokens: rate-limited **1 token/second per user**; max **1 refresh token per API-client-for-integrations + Workday-account pair**; rotate via related action **API Client > Manage Refresh Tokens for Integrations**.
  - Scope gotcha: APIs reading objects with **lookup-hierarchy calculated fields need scopes Custom + Organizations + Roles**.
  - API clients **lock out after excessive failed sign-ins** - the View API Clients report shows the lockout end time (check it when troubleshooting 401s).
  - Grant Administrative Consent = tenant-wide consent; CORS Allowed Origin only works with Auth Code + PKCE; authorization codes expire in 10 min; Workday-delivered OAuth clients arrive disabled; revoke via Maintain API Client Access (admin) or Manage My API Client Applications (self-service).
  - JWT Bearer grant can be restricted to selected ISUs (x509 validates signatures); the "Allow Integration Messages" checkbox feeds integration status back.
- EIB security model: EIBs have **no independent permissions** - they inherit the launching/scheduling worker's security, including contextual filtering of output.
- Permission-implication rule: **Get on a domain implies View on its reports/tasks; Put implies View and Modify** - why an ISSG-only grant also unlocks the UI side.
- Key expiry notifications at 30/15/7 days - put key renewal on the support calendar (wd-post-go-live).
- Tenant-to-tenant migration verification (per-integration checklist: ISU/ISSG in target, env restrictions, keys, RaaS ownership, retention, scheduled processes, DART) is a tracked deliverable - wd-deployment `references/migration-checklist.md`.

## Efficiency notes

Run PECI at most once daily; avoid CCW full-file runs; schedule CCW end-of-day. Large-read design: RaaS/WQL guidance in orchestration.md (in the wd-extend-dev skill) applies to Studio report calls too.

## Payroll Interface / Certified Integration pattern (PECI/EXPR family)
> Folded in from a config-guide distillation sweep (2026-08-10). Vendor-neutral; no client specifics.

Tool-agnostic pattern for integrating Workday with a third-party payroll engine via the certified
Payroll Interface (PICOF/PECI family). Three integration instances:
- PECI (Payroll Effective Change Interface) - OUTBOUND demographic/effective-change export.
  Captures all Workday events with effective dates in the sequence they occurred. At least one PECI
  instance per country; the instance is configured to include only fields relevant to that country
  (names, addresses, National IDs, payment elections are country-specific). One instance can serve
  multiple pay groups; rarely a reason for more than one primary instance per country.
- EXPR (External Payroll Results) - INBOUND. Brings periodic payroll results from the third-party
  engine back into Workday for management reporting.
- Import External Pay Slips - INBOUND. Brings pay slips from the third-party engine into Workday so
  employees can view them.

WD -> third-party LIST-VALUE MAPPING CHECKLIST (every list value must map to a value in the payroll
system; get vendor-side values from the payroll vendor's team; client maintains sync post go-live):
- Cost Center
- Earning / Deduction codes - map via the "Maintain External Payroll Earnings" and "Maintain
  External Payroll Deductions" tasks
- Frequency (weekly / bi-weekly / semi-monthly / monthly)
- Pay Group (shares pay frequency + rate type; country-specific; all members share one period
  schedule and run category) - when creating, check "Used in Payroll Interface" so the country
  appears
- Payroll Company (legal tax entity; one country only; can be multiple per country) - enable
  "External Payroll Code"
- Period Schedule / pay calendar (defines period start/end; status must be maintained in BOTH
  systems)
- Also commonly mapped: Location, Gender, Marital Status, Pay Rate Type, Payment Type, Job Family,
  Management Level, Business Site, Organization
- Staffing events / business processes - confirm which the payroll engine supports. Typically
  supported: Hire, Termination, Pay Company Transfer In/Out, Pay Group Transfer In/Out, Organization
  Change, Leave of Absence + Continuation + Return from Leave (and their corrections/rescinds), Other
  Data Changes. Common gap: Hire-Rescind across the period/cycle.

Design notes: maintain a Data Dictionary mapping Workday fields to the payroll engine's fields (one
column per country); mark the certified-integration attribute and PECI file version; set the
document retention window; use payment-election rules to scope which workers/elections land in the
output. This is a config-and-mapping pattern - the heavy lifting is the list-value mapping exercise,
done per client by the Workday implementation team.

## Admissions inbound data-load object set + mass-tag pattern
> Folded in from a config-guide distillation sweep (2026-08-10). Vendor-neutral; no client specifics.

Add the standard Admissions data-load object set + a mass-tag pattern (no client/vendor specifics):

Standard Admissions inbound data-load object set (EIB/iLoad per object):
- Student Application (Put Student Application)
- Application Grouping (Put Application Grouping)
- Education Test Result (Put Education Test Result)
- Educational Institution Course (Put Educational Institution Course)
- Marketing Activity Definition (Put Marketing Activity Definition)
- Recruiting Region (Put Recruiting Region)
- Search Service Definition (Put Search Service Definition)
- Institutional course catalog (institutional-course iload)

Mass-tag-existing-records-via-EIB pattern:
- To add a Student Tag to many EXISTING student applications, use the Student Application EIB in add-only mode ("Add Only" = N) supplying only the minimum required fields to re-identify each application plus the new tag: the Student_Application_ID (Reference ID), Active = Y, Student Prospect Stage, Student Applicant Type, Application Date, program-of-study line (Order + Program of Study), the Academic Period line, Anticipated Load Status, and the new Student_Tag_ID.
- General pattern: to bulk-append a repeating child element (a tag, a period, etc.) to existing parent records, load the parent's key + required identifying fields alongside the new child value rather than a full re-load - minimizes the field set and avoids overwriting unrelated data. Validate required-field behavior in a Sandbox load first.

> Calculated fields used in reports/EIBs: see the calc-field type selector in wd-extend-dev `references/model.md` (single owner).
