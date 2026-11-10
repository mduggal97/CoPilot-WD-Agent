# O4I node catalog - config keys and minimal JSON shapes

Companion to [orchestration.md](orchestration.md), which owns the BEHAVIORAL notes (limits, auth,
patterns, gotchas). This file owns the SHAPES: for each node type, the config keys its `_value`
takes and a minimal JSON skeleton, extracted from real source. Per orchestration.md, the visual
Orchestration Builder remains the source of truth for NET-NEW flow layout - use these shapes to
edit, review, and generate variations of existing flows, and run the structural linter before upload.

Corpus censused 2026-08-25: 206 flow files - 173 catalog files (Workday App Catalog samples under
`_reference/app-catalog/` plus `gq-bo-demo`, `supplier-invoice-template`, `o4i-example`,
`bpTriggeredOrchestration`) and 33 first-party delivered flows (billonly-v2, ap-statement-recon,
payroll-input-inbound, User Access Provisioning v2). Provenance per node:
**sample-verified** = seen only in catalog samples; **build-verified** = also present in the
first-party delivered flows. flowVersions span 2.2.0-3.3.0; prefer 3.x shapes for new edits.

Key legend: `req` = present in EVERY corpus instance of the node; `opt` = present in a subset
(usually flowVersion drift - older Builder versions omit newer keys). When editing an existing
file, keep whatever key set that file already has.

## The typed-wrapper envelope

Real files are SINGLE-LINE JSON. Every value is `{"_type": <TypeName>, "_value": <payload>}`.
All examples below are pretty-printed and use this shorthand for the envelopes:

- `ID(x)`   = `{"_type":"Identifier","_value":"x"}` - node names, param names
- `S(x)` / `B(x)` / `L(n)` = String / Boolean / Long envelopes
- `EXPR(T,src)` = `{"_type":["Expr","T"],"_value":{"type":{"_type":"Type","_value":"T"},"source":S(src),"isAuto":B(false)}}`
  (the expression-language payload; `isAuto` present in 3.x flows, absent in some 2.x)
- `OPT(null)` = `{"_type":["Opt",<T>],"_value":null}` - an omitted optional
- `LIST(T,[...])` = `{"_type":["List",T],"_value":[...]}`
- `NOTES` = `LIST(Note,[{key:S("description"),value:S("...")}])` - every node carries it

Full-fidelity example - one `Assignment` inside a CreateValues (this is what the shorthand hides):

```json
{"_type":"Assignment","_value":{
  "param":{"_type":"Parameter","_value":{"name":{"_type":"Identifier","_value":"status"},
    "type":{"_type":"Type","_value":"String"},"default":{"_type":["Opt","Any"],"_value":null}}},
  "expr":{"_type":["Expr","String"],"_value":{"type":{"_type":"Type","_value":"String"},
    "source":{"_type":"String","_value":"emptyString()"},"isAuto":{"_type":"Boolean","_value":false}}}}}
```

Entries in the flow's `nodes: LIST(Node,[...])` are the typed node wrappers directly
(e.g. `{"_type":"SendWorkdayApiRequest","_value":{...}}`) - there is no extra Node envelope.

## Flow root (build-verified; UAP v2, gq-bo-demo/getRestApiData.orchestration)

Outer file: `{"flowVersion":"3.1.0","_type":"Flow","_value":{...}}`. The launch-gate
`securityDomains` BARE array sits at this outer root as a sibling of `_type` (see orchestration.md;
zero corpus flows carry it - none of the 206 gate their launch). `_value` keys:

| key | req? | example / note |
|---|---|---|
| name | req | ID of the flow |
| type | req | FlowType `.maya.FlowSync` / `.maya.FlowAsync` / `.maya.FlowSubflow` / `.maya.FlowBusinessProcessTriggered` / `.maya.IntegrationFrameworkTrigger` |
| start / end | req | typed start/end node (pairs per orchestration.md Node vocabulary) |
| nodes | req | LIST(Node, [typed node wrappers]) |
| notes | req | NOTES |
| resources | req | ResourceProvider (see Resources below) |
| defaultWorkdayCredentialRef | req | `[Opt,WorkdayCredentialRef]` or `[Opt,AccessTokenFromInitiatingUser]` |
| errorHandler | opt 194/206 | `[Opt,ErrorHandler]` - the flow-level (global) handler |
| id | opt 166/206 | 32-hex flow id - CallSubflow.subflowId points at THIS |
| mayaVersion / palaVersion | opt | Builder tool versions, e.g. "1.3965.0" - leave as found |
| defaultLocale | opt 164/206 | `Locale {value:"en_US"}` |
| securityDomains | opt 158/206 | NESTED `[Opt,[List,String]]`, null in corpus - NOT the gate (orchestration.md) |
| cancelBarrier / defaultTlsConfigRef / defaultFtpCredRef | opt | null in corpus (`[Opt,...]`; the Tls/Ftp pair is 3.3.0-era) |

## Start / End nodes

All build-verified except StartAsync and the BP-trigger pair (sample-verified).

- **StartBasic** (FlowSync; UAP v2 bulkPublishCatalogItems.orchestration): `structuredRequest`
  req `[Opt,ObjectRequestStructure]` (null = untyped launch body), `notes` req,
  `hasMultipartData` opt B(false), `mcpToolConfig` opt `[Opt,MCPToolInputConfig]` (null in ALL
  corpus instances - the Agent-Actions non-null shape is unevidenced, see Completeness).
  - `ObjectRequestStructure {value: OPT(null), props: [Map,RequestStructure]}`; each leaf prop is
    `PrimitiveRequestStructure {treeValue: [Opt,StructuredRequestParameter {type, default}]}`;
    nest another ObjectRequestStructure for structured params (reads flatten to
    `data.start.$_<prop>_<nested>` per orchestration.md).
- **StartAsync** (FlowAsync; catalog employeeRelationsIncidentManagement/deleteCases.orchestration):
  `structuredRequest` req, `notes` req - same shape as StartBasic minus multipart/mcp keys.
- **StartSubflow** (ap-statement-recon/CreateExcel.suborchestration): `parameters` req
  `[List,ExprParameter]`, `notes` req. `ExprParameter {name: ID, type: Type, expr: [Opt,[Expr,[Opt,Any]]]}`
  (expr = the default).
- **StartBusinessProcess** (UAP v2 updateSecurityAccessForUAPOrchestration.orchestration):
  `parameters` req `[List,ExprParameter]`, `notes` req.
- **StartIntegrationFrameworkTrigger** (UAP v2 UpdateSecurityAccessForUAPIntegration.orchestration):
  `parameters` req, `configureForRetrieval` req B(false), `notes` req.
- **EndSync** (UAP v2): `headers` req `[List,Header]`, `body` req
  `[Opt, DataRefBody | CreateJsonBody | CreateTextDataBody]`, `notes` req, `mcpToolConfig` opt (null).
- **EndEmptyMaya** (async/integration flows; UAP v2): `notes` req - nothing else.
- **EndSubflow** (ap-statement-recon/CreateExcel.suborchestration): `exports` req
  `[List,Assignment]` (each export = an Assignment, read as `data.<CallNode>.<name>`), `notes` req.
- **BusinessProcessTriggerStart/End** (catalog cloudCommute) - 2.x-era BP pair:
  start `{parameters, notes}`, end `{notes}`. **MixedStart/MixedEnd** (catalog crisisCheckin) -
  legacy 2.x only: `{structuredRequest, notes}` / `{notes}`. Never emit new ones (orchestration.md).

Body types (used by EndSync and Send nodes): **DataRefBody** `{dataRef: EXPR(Data,...),
contentType: [Opt,String]}` - **CreateTextTemplateBody** `{message: TextTemplate, contentType: S}` -
**CreateJsonBody** `{template: JsonTemplateRef, mappings: [List,Mapping]}` -
**CreateTextDataBody** `{message: EXPR(String,...), contentType: S}` - **FormDataBody**
`{parts: [List,FormDataBodyPart], contentTypeOverride: [Opt,String]}` with **FormDataBodyPart**
`{nameProp: [Opt,EXPR(String)], data: EXPR(Data), contentTypeOverride, additionalDispositionParams,
additionalHeaders}` (multipart; build-verified in ap-statement-recon/createExcelFile.orchestration).

## Create / transform nodes

- **CreateValues** (build-verified; UAP v2, catalog prismAndExtendDesignPatterns/loadPrismByFileSync.orchestration).
  Assign typed variables. Minimal shape:

```json
{"_type":"CreateValues","_value":{
  "name": "ID(GetParameters)",                 // req
  "values": "LIST(Assignment,[ ...see envelope example above... ])",  // req
  "notes": "NOTES",                            // req
  "isDisabled": "B(false)", "errorHandler": "OPT(null)"}}  // opt 358/422 and 406/422
```

- **CreateTextTemplate** (build-verified; UAP v2 UpdateSecurityAccessForUAPIntegration.orchestration):
  `name` req, `message` req TextTemplate (plain string with `{{ }}` interpolation - NOT an Expr
  envelope), `contentType` req S ("text/plain" / "application/json" / "application/xml"),
  `formatRef` opt `[Opt,TextFormatRef]` (null), `isDisabled`/`errorHandler` opt, `notes` req.
- **CreateJson** (sample-verified; gq-bo-demo/csvToJson.orchestration): `name` req, `structure` req
  JsonTemplateRef - a GUID string naming an InlineResource in `resources.fileLikeResources` whose
  `content` is the JSON template with `@PLACEHOLDER@` slots - `values` req `[List,Mapping]`,
  `notes` req, `errorHandler`/`isDisabled` opt. **Mapping** `{path: JsonPath "$.EmployeeID",
  expr: EXPR(String,...)}`.
- **CreateTextData** (sample-verified; catalog addAdditionalJob/createAdditionalJob.orchestration):
  `name`, `message: EXPR(String, ...)` (expression, unlike CreateTextTemplate), `contentType`, `notes`.
- **ConvertXmlToJson** (sample-verified; catalog cloudCommute/CloudCommute.orchestration):
  `name`, `xml: EXPR(Xml, "data(\"Send\",\"response\").asXML().unwrapSoap()")`, `notes`.

## Send / IO nodes

- **SendWorkdayApiRequest** (build-verified; UAP v2, gq-bo-demo/getRestApiData.orchestration).
  Minimal shape (annotated; real file single-line):

```json
{"_type":"SendWorkdayApiRequest","_value":{
  "name": "ID(GetWorkerInfo)",                                  // req
  "body": "OPT(null) | CreateTextTemplateBody | DataRefBody | FormDataBody",  // req
  "path": "EXPR(String, s\"\"\"wql/v1/data\"\"\")",             // req - relative API path
  "method": "{_type:HttpMethod,_value:GET}",                    // req
  "queryParams": "LIST(QueryParam,[{name:S(query),value:EXPR(String,...)}])", // req
  "headers": "LIST(Header,[{name:S(Accept),value:EXPR(String,\"application/json\")}])", // req
  "auth": "WorkdayCredentialRef{resourceName:S(_DEFAULT_WORKDAY_CREDENTIAL)} | AccessTokenFromInitiatingUser", // req
  "connectTimeoutMs": "L(10000)", "responseTimeoutMs": "L(20000)", "overallTimeoutMs": "L(300000)", // req
  "tlsConfig": "OPT(null)", "proxyConfig": "OPT(null)",         // req, null
  "responseType": "{_type:HttpResponseType,_value:Json}",       // req - Json|Xml|Any
  "retryConfigRef": "RetryConfigRef _DEFAULT_WORKDAY_RETRY_CONFIG", // opt 247/284 (3.x)
  "errorHandler": "OPT(null)", "isDisabled": "B(false)", "isChunked": "B(false)", // opt
  "tlsConfigRef": "OPT(null)", "longRunningRequest": "B(false)", // opt 85/284 (3.2/3.3-era)
  "notes": "NOTES"}}   // legacy 2.x also carried maxRetries/retryDelayMs/responseCodeRange (37/284) - superseded by retryConfigRef
```

- **SendHttpRequest** (build-verified; billonly-v2 Epic_MRN_Validate.orchestration, catalog
  orchestrationToolkit/GetThirdPartyFile.orchestration): same envelope as SendWorkdayApiRequest
  with `url: EXPR(Url, "\"https://...\"")` req INSTEAD of `path`; `auth` req `[Opt,ExternalAuthRef
  {resourceName}]` (null + explicit Authorization header is common); `retryConfigRef` req
  `_DEFAULT_EXTERNAL_RETRY_CONFIG`; `pollingConfigRef` opt `[Opt,PollingConfigRef]` (null);
  `tlsConfigRef` opt (3.3.0 - see orchestration.md flowVersion note).
- **Http** (sample-verified; catalog cloudCommute, orchestrationToolkit/OAuthCCExample.orchestration):
  LEGACY 2.x external-HTTP node - SendHttpRequest keys plus inline `maxRetries`/`retryDelayMs`/
  `responseCodeRange` and no retryConfigRef. Read-only knowledge; do not emit new ones.
- **SendIntegrationMessage** (build-verified; UAP v2): `name`, `isDisabled`, `errorHandler`,
  `severity` req IntegrationMessageSeverity (`INFO|WARN|ERROR`), `summary` req EXPR(String),
  `detail` req `[Opt,EXPR(String)]`, `condition` req EXPR(Boolean) - the Debug-gate, `notes`.
- **SendPrismRequest** (sample-verified; catalog salesCommission/executeDCT.suborchestration +
  executeDCTFromFile.suborchestration - see Discrepancies): `name`, `isDisabled`, `errorHandler`,
  `path` req EXPR(String, "\"v3/dataChanges\"") - Prism-relative, `method`, `body`
  `[Opt, CreateTextTemplateBody|FormDataBody]`, `queryParams`, `headers`,
  `auth` req WorkdayCredentialRef, `requestConfig` req HttpRequestConfig, `responseType`, `notes`.
- **SendWorkdayRestApiPaginationRequest** (sample-verified; catalog
  capitalProjectPlanning/CapitalProjectPlanningBPMonitor.orchestration): `name`, `isDisabled`,
  `errorHandler`, `path` EXPR(String), `auth` WorkdayCredentialRef, `limit` EXPR(Number,"50"),
  `offset` EXPR(Number,"0"), `flatten` EXPR(Boolean,"true"), `maxPages` `[Opt,EXPR(Number)]`,
  `headers`, `queryParams`, `requestConfig`, `notes`.
- **TriggerIntegration** (sample-verified; catalog
  salesCommission/commissionCalculateAndLaunchApprovals.orchestration): `name`, `isDisabled`,
  `errorHandler`, `auth` `[Opt,WorkdayCredentialRefOrAccessToken]`, `childIntegration` req
  EXPR(InstanceReference, "instanceRef.integrationReference(...)"), `debugMode` +
  `includeParentReference` EXPR(Boolean), `requestConfig`, `launchInputDocumentData`
  `[List,IntegrationRepositoryDocumentData]`, `integrationLaunchParameterData`
  `[List,IntegrationLaunchParameterMapping {provider: LaunchParameterProvider {providerId,
  providerType}, parameters: [List,IntegrationLaunchParameter {nameProp: EXPR(String), value:
  Text|Date|InstanceReference LaunchParameterValue, isCustom, shouldSend, isRequired,
  importKey: [Opt,String]}]}]`, `notes`.
- **TriggerPdfGeneration** (sample-verified; catalog
  employeeRelationsIncidentManagement/intGeneratePDFandAttachments.orchestration): `name`,
  `isDisabled`, `errorHandler`, `reportDesign` + `reportData` req `ReportDataConfigFromData {data:
  EXPR(Data)}`, `auth` WorkdayCredentialRef, `businessFormLayoutWid` `[Opt,EXPR(String)]`,
  `locale`/`language`/`timezone` `[Opt,...]`, `applyReportDesignPerRow` EXPR(Boolean), `notes`.
- **Log** (build-verified; UAP v2): `name`, `message` req EXPR(String), `notes` req;
  `condition` opt EXPR(Boolean), `isDisabled`/`errorHandler` opt.
- **LogToFile** (build-verified; UAP v2 UpdateSecurityAccessForUAPIntegration.orchestration):
  `name`, `isDisabled`, `errorHandler`, `logname` req EXPR(String), `values` req
  `[Map,[Opt,EXPR(String)]]` (column name -> expr), `csvFormatRef` req (`_DEFAULT_CSV_FORMAT` or a
  declared format), `condition` `[Opt,EXPR(Boolean)]`, `notes`.
- **StoreDocument** (build-verified; UAP v2, o4i-example/WorkerPhotoOutbound.orchestration): `name`,
  `isDisabled`, `errorHandler`, `document` req EXPR(Data), `documentTitle` req EXPR(String),
  `description` + `collection` `[Opt,EXPR(String)]`, `storageExpiresIn` req S("P7D"),
  `attachToIntegrationEvent` + `deliverFromDeliveryService` req EXPR(Boolean),
  `tags` `[Opt,EXPR([List,String])]`, `requestConfig` req, `notes`.
- **AwsLambdaInvoke** (sample-verified; catalog AWSStarterKit/detectPII.orchestration): `name`,
  `isDisabled`, `errorHandler`, `functionName` EXPR(String), `payload` EXPR(Json),
  `returnTailOfLog` + `isDryRun` EXPR(Boolean), `requestConfig`, `notes`. Siblings with the same
  frame: AwsS3GetObject `{bucket, key, responseContentTypeOverride}`, AwsS3StoreObject
  `{bucket, key, requestBody, contentTypeOverride}`, AwsEventBridgePutEvent `{requestEntries}`.

## Control-flow nodes

- **BranchOnConditions** (build-verified; UAP v2, o4i-example/WorkerPhotoOutbound.orchestration):

```json
{"_type":"BranchOnConditions","_value":{
  "name": "ID(CheckForOverride)",       // req
  "errorHandler": "OPT(null)",          // req
  "ifBranches": "LIST(WhenBranch,[{name:ID(IF), condition:EXPR(Boolean,...), group:ImplicitGroup}])", // req
  "elseBranch": "[Opt,ImplicitGroup] (null = no else)",   // req
  "exceptionMessage": "S(None of the conditions are matched)", "exceptionIfNoBranchMatched": "B(false)", // req
  "enableOutputs": "B(true)",           // req - exposes data.<Branch>.* outputs
  "isDisabled": "B(false)", "notes": "NOTES"}}
```

  `ImplicitGroup {name: ID(_group_IF_CheckForOverride), errorHandler, nodes: [List,Node], notes}` -
  the Builder-generated container all branch/loop bodies live in (a rare legacy `nodes:[List,Node]`
  direct form exists in 2.x files).
- **Loop** (build-verified; UAP v2, gq-bo-demo/getRestApiData.orchestration): `name` req,
  `inputData` req `EXPR([Iterator,[Opt,Any]], "data.X.response.asJSON().iterator(\"$.data[*]\")")`,
  `aggregateNode` req `[Opt,Aggregate]`, `group` ImplicitGroup (body), `notes` req; opt:
  `filter [Opt,EXPR(Boolean)]`, `earlyStopCondition [Opt,EarlyStopCondition {name, isDisabled,
  earlyStopCondition: EXPR(Boolean), forceSequentialProcessing: B, notes}]`, `sorts [List,SortedBy]`,
  `locale`, `errorHandler`, `isDisabled`; rare: `breakCondition` (3/94), legacy `nodes` (6/94).
- **BatchLoop** (build-verified; UAP v2 bulkPublishCatalogItems.orchestration): Loop keys PLUS
  `batchStrategy` req `[Opt, SizeBasedBatchStrategy {size: EXPR(Number,"100")} |
  GroupBatchStrategy {groups: [List,GroupedBy {nameProp, value: EXPR, descending: B}]} |
  CustomBatchStrategy {condition: EXPR(Boolean), keepLeadingItems: B, batchFormationMode:
  "BATCH_FORMATION_MODE_AT"}]` and `foldValue` req (a fold value, exposes `data.<Loop>.batch`).
- **JoinLoop** (sample-verified; gq-bo-demo/JoinLoop.orchestration, CsvJsonJoinLoop.orchestration):
  `name`, `errorHandler`, `outputName` req ID (the left row, `data.<JoinLoop>.<outputName>`),
  `iterator` req EXPR(Iterator), `joins` req `[List,Join {key: EXPR(String), from: [List,JoinWith
  {outputName, iterator, key: EXPR(String), values: [List,JoinedValue {outputName, value: EXPR}]}],
  nameProp: [Opt,ID]}]`, `missingMatch` req `MissingMatchRule {matchType: "SKIP_RECORD",
  log: [Opt,MatchErrorLog]}`, `multipleMatches` req `UseFirst {retainMultipleMatches: B}`,
  `aggregateNode`, `group`, `notes`.
- **CallSubflow** (build-verified; ap-statement-recon/createExcelFile.orchestration): `name`,
  `isDisabled`, `errorHandler`, `subflowId` req S - the 32-hex `id` at the target subflow's Flow
  root - `parameters` req `[List,Assignment]` (values for the subflow's StartSubflow params),
  `notes`; `executionDelay` opt `[Opt,SubflowExecutionDelay]` (2/105, null).
- **Group** (build-verified; ap-statement-recon/CreateExcel.suborchestration): `name`, `isDisabled`,
  `errorHandler`, `nodes` req `[List,Node]`, `notes` - the explicit scope for a shared ErrorHandler.
- **Aggregate** (build-verified; UAP v2) - lives in a loop's `aggregateNode`: `name` req,
  `failOnEmptyStream` req B(false) -- **ALWAYS set false; a Loop ERRORS at runtime when the iteration
  set is empty and this field is true or absent** (build-verified 2026-09-08, UAP v2 rollback flow;
  symptom: "Empty stream @[LoopName.AggregateName]"), `foldValues` req `[List,FoldValue]`, `notes` req,
  `isDisabled` opt.
  Fold value shapes (all `{nameProp, condition: [Opt,EXPR(Boolean)]}` plus):
  - Json/String/Sum/Number/CsvFoldValue: `+ data: EXPR(<type>)`
  - CountFoldValue: nothing more (counts matching iterations)
  - TextFoldValue: `+ data, contentType, lineSeparator, header/footer: [Opt,String|TextTemplate]`
  - XmlFoldValue: `+ data, headerText, footerText, separator: [Opt,S], xpath: [Opt,S], namespaces: [Map,String], includeXmlDeclaration: B` (ap-statement-recon/CreateSingleSheet.suborchestration)
  - FormattedCsvFoldValue: `+ csvFormatRef, values: [Map,[Opt,EXPR(String)]]` (catalog prismAndExtendDesignPatterns/loadPrismByFileSync.orchestration)
  - ZipArchiveFoldValue: `+ data: EXPR(Data), path: EXPR(String)` - path = entry name in the zip (ap-statement-recon/CreateExcel.suborchestration)
  - StringMapFoldValue: `+ key, value` (catalog, single instance)

## Error / validation nodes

- **ErrorHandler** (build-verified; UAP v2 deleteRowsBulk.orchestration): `name` req (Builder names
  them `_errorHandler_<NodeName>`), `strategy` req ErrorHandlerStrategy (`PropagateError` |
  `GlobalErrorHandler` | `ConditionalOutputs` - semantics in orchestration.md), `nodes` req
  `[List,Node]` (handler body, may be empty), `notes` req, `isDisabled` opt. Attached per-node via
  the node's `errorHandler: [Opt,ErrorHandler]` key, or flow-level via Flow.errorHandler.
- **ContinueOnConditions** (build-verified; payroll-input-inbound
  INTXXXX_Payroll_Input_Inbound_O4I_Template.orchestration): `name`, `errorHandler`, `assertions`
  req `[List,Assertion {assertion: EXPR(Boolean), message: EXPR(String)}]`, `notes`, `isDisabled` opt.
  Note: `Assertion` exists only INSIDE this node - it is not a standalone flow node.
- **Validate** (build-verified; payroll-input-inbound ValidateFile.suborchestration,
  supplier-invoice-template ValidateFile.suborchestration): `name`, `errorHandler`, `validations`
  req `[List,ValidationCheck {name: ID, severity: ValidationSeverity "ERROR"|"WARNING",
  expression: EXPR(Boolean), summary: EXPR(String)}]`, `notes`. Outputs (`allValid`,
  `failedValidations`) in orchestration.md.

## Resources (the flow-root `resources` ResourceProvider)

`ResourceProvider {fileLikeResources: [Map,Resource], credentials: [Map,Credential],
xmlNamespaces: [Map,String], retryConfigs: [Map,[WithNotes,RetryConfig]],
csvFormats: [Map,CsvFormat], pollingConfigs: [Map,PollingConfig] (opt, null-empty),
workdayCredentials: opt 15/206}`. Member shapes:

- **InlineResource** (in fileLikeResources; gq-bo-demo/csvToJson.orchestration): `{name: S(<guid>),
  content: S(<json/text template body>), notes}` - CreateJson `structure` and CreateJsonBody
  `template` point at these by name.
- **RetryConfig** (build-verified; billonly-v2 Submit_Requisition_Orch.orchestration): `{name,
  maxTotalRetries: Int, successResponseCodeRanges: [List,ResponseCodeRange {begin: Int(200),
  end: Int(299)}], defaultBackOff: BackOff {intervalMs: L, factor: Decimal, maxBackOffMs: L},
  retryPolicies: [List,RetryPolicy {nameProp, conditions: [List, StatusCodeCondition {codes:
  [List,Int]} | HeaderCondition {header: S("Retry-After")}], maxRetries: [Opt,Int],
  backOffStrategy: [Opt, BackOff | CustomBackOff {interval: RetryAfterHeaderInterval,
  maxBackOffMs}]}]}`. Send nodes reference by name via `retryConfigRef`.
- **Credentials** (in credentials map): **WorkdayCredentialRef** `{resourceName:
  S(_DEFAULT_WORKDAY_CREDENTIAL)}` (the auth value on Send nodes); **ApplicationSystemUser**
  `{name, username: EXPR(String, "attrstore.stringValue(\"appISU\")"), checkEnvironment: B}`
  (build-verified, billonly-v2 Business_Process_Reassignment.orchestration);
  **IntegrationSystemUser** `{username: EXPR(String), checkEnvironment: B}` (sample-verified);
  **OAuthCredential** `{name, token: CredStoreReference {reference}}` (sample-verified,
  orchestrationToolkit/OAuthCCExample.orchestration); **BasicCredential** `{name, username,
  password: EXPR(String)}` (sample-verified, capitalProjectPlanning); **ExternalAuthRef**
  `{resourceName}` = how a SendHttpRequest points at one.
- **CsvFormat** (build-verified; UAP v2): `{nameProp, hasHeader: B, columns: [List,CsvColumn
  {index: Int, columnName: S, type: Type, isRequired: B}], separator/quoteChar/escapeChar: Char}`.
- **HttpRequestConfig** (newer Send nodes' `requestConfig`): `{connectTimeoutMs, responseTimeoutMs,
  overallTimeoutMs: L, retryConfigRef}` - bundles what SendWorkdayApiRequest carries inline.

## Discrepancies vs orchestration.md (flagged, not silently corrected)

1. **SendPrismRequest DOES appear in the local App Catalog** - 6 instances in
   `salesCommission/orchestration/executeDCT.suborchestration` + `executeDCTFromFile.suborchestration`
   (typed node, shape above), used for DCT execution. RECONCILED 2026-08-25: orchestration.md was
   corrected to "RE-CONFIRMED sample-verified" and now documents both routes (raw
   SendWorkdayApiRequest for Prism file LOAD via `prismAndExtendDesignPatterns`, the typed node for
   DCT execution). Still build-verify the typed node in-tenant before production reliance.
2. **successResponseCodeRanges keys are `begin`/`end`** and the key is a TOP-LEVEL sibling of
   `retryPolicies[]`, not nested under it. RECONCILED 2026-08-25: orchestration.md was corrected on
   both points (keys and placement) against all 18 corpus ResponseCodeRange instances.
3. **Loop config-key census (additive):** orchestration.md's Loop/BatchLoop key list holds; the
   corpus adds rare optional keys `breakCondition` (3/94) and a legacy direct `nodes` list (2.x).
4. `Assertion` is a sub-object of ContinueOnConditions, not a standalone node (orchestration.md
   line "Group/Assertion" reads as if it were one).

## Completeness - node types NOT evidenced in this corpus (shapeless, do not guess)

- **SendWorkdayRaasRequest** - zero instances anywhere local (name source-verified per
  orchestration.md from a delivered app not in this corpus). No key census - pull a real instance
  before generating one.
- **SendWwsPaginationApiRequest** - donor app (supplierInvoicesInbound) not present locally.
- **MCPToolInputConfig / MCPToolOutputConfig** - the `mcpToolConfig` key exists on 17
  StartBasic/EndSync pairs but is null in every instance; the Agent-Actions non-null shape is
  unevidenced.
- **SFTP Transport File node** (DevCon 2026) - no instance.
- **Integration Maps** (`intsys.mapLookup`) config shape - expression side only, no node/resource
  instance found.
- Low-instance shapes (n<=3, sample-verified only, trust but verify): TriggerPdfGeneration,
  SendWorkdayRestApiPaginationRequest, TriggerIntegration, FormattedCsvFoldValue,
  StringMapFoldValue, OAuthCredential, BasicCredential, EarlyStopCondition, StartAsync.
