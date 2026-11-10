# Build from scratch - compose any Extend/O4I artifact from primitives

The point of this file: be sharp enough to AUTHOR any Extend or O4I artifact from a mental
model of the platform, instead of hunting for an app to clone. Every skeleton here is the
SMALLEST correct starting shape distilled from a sibling reference that owns the full vocabulary
- start here, then grow it using the ref cited. Shape provenance is inherited from those refs
(build-verified > sample-verified); where a skeleton is COMPOSED (assembled from verified
fragments, not quoted verbatim) it says so and carries "build-verify on first upload."

## 1. The stance

**Default to AUTHORING from primitives, not cloning.** Knowing the file types, non-negotiable
keys, and runtime landmines, you write the smallest correct artifact and grow it - rather than
inheriting an unrelated app's baggage and editing it down.

- **Examples are for SPARKING and VERIFYING, never for copying.** app-catalog-registry.md and
  donor apps broaden the options you canvass (solutioning.md) and let you confirm an
  unfamiliar shape against a real instance. That is inspiration and verification - not a
  copy-source.
- **MODIFYING an existing/shared app is a different discipline.** When you touch an app that
  is already deployed or that a client developer edits, PULL LATEST first
  (`wdcli app download`), diff, and hand back a change-list - do not author over a stale copy.
  That workflow rule stands (workflow.md); it is orthogonal to building net-new.
- **A few legitimate must-clone cases remain - they are the EXCEPTION.** A flowVersion 3.3.0
  top-level scaffold for an outbound `SendHttpRequest` (`tlsConfigRef`/`pollingConfigRef`
  wiring) is easier cloned from a known-good donor than hand-built (external-apis-and-genai.md);
  likewise a net-new full orchestration is laid out in the visual Builder, not typed from zero
  (part 2g). Naming these does not license clone-by-default for everything else.
- **Pair every from-scratch artifact with its gotcha sweep + the validator.** Authoring
  without a donor is reliable ONLY because you also run the runtime-landmine scan
  (pmd-gotchas.md) and the structural linter (`scripts/validate.py`) before upload. The green
  build proves almost nothing (standards.md) - the gotcha sweep is what a donor gave for free.

## 2. Minimal-correct skeletons

Generic names throughout (app `assetRequest`, BO `AssetRequest`, domains
`ManageAssetRequestPages` / `AssetRequestData`). Swap in real names; never ship client tokens.

### (a) App directory + appManifest.json  (schema: references/pmd.md)

```
assetRequest_<orgsuffix>/
  appManifest.json
  model/                     # BOs, security domains, BPs, .task files
  attributes/default.attributes
  presentation/              # .amd .smd *.pmd, plus pods/ cards/ scripts/ wqlQueries/
  orchestration/             # optional; INTEGRATION apps have ONLY this + manifest
```

```json
{ "id": "<assigned>", "referenceId": "assetRequest_<orgsuffix>",
  "name": "Asset Request", "latestVersion": 1, "organizationId": "<org>" }
```

- **Every one needs:** `referenceId` (lowerCamelCase app name + org suffix, assigned by wdcli),
  `name`, `organizationId`. Create the tree with `wdcli app create`, not by hand.
- **Grow it:** add `model/` + `presentation/` for an Extend app; `orchestration/` only for
  flows. `wdcli app create --app-type INTEGRATION` scaffolds the orchestration-only variant.
- COMPOSED literal - build-verify on first upload; prefer `wdcli app create` to emit it.

### (b) Security domain  (schema: references/model.md)

```json
{ "id": 1, "name": "ManageAssetRequestPages",
  "enabledForPageSecurity": true, "enabledForOrchestrationSecurity": false }
```

- **Every one needs:** `id` (unique in its space), `name` (PascalCase, role-aligned, suffix
  `Pages` or `Data`), and the matching `enabledFor*` flag for how it gates. A page domain sets
  `enabledForPageSecurity`; a flow-launch domain sets `enabledForOrchestrationSecurity`.
- **Grow it:** the flag is only the model half - it takes effect via `securityDomains: [...]`
  on the PMD (2d) or at the orchestration root (2g). Two-domain (persona `Pages` + shared
  `Data`) is the norm; max 10 per app, max 3 per page. After first deploy, data calls return
  S22 until an admin grants the domain in-tenant (model.md).

### (c) Business object  (schema: references/model.md)

```json
{ "id": 1, "name": "AssetRequest", "label": "Asset Request",
  "defaultSecurityDomains": ["AssetRequestData"],
  "defaultCollection": { "name": "assetRequests", "label": "Asset Requests" },
  "fields": [
    { "id": 1, "name": "requestName", "label": "Request Name", "type": "TEXT" },
    { "id": 2, "name": "requestedOn", "label": "Requested On", "type": "DATE", "precision": "DAY" },
    { "id": 3, "name": "active", "label": "Active", "type": "BOOLEAN" }
  ],
  "derivedFields": [] }
```

- **Every one needs:** app-unique `id`, PascalCase `name`, a `defaultCollection` (its `name`
  is the REST collection path segment), and at least one field. Field ids unique within the BO.
- **The append-only rule (non-negotiable):** on a deployed BO, only APPEND new fields at the
  END. Inserting/reordering/removing renumbers field ids and fails redeploy ("Error 10:
  duplicate metadata"). To change a field's type/target, append a new field and migrate - never
  repurpose in place (model.md).
- **The Active gate:** an `active` BOOLEAN is the standard soft-delete (hard DELETE 500s when a
  child references a parent). An UNSET boolean stores `false`, not null - so set `active: true`
  on EVERY create and carry it on EVERY full-replace PUT, or filtered rows silently vanish
  (pmd-gotchas #45).
- **Grow it:** field-type vocabulary (SINGLE_INSTANCE targets, CURRENCY/DECIMAL shapes,
  `isReferenceId`, reserved names, caps) all in model.md. The auto-generated REST API lives at
  `.../apps/<refId>/v1/<collectionName>`.

### (d) A VIEW page and an EDIT page  (schema: references/pmd.md)

Smallest VIEW page that renders and reads data (no footer, no input widgets):

```json
{ "id": "assetRequestList", "securityDomains": ["ManageAssetRequestPages"],
  "presentation": { "pageType": "VIEW",
    "title": { "type": "title", "label": "Asset Requests" },
    "body": { "type": "section", "children": [
      { "type": "grid", "rows": "<% listEp.data %>", "rowVariableName": "reqRow",
        "columns": [ { "type": "column", "label": "Name",
          "cellTemplate": { "type": "readOnlyText", "value": "<% reqRow.requestName %>" } } ] }
    ] } },
  "endPoints": [ { "name": "listEp", "baseUrlType": "app", "url": "assetRequests" } ] }
```

Smallest EDIT page that WRITES one row (input widgets + `onSend` outbound):

```json
{ "id": "addAssetRequest", "securityDomains": ["ManageAssetRequestPages"],
  "presentation": { "pageType": "EDIT",
    "title": { "type": "title", "label": "Add Asset Request" },
    "body": { "type": "section", "children": [
      { "type": "text", "id": "requestName", "label": "Request Name" } ] } },
  "outboundData": { "outboundEndPoints": [
    { "name": "createReq", "baseUrlType": "app", "url": "assetRequests", "httpMethod": "POST",
      "onSend": "<% { 'requestName': requestName.value, 'active': true } %>" } ] } }
```

- **Every page needs:** an `id`, top-level `securityDomains` (pairs with the domain's
  `enabledForPageSecurity`), and a `presentation` with a `pageType`. VIEW renders read-only and
  cannot host input widgets; EDIT hosts inputs and gets the platform OK/Cancel footer.
- **Grid gotchas baked into the skeleton:** the property is `rows` (not `value`);
  `rowVariableName` must not be a JEXL word-operator; default cellTemplates to `readOnlyText`
  so an EDIT-turned page does not make cells editable (pmd-gotchas #47).
- **Grow it:** widget cheat-sheet, page shells (`hub`/`tabs`/`columnLayout`), WQL/orchestration
  endpoints, and the outbound reconciliation (grid `outboundFields` vs the reliable VIEW-page +
  deferred-POST bulk pattern) all in pmd.md. `script` is a TOP-LEVEL PMD key, not inside
  `presentation` (pmd-gotchas #42).
- COMPOSED literals (assembled from pmd.md fragments) - build-verify on first upload.

### (e) AMD (routing + dataProviders) and SMD (siteAuth)  (schema: references/pmd.md)

```json
// presentation/assetRequest.amd
{ "tasks": [
    { "id": "addAssetRequest", "routingPattern": "/add", "page": { "id": "addAssetRequest" } },
    { "id": "assetRequestList", "routingPattern": "/", "page": { "id": "assetRequestList" } } ],
  "dataProviders": [
    { "key": "app", "value": "<% `{{apiGatewayEndpoint}}/apps/{{site.applicationId}}/v1/` %>" } ],
  "appProperties": [], "flowDefinitions": [] }
```

```json
// presentation/assetRequest.smd
{ "siteId": "assetRequest", "applicationId": "<refId>",
  "languages": ["en_US"],
  "siteAuth": { "authTypes": [ { "scheme": "SSO", "id": "sso" } ] } }
```

- **AMD needs:** a `tasks[]` entry per page (route param, if any, MUST be the FINAL segment) and
  a `dataProviders[]` entry per API base URL the endpoints reference by `baseUrlType`. SMD needs
  `siteId`, `applicationId`, `languages[]`, and `siteAuth.authTypes[]`.
- **flowDefinitions + the endsFlow rule:** post-submit EDIT navigation uses `flowDefinitions`
  (flowSteps with `startsFlow`/`endsFlow`/`transitions`). A flow MUST have at least one
  `endsFlow: true` step - the BUILD passes without it but the DEPLOY fails. Combined
  `flowDefinitions` + `editWizard` count is capped at 25 per app; treat it as a budget (pmd.md).
- **Grow it:** add an ISU `authType` on SMD to read admin data as an ISU, `errorPageConfigurations`
  for branded errors, `workday-wql` / `workday-orchestration` dataProviders (pmd.md).

### (f) Home .task  (schema: references/model.md)

```json
{ "id": 90, "name": "AssetRequestHome", "label": "Asset Request",
  "securityDomains": ["ManageAssetRequestPages"], "routePath": "/" }
```

- **Two build validations (build-verified Sep 2026 - two failed builds, then a clean one):**
  `name` must be UpperCamel (**E102** - `assetRequestHome` fails, `AssetRequestHome` builds).
  `label` must start with an uppercase letter or a digit and hold only letters, digits, spaces,
  hyphens and colons (**E103**). Parentheses are rejected, so a tenant naming convention that
  marks app copies with a "(suffix)" cannot carry into a `.task` label - use a hyphen instead.

- **Every app with a home page needs one (MANDATORY house standard).** The `.task` is the ONLY
  thing that makes the app appear in the tenant SEARCH bar; without it the app is reachable by
  URL but invisible to users. Use a HIGH `id` (90/91) to stay clear of BO ids; list ALL page
  domains a launcher persona could hold (OR semantics). It is a plain launcher - no BO involved.
- **Grow it:** ship multiple `.task` files for multiple entry points (one per landing route).
  Re-run "Activate Pending Security Policy Changes" after deploy or it stays hidden. Verify a
  home `.task` exists after any `app copy` - it does NOT come along for free (model.md).

### (g) Minimal orchestration - FlowSync  (schema: references/orchestration-nodes.md)

Net-new flow LAYOUT belongs in the visual Orchestration Builder (orchestration.md); these
shapes are for EDIT/REVIEW/GENERATE and to know the minimal envelope. The file is a single-line
typed-AST (`{"_type":..,"_value":..}` per value); shown here in the orchestration-nodes.md
shorthand:

```
Flow root: { flowVersion "3.1.0", _type "Flow",
  securityDomains ["AssetRequestData"],        // BARE array at outer root = the launch gate
  _value: { name ID(GetAssetRequests), type ".maya.FlowSync",
    start StartBasic{ structuredRequest OPT(null), notes },
    end   EndSync{ headers [], body DataRefBody{ dataRef EXPR(Data, "data.ReadReq.response") }, notes },
    nodes [ SendWorkdayApiRequest{ name ID(ReadReq), method GET,
              path EXPR(String, "wql/v1/data"), auth _DEFAULT_WORKDAY_CREDENTIAL, ... } ],
    notes, resources ResourceProvider{...}, defaultWorkdayCredentialRef } }
```

- **Every FlowSync needs:** at the root `flowVersion`, `_type "Flow"`, and (to gate launch) the
  bare `securityDomains` array as a SIBLING of `_type` - NOT the nested typed-null
  `securityDomains` the Builder emits inside `_value` (leave that null). Inside `_value`: `name`,
  `type`, a `StartBasic`/`EndSync` pair, `nodes`, `notes`, `resources`,
  `defaultWorkdayCredentialRef`. Pages launch it via `POST <FlowName>/launch` (the ONLY bridge).
- **How FlowAsync differs:** type `.maya.FlowAsync`, `StartAsync` -> `EndEmptyMaya` (NO EndSync
  body - it acks immediately and runs headless), so it ESCAPES the 25-second page-sync cap. Use
  sync for a small read/write the page waits on; async for real work.
- **Grow it:** full node catalog + config-key shapes in orchestration-nodes.md; behavior, auth,
  bulk-write and error-handler patterns in orchestration.md. Run `scripts/validate.py` before
  uploading generated JSON.

### (h) Minimal Model BP  (schema: references/model-bp.md)

```json
{ "id": 1, "name": "CreateAssetRequest", "label": "Create Asset Request",
  "useForOrchestrate": false, "allowsCancel": true, "allowsManualSendBack": false,
  "targetBusinessObject": "AssetRequest",
  "securityDomains": ["ManageAssetRequestPages"],
  "approvalStep": { "pageRoute": "/approveAssetRequest/{eventId}", "actions": ["APPROVE", "DENY"] } }
```

- **Every one needs:** `id`, PascalCase `name`, `targetBusinessObject`, `securityDomains`, and a
  step. Every `pageRoute` maps to an AMD task whose `routingPattern` matches EXACTLY, param as
  the FINAL segment (`{eventId}` for approval/details, `{eventStepId}` for action/revise).
- **Grow it:** SEND_BACK needs a `revisePageRoute`; `useForOrchestrate: true` hooks a write-on-
  approval flow; an actions-only approval omits `pageRoute`; the create page launches the BP via
  two chained POSTs (BO create, then `<bpNameLowerCamel>Events`) - all in model-bp.md. The
  multi-step approver chain is tenant config after deploy, not in this file.

## 3. The compose decision path (need -> primitive)

Reason from the requirement to the primitives, no precedent required:

- **Need a UI** -> a PMD page (2d) over a BO (2c); pick the page shell by interaction (page /
  card / hub / tabs / A2UI). Register it with an AMD task (2e) + a home `.task` (2f).
- **Need to write ONE row from a form** -> EDIT page + `onSend` outbound POST (2d).
- **Need to write MANY rows** -> the VIEW-page + deferred-POST bulk pattern (`values` +
  `outboundPath`, pmd-gotchas #56/#59), or a sync orchestration running a `BatchLoop` ->
  `?bulk=true` (<=100/batch). Do NOT use script-side `.invoke()` writes (roll back, #52).
- **Need to READ native tenant data** -> a delivered WQL data source from the page, or RaaS /
  paginated REST at scale (data-loading-and-retrieval.md). Bound every read; respect the 100-row
  BO REST cap.
- **Need an approval** -> a Model BP on the BO (2h).
- **Need to call SOAP / REST / an external API** -> an orchestration (SOAP for FDM master data;
  `SendHttpRequest` for external, secret proxied via `attrstore`); the page bridges via
  `/launch` (orchestration.md).
- **Need per-tenant config text / flags** -> App Attributes (`attributes/default.attributes`,
  read as `attrstore`), not hardcoded literals (standards.md).
- **Need a file transform** -> the wd-integration-dev skill's XSLT 3.0 territory (streaming
  `for-each select="X/copy-of()"`); orchestrations read delimited files positionally.

Route with solutioning.md; load mechanics in data-loading-and-retrieval.md; flow patterns in
orchestration.md.

## 4. Solutioning from primitives

Creative solutions come from RECOMBINING knowable primitives, not from finding a precedent that
already does the whole thing. The building blocks you canvass are exactly the skeletons above -
BOs, VIEW/EDIT pages, sync/async flows, WQL reads, Graph mutations, AI Gateway calls, home
cards, native agents - each composable with the others. When a requirement looks novel, break it
into "which primitive produces each part" (part 3) and assemble; the from-scratch shapes here
are what you assemble WITH. That is the toolbox mindset (solutioning.md): reach past the first
familiar pattern to the leanest recombination that fits, and be able to say at architecture
review why the composition beats the alternatives.
