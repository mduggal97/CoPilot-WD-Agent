# Workday App Catalog - sample registry (which sample shows X)

50 official Workday App Catalog sample apps, extracted to `_reference\app-catalog\<appName>\` in your Extend workspace. When you need a copyable, official example of a construct, find it here and read the named files. Tier = **sample-verified** (official Workday source; above doc-sourced, below our own build-verified - sample code is the *shape* authority, our references win on runtime *behavior* where they conflict). Mined 2026-08-06.

> **Snapshot currency (cross-checked 2026-08-07 vs the canonical `Workday/WorkdayDeveloperProgram` DevRel catalog, 32 apps).** The two catalogs are a HYBRID, not one a superset of the other: ~26 apps below are **mined-only** (present in the App Catalog snapshot we mined, absent from today's public DevRel repo - keep them; some may be older/legacy, so confirm the app still exists before citing it to a client), and 8 DevRel apps were **not** in our snapshot - added in the "Integration / O4I-for-integrations" section below. Net: use this registry for breadth; confirm a specific donor's current existence against the live catalog before relying on the exact name.
>
> **The live catalog is now a browsable HUB** (`Workday/WorkdayDeveloperProgram`, DevRel - non-official support): `catalog/` = Workday-maintained apps (30+, growing) + `examples/` = community contributions with a `_template/` scaffold and `scripts/new-example.mjs` generator, all CI-validated, plus a searchable **gallery site** at `workday.github.io` - the fastest way to browse/filter by content TYPE (Extend App / Integration App / Orchestration / **Agent Skill** / Reference). Newer catalog additions worth knowing: the AI Gateway family (sentiment / skills / document-intelligence / forecasting / recommended-reports) and AWS samples (Badge Generator w/ EventBridge, Drivers License/Textract) - all already in the tables below. Browse the gallery when solutioning (solutioning.md); `wdcli app copy` a template to adapt. The "Agent Skill" content type is covered in custom-agents.md.

**This is an IDEA catalog, not a copy-source.** Its first job is to broaden what you consider possible when solutioning a new build - browse "Demonstrates" to see the breadth of the platform and spark a better-fit design (see [solutioning.md](solutioning.md)). Its second job is a shape lookup: when you need the exact JSON of a widget/node/file-type, a working end-to-end pattern to adapt (`wdcli app copy` a template then strip), or proof a capability exists. Do NOT clone sample *code style* - the samples have sparse comments and `CreateValues_1`-style names, below our KT-comment house standard; and our build-verified references govern runtime *behavior* where they differ. Let the samples expand your options; design in the suite's voice.

## UI / PMD / charts

| App | Demonstrates | Notable files/constructs |
|---|---|---|
| `pmdWidgetDictionary` | Canonical live catalog of ~60 widgets, one PMD each | tabs, projectHub (hub), ticketsListDetail (listDetailHub), dynamicSection+progressIndicator, bpExtender+helper orch, sortFilterEditGrid, areaLayout, basicFormLayout, loops, calendar |
| `chartDictionary` | Complete Chart 2.0 vocabulary - 13 types + 14 feature pages (see [charts.md](charts.md)) | `*Chart2.pmd` per type, `feature*.pmd`, `podiumChart.pmd` |
| `pmdScripting` | Script-layer teaching app | scripts/*.script (7), pageEvents (onSubmit), updateWidgetState (standardEditButtonsHidden (!)), gridEvents (onRowSelect) |
| `createAWorkEvent` | Full CRUD + custom BP + GraphQL mutations + wizard + hub + calendar | graphQueries/*.graphquery, .businessprocess, action/approve/revise pages |
| `createAWorkEventWithAIWidget` | Same app + generative-AI text widget - the diff IS the AI wiring | `aiPrompt.buttons[]` on a richText (only delta) |
| `workFromAlmostAnywhere` | Production-shaped BP app: App-Attribute-driven validation, Home cards, calendar, chart card | top-level cards/*.carddefinition+.cardtenantsetting, daysChart.card (chartCard donut), scripts/dates.script (setError/date math), 4-route .businessprocess |
| `tuitionReimbursement` | Native i18n + `guide` help + wqlQueries + orchestration payment | presentationLabels/en-US.properties, wqlQueries/*.wqlquery (5), CreateOneTimePayment orch |
| `charitableDonations` | CRUD baseline: BP, attachments, hub, listDetailHub, wizard | charityHub, charitiesListDetail, CharityLogo.attachment, .report |
| `vaccineManagement` | Large config-BO-driven form suite: 3 BPs, on-behalf-of, attachments | 12 BOs incl. Config, instanceListLoopTag dropdowns, per-BP confirmations |
| `crisisCheckin` | Config-BO dynamic surveys + Model-BP mass launch via async fan-out | AsyncProcessListOfWorkersToLaunchModelBP (self-launch loop), inboxSurvey (workday-bp resolution) |

## Orchestration / integration / model

| App | Demonstrates | Notable files/constructs |
|---|---|---|
| `orchestrationToolkit` | THE node/pattern reference (25 flows): error-handler taxonomy, validation, rollback, paging, OAuth-CC, Excel-gen, multipart attach, Studio launch | RetryConfig successResponseCodeRanges, ConditionalOutputs, Validate/failedValidations, ZipArchiveFoldValue->xlsx, FormDataBody, OAuthCredential/CredStore, JoinLoop |
| `capitalProjectPlanning` | Biggest app (45 subflows/16 BOs): decomposition at scale + Adaptive Planning sync + 2 Model BPs | Verb+Entity / *Stub / *Base / DNU naming, SendWorkdayRestApiPaginationRequest, Adaptive token exchange, bootstrapData.script, .mock_response |
| `salesCommission` | Prism->Extend pipeline: DCT execution, child-integration launch, BP approvals, payroll-input REST | Prism file LOAD via raw REST `SendWorkdayApiRequest` -> `prismAnalytics/v3/fileContainers`, and DCT EXECUTION via the typed `SendPrismRequest` node (6 instances in executeDCT[FromFile].suborchestration - re-confirmed 2026-08-25, see orchestration.md + orchestration-nodes.md), TriggerIntegration, POST /payroll/v2/payrollInputs, parameterized .wqlquery `{{appId}}` FROM |
| `orchestrationManager` | Monitor orchestration runs across apps/tenants via Orchestrate admin REST | MakeOneAPICall generic subflow, system.apiGatewayEndpoint(), StoreDocument CSV |
| `multiRater` | Custom BP embedded in a NATIVE BP + multi-actionStep inbox wizard | MultiRating.businessprocess `allowedParentProcesses`, 8 Performance_Management SOAP flows |
| `projectForecasting` | `.report` model files + BP-gated self-service forecast edit | 3 `.report`, UpdateMyProjectForecast BP+task, Resource_Management SOAP + projects REST |
| `employeeRelationsIncidentManagement` | PDF generation + zip bundling export; protected-data app | TriggerPdfGeneration, ZipArchiveFoldValue, data.Loop.itemNumber, 13 .wqlquery (_All/_ByCase) |
| `assetBarcoding` | SOAP-to-JSON bridge flows for barcode-scan pages | ConvertXmlToJson, `.unwrapSoap()`, Register/Transfer/Dispose_Asset, 2 .report |
| `requestCreditCard` | Canonical useForOrchestrate write-on-approval loop w/ external API | BP-triggered flow (`actionEvent`), external REST + PATCH-back, .report |
| `createAccountingJournal` | Journal submit via Workday Graph API - zero orchestrations | SubmitJournal.graphquery (`submitAccountingJournal` mutation), 6 .wqlquery FDM lookups |
| `changeBusinessTitle` | Title change is plain REST | POST /common/v1/workers/<WID>/businessTitleChanges + connect/v2/sendMessage |
| `createSpotBonus` | Two ops in one GraphQL mutation from a flow | POST /graphql/v1: requestOneTimePayment + initiateWorkerFeedback |
| `disableWorkdayAccount` | Account disable on BP trigger (2.x-era legacy format) | SOAP Get/Update_Workday_Account; GET businessProcess/v1/events/<id> |
| `addAdditionalJob` | Position + job add chain | SOAP Staffing Create_Position -> Add_Additional_Job |
| `cloudCommute` | Flow writes to a tenant CUSTOM OBJECT (not an Extend BO) | POST /customObject/v2/customObjects/<alias> |
| `uiPathOrchestrationPack` | RPA hand-off from BP triggers (legacy 2.2 - pattern only, don't copy JSON) | UiPath start-process / add-queue-item |
| `vndlyErrorManagement` | External SaaS report pull + chart dashboard | attrstore-driven vndly.com custom_reports REST, .card charts |
| `helpCaseCreation` | Workday Help REST from PMD only | baseUrlType workday-help; /cases, /caseSuggestions |
| `suiTaxRates` | Payroll REST from PMD only | baseUrlType payroll; /taxRates, /values/taxRatesGroup/* |
| `wql` / `generateWQL` | WQL playground / query-builder UIs (nothing beyond PMD basics) | - |

## AI Gateway / external / Prism / file-type anatomy

| App | Demonstrates | Notable files/constructs |
|---|---|---|
| `sentimentAnalysisWithTheAIGateway` | Minimal AI Gateway call from a page + result rendering | `workday-ml` provider, sentiment-analysis/v1/predict, dynamicSection->cards, donutChart2, 512-word cap |
| `skillsMiningWithTheAIGateway` | Skills extraction from job text | skills-cloud/v1/extract, .wqlquery + wqlQuery:{queryId} |
| `documentIntelligenceWithTheAIGateway` | Upload -> orchestration scans doc -> typed results | fileUploader->attachment BO, dual GET (bytes vs Accept:json), /ml/docint/v1/{type} octet-stream, gap-analysis, CreateJson, $_document_id launch param |
| `forecastingWithTheAIGateway` | Time-series forecast over an Extend BO series | forecaster/v1/predict holt_winters, DECIMAL `decimals` field |
| `recommendedReportsWithTheAIGateway` | WQL-driven report recommendations (declares `workday-ml` but NEVER calls it - WQL analytics, not ML) | indexedReportRunHistory, customReportsICanRun, report deep-link idiom |
| `employeeRecognitionWithTheAIGateway` | Sync-flow-as-AI-proxy: aggregate feedback -> batch sentiment | GET `.../launch?Worker=`, queryParams.getParam, Loop+JsonFoldValue batch predict |
| `employeeRecognition` | The non-AI twin; tenant-registered home cards | cards/*.carddefinition + .cardtenantsetting |
| `charitableDonationsWithSentimentAnalysis` | Smallest sentiment bolt-on to a CRUD app | `.../ml/sentiment-analysis/v1/`, richText->textArea swap (ML wants plain text) |
| `AWSStarterKit` | Generic AWS toolbox via Lambda from sync flows | AwsLambdaInvoke, AwsS3StoreObject, presentationLabels/*.properties |
| `AWSDriversLicense` (+`WithTranslations`) | Textract ID extraction (+ response-label translation loop) | AwsLambdaInvoke + AwsS3StoreObject, CreateJson |
| `AWSBadgeGenerator` | Event-driven AWS round trip (validate selfie -> EventBridge -> inbound badge) | AwsEventBridgePutEvent, inbound `.../launch` w/ $_detail_bucket, AwsS3GetObject, testing/*.mock_* |
| `prismAndExtendDesignPatterns` | THE Extend<->Prism pattern app: read cds_ table, queue corrections, single-threaded DCT write-back, self-installer | cds_ WQL + WPA_RowID, FormattedCsvFoldValue+`.gzip()`, fileContainers->files->activities, status-poll lock, install.orchestration, `?bulk=true` POST, `iterator(path,100)` |
| `vehicleRegistration` | GraphQL CRUD + i18n + mocks + hub (the file-type showcase) | 8x .graphquery (queries+mutations), .mock_response/.mock_config, 5-locale .properties, model/*.report, hub body |
| `workerBadges` | Attachment CRUD choreography end-to-end | multiPartFileLast, `cid:image` + ep:data:/ep:image: bindings, image widget inline endPoint, attachmentList |
| `commutingEmissionsSurvey` | Survey form -> BO, worker-context enrichment | workers/me?view=..., workerRawPhotoData/<id> |
| `giftRegistry` | Extend UI over TENANT custom objects (no Extend BO) | workday-custom-objects, ?updateIfExists=true&bulk=true, `;item=` composite delete |
| `mileageExpense` | External Maps API + Workday Expense REST chained submit | gmaps provider (key in appProperties), /expense/v1 entries->reports->lines |
| `businessCards` | Tiny 2-page order form against purchase items | attrstore purchaseItem |

## Integration / O4I-for-integrations (added 2026-08-07 from canonical DevRel - not in the 2026-08-06 mine)

These 8 are the traditional-integration / O4I-as-integration donors; several are the canonical evidence behind the orchestration.md fold-ins of 2026-08-07. Cross-reference wd-integration-dev.

| App | Demonstrates | Notable files/constructs |
|---|---|---|
| `supplierInvoicesInbound` | The WWS high-volume **Import framework** natively in O4I (submit -> poll -> harvest messages -> audit file) | `Import_Supplier_Invoice` POST `/soap/v43.0/Resource_Management`, `X-Validate` dry-run, `SendWwsPaginationApiRequest` over `Get_Import_Process_Messages`, `system.namedLogFile`->`ImportResults.csv` |
| `employeeDemographicOutbound` | Delimited/fixed-width demographic OUTBOUND (parallels a Person-Hub extract) | RaaS -> map -> `CsvFormat`/`FormattedCsvFoldValue`, `lp.sequencedValue("Filename")`, RaaS ~2083-char URL guard |
| `locationChangesOutbound` | O4I as a **post-processor** bolted onto a delivered Core Connector | `documents.labelsMatchAny(List.stringList("Deliverable"))`, fixed-width `rightPad/substring`+`TextFoldValue` OR `CsvFormat`, branch on `lp.simpleData("Output File Type")` |
| `workerInboundImageUpload` | Worker photo inbound with padded sequence IDs | `data.PhotoLoop.itemNumber` / `data.JoinLoop.itemNumber` `.leftPad(4,"0")` |
| `orchestrateForIntegrationsSampler` | THE O4I-for-integrations toolbox | `TriggerIntegration` (typed launch params + `childDocuments` readback), `intsys.mapLookupWithDefault(...)` (Integration Maps), `CreateExcel`/`CreateSingleSheet` xlsx-gen, `range(a,b)`, `iterator.combineXMLIterators`, `BatchLoop_{Size,Group,Custom}Strategy`, `BooleanFoldValue` |
| `updateServiceDateBoomerang` | Boomerang shape in O4I (RaaS -> loop -> SOAP update -> dual logs) | `intsys.stringAttributeValue("ReportCall")`, SOAP `Update_*` `/soap/v42.2/Staffing`, `responseStatusCode.is2xxStatusCode().not().or(response.isSoapFault())`, `SuccessLog.txt`/`ErrorLog.txt` |
| `learningEnrollments` | Boomerang: fetch workers meeting a condition -> enroll in a course | `LearningEnrollmentBoomerang.orchestration` |
| `updateWorkdayAccounts` | Boomerang: fetch workers -> update their Workday account usernames | `BoomerangWDAccnt.orchestration` |

## The DEV-tenant probe backlog (settle these in ONE session)

Items that a live dev-tenant check would resolve - the highest-value follow-up from the mining + coverage audits. The [tenant-ops.md](tenant-ops.md) toolkit settles most in one session (deploy a small probe app or read an existing one). Two buckets:

**A. Samples that CONTRADICTED our build-verified text - MOSTLY RESOLVED 2026-08-07 against the canonical DevRel repo (a resolution stronger than sample-alone: official DevRel code + direct token/file verification).** Live-tenant probe is now optional for the confirmed items; A3/A7 still warrant a live check.
1. `standardEditButtonsHidden` - **RESOLVED (CORRECTED).** The prop DOES suppress EDIT OK/Cancel (`createAWorkEvent/.../registerConfirmation.pmd`, `generateWQL/.../queryBuild.pmd`); pmd-gotchas #26/#28 + pmd.md fixed. Trade-off: you then own the commit.
2. `progressIndicator` native widget + `dynamicSection` reactive rerender - **RESOLVED (CORRECTED).** `progressIndicator` is native (`value`/`maximumValue`/`isPercentage`); `dynamicSection` re-renders on `<section>.data` reassignment (`pmdWidgetDictionary/.../progressIndicator.pmd`); gotcha #38 + pmd.md fixed.
3. Page-layer date arithmetic - **PARTIALLY RESOLVED.** `date:add`/`date:after`/`date:month`/`date:year`/`date:extractValue`/`date:parseDateString` CONFIRMED in a canonical PMD `.script` (`pmdScripting/.../dateCalculations.script`); the method-forms `.between()`/`.withMonth()` were speculative and do NOT appear. Still build-verify `date:add` in your target tenant before moving relative-date math out of an orchestration. (pmd.md updated.)
4. `sortableAndFilterable: true` on VIEW - **RESOLVED.** Confirmed on `pageType: VIEW` (`capitalProjectPlanning/.../CapitalPlanningRequestsIndex.pmd`); retires the filter-bar-forces-EDIT workaround for read-only lists. (pmd.md updated.)
5. `searchEndPoint`/`searchResultValues` as a page-body widget - **RESOLVED (REFINED).** Works as a page-body PICKER widget (`capitalProjectPlanning/.../CapitalPlanningRequestCreate.pmd`), also carrying `selectedValuesAndDescriptors`. (pmd.md updated.)
6. `data.<Loop>.itemNumber` runtime counter - **RESOLVED.** Confirmed on Loop/BatchLoop/JoinLoop (`ImportProcessor.orchestration`, `WorkerPhotoInbound.orchestration`); runtime output, not a config key, so no conflict. (orchestration.md updated.)
7. `.task` id vs BO id space - **OPEN (leaning).** Canonical samples suggest the id space is per-artifact-type (so the "use 90/91" habit may be over-strong), but not independently confirmed here - treat 90/91 as optional and verify live before retiring the convention. (model.md)

**B. THIN capabilities the coverage audit wants pinned to build-verified:**
8. Integration Maps - **RESOLVED.** `intsys.mapLookupWithDefault(...)` appears in a canonical suborchestration (`orchestrateForIntegrationsSampler/orchestration/ProcessOneFile.suborchestration`, which takes `mapName`/`keyLength`/`dateFormat` params and map-transforms file data) - note the **WithDefault** variant is the canonical form, which sidesteps the "unmatched key throws" trap. Read that file for the exact call shape when authoring. (orchestration.md)
9. `SFTP Transport File` node anatomy (Retrieve/Deliver/List/Delete) - **STILL OPEN** - not exercised in the canonical repo cluster mined; outbound O4I file delivery without the Delivery Service, verify-GA. (orchestration.md)
