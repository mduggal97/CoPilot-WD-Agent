# Error handling, logging, retries, and recovery

How an Extend app reports, logs, retries, and recovers - pages + orchestrations + house conventions.
This file is the HUB: orchestration.md owns node vocabulary, pmd.md owns the page widget surface;
this file owns the error STORY. Provenance: "sample-verified" = a named Workday App Catalog sample;
"build-verified" = proven in a delivered build/production app; "(!) verify" = inference.

## Layer 1 - PAGE: what the user sees when something fails

### Endpoint failure handling
- `failOnStatusCodes: [{"code": 400}, ...]` on an outbound endpoint declares which HTTP statuses
  fail the submit; without it a bad status can pass silently. Pair with `responseErrorDetail` to
  shape the user-visible message (build-verified, delivered production app - see pmd.md).
- `responseErrorDetail.errorSummary` is an expression with implicit `error` / `errors` variables.
  Real shape (sample-verified, badge-scanning `customErrorView.pmd`):

```json
"responseErrorDetail": {
  "errorSummary": "<% ! empty errors ? [error].addAll(errors.map(e => {e.error})).join('\\n') : [error] %>"
}
```

- GraphQL trap: Graph errors arrive HTTP 200 + `errors[]` - `failOnStatusCodes` alone will not
  catch them; read `responseErrorDetail.errors` / `list:mapAttribute(errors,'error')`
  (rest-api-catalog.md, sample-verified).
- BUILD-VERIFIED: `bestEffort: "true"` on a non-deferred inbound endpoint lets it fail soft -
  the endpoint result is undefined but the page still renders. Use for page-load endpoints that
  may 404/error (e.g. `workers/me` under ISU login). `failOnStatusCodes` is for OUTBOUND/submit
  endpoints ONLY - it has NO effect on page-load endpoints. Verified in UAP v2 build
  b39834766401d3acfe7496ceec484c88 (2026-08-28).
  NOT a fix on a DEFERRED endpoint (runtime-verified 2026-10-05; pmd-gotchas #85). On a deferred
  `.invoke()`, a flow that COMPLETES with a non-JSON answer shows the platform page error, and a
  flow that FAILS comes back as an empty answer with no error (corrected 2026-10-07 from the
  developer-site log). The script can catch neither. Fail soft in the flow.

### In-page error display
- `applicationException` - declarative page-level error/warning banner (sample-verified,
  `AWSBadgeGenerator`, `commutingEmissionsSurvey`): a `presentation.applicationExceptions[]` entry
  `{"type":"applicationException", "severity":"ERROR"|"WARNING", "message":"...", "render":"<% expr %>"}`.
  Prefer over the old setError + richText-div banner workaround.
- Field-level: `widget.setError(msg)` / `widget.clearError()` from script (sample-verified).
  Build-verified trap (pmd-gotchas #52): `setError()` inside `onSubmit` forces a transaction
  ROLLBACK of script-side `.invoke()` writes - do not mix script-side POSTs with onSubmit gating.
- Cross-field submit gate: a widget `validations` array with a `value` EXPRESSION (true = valid)
  + `errorMessage` - the build-verified way to block OK where `required` cannot (pmd-gotchas).
- Message discipline: users get short, coded, catalog-driven messages (Layer 3) - raw
  `processingError` / `errors[]` payloads belong in logs, never on screen.

### Custom error pages (SMD-routed)
- `errorPageConfigurations` in the `.smd` routes HTTP errors to a branded PMD (build-verified for
  400/401/403/404/407/408/500/503):
  `"errorPageConfigurations": [ { "statusCode": "400", "page": { "id": "errorPage" } }, ... ]`
- The routed page receives implicit `errorCode` and `errorMessage` variables (sample-verified,
  `orchestrationManager/presentation/genericErrorRedirect.pmd`: title `<% 'Error Code ' + errorCode %>`,
  body texts bound to `<% errorMessage %>` / `<% errorCode %>`, plus a LINK button back to `home`).
- Production exemplar (a delivered supply-chain app, `errorPage.pmd`): one page, per-code friendly
  copy via `visible` gates - `"visible": "<% errorCode == '401' %>"` -> "We couldn't verify your
  identity...", 404/408 variants - plus a raw `HTTP Error code: <% errorCode %>` detail line and a
  branded image from a script module (`errorImage.script` returns a base64 data-URI read by an
  image widget as `<% errorImage.errorImageBase64EncodedFormat() %>`).
- Translated exemplar (sample-verified, badge-scanning `customErrorView.pmd`): the error page loads
  a translations BO in `onLoad`; labels read `pageVariables.translations.get('key')` - an error
  page is still a page with the full i18n chain.


## Layer 2 - FLOW: how an orchestration fails, retries, and recovers

### ErrorHandler anatomy
An `ErrorHandler` attaches to a node/group (local) or at flow level (global). Strategy enum
(sample-verified across the orchestrationToolkit samples): `PropagateError` (run handler nodes,
then raise), `ConditionalOutputs` (absorb - the failed node exposes `isSuccess` and the flow
continues), `GlobalErrorHandler` (the flow-level catch-all).

Local handler, trimmed shape (sample-verified, `LocalErrorHandlerPropagateNoGlobalHandler.orchestration` -
the real file wraps every value in the typed-AST `{"_type","_value"}` envelope):

```json
"errorHandler": { "name": "_errorHandler_CreateValues", "strategy": "PropagateError",
  "nodes": [
    { "CreateTextTemplate": "{ \"locationId\":\"{{data.CreateValues.processingError.locationId}}\",
                                \"locationPath\":\"{{data.CreateValues.processingError.locationPath}}\" }" },
    { "Log": "data(\"CreateValues\", \"processingError\").message()" } ] }
```

Global handler reads `data("_orchestration","processingError")` instead (sample-verified,
`GlobalErrorHandlerDemoNoModificationOfResponse` logs `.locationId` / `.locationPath` / message;
`AsynchGlobalErrorHandlerLogging` is the async `.Mixed.MixedFlow` variant - same `_globalErrorHandler`
block, Log node only). Loop-group handlers expose `data._group_X.isSuccess` and
`data._group_X.processingError.locationId()/.rawMessage()` (orchestration.md).

**A global handler cannot read the launch inputs (build-verified 2026-10-07, a client app).**
Referencing `data.start.headers...` inside `_globalErrorHandler` fails the build with "There is no
upstream component with id start". So a global handler cannot branch on who called the flow. When
the error answer must differ per caller, use step-level ConditionalOutputs handlers and do the
caller check in normal steps after them: a ContinueOnConditions gate re-raises for one caller, and
the EndSync mapping shapes the answer for the other (worked example: pmd-gotchas.md #85).

### Shaping the sync response on error
- `ConditionalOutputs` + a conditional EndSync mapping (sample-verified,
  `LocalErrorHandlerConditionalOutputNoGlobal`): `if ((data("CreateValues","isSuccess") == true))
  data("CreateValues","Input") else "<fallback text>"`. Rule the sample itself states: the EXACT
  error cannot be surfaced as flow output from a LOCAL handler - only logged.
- Global-handler shaping (sample-verified, `ModifyingSyncOrchResponseWithErrorHandlerOutput`): the
  global handler builds a message node; EndSync maps
  `$.successful = if (data("_orchestration","isSuccess") == false) false else true` and
  `$.response = if (...isSuccess == false) data("GlobalErrorHandlerCreateTextTemplate","message") else <normal>`.
  Only values defined IN the global error handler are returnable in the error response.
- No handler at all (sample-verified, `ValidateWithCustomResponseForcedUnhandledError` forces
  `math.div(1,0)`): the caller gets the platform's raw unhandled-error response, not your shaped
  JSON. Every sync flow a page calls needs a global handler + shaped `{successful, response}`.
  **What a PMD page sees (log-verified 2026-10-07, a client app):** a failed flow called
  through a deferred endpoint's `.invoke()` comes back as an EMPTY answer, with no page error
  and nothing the script can test. `math.div(1, 0)` in a value step does raise ("/ by zero"), and
  so does a false ContinueOnConditions assertion - both failed the flow, and both looked like
  "no data" on screen. Only a shaped answer reaches the page (pmd-gotchas #85).

### Retries, success ranges, and the 4xx-silent-failure trap
- `SendWorkdayApiRequest` does NOT hard-fail on 4xx - a rejected POST "completes clean" with 0
  records written (HIGH, silent data loss - orchestration.md caveat, build-verified). A clean
  completion is not proof of a write.
- Declarative fix - a `retryConfig` resource with `successResponseCodeRanges` (sample-verified,
  `HTTPwithValidResponseCodesConfig.orchestration`); a status outside the range finally raises:

```json
"retryConfigs": { "lPp8JOl3": { "value": {
  "name": "errorConfig",
  "maxTotalRetries": 0,
  "successResponseCodeRanges": [ { "begin": 200, "end": 299 } ],
  "defaultBackOff": { "intervalMs": 1000, "factor": 1.0, "maxBackOffMs": 300000 },
  "retryPolicies": [] } } }
```

  Reference it on the Send node via `"retryConfigRef": "lPp8JOl3"`; named defaults exist
  (`_DEFAULT_WORKDAY_RETRY_CONFIG` / `_DEFAULT_EXTERNAL_RETRY_CONFIG` / `_DEFAULT_INTEGRATION_RETRY_CONFIG`).
  Counter-example (sample-verified, `HTTPwithGlobalErrorHandlerNoValidResponseCodesSet`): with the
  default config and no ranges, NO handler triggers for ANY status - even a global handler sits idle.
- Per-node form on `SendWorkdayApiRequest`: `"responseCodeRange": {"begin": 200, "end": 208}`
  (sample-verified, LunchAccount PATCH nodes). Imperative guards:
  `data.<Send>.responseStatusCode.is2xxStatusCode()`, `response.isSoapFault()`,
  `ContinueOnConditions` assertions (orchestration.md, sample-verified).

### A vendor's non-2xx can be a valid ANSWER - probe before you guard on status
**Runtime-verified 2026-10-08 (a client app, build f2972840).** A status guard written as
"non-2xx = the call failed" turned a vendor's ordinary "no data" reply into a fake outage. The vendor
(the vendor) sends `{"state": 2, "messages": ["No data is available ..."]}` with **HTTP 404**. The
guard replaced it with "The call failed (HTTP 404) - check the address", and the page then held back
its no-match fallback. Live tests of the guard passed, because they only broke the call (wrong path,
unreachable host); none asked for a combination the vendor has no data for.

- **Before writing any status guard, probe the vendor's non-success-but-valid answers** - no data,
  not found, validation refusals - and record the status and body of each. Many REST APIs use 404 or
  400 with a readable JSON body for these.
- **Pass the vendor's own answer through whatever its status; synthesize an error only for a reply
  that is not the vendor's answer.** Detect the answer by its shape, not the status. Build-verified
  expression: `data.<Send>.response.toString().contains("\"state\"")` (the vendor's own key, quoted,
  so an HTML error page never matches). `response.asJSON()` cannot be the test - it does not check the
  body (gotcha #85).
- **Order the OR so callers that must not change never read the body.** The shipped form:
  `is2xxStatusCode() || <caller-opts-out test> || response.toString().contains(...)` - the
  standalone caller stops at the second test and behaves exactly as before.
- **Add a negative-path test that sends a no-data request through the guarded path** (a gateway
  launch with the caller's headers is enough), next to the break-the-call tests.

### Gate a write's outcome on 2xx + a positive marker (never faultstring-only)
Do NOT decide a write's success/failure (or a persisted status like Active/Removed) from the SOAP
`faultstring` alone. **Anti-pattern (real defect, found across multiple provisioning flows; build-verified):**
`data.<Send>.response.asXML().isValueAtXPath(".../SOAP-ENV:Fault/faultstring")` as the SOLE signal is
silently wrong twice - (1) an HTTP-level failure (5xx / gateway / 403 / blank body) usually has NO
well-formed faultstring at that XPath, so it reads as SUCCESS and writes phantom Active/Removed rows that
corrupt the source of truth; (2) a validation discard (`Discard_On_Exit_Validation_Error=true`) returns a
normal 2xx with the event NOT applied - also read as success.

**Correct gate - require POSITIVE proof of success (build-verified, deployed):**

```
data.<Send>.responseStatusCode.is2xxStatusCode()
  .and(data.<Send>.response.toString().contains("Event_Reference"))     // the op's own positive marker
  .and(data.<Send>.response.toString().contains("faultstring").not())
  .and(data.<Send>.response.toString().contains("Validation_Error").not())
```

Use `.response.toString().contains(...)` (robust even when the body is not well-formed XML), and pick the
operation's own positive marker (Assign_Roles -> `Event_Reference`; other ops have their own
`<wd:*_Event_Reference>`). The mirror for an IF / `BranchOnConditions` "did it fail" branch is
`is2xxStatusCode().not().or(contains("faultstring")).or(contains("Validation_Error"))`.

**Idempotency note (verified live):** Workday REJECTS removing a non-held role assignment with a fault
("Role Assignees to Remove must be an existing assignee") - it is NOT a no-op. Make a remove idempotent by
EXCLUDING already-removed rows in the selector, not by relying on a "no-op-accepted" remove.

Codified: `scripts/pmd_preflight.py` FAILs a `.orchestration`/`.suborchestration` that gates on `faultstring`
with no `is2xxStatusCode` guard (`EH:write-gate`).

### Validate node + failedValidations iteration
Input gate at the top of a write flow (sample-verified, `ValidateWithValidationIterator.orchestration`):
each `ValidationCheck` = `{name, severity: "ERROR", expression: <bool>, summary: <message>}`.
Outputs: `data("Validate","allValid")` and `data("Validate","failedValidations")` (iterable).
Failure branch: Loop `failedValidations`, per item build
`{"ValidationName":"{{item.name}}", "SeverityLevel":"{{item.severity}}", "Summary":"{{item.summary}}"}`,
Log each, collect via a `JsonFoldValue` aggregate, return
`{"successful": false, "response": {{data.Loop.JSONListOfValidations}}}` from EndSync.

### Compensating rollback (journal-then-compensate)
O4I has no transaction - unwind a partial bulk write yourself. Node sequence (sample-verified,
`LunchAccountUpdateWithRollback.orchestration`):
1. `DeleteJournals` - clear the journal BO (WQL ids -> bulk DELETE) so each run starts clean.
2. `MakeChanges` Loop per input row:
   a. `CollectCurrentState` - GET the current value (local `ConditionalOutputs` handler: log-and-continue).
   b. `BranchOnConditions` on `data("GetPreviousValues","isSuccess")` - journal only when the old
      value was captured: POST a journal row `{accountID, lunchBalance:<old>}`.
   c. `PatchInChange` - PATCH the new value, `responseCodeRange` 200-208, and a `PropagateError`
      handler whose nodes ARE the rollback: `GetJournalsForRollback` (WQL read the journal) ->
      Loop PATCHing each original value back -> `ContinueOnConditions` with assertion `false`,
      message "An error was detected and all changes have been rolled back." (the always-false
      assertion re-raises so the caller sees the failure AFTER compensation).
3. Aggregate `NumberFoldValue` of `PatchInChange.responseStatusCode` -> EndSync returns the code list.

### Operational logging and bulk error collection
- `SendIntegrationMessage` - writes to the integration event log with a `severity` (INFO/WARN/...)
  and a `condition` expression; gate DEBUG-severity messages on a launch param or integration
  attribute so verbose logging is a runtime toggle (orchestration.md, sample-verified).
- Bulk/batch error rows (sample-verified pair `bulkErrorsMultiPage.orchestration` +
  `testOrchestrateBulkErrors.pmd`): the flow pages input `.iterator("$.data[*]", 100)`, POSTs each
  page to the BO collection with `?bulk=true`, and folds the PER-ROW responses (each row carries
  its own `status` + `body.error`) into one flat array. The page keeps only failures for fix-and-resubmit:

```js
// page script (sample-verified): map grid rows to POST responses, keep only errors
newRow.status = postRow.status;
if (newRow.status != 201) { newRow.message = postRow.body.error; }
const failureRows = newGridRows.filter(tempRow => {tempRow.status != 201});
```

  Good rows commit; error rows return to the grid with code + message. Use when >100 rows expected.

## Layer 3 - CONVENTIONS: the house standard

### Level-gated logging module (build-verified, a delivered production app: logging.script)

```js
script.include("setupSetting.script");
var logData = function(level, message) {
  if (level == setupSetting.getLoggingMode()) {
    if (level == 'debug')      { console.debug('Debug the current value: ', message); }
    else if (level == 'error') { console.error('Invalid value error: ', message); }
    else if (level == 'info')  { console.info('Informational value: ', message); }
    else if (level == 'warn')  { console.warn('Warning value: ', message); }
  };
};
{ "logData": logData };
```

`setupSetting.script` owns `getLoggingMode()` / `setLoggingMode(level)`; pages call
`logging.logData('debug', payload)` everywhere and the level decides what lands. (!) verify: in
that app the mode is a script-local default - back it with an App Attribute so admins change it in-tenant.

### Coded message catalog (build-verified, same app: errorMessages.script)

```js
var getErrorMessage = function(lookupKey) {
  var errorMessageList = [
    { "messageDescription": "Invoice Number cannot be empty", "code": "1000", "isActive": true },
    { "messageDescription": "Invoice Amount cannot be empty", "code": "1001", "isActive": true }
    // ... one entry per user-facing message, codes grouped by page/feature
  ];
  var errorMessageMap = {:};
  for (var errorMess : errorMessageList) {
    if (errorMess.isActive) { errorMessageMap.put(errorMess.code, errorMess); }
  };
  return errorMessageMap.get(lookupKey).messageDescription;
};
{ "getErrorMessage": getErrorMessage };
```

Pages call `errorMessages.getErrorMessage('1004')` in `setError` / `applicationException` message
expressions. One catalog = consistent wording, searchable codes in logs, `isActive` retirement.

### Debug toggle + log surfaces
- Gate `console.info()` diagnostics behind an App Attribute:
  `attrstore.debugFlag ? console.info(...) : null` - admins toggle in-tenant, no redeploy
  (build-verified house convention; standards.md). Leave gated calls in shipped code.
- `console.debug/info/warn/error` all land in Analytics/Logs - filter `wd_category is console`
  (sample-verified). Orchestration run logs: filter `wd_log_type = remote`, read
  `wd_response_code` / `wd_message` for API-call debugging.
- Audience split: `console.*` + flow `Log` nodes = DEVELOPER surface (Analytics/Logs);
  `SendIntegrationMessage` = ADMIN surface (visible on the integration event without log access);
  coded catalog messages + error pages = USER surface.

### Correlation discipline
Every log line must make a failure traceable without a debugger: flow/page name, the node or step
(`processingError.locationPath` gives it free in handlers), and the row/business identifier being
processed (account ID, invoice number, worker WID). The rollback sample logs the whole failed
`item`; the validation sample logs name + severity + summary per rule - copy that habit.

## Decision table: failure type -> handler

| Failure type                     | Surfaces where             | User/admin/dev sees                        | Your handler |
|----------------------------------|----------------------------|--------------------------------------------|--------------|
| Page endpoint 4xx/5xx            | Submit blocked on page     | `responseErrorDetail.errorSummary` text    | `failOnStatusCodes` + errorSummary |
| Page-load HTTP error (401/404..) | Whole page replaced        | Branded error page (errorCode/errorMessage)| SMD `errorPageConfigurations` + errorPage.pmd |
| Field/cross-field input error    | Inline on the widget       | `setError` text / `validations` errorMessage | catalog-coded message |
| Page-level condition             | Banner                     | `applicationException` message             | render-gated exception entry |
| Flow input bad                   | Sync response              | `{successful:false, response:[validations]}` | Validate + failedValidations loop |
| Workday API 4xx in a flow        | NOTHING by default (trap)  | dev: log; caller: shaped error             | successResponseCodeRanges / is2xxStatusCode + handler |
| Node failure, keep going         | Flow continues             | dev: handler Log                           | local ErrorHandler, ConditionalOutputs |
| Node failure, must abort         | Flow fails                 | caller: global-handler response; dev: log  | PropagateError local + GlobalErrorHandler shaping |
| Partial bulk write               | Some rows committed        | admin: event log; user: error rows in grid | journal-then-compensate rollback; bulk per-row filter |
| Anything, unhandled              | Platform error blob        | raw platform message (avoid)               | always add a global handler on page-called flows |

## Cross-references
- orchestration.md - node vocabulary, ErrorHandler/retryConfig source anatomy, 4xx caveat origin.
- pmd.md - page surface: applicationException, failOnStatusCodes/responseErrorDetail, SMD error pages.
- rest-api-catalog.md - GraphQL 200-with-errors handling.
- external-apis-and-genai.md - external-call failure handling from pages.
- app-review-audit.md - error handling is an audit dimension; use this file as the checklist source.
