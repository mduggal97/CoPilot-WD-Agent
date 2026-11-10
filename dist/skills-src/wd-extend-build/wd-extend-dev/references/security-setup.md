# Security & access setup - ISUs, domains, API clients, who does what

Security setup is the most common hidden critical path on Extend projects: most of it must be done by the CLIENT's security administrator, per tenant, and requests routinely take days-to-weeks. Surface these needs at kickoff (wd-extend-lifecycle) and again before every tenant promotion (wd-deployment).

> **Click-level steps:** for novice-grade, copy-pasteable recipes (exact Workday task names + numbered clicks + "you're done when..." checks) for each item below - domain grant/S22, Activate Pending Security Policy Changes, ISU, ISSG, Integration System, API Client + Refresh Token, App Attributes, SSH/PGP keys - see `wd-deployment/references/tenant-task-recipes.md`. This table says *what and who*; that library says *exactly how*.

## The pieces and who owns them

| Item | What it's for | Who typically does it | When |
|---|---|---|---|
| Security domain grants | App BO data access (the S22 fix): Domain Security Policies -> app -> add security group View+Modify + Get/Put -> Activate | Client security admin (the delivery team can draft the request) | After FIRST deploy to each tenant, and after every `app copy` |
| Security groups + role assignments | Map app domains to real users/roles (often assigned to org/location hierarchies) | Client security admin | Before UAT in each tenant |
| ISU (Integration System User) + Integration System | Auto-auth for orchestration Workday calls (SOAP needs Integration Permissions; REST needs Report/Task domain permissions) | Client security admin creates; the delivery team specifies required domains | Before first orchestration run per tenant |
| API Client + Refresh Token | EXTERNAL access to BO REST / WQL (scripts, external integrations) - refresh-token grant (the OAuth flow + token caching are owned by `wd-auth/references/oauth-setup-guide.md`) | Client (registers) to the delivery team's spec | When external REST access is needed |
| App Attributes | Tenant-specific WIDs/config the app reads at runtime | Delivery team sets per tenant | Each tenant, at deploy |
| BP definitions / approver chains | Configured on the BP definition in-tenant (NOT in source) | Functional consultant / client admin | Each tenant, after deploy |
| Agent credentials (custom agents) | Live in ASOR, not the App-Hub OAuth client | Client admin | If/when agents ship |

## ISU-authenticated PAGE endpoints (deliberate domain bypass)

Pages - not just orchestrations - can run individual endpoints as an ISU: the SMD's `siteAuth.authTypes` gains `{ "scheme": "ISU", "id": "isuAuth", "username": "ISU_XTND_<app>_<purpose>" }` and the page endpoint sets `"authType": "isuAuth"`. That endpoint then executes with the ISU's domain grants, so ANY user's page can read admin-domain data (translations, config/reference rows) without the user holding the domain. Verified in a delivered production app (2026-08-05); note the `ISU_XTND_<app>_<purpose>` naming convention.

**Design consideration:** this is a deliberate security bypass - the user-context domain check is skipped for that endpoint. Use it only for read-mostly config/reference data, never for person-level or writable data a user shouldn't reach, and document every ISU-authed endpoint (which ISU, which data, why) in the design doc's Security section. The ISU itself is one more client-security-admin item per tenant (add it to the request package below).

**An ISU binds to ONE Extend app per tenant - a copied app cannot reuse the parent's ISU** (field-observed Sep 2026, one engagement's dev tenant; cost about a day to work out). A copy's `.smd` still names the parent's ISU, and assigning that ISU in App Manager fails silently: the Add-ISU prompt lists only UNASSIGNED ISUs, so it just says **"No matches found"** - which reads like a search problem, not a constraint. Until the copy has its own ISU, every `isuAuth` endpoint in it fails server-side with a 500 and a null response body. Rule: every app copy gets its OWN ISU (it can join the same ISSG as the parent's, so the grants match); repoint the copy's `siteAuth` ISU username and assign the new ISU in App Manager before the first deploy (wdcli-workflow.md "Cloning apps"; recipe wd-deployment tenant-task-recipes.md R3).

## The request package pattern

For each tenant, hand the client security admin ONE written request listing: app name + reference ID, each security domain with the exact permissions needed (View/Modify, Get/Put), the security groups to attach, the ISU + Integration System spec (domains, SOAP integration permissions if any), and API-client needs. Batch requests - five separate tickets take five lead times.

**Auto-populate the domain list, don't hand-derive it.** `scripts/security_domain_discovery.py discover` (spec in `scripts.md`) takes the reports/web-service-operations/BPs the app or integration actually calls and resolves them to the domains and BP permissions that secure them, checks whether a named ISSG already has them, and flags domains that should redirect to a parent because they're currently inheriting. Reverse-mined from the partner tool (a Workday-delivered implementation-partner tool for exactly this job) and live-verified against a dev tenant - it queries WQL directly (`allCustomReports`, `allWebServiceOperations`, `allDomains`) plus one read-only SOAP call for BP security, so no custom report needs to exist in the tenant first. Read-only: it produces the checklist, it does not grant anything.

**When the client wants the delivery team to apply the grants directly** (rather than just handing the client admin a request), `scripts/security_domain_apply.py` (spec in `scripts.md`) is the guarded write half - plan a set of grants, review the exact diff, then apply with a human confirming every write. It never touches a tenant declared `prod`, defaults to dry-run, backs up every document before writing, verifies each write landed, and never activates the resulting pending security policy changes (that stays a human step, same as always). Read `domain-apply-safety.md` in full before using `--execute` for the first time against any tenant.

> **This request package IS the guide's Security Setup Section.** When any guide (Deployment Guide, tenant-setup, wd-kt admin guide) writes up security, it uses the reusable novice template in wd-deployment `security-setup-section.md`: exact tasks in order (Part 1), the naming block for every object created (Part 2), and the **enumerated domains-and-permissions table** - every domain, plain-English purpose, exact View/Modify + Get/Put access, and the group it's granted to (Part 3). Populate that table from the design doc's Security tab / IDD `WD Solution` tab; a blank domain table is a defect.

## Segment-based integration security - which PEOPLE see which integrations

Everything above secures the *machine* side (ISU running the integration). The
client also needs the *human* side segmented: integration events, files, and configs
carry sensitive data (payroll, benefits), so "can monitor integrations" must not mean
"can open every integration's output." The recommended pattern is segment-based security,
built per functional area (e.g. Benefits / HRIS / Payroll) from a three-object triad -
**regenerate the worksheet via `build_security_segment_worksheet.py`** (spec in
`scripts.md`, both in the wd-integration-dev skill), or obtain the firm's branded master per engagement (environment memory).
Its Setup Details sheet maps users -> groups -> segments -> integration
systems; any delivered-tenant screenshot tabs are intentionally omitted (they carried
tenant data) - capture your own tenant's views when instantiating:

1. **Integration System Security Segment (ISS)** - the bucket of Integration
   Systems for one functional area (selection criteria: specific integration
   systems; category/template/all also exist). Example name: `ISS <Area> Integrations`.
2. **User-based security group (ISUG)** - unconstrained, holds the human operators:
   `ISUG <Area> INT Operator`. May go live with no members and be populated later -
   the structure ships even if staffing lags.
3. **Segment-based security group** - `ISSG <Area> Segment Security Group`, context
   type *Constrained by Segment Access*: group criteria = the ISUG, access rights ->
   Access to Segments = the ISS. **The integration domains are granted to this
   group**, so a member only reaches integrations inside the segment.

Every triad gets a **`... VIEW Only` twin** (ISUG + segment group) for read-only
monitoring access - auditors, functional SMEs, help desk.

Observed grant set on a delivered VIEW-only segment group (Report/Task permissions;
the full-operator twin raises access on the same domains - pull its exact levels from
the tenant when instantiating): **View & Modify** on `Integration Event` (needed to
work the run events even for viewers); **View Only** on `Integration Reports`,
`Integration Configure`, `Integration Debug`, `Integration Process`,
`Integration Build`, `Integrations: EIBs`.

Doc-corroboration and two nuances (per Workday Admin Guide (Authentication & Security),
Jul 2026, chapter "Steps: Secure Integrations by Segment"): the segment can contain
integration *templates, systems, or categories* (not just specific systems); a
**role-association variant** exists (tie the integration's process event to an org and use
an unconstrained role-based group inside the segment group); and **Message Queue security
segments** exist for Studio message queues (Message Queue (segmented) domain). Also note
**constrained ISSGs exist** - an org-constrained Integration System Security Group filters
public web services *by element* and RaaS output *by row* - so our unconstrained default
is a deliberate choice, not the only option.

Naming note: the worksheet segments by **functional area** (`ISS Payroll
Integrations`); `integration-naming.md` (in the wd-integration-dev skill)'s security-segment row shows a per-INT-ID
pattern (`INT005 Security Segment Payroll Integrations`). Resolve per client and
record the choice in the IDD (same rule as that file's other discrepancies). These
groups are one more client-security-admin item - add the filled worksheet to the
request package above. The bundled workbook's Setup Details example rows are
delivered-example provenance - replace, never reuse, when instantiating for a client.

## Verification per tenant

After grants: page loads (works even ungranted) -> BO data call (S22 gone?) -> orchestration smoke run (check run logs `wd_log_type = remote`) -> BP launch + inbox routing with a real test user in each security group (positive AND negative: the wrong role must see nothing - that's a unit scenario, wd-testing). The BO-data-call and Get/Put checks are runnable live via tenant-ops (the tenant-readiness read-set) - capture the before/after result as the grant evidence (references/tenant-ops.md).

## Identity governance - Workday drives the Joiner-Mover-Leaver lifecycle

Step back from the per-tenant setup and the credentials themselves and look at *who* holds access over time. Workday is the client's HR system-of-record, so it is also the source of the identity events that should drive provisioning and de-provisioning: a **Joiner** (hire) needs the right security-group membership and, where an app is machine-driven, the right ISU/Integration-System access; a **Mover** (transfer, promotion, org change) should gain the new context's access and *lose the old* - access does not follow a person around by default; a **Leaver** (termination) must be de-provisioned, and any ISU or refresh token that person personally held gets rotated (the staff-departure rotation trigger in the table below is exactly the Leaver case).

The governance concern the JML lens surfaces: **orphaned and former-employee access**. Human security-group memberships and ISU domain grants both tend to accumulate and never shrink - a Mover keeps stale access, a Leaver's group membership lingers, a `... VIEW Only` twin quietly fills with people who should have full access or none. The countermeasures are **de-provisioning on the Leaver/Mover event** and **periodic access recertification** - do not re-own either here: recertification is the client-handed annual access review in the next section (memberships, ISU grants, VIEW-only twins), and the human-vs-machine split those groups enforce is the segment-based security section above.

(!) Workday-specific mechanics unverified: whether the client's Workday drives provisioning automatically (via a JML/IGA integration, SCIM, or an Extend/Studio provisioning flow) versus the security admin working the events manually is a per-client fact - confirm and record it in the design doc's Security section before promoting any "provisioning is automated" claim. (Cross-cutting framing folded in from external skillsmp `building-identity-governance-lifecycle-process`; the JML->provisioning idea is the reusable part, not a verified Workday feature.)

## Credential lifecycle - rotation triggers and owners

Every credential created above outlives the project; hand each one a lifecycle, not just a birth. Rotation triggers are the same for all rows: **on schedule, on staff departure (anyone who held the value leaves the client or the delivery firm), and on suspected incident**. Cadence splits by credential type (per Workday Admin Guide (Authentication & Security), Jul 2026): **keys are expiry-driven** - x509 and PGP private key pairs carry built-in Valid To dates (View x509 Private Key Pair / View PGP Private Key Pair reports); regenerate BEFORE expiry via related action -> Regenerate Key Pair, then re-share the new public half with the partner. **Secrets and ISU passwords have no Workday-stated cadence - that remains client security policy**; the conservative default when the client has none is **annual or on-event, whichever comes first**. Refresh-token / access-token timeouts are verify-first, not a fixed number - confirm the current defaults and configurable ranges in `wd-auth/references/oauth-setup-guide.md` before quoting one. Record the client's actual answers in the design doc's Security section.

| Credential | Rotation mechanics | Owner (per the who-does-what table) |
|---|---|---|
| Refresh tokens | Re-generate on the API Client (recipe R6, wd-deployment `tenant-task-recipes.md`); update every consumer that stored it | Client security admin |
| API client secrets | Re-generate in Register API Client; coordinate with external callers before cutover of the value | Client security admin |
| PGP private keys | Re-issue key pair (recipe R9); exchange new public key with the counterparty; keys do NOT migrate between tenants - rotate in the master tenant | Client security admin (delivery team specifies) |
| ISU passwords | Reset on the ISU account; update the Integration System credential mapping (`_DEFAULT_WORKDAY_CREDENTIAL`) in the same change window or every flow run fails | Client security admin |

**Annual access review (client-handed item):** once live, the client reviews ISSG memberships and the app's role/security-group assignments at least annually - who is still in each group, whether each ISU's domain grants still match what the app actually calls, and whether any `... VIEW Only` twin quietly accumulated full-access members. This is a client-owned row on the support-ownership matrix (wd-post-go-live `references/handoff-and-closeout.md`) - hand it over at closeout, don't let it default to nobody.

## OAuth refresh-token flow (external REST) - owned by wd-auth

The token-exchange mechanics (the `/ccx/oauth2/{tenant}/token` refresh grant, the access-token
cache/re-mint cadence, and access/refresh-token lifetimes) are owned by
`wd-auth/references/oauth-setup-guide.md` - do not restate the endpoint or the timing numbers
here. This skill's lane is only the **security grant model** above (ISU / ISSG / security
domains). The endpoint MAP the app calls once it holds a bearer stays a build fact: REST
`{base}/ccx/api/v{n}/{tenant}`; BO REST `https://api.us.wcp.workday.com/apps/<refId>/v1/<collection>`;
WQL `https://api.us.wcp.workday.com/wql/v1/...`; SOAP `{base}/ccx/service/{tenant}/<Service>/v46.1`
(host discovery in [tenant-ops.md](tenant-ops.md)). A reusable helper (`workday_rest.py`) can
live in your Extend workspace.

## Grant-list documentation format (STANDING, 2026-09-04)

When writing the ISU/ISSG (or any group's) domain grants into a design doc Tenant Config tab, a
Deployment Guide, or a user-action checklist, group by PERMISSION BUCKET with the domains listed
underneath - exactly mirroring the Maintain Domain Permissions UI so the person granting can work
top-to-bottom:

- **Modify and View** (report/task permissions)
- **View Only**
- **Put and Get** (integration permissions)
- **Get Only**

Omit empty buckets; a domain may appear under both a report/task bucket and an integration bucket.
Flag delivered domains whose exact names still need in-tenant confirmation (View Data Source) inline.
Never emit a per-domain 'domain -> permissions' table for grant instructions.
