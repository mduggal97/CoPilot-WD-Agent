# Custom Business Process on a BO ("Model BP") - verified schema

Pattern verified in a deployed build (e.g., a delivered app, `masterDataRequest`); a full reference family is downloadable as example provenance: `jlvModelBusinessProcessesApp`, `modelBusinessProcessApp`, `subBusinessProcess`, `triggerOrchestrationsWithBpsAppng` (Workday sample apps).

## The .businessprocess file

```json
{ "id": 1, "name": "CreateCostCenterRequest", "label": "...", "useForOrchestrate": false,
  "allowsCancel": true, "allowsManualSendBack": false, "targetBusinessObject": "Request",
  "securityDomains": ["MasterDataRequestPages"],
  "approvalStep": { "pageRoute": "/approveCostCenter/{eventId}", "actions": ["APPROVE","DENY"] },
  "details":      { "pageRoute": "/detailsCostCenter/{eventId}" } }
```

- **SEND_BACK requires `revisePageRoute` + a revise page** (build error P400 otherwise) - omit SEND_BACK or add `"revisePageRoute": "/revise/{eventStepId}"`. Optional `actionSteps[]`: `{id, name, label, pageRoute: "/review/{eventStepId}"}`.
- Every pageRoute must map to an AMD task whose `routingPattern` matches EXACTLY, param as the FINAL segment. Approval/details routes get `{eventId}` (the BP event WID); action/revise routes get `{eventStepId}`.
- `useForOrchestrate: true` is the hook for write-on-approval (an orchestration triggered on BP completion). `allowsRescind: true` is also a valid root key (verified in a delivered production app, 2026-08-05).
- **Headless variant (verified in a delivered production app, 2026-08-05):** a `.businessprocess` with `useForOrchestrate: true` and NO `approvalStep`, NO `details`, and empty `actionSteps` is legal - it exists purely as an async-job hook. A flow POSTs `/v1/<bpNameLowerCamel>Events` to fire it, and the BP triggers the downstream (BP-triggered) orchestration. BP events can be launched FROM a flow this way - the page-side two-POST chain below is not the only launcher.
- **[BV 2026-09-04] Model BP TYPE NAMES are TENANT-GLOBAL - a name collision fails the DEPLOY silently.** Two apps deployed to the same tenant cannot both declare a `.businessprocess` with the same `name`: the second app's `wdcli app deploy` returns `success: false` with NO error text (JSON output included), while its BUILD passes clean - so the failure looks like wdcli flakiness. Diagnose by probing whether the sibling app is deployed (its BO REST returns S22, not 404) and comparing BP names. Fix = rename the BP (remember the events collection renames with it: `<bpNameLowerCamel>Events` - grep every PMD/flow for the old collection). Hit on a replacement app deployed beside its predecessor: 3 silent deploy failures until the BP was renamed. RULE: a replacement/clone app deployed alongside the original MUST rename its model BPs.
- The multi-step approver chain is NOT in this file - it's configured on the BP definition in-tenant after deploy (per-tenant setup; see security-setup.md).
- **`allowedParentProcesses` - run a custom BP as a SUB-PROCESS of a NATIVE Workday BP (per Workday App Catalog samples, sample-verified).** A root-level `allowedParentProcesses` array (listing the native parent BP type(s), e.g. Hire / Job Change) lets the custom `.businessprocess` be added as a sub-process step inside a delivered Workday BP, and lets it **inject its Extend initiation page into that native process** - so the custom Extend form runs as a step of, say, Hire, rather than only as a standalone Extend-launched BP. Use this when the requirement is "add our custom data-capture step into an existing Workday process," not a wholly separate request.
- **Actions-only approval step - omit `pageRoute` (per Workday App Catalog samples, sample-verified).** An `approvalStep` (or `actionSteps[]` entry) may carry `actions` with NO `pageRoute`: the step is pure inbox action buttons over Workday's native event summary, with no custom Extend review page to build. Reach for this when the approver just needs APPROVE/DENY on the standard summary; add a `pageRoute` only when you need a custom rendering of the BO for review. (Contrast the `approvalStep.pageRoute` example above, which DOES render a custom page.)

## Launching the BP - two chained POSTs on the create page

Extend chains them automatically by data dependency:

```
1) POST <BO collection>  (name it e.g. "createRequest")            -> returns createRequest.id (BO WID)
2) POST "<bpNameLowerCamel>Events"  (baseUrlType "app")
   values: [{ outboundPath: "businessProcessTarget.id", value: "<% createRequest.id %>" }]
```

The BP-events collection name = the BP `name` in lowerCamelCase + `Events` (e.g. `createCostCenterRequestEvents`).

## The approval/details page

Opened from the Workday inbox, the route supplies `queryParams.eventId` (BP event WID). Resolve the target BO in two endpoints:

```
getRequestId (workday-wql): SELECT businessProcessTarget FROM <% site.applicationId %>_createCostCenterRequestEvents
                            WHERE workdayID = "<% queryParams.eventId %>"     (url: 'data?query=' + query.urlEncode())
getRequest   (app):         'requests/' + getRequestId.data[0].businessProcessTarget.id
```

Fields read directly off `getRequest` (single-instance - NOT `.data`). APPROVE/DENY buttons are platform inbox chrome from the approval step, not widgets you build - the page only renders the BO for review. `site.applicationId` works in PMD inline expressions (it's reserved only inside `.script` files).

**Flow-side equivalent (per Workday App Catalog samples, sample-verified).** A BP-triggered (or BP-event-handling) orchestration resolves the same target WITHOUT a WQL round-trip: `GET .../v1/<bpNameLowerCamel>Events/<eventId>` and read `$.businessProcessTarget.id` to get the target BO WID, then GET that BO. Use the WQL lookup on the page, the direct events-collection GET in a flow (see orchestration.md "Flow-side BP-event -> target BO resolution").

## Completing an action step from a page (programmatic step submission)

When the BP's work step is an `actionSteps[]` form rather than an approval, the action page completes the step itself. The route supplies `{eventStepId}`; a deferred `wd-bp` endpoint submits it. Source: developer.workday.com "Submit Event Steps REST API" (official docs).

```
POST "eventSteps/{eventStepId}/submit"      baseUrlType wd-bp, authType sso
body:  { "comment": "<optional>" }          {} is the documented example
reply: { "id", "descriptor",
         "stepAction": { "descriptor": "Submitted", "id": "d9e4223e446c11de98360015c5e6daf6" } }
```

This POST is what advances the BP past the action step - the APPROVE/DENY inbox chrome only exists on approval steps.

- **Prerequisites (official):** an Extend BP, not a Workday-delivered one. The CURRENT user is awaiting action on the step. The step is an Initiation or an Action step.
- **Gateway only (official).** The endpoint exists on the Extend API gateway, never on the tenant URL. The API's own `swagger.json` (`GET businessProcess/v1/swagger.json` with a tenant token; read 2026-09-28 and 2026-10-06) does not list it, so a path guard pinned from that swagger wrongly flags `/submit`. That swagger lists the other step verbs: approve, deny, reassign, sendBack, submitTaskStep, toDo, questionnaire.
- **Do not borrow a body from those neighbours.** In that swagger, `/toDo` and `/questionnaire` REQUIRE `stepAction`, and their descriptions are where the Submit WID `133d5c88...` comes from (valid only for To Do and Complete Questionnaire steps). `/submitTaskStep` is for Task events that orchestrate sub-process steps. None of them is the Extend action-step call.
- **`stepAction` is reply-only - never send it.** Runtime-verified refusals, 2026-10-06, a client app. Both built clean and failed live:
    - the step's task WID: "Invalid id for field" (field=stepAction);
    - the delivered Submit step-action WID `133d5c88baa64136aab041c1d2e9ed53`: **A169 "This step isn't valid for submission"**.
    - Preflight FAIL #87 catches it. **Correction:** this section used to teach `{ "stepAction": { "id": "<action WID>" } }`. That was wrong.
- **`/approve` on an action step is refused with A190** "This event step type cannot be approved". Approve and deny belong to approval steps.
- **A refused submit returns an error object; it does not throw** (runtime-verified 2026-10-06). Check `res.error` before telling anyone, or any other system, that the step completed.
- **Workday's documented order:** update the target BO through Extend BO REST, then submit the step.
- **Status: runtime-verified 2026-10-06** (a client app build `d82eedc9`, a dev tenant). The approver, working by proxy, submitted `{"comment": "approve"}` from the action page. Workday answered **HTTP 201** with `stepAction` Submitted (`d9e4223e...`). The step read back **Submitted**, the event **Successfully Completed**, and the later calls on the page (platform, BO patch) ran on the success branch. A user acting by proxy counts as the awaiting user.

## Custom-validation matrix & business-process landmines
> Folded in from a config-guide distillation sweep (2026-08-10). Vendor-neutral; no client specifics.

- ****Custom-validation matrix pattern:**** A maintainable pattern for a matrix of custom validations across many transaction types. Model each validation as a row with three parts: (1) a stable **condition-rule ID** (e.g., CONDITION_RULE_<SHORT_NAME>) that the validation is keyed to, so the rule logic and its message stay linked and are easy to audit; (2) **help text that injects dynamic transaction fields at runtime** - write the message with placeholders for the actual values that tripped the rule (the offending category, the funding source, the object, a date), plus a plain-English "what to do next / who to contact" instruction, so the end user sees a specific, actionable message rather than a generic failure; and (3) a **severity per transaction type** expressed as a grid - the SAME logical rule can be a hard error (block) on some documents, a warning (soft, proceed-with-acknowledgement) on others, and "not available"/not applicable on the rest. Decide error-vs-warning by whether proceeding is ever legitimately correct: block only when the action is never allowed, warn when it is usually wrong but a valid exception exists. Keep the whole matrix in one source-of-truth table (rule ID x transaction type -> severity) so reviewers can see coverage and gaps at a glance. (Example domain: grant spend restrictions - e.g., an unallowable-category or closed-funding-source rule that hard-blocks on some spend documents but only warns on internal/journal documents - but the pattern is general to any regulated-transaction validation.)

- ****Business-process landmines:**** Two tool-agnostic Workday BP gotchas to design around:
  1. **Questionnaires become read-only once attached to a BP.** After a questionnaire is attached to a business-process step you can no longer edit it - to change a question you must build a NEW questionnaire and re-attach it everywhere it was used (which can be many steps/BPs). So fully finalize and get sign-off on questionnaire content BEFORE attaching it, and minimize how many places reference it.
  2. **Related worktags are not natively enforced - enforce them with validation rules.** Workday does not automatically require or auto-populate the correct related worktags on a transaction, so do not assume the platform will keep worktag combinations valid. Build explicit validation rules (or condition rules) to require/verify related worktags, and remember that bulk data loads (e.g., mass EIB-style loads) can BYPASS transaction-level validations - so pair the validations with exception reporting that detects invalid combinations after the fact.

## Model BP official constraints (official-docs - Workday Education course manuals, crawled 2026-08-25; spot-verify in-tenant)

- Supported step types: Action, Approval, Approval Chain, Checklist, Complete Questionnaire, Integration, Report, Report Group, Review Documents, Service, To Do. NOT supported: Batch/Job, Consolidated Approval, Consolidated Approval Chain, Edit Additional Data.
- Hard behaviors: NO delegation support for Extend business processes; a BO CANNOT be deleted once associated with a business process; NO automatic data locking after event completion (matches the staging/proposed-object doctrine in model.md).
- BP event REST endpoint (`https://api.workday.com/apps/{app}/v1/{bpName}Events`): POST only, NO bulk support; external callers need an OAuth 2.0 client with Workday-owned scope (the page-side chained-POST launch above rides platform auth). **(!) Diagnostic: a wdcli tenant token (Extend-platform-scoped) returns 403 on this endpoint even when the BP is correctly built, configured, and has live traffic** -- verified 2026-08-26: the same 403 occurs on a known-working BP with 66 live requests. Got 403 on BP launch? Do NOT assume a config error -- test the same token on a confirmed-working BP first; if that also 403s, the token scope is the gap, not your app. BP launch is testable only via a real user UI session (the page-side platform auth carries the needed scope).
- Constrained routing: routing to a constrained security group (e.g. Managers) requires `secureByTarget` on the target instance.
- Custom page routes are supported on Action steps, Approval steps, Details pages, Revision pages, and Initiation pages; only action / initiation / revision pages support outBoundEndPoints.
- Orchestration launch from a BP goes through a Service step configured as "Orchestration Service" with parameter mapping to the orchestration's inputs.

## Tenant behavior notes (verified in-tenant 2026-08-31, a dev tenant, UAP v2 approval build)

- **Workday AUTO-APPROVES a BP step when the event INITIATOR is among the resolved approvers.** The event completes in seconds and looks like the approval was skipped. Demo super-users (e.g., GMS Logan McNeil holds Security Administrator + Security Partner) silently skip every approval step they appear in. ALWAYS test BP approvals with an ordinary worker (not in any approver group) as the requester; verify a test worker's groups via `allWorkdayAccounts WHERE worker = "<wid>"` WQL before concluding a step was skipped vs. auto-approved.

- **Extend page SSO REST calls check VIEW/MODIFY domain permissions, NOT Get/Put.** A "Get Only" domain grant does nothing for page-context reads -- use "View Only". Get/Put governs integration-context (O4I/Studio) calls only. Corollary: BOs on an ADMIN domain are invisible to end-user pages until the shopper population gets View on that policy.

- **The BP definition step's "Security Groups allowed for Workflow Step" picker ONLY offers groups from the ACTIVE BP security policy.** If you add a new security group to the policy but have not yet activated it, that group will not appear in the step editor's allowed-groups list. Sequence: edit policy -> Activate Pending Security Policy Changes (R2) -> THEN edit the definition step to add the group. Cross-reference: wd-deployment tenant-task-recipes.md R2; wd-tenant-config config-flows.md.

- **The BP events list endpoint (`<bpName>Events?limit=`) returns ONLY id/descriptor/businessProcessTarget -- NO status field.** Reading `.status` off list rows silently returns empty (not an error). Status requires a per-event GET: `businessProcess/v1/events/{id}`. The `eventSteps` collection only returns steps awaiting the CALLER -- useless for admin inspection of another user's event.

- **A demo worker who appears to be in a grant target group may still silently receive no access if that worker is excluded by the group's constraint.** Example: "All Employees (Excluding CXO)" excludes CXO-role workers -- a demo cast member who is a CXO sees nothing when scoped to that group even after activation. Verify the test worker's actual group memberships via WQL or "View Security Groups for User" before diagnosing a failed grant as a config error.

- **Model BP names are TENANT-GLOBAL** (build-verified 2026-09-04): if a predecessor or sibling app in the same tenant already uses a given BP type name, a new deploy with the same name fails SILENTLY -- success:false, zero error text from `wdcli app builds logs`. Rename the BP in the new app's `.businessprocess` file before deploying alongside a predecessor. This surfaces on every "replace the old version" scenario where the referenceId changes but the BP name was not updated. [Corporate Card Requests build, a dev tenant, 2026-09-04]
