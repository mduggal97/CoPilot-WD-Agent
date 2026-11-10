# Workday Studio - project anatomy, assembly vocabulary, and when to use it

Workday Studio is the Eclipse-based IDE for building complex tenant integrations
("mediation assemblies") deployed as CLARs. This reference covers the anatomy and
vocabulary; the named reusable designs live in [studio-patterns.md](studio-patterns.md).
Everything here was verified against 13 real production/demo Studio projects (firm-authored
conversion tooling, boomerang/Prism builds, a chained DIS-compare demo set, a production
university-ERP inbound, and the community SMTP framework).

## When to choose Studio (vs EIB / Core Connector / Extend O4I)

Studio earns its complexity when the integration needs any of:

1. **Launching/orchestrating other integrations** (`Launch_EIB` / `Launch_Integration_Event` from inside a run).
2. **DIS multi-extract** - several Data Initialization Services in one launch, especially the *same report at two moments in time* for change detection.
3. **High-volume streaming** - XSLT 3.0 streaming over arbitrarily large files, explicit batching/aggregation, parallel `PagedGet`.
4. ~~**The WWS high-volume import framework**~~ - **NO LONGER Studio-only (refuted 2026-08-07).** `Put_Import_Process` submit + post-run error harvesting (`Get_Import_Process_Messages`) + an audit file back is now doable natively in O4I - canonical `supplierInvoicesInbound` (`INT_Supplier_Invoices_Orch_Inbound.orchestration` + `INT_Check_Import_Result_Orch.orchestration`) runs the full submit -> poll -> harvest -> `ImportResults.csv` loop (see wd-extend-dev orchestration.md). This is no longer a reason to pick Studio; weigh it on the OTHER factors (streaming, Java, Excel READ, PGP/SMTP - below).
5. **Custom Java steps** - BOM/encoding handling, typed collection lookups, regex templating (things MVEL can't do cleanly).
6. **Direct SMTP or arbitrary HTTP endpoints** with custom auth headers.
7. **Reusable cross-integration libraries** - public `local-in` endpoints callable from other deployed CLARs.

EIB suffices for single-document/single-transform/single-endpoint. Core Connector when a
delivered connector template matches. **Extend O4I** overlaps with (1) and simple (3)/(6)
today, but still lacks equivalents for DIS, streaming XSLT over multi-GB files, custom Java,
and CLAR-level shared libraries - and O4I has hard runtime limits (see orchestration.md in the wd-extend-dev skill).
Many production Studio builds also simply predate O4I; don't rewrite a working Studio
integration in O4I without a driver.

## Project anatomy

A Studio project is an **Eclipse project** (CapeClear + Workday builders in `.project`).

| File | Role |
|---|---|
| `WorkdayManifest.xml` | CLAR manifest: `<wm:clar version="3.0"/>` + title / description / author / timestamp. The description is the ONLY free-text doc that travels with the deployed archive - use it as a runbook (see "manifest-as-runbook" below). |
| `ws/WSAR-INF/assembly.xml` | **The entire integration.** A Spring `<beans>` document; components are `cc:*` elements (`http://www.capeclear.com/assembly/10`), tenant-side declarations are `cloud:*` (`urn:com.workday/esb/cloud/10.0`). `<cc:assembly version="...">` records the Studio release used. Custom Java steps register at the bottom as plain Spring beans (`scope="prototype"`). |
| `ws/WSAR-INF/assembly-diagram.xml` | Canvas layout only - never edit or diff it for logic. |
| `ws/WSAR-INF/**/*.xsl` | XSLT 3.0 transforms, referenced by relative URL from `cc:xslt-plus`. Convention: put them in `lib/xslt/`. |
| `src/main/java` | Custom Java compiled into the CLAR. |
| `ws/WSAR-INF/lib/Supporting Workday Configuration/*.xlsx` | Strong practice: ship the supporting tenant config exports (custom reports, BP wiring workbooks) WITH the code. |

**Deploy model / what a CLAR is:** the builders package `ws/` + compiled classes into a
CLoud ARchive uploaded from Studio (right-click project -> "Deploy to Workday" - the current
menu label; older docs say "Deploy to Cloud"). On the tenant, each `cc:workday-in`
materializes as one **Integration System** with ID of the form
`Project/Project/EntryPointName` (e.g. `.../StartHere`). One project can host multiple
integration systems (e.g. a `StartHere` import run + an `AuditResults` post-run). All launch
parameters, integration attributes/maps, and services (DIS, retrieval, listener,
sequence-generator) are declared inside `cc:workday-in` and provisioned on the tenant
integration system at deploy time.

Deployed-CLAR facts (per Workday Admin Guide (Workday Studio), Jul 2026): CLARs are
**binary (no Java source) and stored encrypted** in the Cloud Repository; the Deployment
preference **"Include source code in deployed CLAR"** enables Import Source from Cloud
Explorer, and the tenant-side **Require Source Code** checkbox (Edit Tenant Setup -
Integrations) can enforce it - both reinforce the Git-as-source-of-record gate. Official
runtime limits: integrations are **killed at 2 hours** (course-manual nuance, crawled
2026-08-25: 2 hours is the DESIGN target; runs "may run for up to four hours in production if
resources available" - treat 4 h as conditional, not guaranteed); output files max **1 GB compressed
each / 3 GB total**; custom Java cannot touch the file system, Java system properties, or
spawn threads.

Built-in tenant services are called as local endpoints under `vm://wcc/...` - the four
workhorses: `PutIntegrationMessage` (event messages), `GetEventDocuments`, `PagedGet`, and
`PutIntegrationEvent` (the PROGRESS BAR mechanism: from a loop,
`cc:local-out endpoint="vm://wcc/PutIntegrationEvent" clone-request="true"` with
`cc:set is.percent.complete = props['percent']`; THROTTLE updates
(`execute-when="props['loop'] % 5 == 0"`); percent =
`(int)java.lang.Math.floor(100/(count/loop))` - drop into any long loop so Process Monitor
shows movement). Also delivered: `vm://wcc/ParallelSubroutine` (parallel fan-out; props
`parallel.processing.worker.endpoint`, `.aggregation.endpoint`,
`.splitter = spring.getBean('ParallelBlockSplitter')`, `.worker.count`, `worker.timeout`,
`timeout`) and `vm://wcc/PrismAnalytics` (full Prism table load -
[studio-patterns.md](studio-patterns.md) section 2).

**Redeploying over a live Integration System - semantics.**
(a) **Tenant config survives redeploy - official** (per Workday Admin Guide (Workday
Studio), Jul 2026): Studio integration *design* (the CLAR) and tenant integration
*configuration* are deliberately separate layers - redeploy replaces the deployed code but
does not touch tenant-side security (launch/run-as), notifications, parameter/attribute/map
values, or schedules (attribute/map values are configured tenant-side via View Integration
System -> related action -> Integration Generic Service > Configure Integration Attributes /
Maps). Exporting/screenshotting tenant config before a redeploy is now hygiene, not a
required gate. **Counter-caution:** enumeration definitions are **tenant-global** - if a
deployed assembly declares an enumeration whose Type Name matches an existing tenant
definition, the deploy **overwrites** it; redeploys CAN clobber that one class of tenant
object.
(b) **Rename semantics - (!) still unverified:** the guide confirms only that deploy
"automatically registers a new integration system for every workday-in transport"
(registration keyed to the workday-in identity) - consistent with our stance but not a
direct answer. **Never rename a live project or entry point** - the
`Project/Project/EntryPointName` ID structure makes a rename a new integration system by
construction; treat it as a new deployment plus a migration of every reference (schedules,
BP event-step wiring, `Launch_Integration_Event` callers).

## Assembly vocabulary (components you'll actually meet)

**Entry / exit**
- `cc:workday-in` - tenant-launched entry point; wraps `cc:integration-system` with the `cloud:*` declarations.
- `cc:local-in` / `cc:local-out` - the *subroutine mechanism*. `local-in` defines a named entry with a typed parameter contract (`cc:parameter` with `default`/`required`/`documentation`, `cc:out-parameter` for returns); `local-out` calls it via `endpoint="vm://<ProjectName>/<SubName>"` passing values with `cc:set`. **`access="public"` on a local-in makes it callable from OTHER deployed CLARs** - the shared-library mechanism. Contract extras: `cc:parameter validation="<MVEL>"` (shape assertions) and `type=`; local-in `icon=`/`tooltip=`; `cc:local-out unset-properties="true"` (clean prop slate) / `propagate-abort="true"`.
- `cc:workday-out-soap` - WWS call; `application` selects the service (Payroll, Integrations, Human_Resources, Workday_Connect...), `version` usually `@{props[...]}`-driven.
- `cc:workday-out-rest` / `cc:http-out` / `cc:rest-binding` / `cc:http-basic-auth` - REST/HTTP out.
- `cc:sftp-out method="get"/"mget"` - sftp-out doubles as a READER with `routes-response-to` (single/multi-file pull).
- `cc:email-out` - direct SMTP with host/port/ssl/starttls/cc/bcc/reply-to, custom headers, oauth-config.

**Mediation containers**
- `cc:async-mediation` - one-way step container; key attrs `routes-to`, `execute-steps-when` (conditional skip), and `handle-downstream-errors="true"` + nested `cc:send-error routes-to="..."` (local catch).
- `cc:sync-mediation` - request/response pair (`cc:request-steps` / `cc:response-steps`) when you need post-processing after the downstream chain returns.
- Top-level `cc:send-error` = global error handler (`rethrow-error="false"` to swallow).

**Steps**
- `cc:eval` - MVEL expressions (the workhorse - see MVEL section).
- `cc:xslt-plus` - Saxon XSLT 3.0. **All message props are implicitly available as `<xsl:param>` of the same name.** `input="variable" input-variable="v_x"` transforms a stored variable instead of the live message. `messages-property="<propname>"` captures `xsl:message` output into a props List (`cc:etv`/`cc:xtt message-property=` do the same for validation messages). Dynamic stylesheet: `url="mctx:vars/<varname>"` runs an XSLT held in a runtime variable - the MDT config-driven-transform mechanism ([studio-patterns.md](studio-patterns.md) section 7).
- `cc:copy` - message<->variable moves (`input-variable`/`output-variable`, `output-mimetype`); `input-xpath=` + `stream-xpath="true"` copies a subtree straight out of the stream. The ubiquitous idiom `copy->store->copy back` snapshots the stream around a `cc:store`.
- `cc:write` - compose a message from literal text + `@{MVEL}` + `<cc:message-content/>` (wrap Base64 in XML; hand-write small SOAP requests).
- `cc:store` - persist message/variable as an integration-event document: `expiresIn="P180D"`, `title`, `createDocumentReference`, `output-variable` for the doc reference.
- `cc:log` (server log) vs `cc:cloud-log` (tenant-visible consolidated log; `level`, `message-details`, `output-file-type="HTML"` or `"XLSX"`, custom `cc:log-column`s; accumulate into a variable then `cc:store` for the end-of-run file).
- `cc:validate-exp` - assert MVEL with `failure-message`/`error-number` (e.g. input file present: `da.size() > 0`).
- `cc:set-headers` - transport headers; the recurring one is **`X-Validate-Only: 1`** for WWS validate-only mode (and REMOVE it before any real logging/storage call). `cc:add-headers`/`cc:remove-headers` for surgical changes.
- `cc:wrap-soap`, `cc:base64-encode`/`-decode`, `cc:character-conversion`, `cc:zip`.
- `cc:custom ref="beanId"` - run a registered Java bean.
- `cc:csv-to-xml` (supports `separator="|"` etc.) / `cc:xml-to-csv`; `cc:xtt` - text transform via a text schema (fixed-width audit files).
- `cc:textschema style="text2xml"` - inbound delimited-text->XML via a CapeClear TextSchema XSD (`ts:rootElement`, `ts:separator="\|"`, per-field `ts:format` regex, nested multi-value cells via `ts:occurrenceSeparator` + `ts:quoted="optional"`, `ts:endTag`, `ts:eofStrip`, `ts:numberFormat`). The schema URL can be prop-dynamic (`url="xsd/@{props[...]}_TextSchema_....xsd"`) - one assembly, N layouts. The inbound counterpart to XTT; richer than `cc:csv-to-xml` (handles delimited-within-delimited).
- `cc:text-excel style="text2excel"` - text/CSV -> real .xlsx (audit files as spreadsheets).
- `cc:retrieve` - fetch a repository document directly by collection/entry (split a Document_ID at the first `/`).
- `cc:mtable-builder` + `cc:csv-mtable-reader`/`cc:json-mtable-reader` - in-memory indexed lookup table (config/credentials caching, row-loop drivers).

**Routing / fan-out / fan-in**
- `cc:route` strategies: `cc:doc-iterator` (iterate event documents; `labels="..."`, `sort-by="FILENAME_ASCENDING"`, `variable-name` to load into a var), `cc:mvel-strategy`/`cc:choose-route` (branch), `cc:all-strategy` (fan to all sub-routes), `cc:xpath-strategy`.
- `cc:splitter` strategies: `cc:xml-stream-splitter` (streaming split on an XPath), `cc:unzip-splitter` (per zip entry), `cc:mtable-splitter` (per table row -> `props['row']`), `cc:xpath-splitter`. `no-split-message-error="false"` tolerates zero matches.
- `cc:aggregator` strategies: `cc:size-batch-strategy` (`batch-size="-1"` = collect all), `cc:message-content-collater` (`header-text`/`footer-text`/`separator` build one well-formed doc from fragments; `cc:xml-message-content-collater` is the XML-aware sibling). **The open/close idiom:** `collate-when="!props['p_close.X']" force-batch-when="props['p_close.X']" force-batch-on-last-message="false"` - fragments accumulate across calls until a final call with the close flag flushes the batch.
- `cc:loop-strategy` - polling loops (e.g. import-status wait).

**`cloud:` declarations (inside `cc:integration-system`)**
- `cloud:param` - launch parameter: `simple-type` (boolean/text/number/datetime), `enumeration-type`, or `class-report-field` (tenant object picker, `singular` true/false); `cloud:default` (including dynamic defaults like the *Current Moment (DateTime)* report field); `cloud:launch-option` `required`/`do-not-show`.
- `cloud:attribute-map-service` - integration **attributes** (typed; `display-option`: `required-for-launch`, `display-as-password`) and **maps** (key->value config tables edited on the tenant). This is the config store; secrets go in `display-as-password` attributes. An attribute's Name must be **unique across ALL integration systems in the tenant** (per Workday Admin Guide (Workday Studio), Jul 2026).
- `cloud:data-initialization-service` - DIS declaration (or `cloud:service-reference` to a DIS defined tenant-side).
- `cloud:retrieval-service` (inbound file into `vars['wd.retrieve.variable']`), `cloud:listener-service` (REST-triggered runs), `cloud:sequence-generator-service` + `cloud:sequencer` (generated filenames), `cloud:report-service` (RaaS binding), `cloud:delivery-service` (outbound delivery - do encryption HERE, not with a Studio sftp-out/encrypt step, for better performance).

## MVEL quick reference (real observed idioms)

Context objects: `props` (message properties), `vars`, `parts[n]` (message parts), `lp`
(launch params), `intsys`, `mtable`, `context`, `util`, `da` (document accessor), `message`.
`@{ ... }` embeds MVEL inline in component attributes and `cc:write`/collater text.

```java
// String concat - both '#' and '+' work
props['p_settings.logfilename'] = props['p_attribute.integration_name'] # '_Cloud_Log_'
    # props['p_settings.current_moment'].toString().substring(0,19) # '.html';

// XPath over a part, with namespace bindings; xpathB() = boolean; xstream() = streaming read
props['p_batch.integration_event'] = parts[0].xpath(
  "/env:Envelope/env:Body/wd:Launch_EIB_Response/wd:Integration_Event/wd:Integration_Event_Reference/wd:ID[@wd:type='WID']",
  'env=http://schemas.xmlsoap.org/soap/envelope/ wd=urn:com.workday/bsvc');

// Launch params
(boolean) lp.getSimpleData('Validate Mode');
lp.getReferenceData('EIB Integration_System_ID','Integration_System_ID');  // 2nd arg = ID type ('WID' common)
lp.getReferenceDataList('Orgs','Organization_Reference_ID');               // multi-select
lp.isSet(); lp.getIntegrationEventWID();

// Integration attributes
intsys.getAttribute('Prism Table Name');
intsys.getAttributeReferenceData('Web Service Version','Version');
intsys.getName();                       // 'Project/Project/StartHere' - substring to first '/' for the short name

// Conditional defaulting in a component attribute (debug replay pattern)
"ie.event.wid" value="props['p_debug'] ? lp.getSimpleData('Debug Event WID')
                                       : {lp.isSet() ? lp.getIntegrationEventWID() : null}"

// Runtime context + files + tables
context.getErrorMessage(); context.errorComponentId; context.setAbort(true);
vars['wd.retrieve.variable'].fileName; util.currentFilename.toString();
mtable.get('SMTPCredentials').findFirst('Username', props['Username'])[2];
message.addAttachment(vars.getVariable(props['Attachment Variable']), props['Attachment Type']);

// Templating directives inside cc:write text - hand-built SOAP over a collection, no XSLT
@foreach{props['wids']} <wd:ID wd:type="WID">@{item}</wd:ID> @end{}
@if{props['p_flag']} ... @else{} ... @end{}

// More helpers
spring.getBean('ParallelBlockSplitter');
util.cleanString(s); util.listToCommaDelimString(l); util.setCurrentFilename(f);
parts[0].isXml(); xstreamB(...);                       // boolean streaming read
vars['pdfDoc-1'] = [ parts[0].source, 'application/pdf' ];  // pair-assignment: source + mimetype
foreach ( v : props['p_count'] ) { ... }                // iterate N times

// Saxon error forensics on transform failure (community util)
SaxonUtils.getErrorDetails(null, context.exception.cause);
```

**When MVEL isn't enough, write a Java step** - the community libs justify it explicitly:
typed collection handling (MVEL can't infer `findFirst` return types), regex templating,
static lookup tables, byte-level work (BOM removal, character encoding). Authoring pattern
and the community utility catalog below.

## Custom Java steps - authoring pattern

A mediation step is a POJO - no base class:
- `@Component(name=..., type=mediation, scope="prototype", smallIconPath=..., largeIconPath=...)`
  plus one `@ComponentMethod` whose SIGNATURE the framework matches:
  `process(InputStream, OutputStream)` (body in/out), `process(MediationContext)`
  (metadata-only), or several named methods selected per use via
  `cc:custom method-name="processText|processXml"`.
- Context access: `MediationTube.getCurrentMediationContext()` -> `ctx.getProperty(...)`,
  `ctx.getVariables().getVariable(name)` (returns a StreamSource), `ctx.addDisposable(...)`
  (auto-cleanup at end of run).
- Registration: a plain Spring bean at the bottom of assembly.xml WITH `<property>`
  injection for config; consumed via `cc:custom ref=` / `cc:custom-splitter ref=` /
  `spring.getBean(...)`.
- Custom splitters implement `MediationMessageSplitter` (`setMediationMessage` /
  `getNextMessage` returning null to end / `setConfig`) and optionally
  `MediationContextSplitter` (`hasMore`/`splitIntoContext`) to run under
  `vm://wcc/ParallelSubroutine`.
- Large-data plumbing: `FileBackedManagedData` (disk-spilled parts - `setLongLived(true)`
  while iterating, register with `addDisposable`), temp dirs via
  `FileUtils.createTempDirectory(context, ...)`, filename from the Content-Disposition header.
  Third-party jars go in `ws/WSAR-INF/lib` (PDFBox in the PDF-merge pattern -
  [studio-patterns.md](studio-patterns.md) section 11).

Community utility catalog (reusable as-is with attribution): `RemoveBOM`,
`ParallelBlockSplitter` (StAX
block splitter, classic/parallel dual-mode), `DirectorySplitter` (iterate a temp dir's files
as messages), `ChangeCharacterEncoding` (BOM add/remove + transcode, StAX-aware),
`BOMUtils`/`CharacterUtils`, `FileUtils` (auto-disposed temp files/dirs), `IOUtils`,
`ObjectIterator` (shim because MVEL 1.3 can't call generic-returning methods - the concrete
"when MVEL isn't enough" case), `SharedHelper.attributesToProperties(context)` (all
integration attributes -> `attr_*` props in one line).

## The standard launch-parameter block (canonize on every build)

Reused across every well-built project reviewed - start each new Studio integration with:

| Param | Type | Default | Purpose |
|---|---|---|---|
| Validate Mode | boolean | false | Adds `X-Validate-Only` to WWS calls; also gates storing intermediate debug documents |
| Debug Mode | boolean | false | Verbose `cc:log` dumps between transform stages |
| Debug Event WID | text | - | Re-point `GetEventDocuments` at an OLD event to replay without re-launching the upstream chain - essential for chained designs |
| Web Service Version | text | `vNN.0` | Pin the WWS version per environment |
| Document Retention in Days | number | 180 | Build `'P'+n+'D'` ISO period for every `cc:store expiresIn` |
| As of Entry DateTime | datetime | *Current Moment* report field | Point-in-time consistency across extracts |

## Error handling / audit framework (the house standard)

- **Global catch:** top-level `cc:send-error` -> strip `X-Validate-Only` -> `vm://wcc/PutIntegrationMessage` severity CRITICAL with `context.getErrorMessage()`.
- **Local catches:** every functional `async-mediation` sets `handle-downstream-errors="true"` and routes its `send-error` to a dedicated, named `Log<Step>Error` - every failure becomes a human-readable integration message.
- **SubLogMessage subroutine** (`local-in`: Severity, Summary, Detail, SendToIntEventMessages, Reference): maps severities to PutIntegrationMessage levels, increments `p_log_*_count` props, writes `cc:cloud-log` HTML, optionally PIM.
- **End-of-run rollup:** store the accumulated cloud-log variable as `<IntName>_Cloud_Log_<timestamp>.html`, then a chained severity ladder (`PIM-Info -> PIM-Warning -> PIM-Error -> PIM-Critical`, each `execute-when="props['p_log_X_count'] > 0"`) so the event ends with one summary message per severity present.
- **Logging-about-logging:** log subroutines carry their own error handlers (with `is.message.storage.enabled=false`) so a log failure can't recurse.
- Library variant: adjust severity by an `AbortOnError` parameter (`ERROR`->`CRITICAL` when aborting), `context.setAbort(true)` to kill the run, and return an errors out-parameter so callers decide.

## Naming & versioning conventions

- Project: `INT###_<Source>_<Subject>_Studio_<Inbound|Outbound>` for client builds; `INT_<Subject>_Studio` for utilities; pattern tags in the name where they aid discovery (`_Boomerang`); `INT_CNV_` prefix for conversion tooling. (Full integration naming standard: [integration-naming.md](integration-naming.md).)
- Chained designs: `_v2a/_v2b/_v2c` letters = position in the chain; `_original_copy` = frozen baseline kept beside the working copy; whole-project copy (`_v2`) for major rework.
- Tenant artifacts: typed prefixes documented in the manifest - `CR ` custom reports, `DIS_` services, `<INT>_Integration_Atrb` attribute services, `<INT>_Sequence_Generator_Service`.
- XSLT: `INT###_<Verb><Noun>.xsl` with a recurring stage vocabulary: **Scrub / Merge / Create / Transform / Trim / Batch / Split / Compare / Insert**.
- **Manifest-as-runbook (house standard):** Summary ("This is 1 of 3 Studio Integrations used to..."), Setup Notes (custom-report creation incl. RaaS + date prompts, BP event-step wiring, launch-parameter pointing), then explicit lists of Studio Integrations / Custom Reports / DIS Services / Document Builders, plus author + email.
- **Anti-patterns to catch in review:** manifest left as `Sample/Sample Description` or a stale copy from the project it was cloned from; test data files committed at project root; source-control metadata folders (`$tf/`) committed inside the project.

## Where to find working Studio examples (your local library)

Donor Studio projects live in YOUR local workspace, not in this skill. Point Claude at your library (the Engagement input below), then re-rank by recency; the table further down shows the KINDS of donor projects to look for.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Your local Studio library path** - the workspace root holding your Studio projects (example - your paths differ; a typical layout spans a working workspace, a prior-year workspace, and an archive). **Not all copies are good examples - prefer the most recently updated version of anything** (older siblings are usually superseded drafts). Caveat on timestamps: copying a project resets mtimes and opening in Studio can touch `assembly-diagram.xml`, so treat recency as a strong prior, not proof - confirm the newest copy actually has the pattern. Re-rank any time: walk for `.project` dirs, take the max mtime of `*.xml/*.xsl/*.java` excluding `build/.settings`.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

The table below is an ILLUSTRATIVE example library (one contributor's local projects - your workspace will differ). Treat the names as shapes of the KINDS of donor projects to look for, not files you will have:

| Pattern you need | Best example project(s) |
|---|---|
| **Real-time REST API outbound** (bank/vendor API, request/response) | `INT555_<Bank>_Credit_Card_Application_Process_API_Studio_Outbound` (2024-12), `INT553_<Bank>_Account_Update_API` (2024-10), `INT554_<Bank>_Credit_Card_Limits_API` (2024-07) |
| Assembly component teaching sampler | `ITM_INTXXX_Web_Service_Examples` (2024-04), `INT_Studio_StarterKit` |
| Shared-library CLAR + SMTP email framework | `INT_SMTPMessageLib` + `INT_SMTPMessage_List_Studio` (2024-05) |
| Full vendor-suite family (bidirectional, async budget check, PO/receipt/invoice) | `INT191`-`INT200` <ProcurementVendor> projects (2023-2024) |
| Outbound demographics / person hub | `INT155_Person_Hub_Worker_Demographics_Outbound` (2024-04) |
| Prenote / settlement banking flows | `INT060_<Bank>_Prenote_Status_Update_Studio` (2024-03), `INT003_Update_Settlement_Date` (2023-10) |
| Remittance email w/ generated XML | `INT540_Remittance_Emails_for_ACH_and_Wires_Studio_Outbound` (2024-01) |
| Production inbound + WWS import framework | `INT165_<SIS>_Workstudy_Studio_Inbound` (2024-01; successor of INT041), `INT086_<BenefitsVendor>_Enrollments_Studio_Inbound` (2023-12) |
| Boomerang (compare / Prism load) | `INT558_SCM_Supplier_And_Worker_Comparison_Boomerang` (2024-01), `INT126_Burdening_Journals_Boomerang_v2` (2022 - prefer `_v2` over base) |
| Multi-EIB conversion launcher | `INT_CNV_Submit_Multiple_EIBs_Studio` (2023-10) |
| Chained DIS two-moment compare | a `..._v2a/v2b/v2c` demo set (the non-suffixed project is the v1 all-in-one) |
| Reference-ID extraction utility | `INT_Studio_Reference_IDs_Outbound` (2023-06) |
| Streaming student-import conversion | `Convert_Student_Import_Template_Streaming` (2022-03) |
| MDT endpoints - the deployable `mdtUtilities` library CLAR ([studio-patterns.md](studio-patterns.md) section 7) | `mdtUtilities` (2022-08; also carries 15+ aunit tests) + `INT_Studio_Multi_Document_Transform_Outbound` wrapper |
| Community custom-Java steps | `CommonCustomJava` (2022-08) |
| PDF merge (custom step + bundled PDFBox jar) - also THE aunit example | `demoPdfMerge` |
| Delivered Prism-load component demo (`vm://wcc/PrismAnalytics`) | `PrismAnalytics` - (!) hardcodes real-looking credentials (anti-pattern: feed from attributes) and has NO error handling |
| Progress-bar mechanism (`vm://wcc/PutIntegrationEvent`) | `Test_Integration_Progress_Bar` |

On another machine: regenerate the ranking against your own workspace, or ask whoever owns
the shared library to share the specific donor project.

## Setup prerequisites

Workday Studio itself is a separate install (Eclipse-based; download via Workday Community,
requires a Studio-enabled tenant + Community account). Deploy ("Deploy to Workday") and
tenant auth are interactive - the developer signs in; never automated. There is no CLI
equivalent of wdcli for Studio. Without Studio you can still do real work - everything
readable lives in `ws/WSAR-INF/assembly.xml` + the XSLTs, plain XML/text, reviewable and
editable in any editor - but building, deploying, and running tests require the IDE.

More setup facts (per Workday Admin Guide (Workday Studio), Jul 2026):

- **Deploy/launch permissions (SoD):** deploy requires **Modify in Integration Build**
  (+ the Integration Configure domain); launching from Studio requires **Put in Integration
  Event, Integration Build, or Integration Debug**; deploying a CLAR containing a
  **delivery or retrieval service** additionally requires Put in Business Process
  Administration, Manage: Business Process Definitions, or iLoad Web Services (a documented
  "deploy denied" error otherwise). Studio's Test Connection shows Deploy / Launch /
  Business Process groups - you need at least one.
- **Release management:** only 1 valid Studio release at a time; an out-of-date Studio can
  still develop locally but is **blocked from connecting to Sandbox/Production**; never
  update the Eclipse platform independently.
- **MFA users cannot basic-auth from Studio** - register an API client (Auth Code + PKCE,
  Bearer, HTTPS redirect URI; scopes must include Implementation, Integration, System,
  Tenant Non-Configurable + Include Workday Owned Scope; do **NOT** check Enforce 60 Minute
  Access Token Expiry - it's irreversible and kills the Studio connection after an hour).
  The Enforce-60-Minute / irreversible checkbox fact is owned by
  `wd-auth/references/oauth-setup-guide.md`; the PKCE + scope details above are the
  Studio-specific slice.
- Studio never persists credentials to the workspace after the session ends. From Cloud
  Explorer you can assign the ISU (Assign Integration System User; requires the Integration
  Security domain) and **Copy Launch URL** - a third-party REST launch URL for a deployed
  integration.

**Testing assemblies (aunit).** Assemblies ARE unit-testable inside Studio: subclass
`com.workday.aunit.AssemblyTestCase` with `@AssemblyTest(project=...)` +
`@UnitTest(startComponent=...)`; `@AtComponent(id=..., step=...)` handlers return
`new StandardAction(Type.mock)` to MOCK tenant-touching components (e.g. canned
`Get_Integration_Systems` responses served from `ws/test/*.xml` files);
`@AssertAfterCompletion` asserts on `getMediationContext()`. The `mdtUtilities` donor
carries 15+ real tests; `demoPdfMerge` is the compact example.

## Official course-manual facts (official-docs - Workday Education course manuals, crawled 2026-08-25; spot-verify load-bearing numbers in-tenant)

- **Kill limits (full official set):** run terminated if it generates >3 GB of files total, any single file >1 GB, or uses >12 GB memory; XPath cannot process XML over 1,000,000 characters; custom reports max 2 GB; delivery/retrieval services max 5,000 integration documents per run. Variables hold "the first 100 MB or so" of a file in cloud runtime memory (rest spills to ESB disk - the "or so" hedge is the manual's own; not a hard boundary).
- **Logging caps:** server log 48 MB; log line 128 KB; View Log File truncates lines to 32 KB; PutIntegrationMessage max 500 messages per event. PIM severity -> event status: INFO -> Completed; WARNING -> Completed with warnings; ERROR -> Completed with errors (processing continues); CRITICAL -> Failed (processing stops).
- **Blobitory (cc:store):** 1 GB per stored message (compressed); 3 GB cumulative (compressed); Expires In default P7D. Create Document Reference default true auto-calls PIM with is.document.deliverable=false; an EXPLICIT PIM call defaults deliverable=true.
- **The 6 Studio security domains:** Integration Build (deploy), Integration Configure (configure services), Integration Debug, Integration Event (launch/view events), Integration Reports, Integration Subscriptions.
- **Report-service alias anti-hardcoding:** declare a report-service on the workday-in Services tab, reference it via `@{intsys.reportService.getExtrapath('AliasName')}` in the workday-out-rest Extra Path, then map alias -> real report in the tenant via integration system Related Actions > **Configure Integration Reports**. Hardcoded extra paths break on report rename/owner change and force redeploys.
- **doc-iterator internals:** uses the `da` object to select each event file matching the labels (if any); copies each file into a variable whose DEFAULT name is `wd.retrieve.variable`; optional asc/desc sort by file name; iterates documents uploaded by retrieval services via the Integration Process Event BP.
- **Debugger settings:** Session connect retries = 400; Wait for startup max iterations = 600; the debugger will NOT launch if the workspace path contains a space; breakpoints live in the local workspace and do not affect normal launches.
- **PagedGet:** studio-patterns.md pattern 8 already carries the working config fragment; the manual's full property catalog adds `is.paged.get.page.zero` (default false), `is.paged.get.store.requests` (default false), `is.paged.get.overall.timeout.seconds` / `.page.timeout.seconds`, `.parallel.aggregation.endpoint`, and the outputs `is.paged.get.last.page` / `.current.page` / `.total.pages` / `.total.results`. A single WWS page = 1-999 records; pin `As_Of_Entry_DateTime` in the Response_Filter so the dataset does not shift while paging; parallel mode is "an almost free performance boost" unless data order matters.
- **Import-vs-Submit reconciliation:** the manual quantifies the house rule (see wd-extend-dev orchestration.md "Import_ vs Submit_/Put_"): submit-type operations for "up to 200 records (sometimes more, depending on the operation)"; import operations "reserved for high volumes (thousands of objects)". Consistent with the file-vs-transaction rationale; adds the ~200-record number.

### BIRT / Studio Report Designer (doc-sourced)

- The feeding report must be Advanced type + web-service enabled, max output 2 GB; EVERY column, prompt, and related BO needs a Column Heading Override XML Alias. The data source takes two inputs: the report's XSD + a sample XML file.
- Deploy (right-click .rptdesign > Deploy > Deploy to Workday) auto-creates the tenant **business form layout** object. Wizard settings: Description, Active (default on), **Document Expiration** (days until the generated PDF expires), Apply per row, Default (only enabled when a design already exists).
- **Apply per row**: Workday generates one PDF per data row then MERGES them into a single PDF - page numbering RESETS per row; removes the need for table containers in the layout.
- Translation `.properties` resource files are NOT carried by the Studio deploy wizard - upload them manually via **Manage Layouts**. Local-XSD data sources must Select Custom Report at deploy time.
- Multi-instance / related-BO data needs a "Workday Secondary Report Data Set" bound to the primary via the **PrimaryRowNumber** parameter (the primary dataset auto-includes a Row_Number column); two-levels-deep multi-instance binds via expression `row_outer_rownum` + SecondaryRowNumber. 1:1 related-BO fields fold INTO the primary dataset automatically - no secondary dataset needed.

## Auditing a Studio estate for O4I conversion (verified method, 2026-08-06)

Ran against a real 80-project workspace. The method matters more than the numbers.

### Search traps that invalidate a naive inventory

- **Match BOTH namespace prefixes: `(?:wd|bsvc):`.** The Workday namespace
  `urn:com.workday/bsvc` is bound to `wd:` in some projects and `bsvc:` in others. Grepping only
  `<wd:` silently skipped an entire second payroll-input integration whose XSL had been generated
  from the WSDL - the single richest schema artifact in the estate. This one omission produced a
  wrong element map that had to be redone.
- **Walk `Archived_Workspaces/` and any `workspace<year>/` folders.** The live
  `studio_workspace` is not the whole estate. A first pass found 2 payroll-input integrations; the
  full sweep found **8**, several of them the deduction-inbound feeds that are the best
  productization candidates.
- **Studio logic lives in `ws/WSAR-INF/assembly.xml`** plus `lib/xslt/*.xsl`. There are no `.grf`
  files - that is CloverDX, not Studio. A `.grf` count returns 0 and looks like an empty estate.
- **XSL files are shared across forked projects.** Summing per-project XSL line counts massively
  overstates the real rewrite burden. Hash the files: on one 7-project family, 8,688 naive lines
  deduped to 2,766 distinct - a 68% overstatement.

### Rank by REUSE, not by porting cost

Score conversion effort however you like, but do not let it drive the order. The cheapest project
to port is often a single-client one-off that teaches nothing reusable. Sort by how often the
pattern recurs across clients (payroll input, accounting journals), then use effort as a tiebreaker.

### Roll up cross-project dependencies before quoting anything

Studio projects call each other with `vm://<project>/<route>` endpoints. A shell that looks like 27
components can pull in a 4,400-line Java utility. Build the dependency graph, compute the
transitive closure, and report **own vs. total** effort - one apparently trivial project scored 1.4
alone and 520 with its closure. Exclude `vm://wcc/...` (Workday-delivered services).

### Detect forks before scoping duplicates

Compare projects by their `cc:*` component-type multiset, not by name. On the audited estate this
exposed a 7-project family sharing **61 of 64-74 node ids** - the same firm-built
boomerang/DIS framework (`InitiateIntegration` / `IntiateLaunchParameters` / `InitiateAttributes` /
`InitiateLogging` / `ValidateExp` / `GlobalErrorHandler` / `PIM-Critical|Error|Warning|Info` /
`Store-Logs` / `DataAggregator` / `ScrubDISFile` / `MergeData`). Each project's distinct business
logic was only 6-10 nodes. Port the framework ONCE as an O4I suborchestration library and the rest
become thin variants - a very different plan from seven independent conversions.

### O4I gap list (what has no equivalent)

Drives most of the real effort. No **XSLT node** (the big one - rewrite as `CreateTextTemplate` with
`{{#each}}`/`{{#if}}`), no **Java runtime**, no **Excel READER** (O4I CAN WRITE `.xlsx` and ASSEMBLE
a zip via `ZipArchiveFoldValue`/OOXML-part substitution - it's the READ/unzip side that's missing;
see orchestration.md), no **PGP**, no **SMTP**, no **xmldiff**, no **JMS**. The WWS high-volume
**import** framework is NO LONGER a gap (see "When to choose Studio" item 4 above). Mapping tables
(`mtable`/`xtt`/`etv`) become tenant-side Integration Maps via `intsys.mapLookup` - and those **throw
on an unmatched key unless a Default Value is set**, which turns one bad code into a whole-run
failure. **Canonical mitigation (confirmed 2026-08-07):** use the **`intsys.mapLookupWithDefault(...)`**
variant (canonical `orchestrateForIntegrationsSampler/.../ProcessOneFile.suborchestration`) so an
unmatched key returns the default instead of failing the run; still make setting the map Default Value
a deployment-checklist item.

`cc:parameter` in an assembly is a SUB-ROUTE parameter, not a launch parameter. The tenant-facing
config surface is `cloud:param` (Launch Parameters) and `cloud:attribute-map-service` /
`cloud:attribute` (Integration Attributes) - that is what to inventory when judging how
template-ready an integration already is.

## Studio Builder and Integration Runtime 2 (IR2) (doc-sourced 2026-09-04 - work in progress, NOT YET GA)

Workday announced a browser-based Studio IDE alternative and a new underlying runtime at DevCon 2026.
The version shown at DevCon is explicitly described as "a work in progress and not fully representative
of the finished product" - treat all facts here as preview/directional until GA.

Source: Workday/2026-DevCon-Hackathon repo docs (official Workday DevCon materials, July 2026).

### Studio Builder

A lightweight, browser-based tool on the Workday Developer Site for MAINTAINING existing Studio
integrations (including those with custom Java code). Key differences from classic Eclipse Studio:

- No local install - runs entirely in the browser via the Workday Developer Site
- Centralizes developer tenant access, security, and governance behind a single login (alongside
  Extend apps)
- Deploy, manage, and migrate Studio integrations from the same Developer Site session
- The DevCon preview shows maintenance/migration capabilities; net-new Studio development still
  requires the Eclipse IDE until Studio Builder GA

### Integration Runtime 2 (IR2)

The new runtime that Studio Builder runs on. Key improvements over the original Integration Runtime
(IR1):

- **FedRAMP-compliant** security level
- **Up to 40% faster** than IR1
- **Classpath separation** - package only the required library versions (reduces conflict risk on
  custom Java steps)
- **App Hub interoperability** - seamless interop with App Hub and new Workday services
- **IR1 -> IR2 migration**: the majority of existing IR1 custom integrations can be dynamically
  migrated with NO customer input required; Studio Builder handles the minority that need manual
  adjustment

### Design implications for in-flight Studio builds

- Classic Eclipse Studio + IR1 remain the current build path; Studio Builder / IR2 are not GA.
- When Workday announces an IR1 deprecation timeline (none announced as of Sep 2026), in-flight and
  live Studio integrations will need an IR2 migration check. The migration posture is:
  (most integrations) automatic / no customer input -> (minority) Studio Builder-assisted adjustment.
- Watch the GA-status tracker in release-impact.md (wd-extend-dev) - a row for Studio Builder / IR2
  is seeded there. Re-verify status each R1/R2.
- Custom Java jars may need classpath review at migration (IR2's classpath separation may surface
  conflicts that IR1 masked).
