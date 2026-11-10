# Workday Studio - named reusable patterns

Companion to [studio.md](studio.md) (anatomy/vocabulary - read that first). Each pattern
below: the problem it solves, the component chain, and the gotchas visible in real code.
All were extracted from production/demo Studio projects plus the community SMTP
framework; client specifics are genericized.

## 1. Submit-many-EIBs / launch-integration-from-integration

**Problem:** conversion loads need one EIB run per file; launching dozens by hand is untenable.

**Chain:** `workday-in` -> read launch params -> `vm://wcc/GetEventDocuments` ->
`validate-exp` `da.size() > 0` -> `doc-iterator` (FILENAME_ASCENDING) -> route on a
"Compressed/Zipped?" param -> `unzip-splitter` per entry -> per file: `base64-encode` ->
`cc:write` wrapping `<File><Filename>@{util.currentFilename}</Filename><FileContent>...` ->
XSLT builds `wd:Launch_EIB_Request` (target EIB's `Integration_System_ID` from a
class-report-field launch param restricted to "Integration System (EIB only)") ->
`wrap-soap` -> `workday-out-soap application="Integrations"` -> parse
`Launch_EIB_Response/.../Integration_Event_Reference/ID[@wd:type='WID']` and log each run's WID.

**Gotchas:** the target EIB must accept an attached Base64 file in `Launch_EIB_Request`;
filename sort drives processing order. Same technique launches full integrations via
`Launch_Integration_Event_Request` (see pattern 3), passing the target's launch parameters
by `Launch_Parameter_Name` - the names must match the target's `cloud:param` names EXACTLY.

## 2. Boomerang (Workday -> transform -> back into Workday / Prism)

**Problem:** compute something Workday can't (e.g. burden calculations on journals) using
Workday's own data, then load results back - often into a Prism table.

**Chain:** `workday-in` declaring 2+ DIS services (e.g. rules + transactions) -> DIS delivers
report output as event documents labeled **`Data - Partial`** -> `GetEventDocuments` ->
`doc-iterator labels="Data - Partial"` -> per-file streaming XSLT scrub (DIS fields are in
namespace `tdf: urn:com.workday/tdf`; build XSLT 3.0 keyed maps) -> open/close aggregator ->
merge XSLT -> calculation XSLT -> store outputs as retained documents -> load leg: the
delivered **`vm://wcc/PrismAnalytics`** component (or `Put_Import_Process` for WWS loads -
see pattern 8 for the import framework).

**Prism load leg (`vm://wcc/PrismAnalytics`):** the delivered component does the entire
auth + bucket-create + upload + complete sequence internally. Your assembly supplies three
things: the CSV payload as the current message; a JSON create-table schema doc written to a
variable (fields with ordinal/precision/scale/`type.id="Schema_Field_Type=Text|Numeric"`,
`parseOptions` delimiter/enclosure/headerLinesToIgnore,
`schemaVersion.id="Schema_Version=1.0"`); and props via `cc:set` -
`wd.prism.component.schema.varname`, `.table.name`, `.operation`, `.api.hostname`,
`.client.id`, `.client.secret`, `.refresh.token`. Operation universe (per Workday Admin
Guide (Reporting & Analytics), Jul 2026): **Insert** (= Append), **Truncate and Insert**
(= Replace), **Delete**, **Update**, **Upsert** - delete/update/upsert require an operation
key, i.e. an external-ID field on the target table (WPA_LoadID / WPA_RowID usable for
delete/update only). Component prop SPELLING is build-verified only for 'Replace'; and the
bucket REST load path this component wraps only **inserts** - update/upsert/delete run
through Data Change Tasks.

From INT125/NAS_INT125_Journals_to_Burden_Prism_Table_Boomerang.clar, trimmed (the
`p_attribute.*` props are loaded at init via `intsys.getAttribute('Prism Table Name')` etc.):

```xml
<cloud:service-reference name="DIS_INT125_Processed_Journals"/>
<cloud:service-reference name="DIS_INT125_Journals_to_Burden"/>
<!-- ... -->
<cc:route id="DocRoute">
  <cc:doc-iterator labels="Data - Partial" sort-by="FILENAME_ASCENDING"/>
  <cc:sub-route name="AutoRoute" routes-to="LogProcessingFile"/>
</cc:route>
<!-- ... scrub -> aggregate -> merge -> xml-to-csv into vars['csv'], schema JSON into vars['schema'] ... -->
<cc:local-out id="PrismAnalytics" endpoint="vm://wcc/PrismAnalytics">
  <cc:set name="wd.prism.component.schema.varname" value="'schema'"/>
  <cc:set name="wd.prism.component.csv.input.varname" value="'csv'"/>
  <cc:set name="wd.prism.component.table.name" value="props['p_attribute.table_name']"/>
  <cc:set name="wd.prism.component.table.display.name" value="props['p_attribute.table_display_name']"/>
  <cc:set name="wd.prism.component.operation" value="props['p_attribute.api_operation']"/>
  <cc:set name="wd.prism.component.api.hostname" value="props['p_attribute.api_hostname']"/>
  <cc:set name="wd.prism.component.client.id" value="props['p_attribute.api_client_id']"/>
  <cc:set name="wd.prism.component.client.secret" value="props['p_attribute.api_client_secret']"/>
  <cc:set name="wd.prism.component.refresh.token" value="props['p_attribute.api_refresh_token']"/>
</cc:local-out>
```

**Prism config surface:** keep the connection in an attribute service - Prism Table
Name/Display Name/Description, API Hostname, API Client ID/Secret/Refresh Token (secrets as
`display-as-password`), API Operation. These map 1:1 onto the `wd.prism.component.*` props -
FEED THEM FROM `intsys.getAttribute('...')`, never hardcode. (The Workday sample this pattern
comes from hardcodes real-looking credentials in the assembly - that's the anti-pattern, not
the template - and ships with NO error handling; wrap the load leg per the house framework
in [studio.md](studio.md#error-handling--audit-framework-the-house-standard).)

The declaration + consumption mechanics (secrets as `display-as-password`, values read via
`intsys.getAttribute`) - from the community D9_WorkerDocLoad project (exploded source), trimmed:

```xml
<cloud:attribute-map-service name="Worker Doc Load Attributes">
  <cloud:attribute name="SFTP Endpoint">
    <cloud:type><cloud:simple-type>text</cloud:simple-type></cloud:type>
    <cloud:display-option>required-for-launch</cloud:display-option>
  </cloud:attribute>
  <cloud:attribute name="SFTP Password">
    <cloud:type><cloud:simple-type>text</cloud:simple-type></cloud:type>
    <cloud:display-option>display-as-password</cloud:display-option>
    <cloud:display-option>required-for-launch</cloud:display-option>
  </cloud:attribute>
</cloud:attribute-map-service>
<!-- consumed at runtime - never hardcode credentials in the assembly -->
<cc:sftp-out id="GetDocFileFromSFTP" method="GET" binary-file="true"
    endpoint="@{intsys.getAttribute('SFTP Endpoint')}"
    username="@{intsys.getAttribute('SFTP Username')}"
    password="@{intsys.getAttribute('SFTP Password')}"/>
```

## 3. Chained multi-Studio design with launch-parameter handoff

**Problem:** one assembly doing heavy extract + batch + per-batch compare hits memory/runtime
walls. Split into a chain where each link has one job and its own runtime budget.

**The 3-link shape** (extract -> batch/dispatch -> per-batch process):
- **Link A** does the expensive extraction/merge ONCE -> stores the merged file and labels it
  via `vm://wcc/PutIntegrationMessage` (`is.document.variable.name`, `is.document.labels='MergedData'`,
  `is.document.deliverable='false'`). Tenant wiring: Link A's Integration BP has an event
  step that triggers Link B.
- **Link B** reads `doc-iterator labels="MergedData"` from the *triggering* event
  (`ie.event.wid = lp.getIntegrationEventWID()`; a `Debug Event WID` text param overrides for
  replay) -> streaming batch XSLT (`xsl:iterate` splitting into `<Batch>` elements; batch size
  a launch param, e.g. 1000 records) -> `xml-stream-splitter xpath="BatchedData/Batch"` ->
  re-aggregate N batches per group (e.g. 10) -> store each group labeled `Batch{n}` -> XSLT
  builds `Launch_Integration_Event_Request` for Link C (its ISID is a launch param), passing
  **Batch Document Label** and **Batch Number** as launch parameters -> `workday-out-soap`.
  One Link C run is launched per batch group.
- **Link C** launch params (`Batch Document Label`, `Integration Batch Number`) ->
  `doc-iterator labels="@{props['p_settings.batch_doc_label']}"` picks up exactly its
  document -> split -> process/compare -> store results.

**Gotchas:** keep batch counters in props and trigger the "submit group" flush with an MVEL
guard like `(group_counter == batches_per_int) || (batch_counter == total_batches)`;
document the whole chain in EACH manifest ("This is 2 of 3 Studio Integrations used to...").

The label handoff + flush guard - from INT_KSS_DEMO_Organizations_and_Related_Worktag_Changes_Studio
_v2a/_v2b.clar, trimmed (`<Project>` = the v2b project name):

```xml
<!-- Link A: store + label the merged file for the next link -->
<cc:local-out id="PutIntegrationMessage" endpoint="vm://wcc/PutIntegrationMessage">
  <cc:set name="is.document.variable.name" value="'MergedFile'"/>
  <cc:set name="is.document.labels" value="'DISMergedData'"/>
  <cc:set name="is.document.deliverable" value="'false'"/>
</cc:local-out>
<!-- Link B: read it, label each batch group, flush a Link C launch when the group fills -->
<cc:doc-iterator labels="DISMergedData" sort-by="FILENAME_ASCENDING"/>
<cc:local-out id="LabelBatchFile" endpoint="vm://wcc/PutIntegrationMessage">
  <cc:set name="is.document.variable.name" value="'BatchFile'"/>
  <cc:set name="is.document.labels" value="props['p_batch.document_label']"/>
  <cc:set name="is.document.deliverable" value="'false'"/>
</cc:local-out>
<cc:local-out id="CallSubSubmitBatch" store-message="none"
    execute-when="(props['p_batch.aggregator_batch_counter'] == props['p_settings.batches_per_int']) || (props['p_batch.batch_counter'] ==  props['p_batch.total_batches'])"
    endpoint="vm://<Project>/SubSubmitBatch"/>
```

The launch-request XSLT that hands Link C its batch by label - from the same v2b CLAR
(lib/xslt, trimmed to one of nine `Integration_Launch_Parameter_Data` blocks):

```xml
<wd:Launch_Integration_Event_Request xmlns:wd="urn:com.workday/bsvc" wd:Debug_Mode="false">
  <wd:Integration_System_Reference>
    <wd:ID wd:type="Integration_System_ID">
      <xsl:value-of select="$p_settings.compare_integration_id"/>
    </wd:ID>
  </wd:Integration_System_Reference>
  <wd:Integration_Launch_Parameter_Data>
    <wd:Launch_Parameter_Reference>
      <wd:ID wd:parent_type="Integration_System_ID" wd:type="Launch_Parameter_Name">
        <xsl:attribute name="wd:parent_id" select="$p_settings.compare_integration_id"/>
        <xsl:text>Batch Document Label</xsl:text>
      </wd:ID>
    </wd:Launch_Parameter_Reference>
    <wd:Launch_Parameter_Value_Data>
      <wd:Text><xsl:value-of select="$p_batch.document_label"/></wd:Text>
    </wd:Launch_Parameter_Value_Data>
  </wd:Integration_Launch_Parameter_Data>
</wd:Launch_Integration_Event_Request>
```

## 4. DIS two-point-in-time compare (change detection without an audit source)

**Problem:** detect adds/changes/deletes between two dates for objects with no delivered
audit trail (e.g. orgs + related worktags).

**How:** one custom report (copy of a delivered report, RaaS-enabled, **Effective Date and
Entry Moment exposed as report prompts**) registered as the data source of FOUR DIS services
- Current vs Previous x each subject - so the same report is extracted at two moments in a
single launch. Streaming scrub keys each dataset into XSLT 3.0 maps; merge pairs
Previous/Current per ReferenceID; compare assigns a `ChangeFlag` of **N/C/D/A** using
`snapshot()`/`copy-of()` for streaming-safe deep comparison. Document the required tenant
artifacts (custom reports, the 4 DIS services, document-builder workbooks) in the manifest.

From INT_KSS_DEMO_Organizations_and_Related_Worktag_Changes_Studio_v2a.clar, trimmed
(the 4 DIS declarations, then the merge XSLT pairing Previous/Current per ReferenceID):

```xml
<cloud:data-initialization-service name="DIS_INT_KSS_DEMO_Orgs_and_Related_Wktgs_v2_Previous_Worktags"/>
<cloud:data-initialization-service name="DIS_INT_KSS_DEMO_Orgs_and_Related_Wktgs_v2_Current_Worktags"/>
<cloud:data-initialization-service name="DIS_INT_KSS_DEMO_Orgs_and_Related_Wktgs_v2_Previous_Orgs"/>
<cloud:data-initialization-service name="DIS_INT_KSS_DEMO_Orgs_and_Related_Wktgs_v2_Current_Orgs"/>
```

```xml
<!-- inside a streaming xsl:iterate over Record (lib/xslt/MergeData.xsl) -->
<xsl:variable name="current-entry" select="snapshot()"/>
<xsl:variable name="key" select="$current-entry/ReferenceID" as="xs:string"/>
<xsl:next-iteration>
  <xsl:with-param name="RecordData" select="map:put($RecordData, $RecordKey, $current-entry)"/>
</xsl:next-iteration>
<!-- ... and on output, each pair is emitted side-by-side for the compare leg: -->
<xsl:copy-of select="$GetRecordData/PreviousValue"/>
<xsl:copy-of select="$GetRecordData/CurrentValue"/>
```

## 5. Shared-library CLAR (public local-in endpoints)

**Problem:** the same capability (e.g. templated email) needed by many integrations without
copy-paste.

**How:** a library project whose subroutines are `cc:local-in access="public"` - callable
from ANY deployed CLAR via `local-out endpoint="vm://<LibProject>/<EndpointName>"` with a
typed parameter contract (`cc:parameter` defaults/required/documentation, `cc:out-parameter`
returns). The community SMTP framework is the reference implementation:
- Rich API surface (To Worker/Email, Template, CC/BCC, attachment variable/type/filename, UseCloudLog, AbortOnError, out-param `SMTPErrors` so callers decide what's fatal).
- **Config lives on a host integration system** as attributes + maps (Credentials map with `display-as-password`, per-user alias/from/server maps, per-integration override-recipient map). The lib bootstraps by calling `Get_Integration_Systems` on its own host ISID, converts config to CSV via XSLT, and caches it in **mtables** guarded by `execute-when="!mtable.containsKey('...')"` (load once per run).
- Templates = Workday **Message Templates** fetched via `Get_Message_Template` (`application="Workday_Connect"`); a Java step substitutes worker tags (tag-name -> Get_Workers XPath map) into subject/body; worker email resolved Home->Work fallback.
- Send via paired `cc:email-out` components gated `execute-when="props['SMTP-SSL']"` / `props['SMTP-TLS']`.

**Gotcha (genericize on adoption):** community copies may carry the original institution's
hardcoded impl-tenant override recipient / package names - sweep for client literals before
deploying (check Java sources, not just the assembly).

The mechanism (public local-in with typed contract, and a caller) - from
INT_Studio_Multi_Document_Transform_Outbound_Collection.clar (mdtUtilities assembly - the
flagship instance, see pattern 7), trimmed:

```xml
<cc:local-in access="public" icon="icons/error-24.png" id="ReportError"
    routes-to="PutErrorMessage" tooltip="Reports an error and aborts processing">
  <cc:parameter name="ErrorMessage" type="string"/>
  <cc:parameter name="TargetIDs" required="false"/>
  <cc:parameter default="'WID'" name="TargetIDType" required="false"/>
  <cc:parameter name="DetailMessage" required="false"/>
</cc:local-in>
<!-- a caller - works from ANY deployed CLAR on the tenant -->
<cc:local-out id="reportMessageCloudLogError" store-message="none"
    endpoint="vm://mdtUtilities/ReportError">
  <cc:set name="ErrorMessage"
      value="'An error occurred saving XSLT messages to the cloud-log: ' + context.errorMessage"/>
</cc:local-out>
```

## 6. File -> Base64 outbound (minimal utility shape)

`workday-in` + `cloud:retrieval-service` -> `doc-iterator variable-name="incoming.zip"` ->
`copy` var->message (`application/zip`) -> `all-strategy` route into parallel branches:
(1) `unzip-splitter` -> per entry `base64-encode` + `cc:write`
`<filename>@{util.currentFilename}</filename><file>...</file>` -> collater aggregator with
`<root>` header/footer -> `store` as `encoded.xml`; (2) same but CSV lines -> `encoded.csv`.
Demonstrates retrieval service, unzip fan-out, write-template, collater fan-in, and
`no-split-message-error="true"` for empty archives. ~90 lines total - a good starter skeleton.

## 7. Multi-document transform wrapper (mdtUtilities library CLAR)

The heavy lifting lives in the community **mdtUtilities library CLAR** - a companion project
that must be DEPLOYED on the same tenant. Its endpoints are `cc:local-in access="public"`
(the flagship instance of pattern 5's shared-library mechanism), NOT Workday-runtime
built-ins. Your wrapper assembly is just: one big `cc:eval` Init reading ~11 launch params
(Transform Integration System [required], document-tag filters, Attach To Event, Sequence
Generator, Store Input Data) -> `validate-exp` on required params -> `local-out` calls into
the library.

**Library endpoint surface** (`vm://mdtUtilities/...`):
- `GetIntegrationConfiguration` - params: transformIntegrationSystem WID +
  configurationIntegrationSystems WID/List. Fetches the tenant-supplied XSLT from an
  Integration System's Integration Attachment Service; pulls + prunes the config IS(s) via
  paged `Get_Integration_Systems`.
- `ProcessFiles` - builds the composite MDT input doc (launch params, sibling events, IS
  config, worktag mappings via paged `Get_Integration_Worktag_Mappings`, lookup-IS
  attachments, specified + event documents), runs the tenant-supplied XSLT, routes output
  (`mdto:Files` / plain-XML / non-XML / empty), applies ETV/XTT, stores/attaches outputs +
  cloud logs.
- `ReportError` - ErrorMessage / TargetIDs / TargetIDType (default 'WID') / DetailMessage ->
  PIM ERROR then `context.setAbort(true)`. **ReportError ALWAYS aborts the run** - never
  call it for warnings.
- Plus ~17 more public reusables worth borrowing individually: `CloudLogMessages`,
  `GetAttachmentFromIS`, `GetWorktags`, `StoreOutput`, `TransformMDTInput`, `ClassicDT`
  (with `cc:out-parameter etv.messages`), etc.

**Key mechanism - dynamic stylesheet execution:** `cc:xslt-plus url="mctx:vars/<varname>"`
runs an XSLT held in a runtime VARIABLE; `props.mdt_inputURL = 'mctx:vars/mdt_inputDocument'`
lets the tenant XSLT re-read the input via `doc()`. This is config-driven transform without
redeploying the CLAR - the XSLT is ATTACHED to an Integration System (Integration Attachment
Service) and fetched at runtime. Transform-side namespaces + `mdto:` vocabulary:
[xslt3.md](xslt3.md).

From INT_Studio_Multi_Document_Transform_Outbound_Collection.clar (mdtUtilities
`TransformMDTInput` chain), trimmed:

```xml
<cc:async-mediation id="TransformNonClassic" routes-to="doProcessDirectOutput">
  <cc:steps>
    <cc:eval id="Eval">
      <cc:expression>// Set the URL which the XSLT can use in order to make multiple passes over the input document
props.mdt_inputURL = 'mctx:vars/mdt_inputDocument'</cc:expression>
      <cc:expression>// Clear the input message in order to free up a little memory and disk space
message.setRootPartAsText('')</cc:expression>
    </cc:eval>
    <cc:validate-exp id="ValidateExp">
      <cc:expression failure-message="No stylesheet has been loaded into the variable 'xslt'">context.getVariables().isVariable( 'xslt' )</cc:expression>
    </cc:validate-exp>
    <cc:xslt-plus description="Transforming input with @{vars['xslt'].fileName}"
        id="XsltPlus" input="variable" input-variable="mdt_inputDocument" url="mctx:vars/xslt"/>
  </cc:steps>
  <cc:send-error id="eh" routes-to="GetErrorDetails"/>
</cc:async-mediation>
```

**Wrapper idioms:** read the raw `wd.launchparameters` SOAP variable by XPath when the `lp`
helper can't reach a value (e.g. a Sequence Generator WID); dynamic default
`props.eventWID = (event_list != empty) ? event_list.get(0) : lp.integrationEventWID`.

**Adoption caveats:** sweep stale package names when adopting (one stale
`com.workday.cc.util.ObjectIterator` reference exists in the community copy); the library
bundles CommonCustomJava as a jar under `ws/WSAR-INF/lib` - the jar-drop reuse mechanism.

## 8. High-volume WWS import framework (production inbound, the full lifecycle)

**Problem:** load a large flat file into Workday via web services with validate mode, error
harvesting, and an audit file back to the source system.

**Import run** (`StartHere`): retrieval -> custom Java `RemoveBOM` -> `csv-to-xml`
(delimiter-configurable, e.g. `separator="|"`) -> scrub XSLT -> build `Import_*` requests ->
`wrap-soap` (+ `X-Validate-Only` header when Validate Mode) -> `workday-out-soap` -> capture
`Put_Import_Process_Response/Import_Process_Reference/ID` -> **store the full request payload
as a labeled doc (`importdata`) with run metadata baked into the aggregator footer**
(inputfile, WID, validate flag) - the aggregate document itself is the state handoff.
Guard: `file_count == 1` - a second input file raises a named error.

**Audit run** (a SECOND integration system in the same project, launched after the import BP
completes): `doc-iterator labels="importdata" variable-name="v_import_data"` -> extract run
metadata from the stored doc -> `Get_Import_Processes` -> check
`xpathB('//wd:Has_Messages[text()!="0"]')` -> pull errors via **`vm://wcc/PagedGet`**
`Get_Import_Process_Messages` -> merge imports+errors -> re-query final state -> write a
fixed-width audit file via `xslt-plus` + `cc:xtt`, filename from a
**sequence-generator-service**.

**PagedGet config props worth knowing:** `is.paged.get.request.current.page.xpath`,
`...response.current.page/total.pages/total.results.xpath`, `aggregate.xpath` +
`aggregate.header/footer`, `application`, `version`, and **`is.paged.get.parallel = true`**
for parallel page pulls on big reads.

From Import_Payroll_Input_Integration.clar (one project hosting BOTH entry points -
`StartHere` import + `AuditLog` audit run; labels there are `iws.refs`/`audit.data`), trimmed:

```xml
<!-- audit run: pull errors only when the import reported messages -
     props['iws.ref.has_messages'] = parts[0].xpathB('//wd:Has_Messages[text()!="0"]') -->
<cc:local-out id="IterateErrorPages" routes-response-to="BuildAuditLogWithErrors" endpoint="vm://wcc/PagedGet">
  <cc:set name="is.paged.get.request.current.page.xpath" value="'/env:Envelope/env:Body/*/wd:Response_Filter/wd:Page'"/>
  <cc:set name="is.paged.get.response.current.page.xpath" value="'/env:Envelope/env:Body/*/wd:Response_Results/wd:Page'"/>
  <cc:set name="is.paged.get.response.total.pages.xpath" value="'/env:Envelope/env:Body/*/wd:Response_Results/wd:Total_Pages'"/>
  <cc:set name="is.paged.get.response.total.results.xpath" value="'/env:Envelope/env:Body/*/wd:Response_Results/wd:Total_Results'"/>
  <cc:set name="is.paged.get.application" value="'Integrations'"/>
  <cc:set name="is.paged.get.version" value="'v26.0'"/>
  <cc:set name="is.paged.get.aggregate.xpath" value="'/env:Envelope/env:Body/wd:Get_Import_Process_Messages_Response/wd:Response_Data/wd:Import_Process_Message/wd:Import_Process_Message_Data'"/>
  <cc:set name="is.paged.get.aggregate.header" value="'&lt;errors>'"/>
  <cc:set name="is.paged.get.aggregate.footer" value="'&lt;/errors>'"/>
</cc:local-out>
```

## 9. Streaming XSLT 3.0 idioms (any big-file work)

> Full transform-side treatment - merge strategies, accumulators, iterate, fork, XTT/ETV,
> and the worked-example library - lives in [xslt3.md](xslt3.md). Highlights repeated here
> because they shape the ASSEMBLY design:

- `<xsl:mode streamable="yes" on-no-match="shallow-skip"/>` + `xsl:iterate` with
  `map(xs:string, item())` accumulator params + `<xsl:on-completion>` emitting the whole
  restructured document.
- `copy-of()` / `snapshot()` wherever random access into the current node's subtree is
  needed (deep compares, multi-field reads) - the streaming-safe escape hatches.
- Batch-by-count inside the iterate (counter param, emit `<Batch>` wrapper each N).
- Declare `streamable="no"` explicitly on small request-builder transforms - intent legible.
- Assembly-side pairing: `cc:xslt-plus` passes ALL message props as same-named
  `<xsl:param>`s - set `p_settings.batch_size_limit` in MVEL, declare the param in the XSLT.

Most of the idioms in one place - from
INT_KSS_DEMO_Organizations_and_Related_Worktag_Changes_Studio_v2b.clar
(lib/xslt/BatchData.xsl), trimmed:

```xml
<xsl:mode streamable="yes" on-no-match="shallow-skip" />
<!-- assembly-side prop arrives as a same-named param -->
<xsl:param name="p_settings.batch_size_limit"/>
<xsl:variable name="BatchSizeLimit" as="xs:float" select="$p_settings.batch_size_limit"/>

<xsl:template match="MergedData">
  <xsl:iterate select="Record">
    <xsl:param name="ValuesData" as="map(xs:string, item())" select="map{}"/>
    <xsl:param name="Batches" as="map(xs:float, xs:float)" select="map{}"/>
    <xsl:param name="BatchCount" as="xs:float" select="1"/>
    <xsl:on-completion>
      <BatchedData>
        <BatchCount><xsl:value-of select="$BatchCount"/></BatchCount>
        <!-- ...emit each accumulated <Batch> from the maps here... -->
      </BatchedData>
    </xsl:on-completion>
    <xsl:variable name="current-entry" select="snapshot()"/>
    <xsl:next-iteration>
      <xsl:with-param name="ValuesData"
          select="map:put($ValuesData, $current-entry/ReferenceID, $current-entry/Value)"/>
    </xsl:next-iteration>
  </xsl:iterate>
</xsl:template>
```

## 10. Validate / Debug / Replay modes (bake into every build)

Three launch params that pay for themselves on day one (full block in
[studio.md](studio.md#the-standard-launch-parameter-block-canonize-on-every-build)):
- **Validate Mode** -> `X-Validate-Only` header on WWS calls AND gate the `cc:store` of
  intermediate documents (Aggregated/Merged/Batched/Compare data) so normal runs stay lean
  but validate runs leave a full evidence trail.
- **Debug Mode** -> verbose `cc:log` dumps between transform stages.
- **Debug Event WID** -> re-point `GetEventDocuments` at a past event to REPLAY a run without
  re-launching the upstream chain - the difference between minutes and hours when testing
  link B/C of a chained design.

All three wired - from INT_KSS_DEMO_Organizations_and_Related_Worktag_Changes_Studio_v2b.clar, trimmed:

```xml
<!-- replay: Debug Event WID overrides the live event -->
<cc:local-out id="GetEventDocuments" endpoint="vm://wcc/GetEventDocuments">
  <cc:set name="ie.event.wid" value="props['p_settings.debug_event_wid'] ?  lp.getSimpleData('Debug Event WID') : {lp.isSet() ? lp.getIntegrationEventWID() : null}"/>
</cc:local-out>
<!-- Validate Mode: header ON, WWS call, header OFF (strip before any logging/storage call) -->
<cc:set-headers execute-when="props['p_settings.validate_mode']" id="ValidationOn">
  <cc:remove-headers/>
  <cc:add-headers><cc:add-header name="X-Validate-Only" value="1"/></cc:add-headers>
</cc:set-headers>
<cc:workday-out-soap id="WorkdayOutSoap" application="Integrations"
    version="@{props['p_settings.web_service_version']}"/>
<cc:set-headers id="ValidationOff">
  <cc:remove-headers><cc:remove-header name="X-Validate-Only"/></cc:remove-headers>
  <cc:add-headers/>
</cc:set-headers>
<!-- validate runs leave an evidence trail; normal runs stay lean -->
<cc:store execute-when="props['p_settings.validate_mode']" id="Store" input="variable"
    input-variable="BatchedData" expiresIn="@{props['p_settings.document_retention']}"
    title="Batched_Data.xml"/>
```

## 11. PDF merge (custom step + bundled jar)

**Problem:** many event attachments -> one deliverable PDF (consolidated statements/packets).

**Chain:** `xml-stream-splitter` per doc -> XSLT extracts the base64 -> `cc:base64-decode
output-mimetype="application/pdf"` -> MVEL stashes each part into indexed variables
(`vars['pdfDoc-' # props.docCount] = [ parts[0].source, 'application/pdf' ]`) ->
`cc:custom ref="PdfMerge"` walks `pdfDoc-1..n` via `ctx.getVariables()` and merges with
PDFBox `PDFMergerUtility` using `MemoryUsageSetting.setupMixed(1GB)` (large-file-safe) ->
`cc:store`. The PDFBox jar is bundled in `ws/WSAR-INF/lib` (custom-Java authoring pattern:
[studio.md](studio.md#custom-java-steps--authoring-pattern)).

**Bonus idiom:** `cc:sync-mediation` as an init/teardown BRACKET - request-steps initialize
the counters, response-steps null out the variables after the merge.

Donor: `demoPdfMerge` - also the reference aunit test example (studio.md registry).
