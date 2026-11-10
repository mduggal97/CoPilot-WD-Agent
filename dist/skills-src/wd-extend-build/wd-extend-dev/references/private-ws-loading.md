# Private web services loading - guided workflow

Load tenant configuration programmatically through Workday's PRIVATE (implementer) SOAP
surface - the same operations behind the "advanced load" spreadsheets and iLoad: custom
reports, calculated fields, ISUs/ISSGs, sequence generators, integration config, and the
whole `Put_*` implementation-service catalog. **End-to-end build-verified 2026-09-01**
(dev tenant): calc fields + web-service-enabled custom reports created via
`Report_Metadata`, then executed via RaaS with correct prompt filtering.

Everything here runs under **THE WRITE GATE** (tenant-ops.md): dev/impl/sandbox only,
explicit user opt-in, every write logged with a cleanup plan.

## Step 0 - auth: API client + refresh grant (the ONLY path)

HTTP Basic for web services is **retired (~R2 2026)** - see wd-auth
auth-decision-tree.md Mode 3 for the diagnosis signature. What works:

1. USER registers an API Client for Integrations + generates a refresh token for the
   implementer account (the USER-ACTION runbook: tenant-ops.md "Path B").
2. Secrets land in the OS credential store (keyring), one service name per tool,
   keys `client_id` / `client_secret` / `refresh_token`. Never in chat/files/env.
3. Mint per run: POST `{gwUrl}/ccx/oauth2/{tenant}/token` with
   `grant_type=refresh_token` + refresh token, client id/secret as HTTP Basic ->
   `Authorization: Bearer <access_token>` on every SOAP/REST call.

Paste-check the refresh token WITHOUT printing it: ~100 chars, no dots. A `eyJ...`
JWT in that slot is a mis-paste (wd-auth troubleshooting table).

## Step 1 - enumerate the surface

- **Every operation**: WQL `SELECT webServiceOperationName, webService1, public,
  secured FROM allWebServiceOperations` - runs at the classic host
  (`{gw}/ccx/api/wql/v1/{tenant}/data`) with the same bearer, paged limit=100.
  Yields the op -> service -> public-flag -> security-domain map (~7,000+ ops/tenant).
- **Group into a service directory** (private-op counts, write-verb counts, WSDL URL
  names) and save next to the REST schemas. Worked example:
  `rest-api-schemas/<tenant>_private_ws_directory.md` in the author workspace.
- URL name = service descriptor with underscores, MINUS any " (Public)" / " (Internal)"
  suffix (those are WQL labels, not URL segments).

## Step 2 - fetch the WSDL (anonymous, no auth)

`{gwUrl}/ccx/service/{tenant}/<Service_URL_Name>/v<current>?wsdl` - works for public,
implementation, AND private services. This is pure schema download; the version segment
here does NOT imply the service is versioned at call time (next step).

## Step 3 - call it (two service styles)

- **Versioned services** (Core_Implementation_Service, Integrations, most): call
  `/{Service}/v47.0` with `wd:version` attribute on the request element. Normal.
- **UNVERSIONED services** (`Report_Metadata` proven; suspect other internal ones):
  call the **versionless URL with NO `wd:version` attribute** - any version segment or
  attribute faults with "The web service or version is invalid for the requested
  operation". If a versioned call gives that fault on a service you KNOW exists, drop
  the version everywhere before debugging anything else.
- Envelope: plain SOAP 1.1, `xmlns:wd="urn:com.workday/bsvc"`; element names come from
  the WSDL, never the op display name.

## Step 4 - discovery for authoring (find the WIDs)

Rank these; each solved a real gap in the verified build:

1. **Donor Get** - fetch a hand-built sibling object's full definition
   (`Get_Tenanted_Report_Definitions` by reference, etc.). 12 KB of exact tenant
   serialization beats any documentation. THE primary authoring template.
2. **WQL data-source catalog** - `{gw}/ccx/api/wql/v1/{tenant}/dataSources` (paged):
   each entry's `id` IS the report-writer data-source WID and
   `primaryBusinessObject.id` IS the class/BO WID. (Verified: catalog ids matched
   report-definition serializations exactly.) Save the dump; it is the DS+BO directory.
3. **Per-data-source fields** - `/dataSources/{id}/fields`: class-report-field WIDs
   with type + relatedBusinessObject (more BO WIDs by name). PARTIAL - only
   WQL-exposed fields appear; delivered basics (Name, self field) are often missing.
4. **Field-by-name lookup** - `Get_Integration_External_Fields` (private
   `Integration_Metadata` service): criteria `Field_Name` + `Work_Data=true` returns
   matching field WIDs tenant-wide. Disambiguation is weak (no owning class in the
   response) - prefer 1-3, fall back to this, and RaaS-verify the pick.
4b. **The `allDataSources` meta-catalog (THE data-source-WID answer).** A data-source
   reference is WID-ONLY and a DS unused by any report won't appear via donor Gets.
   Get its WID from the delivered WQL source `allDataSources`:
   `SELECT workdayID, label, primaryBusinessObject, built_InPrompts, allReportFields,
   DEPRECATED FROM allDataSources WHERE label = '<Data Source>'` (`CONTAINS` to browse).
   Each row gives the DS WID (`workdayID`), the primary-BO name, the DS's built-in prompt
   WIDs (`built_InPrompts` - use these as `Prompt_External_Parameter_Reference` on
   target-primary reports instead of a filter+prompt-field), and its full field set
   (`allReportFields`). Companion `classReportFields` resolves a field's owning class +
   related BO. This is the reliable path when `/dataSources/{id}/fields` 404s (some DSs
   are not directly field-enumerable).
5. **Corpus mining** - page a Get-all to disk once (e.g. 77 pages of calc fields,
   39 pages of report defs at Count=100), then grep for donor shapes, category/usage
   WIDs, and reference examples. Cheap and reusable.
6. **Global fields reuse one WID everywhere** ("Workday ID", "Name") - but see the
   column-restriction gotcha below.

## Step 5 - author + Put (behind the gate)

- Reference styles: WID always works. Some types accept richer IDs - custom reports:
  `Custom_Report_ID` with `parent_type="System_User_ID"` (create ISU-OWNED directly,
  skipping post-create ownership transfer); calc fields: `Calculated_Field_ID` = your
  `Calculated_Field_Reference_ID`. **Data sources are WID-ONLY** (fault says
  "Valid Types: WID").
- Put with a `..._Reference` block = update-in-place; without = create. Same body works
  for both (verified).
- Log every write (timestamp, op, name) to a load journal; that journal IS the
  cleanup plan's input.

## Step 6 - verify (never skip)

1. **Get readback** - fetch what you Put; assert the load-bearing elements
   (aliases, references, flags) with a scripted check.
2. **Execute** - for reports: RaaS run via the gateway
   (`https://api.<region>.wcp.workday.com/raas/<owner>/<Report_Name_underscored>`)
   unfiltered AND with prompt values; row counts must respond to the filter.
   Definition-time acceptance does NOT prove runtime validity (see gotchas).

## Fault vocabulary (what Workday's errors actually mean)

| Fault / symptom | Meaning |
|---|---|
| "invalid username or password" tenant-wide, UI login fine | Basic-auth retirement, not credentials (wd-auth) |
| "The web service or version is invalid for the requested operation" | Unversioned service - drop version segment + attribute |
| "Invalid ID 'type'. Valid Types: WID" | That reference type is WID-only; go discover the WID (Step 4) |
| "Invalid instance X for External_Field.for_Business_Object" | You passed a FIELD WID where a BO/class WID belongs |
| "Element Content 'X' is required" | Schema-required element empty/missing (e.g. Text Constant needs non-empty Text) |
| "does not meet the restrictions defined for this field" | Field not usable in that slot for that class (e.g. delivered fields column-restricted on some classes while calc fields pass) |
| HTTP 200 + `Exceptions_Response_Data` "Critical ... functional constraints" | **The object WAS created but is BROKEN at runtime** - treat as failure: fix or mark Do_Not_Use, and runtime-verify before shipping |
| Runtime 500 "No method implementation for method ..." on report run | A calc field the definition accepted cannot evaluate (e.g. self-referencing lookup) - remove/replace it |
| "Label for Prompt XML Alias is required, if the report is Web Service Enabled" | Every prompt on a WS-enabled report needs `Label_for_Prompt_XML_Alias` - even a suppressed one (`Do_Not_Prompt_at_Runtime=1`). Give the built-in date/effective prompt a throwaway alias |
| Global "Workday ID"/"Name" field rejected on a target-primary data source | Those global fields aren't members of every DS's field set - check `allReportFields` for the DS (via `allDataSources`); use a calc field on the primary BO to emit the WID as text instead |
| "does not meet the restrictions" on EVERY column of a target-primary report, even a plain text field | The columns are missing `<wd:Business_Object_Reference>` = the DS's PRIMARY BO WID. Report 1/2 columns always carry it; a column with only `External_Field_Reference` and no BO ref is rejected. Add the primary-BO WID to every column |
| "Invalid instance <Name>--IS for External_Field.for_Business_Object" when creating a calc field | The `External_Field_Reference` (the BO the calc field lives on) is the WRONG object - the error names the object you passed. Similar-sounding objects are a trap ("Abstract Student Award" != "Award Abstract"); confirm the primary BO WID via the DS's `primaryBusinessObject` before authoring |
| RaaS run 500 "The task submitted is not authorized" (report BUILT fine) | The RUN identity lacks the data source's reporting DOMAIN. NB: RaaS run via a wdcli/gateway bearer executes as the CALLING account, not the report's ISU owner - so a wdcli test checks YOUR access, not the ISU's; the production engine calls as the ISU. Grant the domain to the right identity, re-run |
| Domain granted to the ISSG (shows in the group export) but never enforces, and re-activating doesn't help | Check whether the domain has ANY active holder tenant-wide: WQL `securityGroups.domainsGrantedToSecurityGroup` across all groups. If a domain sits on ZERO groups' ACTIVE policy tenant-wide, its FUNCTIONAL AREA is disabled (e.g. Grants Management off => "Reports: Award"/"Manager Reports: Grants" can't compile). The grant is saved but un-activatable - it's a tenant module toggle, NOT a security mistake. Do not keep re-granting; enable the functional area (or accept it's a customer-tenant-only report). Same pattern for any module-gated domain |

## Worked example + reusable client

The author workspace's `advanced-load-analysis/` holds the complete verified example:
`report_metadata_client.py` (bearer mint, envelope wrapper, gated `put` verb with write
journal, corporate-TLS handling), the Put bodies for calc fields + reports, readback
verifiers, and the template column->element maps decoded from Workday's advanced-load
spreadsheets. To regenerate a client for another service, copy that script and change
SERVICE/host constants - or fold the service name into a CLI arg. (Tenant-specific
values stay OUT of this skill per the vendor-neutral rule.)

Cross-refs: tenant-ops.md (WRITE GATE, Path B runbook, implementer-surface discovery,
report/calc-field load facts), wd-auth (auth modes + troubleshooting),
report-writer-admin.md (report/calc-field concepts), data-loading-and-retrieval.md
(when EIB/REST beats this surface).

## Report authoring recipes added 2026-09-04 (Corporate Card Requests replacement - all build-verified)

- **RaaS URL parms need a PROMPT + a FILTER, not just a prompt.** A `Tenanted_Report_Parameter_Options_Data`
  block alone reads back fine but RaaS rejects `?<alias>!WID=` with 'Invalid Parm'. The parm only registers
  when a filter CONSUMES the prompt: a `Tenanted_Report_Definition_Top_Level_Filter_Data` >
  `Tenanted_Report_Filter_Data` > `Condition_Item_Data` with operator `in the selection list`, entry option
  `Prompt the user for the value`, and `Ignore_When_No_Target_Value=1` (so the unfiltered call still works).
  ELEMENT ORDER IS ENFORCED: the top-level filter wrapper goes AFTER the parameter block (bare
  `Tenanted_Report_Filter_Data` under the definition data = 'Invalid Subelement').
- **Column shapes decoded from serialized definitions:** primary-class column = BO ref CLASS WID + field WID;
  RELATED-object column ('hop', e.g. vendorWID) = BO ref = the REFERENCE FIELD's WID on the primary class +
  field = what to show on the target (workdayID for a `<ref>WID` alias); calc-field column = BO ref class WID +
  External_Field_Reference by `Calculated_Field_ID` (so report bodies never need the CF WIDs).
- **Chained calc fields load clean:** Put the ESI with an explicit `Calculated_Field_Reference_ID`, then LRVs
  whose `Related_Business_Object_Field` carries `Calculated_Field_Class_Name` + that reference id +
  `Business_Object_Reference` = the class WID. Framework class-report fields (Business Processes, Any is True,
  event Status/Awaiting Persons/Business Process, global Workday ID) share WIDs ACROSS Extend BO classes -
  clones only swap the class BO and names.
- **Class BO WID lookup without the UI:** `classReportFields` WQL - `SELECT businessObject,
  relatedBusinessObject FROM classReportFields WHERE workdayID IN ('<any field WID of the class>')`.
  Valid SELECT fields: `workdayID`, `field`, `businessObject`, `relatedBusinessObject`. `type` is NOT
  a valid field (400 "Enter a valid report field. This field is invalid: type" - verified 2026-09-08).
- **Tenant-portable RaaS endpoints:** the report OWNER segment is tenant config - read it from an app
  attribute with a shipped default: `(attrstore.raasReportOwner ?: 'ISU_<app>') + '/<Report_Name>'`.
