# Workday REST API catalog (local OpenAPI snapshot)

A full local snapshot of Workday's public REST API OpenAPI schemas, exported from the Community REST API directory (login-gated: `https://community.workday.com/sites/default/files/file-hosting/restapi/index.html` -> "Download Open API Schema"). Because the directory's service list can't be fetched programmatically, this snapshot IS our machine-readable source of truth for endpoint shapes.

**Snapshot location:** `rest-api-schemas\` inside your Extend/wdcli workspace repo (example - your path differs). One JSON per service, named `<service>_v<N>_<yyyymmdd>_oas{2|3}.json` - the date is the export date, not a version date.

**Current snapshot: 51 services, exported 2026-07-27** (customObject v2 and prismAnalytics v3 carry older dates - those are the latest schemas the directory offers for them).

## How to use the snapshot

- **Before writing any orchestration REST call or Extend HTTP outbound**, Read the service's JSON for: exact path + query params, required body fields (look for `required` arrays and `x-conditionally-required`), and **`x-workday-secured-by-domains` per operation** - that domain list feeds the ISSG grant table in security-setup.md and the design doc's Security tab.
- Descriptions embed **validation-error tables** (severity/code/message) - pre-wire error handling against these instead of discovering them at runtime.
- Common envelope across services: `limit` (default 20, max 100 - a few services allow 1000), zero-based `offset`, `total`+`data[]` response, instance refs as `{id, descriptor, href}` where `id` is a 32-hex WID **or** `RefIdType=value` (pattern `^(([0-9a-f]{32})|(\S+=\S+))$`).
- `<tenantHostname>` = the tenanted host. Remember the gateway split: bulk/long work goes to the tenanted host, never `api.workday.com` (shorter gateway timeouts - see prism-and-reporting.md).

## Release-refresh routine (house standard)

Workday ships two feature releases a year (R1 ~March, R2 ~September). **Each release, re-export the full schema set** from the REST directory (user-interactive login) into a fresh dated drop next to the old one, then diff:

1. New filenames -> new services (2026 examples worth watching: `asor` = Agent System of Record, `graph`).
2. Version bumps (e.g. staffing v7): old versions keep working but new fields/ops land only in the new version.
3. Same-version re-exports still change - Workday adds fields/params inside a version; a filename-date diff catches it.

Record the refresh in this file (snapshot date + service count) and update release-impact.md's watch notes if a service the suite depends on changed.

## Extend-delivery highlights (services we actually reach for)

- **wql v1** - `GET /data?query=` caps queries at 2,048 chars; use the read-only **`POST /data`** for longer WQL. `/dataSources`, `/dataSources/{id}/fields`, `/dataSourceFilters` = programmatic discovery for building queries. Domains: Workday Query Language / WQL for Workday Extend / Development. Verified quirks (2026-08-25): `/dataSources` `limit` max is 100 (`limit=200` returns "limit parameter invalid: must be between 1 and 100"), and its `search=` parameter is accepted but performs NO filtering (identical results for different terms) - page through the full list instead. Full language reference: wql.md.
- **worktag v1** - `POST /validateWorktags` = read-only pre-validation of worktag combos against Maintain (Related) Worktag Usage config before submitting a transaction. Body keys: `taggableConfiguration{id}` (`Taggable_Type_ID=EXPENSE_REPORT` style, from View Taggable Types), optional `worktags[]`, `validationTypes[]`, `restrictions[]`. Response enumerates missing-required / not-allowed / invalid-combination buckets. (Also exposed as `validateWorktags` inside **common v1**.)
- **customObject v2** (single + multi-instance, oas3) - the delivered CRUD surface for custom objects on standard BOs: `?bulk=true` (max 100/request in this snapshot; the official docs state a 200 ceiling - see the reconciliation in the Platform limits section below), `?updateIfExists=true` upsert, multi-instance addressing `{businessObjectWID};{refIdAlias}={value}`. Complements the Extend app BO REST verbs in model.md. **customObjectDefinition v1** reads/manages the definitions themselves.
- **budgets v1** - `POST /runBudgetCheck` (read-only): pre-flight a multi-line transaction against budget plans; returns per-plan available/spend/plan amounts + statuses. Domain: Budgets REST APIs.
- **coreAccounting v1** - `/currencies` (precision/code lookups; Core Navigation domain) and `/evaluateAccountPostingRules` (resolve ledger account + resulting worktags for an APR set/type/dimension; Workday recommends parallel calls with unique params).
- **systemMetrics v1** - `/systemMetricsOverview`, `/activeTasks`, `/activeUserSessions` (System Monitor Administrator/Support domains): live queued/running-task and session counts - evidence source for perf-testing and hypercare monitoring.
- **privacy v1** - `/activityLogging` user-activity audit trail. Requires Enable User Activity Logging (Edit Tenant Setup - System); `from`/`to` required; page with `limit=1000&instancesReturned=1` and step `offset` by 1000 (official iteration pattern). Domain: System Auditing. Feeds security-questionnaire audit answers.
- **businessProcess v1** - `/events`, `/eventSteps`, `/types`: inspect in-flight BP events programmatically (complements Extend BP-launch patterns).
- **asor v1** - Agent System of Record: register/read A2A agent cards (`/agentDefinition`), `/agentResourceSearch` (find Workday REST/SOAP/MCP tools by search string), `/registration`. The API side of the DevCon-2026 custom-agents model (see your Extend workspace's CLAUDE.md notes).
  - **Spec detail (per Workday/asor, official Agent Definition API docs - spec v1.2, 2026.05; official-docs tier, NOT build-verified):** base is **`.../api/asor/v1/{tenant}/agentDefinition`**; **GET is secured by `Setup: Agents`, POST by `Development`**. The **POST body is an A2A Agent-Card** (plus a Workday `workdayConfig[]` extension) and **upserts on `name` + `provider` + `version`** - bump `version` to register a new definition rather than mutate one. `agentResourceSearch` and `registration` exist in the OpenAPI snapshot but are **NOT in the published v1.2 doc set** (treat as unpublished/preview). Deeper asor semantics (execution modes, ASU auth, resource WIDs, OTel contract) live in custom-agents.md.
- **attachments v1 + graph v1** - download attachments by `downloadID` from a Graph API query response; `/graph/v1/versions` lists supported Graph API versions. Full GraphQL authoring depth (provider wiring, `.graphquery` shape, query-vs-mutation, combined mutations, the ref-id portability gotcha, HTTP-200+`errors[]`, the BP "(REST Service)" requirement, and when Graph beats REST/WQL/SOAP) is consolidated in **section  Graph API (GraphQL) authoring** below (sources incl. Workday/extend-js-example + App Catalog samples createAccountingJournal / createSpotBonus / vehicleRegistration).
- **Two patterns from the same sample worth knowing service-wide:** create-op **prompt-values endpoints** (`.../<createOp>/values/<prompt>`) return the valid options an external UI should offer before a create; and orchestrations are externally launchable at `POST /orchestrate/v1/apps/<appId>/orchestrations/<id>/launch` (user-context bearer works).
- **connect v2 / communications v1** - `POST /sendMessage` (email/push via message template or inline detail; template and notificationType must match), message-template CRUD; `communications /managedRecipient` = SMS opt-in/out by E164 phone (validation table in schema).
- **skill v1** - `POST /mlSkills` maps Skills-Cloud ML skill IDs -> Workday IDs, creating on first sight; `?bulk=true` with `data[]` (max 100).
- **journeys v1** - `POST /distributionRequests`: <=100 recipients per call; beyond that Workday requires Mass Operation Management (error A2643).
- **prismAnalytics v3** - the classic wBucket flow (Tables/Buckets/Data Changes) - see prism-and-reporting.md and studio-patterns.md section 2 (in the wd-integration-dev skill) before using.
- Big functional surfaces when an app touches HCM/FIN/Student directly: **staffing v7** (144 ops), **person v4** (113), **projects v3** (64), **procurement v5** (44), **performanceEnablement v5** (42), **common v1** (40 - workers, orgs, currencies, validateWorktags), plus the student* family.

### Operations exercised from Workday App Catalog samples (sample-verified - REST/SOAP ops seen called from a flow or page)

- **`POST /payroll/v2/payrollInputs`** - create payroll input via REST from a flow. **This is the REST alternative to the SOAP `Import_Payroll_Input` / `Submit_Payroll_Input` path** and directly feeds the Studio->O4I conversion workstream (payroll-input-first): an O4I can POST payroll inputs without dropping to SOAP. (payroll v2 also exposes `payGroups`, `payGroupDetails`, `jobs`, `taxRates`, `minimumWageRates`.)
- **`common v1 /businessTitleChanges`** - REST business-title change (worker business title) instead of a staffing SOAP op.
- **`payroll v2 /taxRates`** - read effective tax rates by jurisdiction (payroll config lookup from a flow/page).
- **help / `workday-help` REST** (`helpArticle v1`, `helpCase v4`) - read/manage Help articles and cases programmatically; a `workday-help` baseUrlType surfaces these to a page.
- **`customObject/v2` write-from-flow** - the `?bulk=true` / `?updateIfExists=true` custom-object CRUD (detailed above) is called from orchestrations too, not just pages.
- **Drive SOAP** - Workday Drive document ops are SOAP-only (no REST surface) - reach for the SOAP service when moving Drive files.
- **`Performance_Management` SOAP ops** - performance-review actions not covered by `performanceEnablement v5` REST live on the SOAP service.
- **`Resource_Management` SOAP asset ops** - business-asset (fixed-asset) operations are SOAP-served.

Cite these as "per Workday App Catalog samples (sample-verified)"; the shape authority for each is still the service JSON in the snapshot.

Build-verified reference patterns still outrank these schemas where they conflict - the schemas are the *shape* authority, not the *behavior* authority (e.g. DECIMAL-as-string serialization quirks live in model.md, not here).

## Graph API (GraphQL) authoring

Workday's Graph API (GraphQL) is a distinct surface from the REST services above: one POST to `.../graphql/v1` runs a typed **query** (read) or **mutation** (write) against the FDM/HCM object graph. Facts here are sample-verified from the App Catalog; the `.graphquery` file type itself is already documented in model.md/pmd.md - this is the authoring depth, not a re-spec of the file.

> Citation currency (2026-08-07): the `createAccountingJournal` sample cited below is NOT in the current canonical DevRel snapshot; present Graph donors are `createSpotBonus`, `createAWorkEvent`, and `vehicleRegistration` (full CRUD). The facts hold - confirm the donor name against the live catalog before citing it to a client.

- **Provider + endpoint wiring (from a page).** A `workday-graph` dataProvider `<% apiGatewayEndpoint + '/graphql/v1/' %>`; an outbound endpoint sets `baseUrlType: "workday-graph"`, `httpMethod: "POST"`, and a `graphQuery: { queryId: "<id>", parameters: { <name>: "<% expr %>" } }` block where `queryId` names a `.graphquery` file under `presentation/graphQueries/`. (Per Workday App Catalog sample createAccountingJournal.)
- **`.graphquery` file shape** (per samples createAccountingJournal / vehicleRegistration): `{ "id", "parameters": [<names>], "query": "<GraphQL text>", "variables": { <name>: "<% <name> %>" } }` - `parameters`/`variables` bind page values into the GraphQL `$variables`; a parameter-less read can omit both.
- **Query vs mutation = same POST.** Both are just the `query` string text - no separate endpoint. Mutations create/update/delete BOTH standard Workday objects (`submitAccountingJournal`, `requestOneTimePayment`, `initiateWorkerFeedback`) AND, for an app's OWN BOs, the app's generated CRUD ops. vehicleRegistration ships full CRUD as 8 graphqueries (create/update/delete mutations + myVehicles/vehiclesByLocation/currentVehicle/distinctLocations/me queries).
- **Combined multi-op mutation = the efficiency lever.** One mutation document can run several ops in ONE request/round-trip. createSpotBonus's `createSpotBonus` mutation fires `initiateWorkerFeedback` + `requestOneTimePayment` together off a shared `$workerId`, so a spot bonus is one atomic Graph call instead of two REST calls - fewer round-trips, one auth, one failure surface. Reach for a combined mutation whenever one action must write two related standard objects. (Per sample createSpotBonus.)
- **(!) Portability gotcha (the big one).** For an app's OWN BOs the GraphQL type/field/input names embed the app **reference id, capitalized, HARDCODED into the query text** - e.g. `VehicleRegistration20241_nkzjqw_createVehicle` / `..._VehiclesSummary_CreateInput!`. There is NO `site.applicationId` interpolation inside the query string, so a `.graphquery` copied to another app needs every embedded ref-id token hand-edited (vehicleRegistration's files carry an explicit `_comment` to replace the id and to keep the Input type capitalized). Standard-object mutations (createAccountingJournal's `submitAccountingJournal`) are portable - only the app's-own-BO names embed the id.
- **Errors arrive HTTP 200 + `errors[]` - always check the body.** A GraphQL failure returns 200 with an `errors[]` array, not a 4xx. Never trust the status code alone: a page reads `responseErrorDetail.errors`; a flow inspects the response body. Graph analog of the SOAP/REST "completes clean but wrote nothing" trap (orchestration.md).
  - **Copyable endpoint config (confirmed 2026-08-07, `vehicleRegistration/presentation/register.pmd`):** on the `workday-graph` endpoint set `"failOnStatusCodes": [{"code": 400}]` AND a `"responseErrorDetail": { "errorSummary": "<% ... %>", "errors": "<% list:mapAttribute(errors, 'error') %>" }` block - `list:mapAttribute(errors,'error')` is the concrete extraction that turns the `errors[]` array into displayable messages. This is the wire-it-this-way form of the rule above.
- **Mutation identifier-input shape (confirmed 2026-08-07, `createAWorkEvent/presentation/graphQueries/`):** pass a WID as `{"id": {"id": "<% worker %>", "type": "WID"}}` (an `id` object wrapping `{id, type}`), NOT a bare string. An UPDATE mutation takes a SEPARATE identifier argument alongside `input` - e.g. `mutation ...($..._input: ...UpdateInput!, $..._workEventsId: IdentifierInput!)` with `workEventsId: $..._workEventsId` - so an update binds both the changed fields (`input`) and the target instance id (`IdentifierInput!`). Saves a trial-and-error cycle when hand-writing app-BO mutations.
- **BP-secured mutations need "(REST Service)" on the BP.** A mutation that initiates a business process (e.g. one-time payment) requires the op added as a **"(REST Service)" Initiating Action on the BP's security policy** or it's denied - wire this on the tenant BP config alongside the app's security-domain grants.
- **Graph from a flow, not just a page.** A `.maya.FlowSync` flow can POST the same `/graphql/v1` - createSpotBonus's OneTimePaymentWithFeedback.orchestration builds the `{query, variables}` doc in a `CreateJson`, POSTs via `SendWorkdayApiRequest` (`path "/graphql/v1"`, auth `_DEFAULT_WORKDAY_CREDENTIAL`), and returns `responseStatusCode` + body from EndSync. Use a flow when the write needs orchestration (loops, error handling, chaining); use a page `graphQuery` for a single submit (createAccountingJournal submits a journal with ZERO orchestrations - pure PMD + `.graphquery`). See orchestration.md (Graph-from-flows).
- **When Graph beats the alternatives.** **Graph** = modern combined/atomic FDM+HCM writes and nested reads (multi-object write in one call; nested related objects in one read). **WQL** = tabular reads (SQL-like, JSON rows). **SOAP** = where REST/Graph coverage is too narrow (most FDM master-data CREATES are still SOAP-only - see orchestration.md SOAP-write pattern). **Extend BO REST** (`/apps/<refId>/v1/<collection>?bulk=true`) = bulk CRUD on the app's OWN BOs (model.md).

## Platform limits and semantics (official-docs - developer.workday.com, 2026-08-25)

- **Graph API (GraphQL) limits (official):** response page size default 20, max 100; request timeout 3 minutes (partial fields returned on timeout); max 500 related-business-object instances per query; file attachments 30 MB per file; 429 Too Many Requests under load - Workday recommends exponential back-off + caching.
- **Custom Object REST v2 semantics (official):** compound instance ID addressing `{businessObjectID};{referenceId}={referenceIdValue}` (e.g. `Employee_ID=21001;grantName=New_Hire`); `?updateIfExists=true` = upsert; `x-validate-only: 1` header = validate without persisting; PUT is PARTIAL (only supplied fields change; cannot change BO ID or Reference ID); DELETE is permanent; **effective-dated custom objects are REST-UNSUPPORTED - SOAP only**; inactive custom list values are rejected.
  - **RECONCILIATION - bulk cap:** the official Custom Object REST v2 page states `?bulk=true` create is MAX 200 items; the snapshot-derived note above says max 100/request, and the Extend app BO REST bulk cap of 100 is BUILD-VERIFIED (model.md) - but that is a different surface (`/apps/<refId>/v1/`). For customObject v2 specifically, treat 100 as the safe batch size and 200 as the official ceiling; build-verify before batching above 100.
- **Explorer is JS-rendered:** the REST API Explorer and the docs left-nav render client-side - a static fetch gets NO service list, so catalog refreshes MUST go through the local snapshot routine above (user-interactive export). This corroborates the login/fetch caveat at the top of this file.
- **Regional gateways (official):** cross-region API calls fail with 401 - the region is fixed by the Developer Site profile, so always use the matching regional gateway (US `api.workday.com` / `api.us.wcp.workday.com`, EU `api.eu.wcp.workday.com`, SG `api.sg.wcp.workday.com`, UK `api.uk.wcp.workday.com`; personal dev accounts `api.odp.wcp.workday.com`). Full gateway + auth-URL table lives in wd-auth `references/oauth-setup-guide.md`.

## Full service inventory (snapshot 2026-07-27)

| Service | Ver | Base path | Resources (tags) | Ops |
|---|---|---|---|---|
| absenceManagement | v5 | `/absenceManagement/v5` | balances, workers | 15 |
| accountsPayable | v1 | `/accountsPayable/v1` | sendSupplierInvoiceAttachmentsForScanning, supplierInvoiceRequests | 12 |
| asor | v1 | `/asor/v1` | agentDefinition, agentResourceSearch, registration | 6 |
| attachments | v1 | `/attachments/v1` | graphql | 1 |
| benefitEnrollmentEventOfferings | v1 | `/benefitEnrollmentEventOfferings/v1` | employeeEnrollmentEvent | 2 |
| benefitPartner | v1 | `/benefitPartner/v1` | programs | 1 |
| budgets | v1 | `/budgets/v1` | runBudgetCheck | 1 |
| businessProcess | v1 | `/businessProcess/v1` | eventSteps, events, types | 21 |
| common | v1 | `/api/common/v1` | businessTitleChanges, currencies, customers, jobChangeReasons, organizationTypes, organizations, supervisoryOrganizations, validateWorktags, workers | 40 |
| communications | v1 | `/communications/v1` | managedRecipient | 1 |
| compensation | v3 | `/compensation/v3` | scorecardResults, scorecards, workers | 14 |
| connect | v2 | `/connect/v2` | messageTemplates, notificationTypes, sendMessage | 10 |
| contractCompliance | v1 | `/contractCompliance/v1` | supplierContracts | 4 |
| coreAccounting | v1 | `/coreAccounting/v1` | currencies, evaluateAccountPostingRules | 3 |
| customObject (multi-instance) | v2 | `/customObject/v2` | Custom Objects, {Business Object} | 5 |
| customObject (single-instance) | v2 | `/customObject/v2` | Custom Objects | 4 |
| customerAccounts | v1 | `/customerAccounts/v1` | customers, invoicePDFs, invoices, payments | 11 |
| customObjectDefinition | v1 | `/customObjectDefinition/v1` | definitions, fieldTypes | 29 |
| expense | v1 | `/expense/v1` | entries, expenseItems, reports | 17 |
| finTaxPublic | v1 | `/finTaxPublic/v1` | electronicReportingRuns | 1 |
| globalPayroll | v1 | `/globalPayroll/v1` | authorizations, effectiveChanges, eventDrivenIntegrationVendorResponse, notifications, payGroups | 11 |
| graph | v1 | `/graph/v1` | versions | 2 |
| helpArticle | v1 | `/helpArticle/v1` | articleStatuses, articleVersions | 13 |
| helpCase | v4 | `/helpCase/v4` | attachments, caseSuggestions, caseTypes, cases, configuration, externalCreators, externalRecords, serviceCategories | 35 |
| holiday | v1 | `/holiday/v1` | holidayEvents | 1 |
| journeys | v1 | `/journeys/v1` | distributionRequests | 2 |
| learning | v1 | `/learning/v1` | content, enrollments, manageDigitalCourses, manageEnrollments, records | 18 |
| oAuthClient | v1 | `/oAuthClient/v1` | clientDetails | 2 |
| payroll | v2 | `/payroll/v2` | jobs, minimumWageRates, payGroupDetails, payGroups, payrollInputs, taxRates | 25 |
| performanceEnablement | v5 | `/performanceEnablement/v5` | cascadedGoalEvent, feedbackBadges, giveRequestedFeedbackEvents, myPerformanceReviews, organizationGoals, workerGoalEvents, workers | 42 |
| person | v4 | `/person/v4` | countries, homeContactInformationChanges, people, phoneValidation, workContactInformationChanges | 113 |
| prismAnalytics | v3 | `/prismAnalytics/v3` | Tables, Buckets, Data Changes | 21 |
| privacy | v1 | `/privacy/v1` | activityLogging | 1 |
| procurement | v5 | `/procurement/v5` | purchaseOrders, requisitionTemplates, requisitions | 44 |
| projects | v3 | `/projects/v3` | adHocProjectTimeTransactions, planPhases, planTasks, projects, resourceForecastLines, resourcePlanLines, taskResources | 64 |
| recruiting | v4 | `/recruiting/v4` | interviews, jobPostings, prospects | 31 |
| request | v2 | `/request/v2` | requests, types | 6 |
| revenue | v1 | `/revenue/v1` | billableTransactions | 5 |
| skill | v1 | `/skill/v1` | mlSkills | 1 |
| staffing | v7 | `/staffing/v7` | jobChanges, jobFamilies, jobProfiles, jobs, organizationAssignmentChanges, supervisoryOrganizations, workers | 144 |
| studentAcademicFoundation | v1 | `/studentAcademicFoundation/v1` | academicCalendars, academicLevels, academicPeriods, academicUnits, educationalCredentials, programsOfStudy | 14 |
| studentAdvising | v1 | `/studentAdvising/v1` | hypotheticalAcademicProgress | 4 |
| studentCore | v1 | `/studentCore/v1` | holds, immigrationEvents, students | 35 |
| studentCurriculum | v1 | `/studentCurriculum/v1` | courseSections, courseSubjects, courses | 6 |
| studentEngagement | v1 | `/studentEngagement/v1` | students | 4 |
| studentFinance | v1 | `/studentFinance/v1` | students | 6 |
| studentRecruiting | v1 | `/studentRecruiting/v1` | academicRequirementEvaluation | 6 |
| systemMetrics | v1 | `/systemMetrics/v1` | activeTasks, activeUserSessions, systemMetricsOverview | 6 |
| talentManagement | v2 | `/talentManagement/v2` | createMentorshipForMe, createMentorshipForWorker, mentorships, successionPlanEvents, successionPlans | 21 |
| worktag | v1 | `/worktag/v1` | validateWorktags | 1 |
| wql | v1 | `/wql/v1` | data, dataSources | 8 |

Notes: student* services expose `me` as a valid path ID (self-service context). studentEngagement's `/students/{ID}/holds` is **deprecated** (2024-04-05) in favor of studentCore `/holds`. Several services flag deprecated/retired fields inline (`classStanding` -> Latest Class Standing) - check descriptions before binding to a field.
