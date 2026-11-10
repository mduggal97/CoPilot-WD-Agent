# PMD / presentation layer - app anatomy, widgets, layout

## App file structure (verified schema)

```
<referenceId>/
  appManifest.json              # app identity: id, referenceId, name, latestVersion, organizationId
  model/                        # BOs, security domains, BPs, attachments (see model.md)
  attributes/default.attributes # App Attributes: [{name, type, alias}] - schema in model.md;
                                #   read from page expressions as attrstore.<alias> / attrstore['name']
  presentation/
    <referenceId>.amd           # App Metadata: tasks[] (routing: id, routingPattern, page.id),
                                #   dataProviders[] (key -> API base URL), appProperties[], flowDefinitions[]
    <referenceId>.smd           # Site Metadata: siteId, applicationId, languages[], siteAuth.authTypes[],
                                #   errorPageConfigurations[], headerBackgroundColor, cdnEnabled (see SMD section below)
    *.pmd                       # Page Model Definition: id, securityDomains[], endPoints[], presentation{title, body, footer}
    pods/*.pod                  # reusable endpoint+template seeds (deferred WQL search pattern)
    cards/*.card                # parameterized card templates (see "Cards & hub pages" below)
    scripts/*.script            # reusable script files (see scoping rules in pmd-gotchas.md)
    wqlQueries/*.wqlquery       # externalized, reusable WQL: {id, parameters[], query} referenced by queryId (see efficiency.md)
  orchestration/                # O4I flows (see orchestration.md); INTEGRATION apps have ONLY this + manifest
```

- Top-level PMD `"securityDomains": ["<DomainName>"]` gates who can open the page; it pairs with `"enabledForPageSecurity": true` on the matching `.securitydomain` file (flows pair the same way via `enabledForOrchestrationSecurity` - see model.md / orchestration.md). Verified across ~30 PMDs in delivered production apps, 2026-08-05.

## Widget cheat-sheet

- Layout: `title` (**`headerSize` is rejected by the compiler** - omit it; see gotcha #50), `section` (`children[]`, `horizontal` bool), `fieldSet`, `footer`
- Display: `richText` (HTML in `value`), `text`, `grid`, `image`; `hidden` is a dedicated invisible value-holder widget type
- Input: `text`, `date`, `numericStepper`, `checkBox`, `radioGroup`, `instanceList` (type-ahead picker) - input widgets only work on `pageType: EDIT` pages
- Action: `button` (`action`: PRIMARY/AUXILIARY, `taskReference.taskId` navigates), `pageActionButton` (+`onClick` in-page script, no flow/outbound needed - the pattern for "Run Report" style recompute pages)
- `grid`: `rows` (`<% endpoint.data %>` - the property is `rows`, NOT `value`; `value` on a grid fails the build), `rowVariableName`, `columns[]` each with `cellTemplate`; per-row actions = `cellTemplate: {type:"section", children:[{type:"button", taskReference:{taskId, parameterBindings}}]}` with dynamic taskId/label/render. **`grid.getSelectedRows()`** works in outbound `onSend` (verified 2026-08-18): returns the selected rows; values live at `column.cellWidget.value` - use hidden carrier columns (see show/hide patterns below) to pass per-row metadata like internal ids through the selection. **`grid.setRows([])`** from an `instanceList` `onChange` is the verified way to blank a grid when a dependent picker changes - clears rows immediately without a round-trip (verified 2026-08-20).
  - **`rowVariableName` (and any script var) must NOT be a JEXL word-operator: `lt gt le ge eq ne and or not div mod`.** A grid with `rowVariableName: "lt"` fails the build with a generic "Parsing Error" the moment a cell reads `lt.field` (JEXL parses `lt` as less-than). Use a descriptive name (`lotRow`, `line`, `item`) - same class of trap as the reserved `site`/`self` keywords. (Verified 2026-08-11 on an expiry-tracking product's watchlist lots grid.)
- `panelList` - dynamic forms: one template panel rendered per data row; `doNotAdd`/`doNotRemove` suppress the user's +/- row controls; submit handlers read answers by walking the widget tree: `questionPanel.children[i].childrenMap.<widgetId>.value` (verified in a delivered GenAI feedback app, 2026-08-05)
- Data binding: `<% endpointName.data %>`, `<% rowVar.fieldName %>`; endpoints pull from AMD `dataProviders` via `baseUrlType`
- Outbound (writes): `outboundData.outboundEndPoints[]` with `httpMethod`, `url`, `onSend` (an `onSend` returning a fully-constructed payload object is the cleanest POST/PUT pattern)
- **The outbound mechanism is GRID/ROW-CONTEXT-DRIVEN (verified 2026-08-25):** grid `outboundFields` (referencing an `outboundEndPointName`) makes the framework POST once per grid row on submit - a page-side BO-create path. Caveats, all verified: (a) rows PRE-POPULATED via the grid `rows` property do NOT fire outbound POSTs - only rows the user adds/edits fire; (b) a standalone outbound endpoint with an explicit `values` array and NO grid binding NEVER fires; (c) `exclude` + `values` on an outbound can evaluate at RENDER time (before onSubmit sets pageVariables) and silently skip the endpoint. Working delivered patterns carry NO `values` and NO `exclude` - the payload comes implicitly from row context or `onSend`. **(!) reconcile (2026-08-26):** `outboundFields` was also observed to SILENTLY FAIL (200, 0 instances created) for a simple BO on an EDIT grid in the same app - cause unknown (pmd-gotchas #60). It is NOT guaranteed for a new simple-BO create; the reliable bulk-create path is the VIEW page + deferred POST with `values`+`outboundPath` (pmd-gotchas #56/#59, data-loading-and-retrieval.md). For bulk imports do not use script-side `.invoke()` writes (transactional rollback - pmd-gotchas #52), and do not pass the body as an `.invoke()` argument (silently dropped - #59).
- **`valuesOut` does not work on `pageType: EDIT`** - outbound POSTs from EDIT pages must use `onSend`. (Verified 2026-08-25.)
- Outbound upsert switch: one endpoint creates OR updates via `"updateId": "<% wid ?: '' %>"` + `"updateUrl": "<% wid ? 'things/' + wid : '' %>"` - empty => POST create at `url`, non-empty => update the instance (verified in a delivered production app, 2026-08-05)
- Micro-pages (modal/slide-over confirms): page-level `"micro": true` + `"microFirstPageOnly": true` (+ optional `"microConclusion": true`); there is also `"pageType": "CONFIRM"`

## Layout tags (26R1 / DevCon 2026 - verify in tenant before first production use)

- **`columnLayout`** - native side-by-side; top-level `body` child (not inside a pod); 1-3 auto-sizing `layoutSection` columns; works on EDIT and VIEW. Retires the nested-horizontal-section hack.
- **`multiStepLayout`** - multi-step wizard in ONE PMD (`steps[]` up to 10 layoutSections, runtime renders next/back). Replaces page-per-step + AMD flowDefinitions for wizards.
- Form `layout` props on `section`/`fieldSet` (children inherit): `density` (low|medium|high), `alignment`, `horizontalSizing`, `labelPosition`.
- editWizard `"enableSaving": true` = Save-for-later + ~30s autosave (drafts ~30 days; every tag needs a stable `id` - changing ids after deploy loses drafts; disabled in App Preview).
- Extend AI widgets: generative prompt on a `richText` (EDIT pages only, max 3 per app, prompt <=1000 chars, can reference live field values). No `onChange` fires when AI populates - design conditionals accordingly. **Concrete shape (per Workday App Catalog samples):** the prompt buttons hang off the `richText` as `aiPrompt: {buttons: [{label, prompt: "<% expr %>", dependencyTags: []}]}` - `prompt` is an expression (can splice live field values), `dependencyTags` lists the fields it depends on. (Upgrades the DevCon doc-level AI-widget note to a sample-verified schema.)
- **Known platform limits (workarounds in pmd-gotchas.md):** EDIT-page empty gutter column, grid column pixel width, filter-bar-forces-EDIT. **RESOLVED since (sample-verified 2026-08-07, supersedes the old "not solved" note):** there IS a native progress widget (`progressIndicator`, pmd-gotchas #38) and the EDIT OK/Cancel footer CAN be suppressed (`standardEditButtonsHidden`, pmd-gotchas #26/#28) - use those, not a workaround.

## Additional widgets & layout (per Workday App Catalog samples)

Official sample apps surface a wider widget vocabulary than our build-verified cheat-sheet (sample-verified - above doc-sourced, below build-verified; build-verify before first production use). NON-chart widgets (Chart 2.0 family lives in charts.md):

- **Page shells / hubs:** `hub`, `listDetailHub` (master-detail), `tabs`, `areaLayout`, `basicFormLayout` (+ `layoutSection` - ships today). **Shapes (per Workday App Catalog samples - these are the modern page shells; default to them over deep nested-section layouts):**
  - `hub` (left-nav multi-page shell): `body {type:"hub", label, initialTask:{taskId}, navigationTasks:[{type:"group", icon:"wd-icon-*", label, items:[{label, task:{taskId}}]} | {icon, label, task:{taskId}}], additionalLinks:{title, links:[{type:"task"|"external", label, task|url}]}}` - each nav item routes to its own task/page (sample `pmdWidgetDictionary/projectHub.pmd`).
  - **[BV] Hub navigation behavioral rules (plan page types BEFORE building the shell):**
    - **A `navigationTasks` item MUST reference a VIEW page.** An EDIT page placed in a hub nav task is a hard BUILD ERROR ("Hub tags can't reference an edit page. `<id>` is an edit page. Change the referenced page's pageType to view or remove the task from the hub navigation").
    - **`taskReference` (a button/card footer) to an EDIT page opens a MODAL overlay over the hub** - platform Save/Cancel close it and return in-frame; the left nav is PRESERVED.
    - **`taskReference` to a VIEW page BREAKS OUT of the hub** - full navigation, the left nav is LOST (no path back except tenant search / the hub URL). If you make VIEW-page tiles clickable anyway, give each target VIEW page a "Back to Home" button pointing at the hub task id so the user re-enters the frame.
    - **A hub nav GROUP caps at 5 items** (build error "You can only specify up to 5 navigation items in a group").
    - Input widgets do NOT render on VIEW pages (VIEW is read-only - see pmd-gotchas.md #27), so any page with a filter bar, form inputs, or a submit action must be EDIT and therefore must be reached via a button (opening as a modal), never placed directly in `navigationTasks`. Canonical shape: a nav item points at a read-only VIEW landing page that hosts status + `button`/`card` `taskReference`s opening the real editors as EDIT modals.
  - `listDetailHub` (master/detail generated per row): `body {type:"listDetailHub", label, items:"<% list %>", itemVariableName, icon, navigationTemplate:{icon, label:"<% ... %>", task:{taskId, parameters}}, additionalLinks}` - one nav entry per row, click opens the detail task (sample `pmdWidgetDictionary/ticketsListDetail.pmd`; real use in `charitableDonations`).
  - `tabs` - NOT a body widget (`type: "tabs"` inside `body` fails with "You defined an invalid tag: tabs"). It is a page-level `presentation.tabs[]` ARRAY (needs >=2), sibling of `body`. Each entry is either a `section` (`{type:"section", label, id, children[]}` - sample `capitalProjectPlanning/CapitalPlanningRequestEdit.pmd`) or a POD reference (`{type:"pod", podId, parameters}` - build-verified 2026-08-18; the tab's visible label comes from the pod template's own `label`, typically computed from a passed-in parameter). If tabs share a pod template, use ONE POD PER TAB, not one template instantiated twice (duplicate widget ids - gotcha #74).
  - `areaLayout` - `body {type:"areaLayout", layout:"left", primaryArea:[...], secondaryArea:[...]}`: main content + side rail (sample `pmdWidgetDictionary/areaLayout.pmd`).
  - `basicFormLayout` - `body {type:"basicFormLayout", sections:[{type:"layoutSection", children:[]}]}`: stacked form sections; confirms `layoutSection` ships TODAY, not only inside the 26R1 `columnLayout` (sample `pmdWidgetDictionary/basicFormLayout.pmd`).
- **Reactive layout:** `dynamicSection` - a re-render primitive whose children re-evaluate when you reassign `<section>.data` (the reactive escape our grids' non-reactive `rows` lack). CONFIRMED against canonical DevRel sample `pmdWidgetDictionary/presentation/progressIndicator.pmd` (a `progressIndicator` inside a `dynamicSection`, refreshed by `dynamicAttachmentSection1.data = {...}` on each click), 2026-08-07.
- **Proportional columns (per Workday App Catalog samples):** a `section` with `"horizontal": true` + `"columnWidthRatios": [0.7, 0.3]` sets each column's width as a fraction - the width control the nested-horizontal-section hack lacked (samples `assetBarcoding/home.pmd`, `capitalProjectPlanning`, `crisisCheckin`). Horizontal `section`s ONLY - NOT grid table columns (grid column `width` is still rejected; see grid gotchas).
- **Inputs:** `dropdown`, `multiSelectCalendar`, `snapSlider`.
- **Calendar event surface (per Workday App Catalog samples):** `multiSelectCalendar` is a full month calendar with per-event click-through: `{type:"multiSelectCalendar", calendarStartDate, eventData:{on:"<% events %>", as, template:{startDate:"<% date:parse(x) %>", endDate, style, title, editTask:{render, task:{taskId, parameters}}}}, sidebar?, submitButton?}` - common in scheduling/assignment apps (samples `pmdWidgetDictionary/calendar.pmd`, `workFromAlmostAnywhere`, `createAWorkEvent`).
- **Prefer these native widgets over the workarounds we previously documented (per Workday App Catalog samples):**
  - **`applicationException`** - declarative page-level error/warning banner: a `presentation.applicationExceptions[]` entry `{type:"applicationException", severity:"ERROR"|"WARNING", message, render:"<% expr %>"}`. Prefer over the `setError` + richText-`<div>` banner workaround for page-level messages (samples `AWSBadgeGenerator`, `commutingEmissionsSurvey`).
  - **`congratulationsPopup`** - native success popup: `{type:"congratulationsPopup", render:"<% expr %>", textCongrats, textSubmitted}`. Prefer over a micro-conclusion confirm page for simple "done!" moments (sample `giftRegistry`).
  - **`checkBoxList`** - native bounded multi-select: `{type:"checkBoxList", idKey, displayKey, maxSelectable, values:"<% list %>"}`. Prefer over a hand-rolled multi-select (sample `pmdWidgetDictionary/instanceList.pmd`).
- **Niche widget tail (discoverability only - see `app-catalog-registry.md` / `pmdWidgetDictionary` for the shape when a build needs one):** `time` (time-of-day input, distinct from `date`), `templatedListItem` / `bpTemplatedList` (home link-lists), `monikerLevel` (org-hierarchy drill navigator), `video` (`mediaId`), `labeledImage` / `labeledThumbnail`, `superEdit`, and `sidebar` / `popup` layouts. All present in the catalog samples.
- **Actions / buttons:** `buttonGroup`, `dropDownButton`, `editButtonBar` (with `ignoreRequiredFields` to let a save bypass required-field validation).
- **Cards:** `pillCard`, `chartCard`.
- **Contextual help / links:** `guide` (in-page contextual help), `externalLink`.
- **Loops:** `loop` / `instanceLoop` (render a template per instance in the page body).
- **BP surfaces:** `bpExtender`, `bpButton`, `commentHistory`, `processHistory` (surface a business process's comments/history in-app).
- **`progressIndicator`** - CONFIRMED native progress widget (canonical DevRel sample, sample-verified 2026-08-07); this RESOLVES the old "no native progress widget" note above (pmd-gotchas #38). Use it instead of a custom workaround.

**Grid props (per Workday App Catalog samples):** `gridType: "LIST"`; `selectionEnabled: true` + an `onRowSelect` handler for row selection; `sortableAndFilterable: true` (native column-header sort/filter) - CONFIRMED working on a **VIEW** page (canonical DevRel `capitalProjectPlanning/presentation/CapitalPlanningRequestsIndex.pmd` + `...IndexAll.pmd`, both `pageType: VIEW`), 2026-08-07. This is the real escape from the filter-bar-forces-EDIT / non-reactive-grid workarounds: a read-only list can offer column sort/filter without turning EDIT.

## AMD routing and flows

- `routingPattern` params must be the FINAL segment: `/add-item/{id}` works; `/room/{id}/add` builds fine but the route silently never registers.
- `flowDefinitions` (flowSteps with startsFlow/endsFlow/transitions) drive post-submit navigation of EDIT pages. Pass context between steps via `outboundVariable` with `variableScope: flow` -> read as `flowVariables.x` on the next page. Do NOT rely on route-param carryover. **A flow must contain at least one `endsFlow: true` step - the build PASSES without it but the DEPLOY fails** (verified 2026-08-25).
- A flow can end (`endsFlow`) on a normally-routed page; that page renders reading flowVariables (route param empty). Make dual-use pages resolve context as `(empty queryParams.x ? flowVariables.x : queryParams.x)`.
- **HARD APP LIMIT: max 25 combined `flowDefinitions` + `editWizard` widgets per app** - exceeding it FAILS THE BUILD ("has exceeded the combined maximum of 25 flow definitions and editWizards... Revise the app to stay within the limit"). Easy to blow past on CRUD-heavy apps: the standard return-nav pattern (each add/edit/remove/confirm page = its own 2-step flow) burns one flow PER page. **Verified mitigation (26->25, behavior-identical): consolidate near-duplicate flows into ONE param-driven page+flow** - e.g. cancel + restore merge into one `setActive` page where `queryParams.activeVal` drives both the PUT value (`'active': (queryParams.activeVal == 'true')`) and the confirm message (`<% queryParams.activeVal == 'true' ? 'Restore...' : 'Cancel...' %>`); callers pass it via `parameterBindings`. Same trick collapses a family of delete-confirm pages sharing a return target into one generic remove page (queryParams: collection + recId + returnId). Verified in a delivered build session, 2026-08-05. Treat flow count as a BUDGET from the first CRUD page (see efficiency.md section 7).

## SMD: auth schemes & custom error pages (verified in a delivered production app, 2026-08-05)

- `siteAuth.authTypes[]` is NOT SSO-only. Add an ISU scheme - `{"scheme": "ISU", "id": "isuAuth", "username": "ISU_XTND_<app>_<purpose>"}` - and mark a page endpoint `"authType": "isuAuth"`: that call runs as the ISU, so any user's page can read admin-domain data (config, translations) WITHOUT the signed-in user holding the domain. ISU security setup: security-setup.md. **Two verified failure modes (2026-08-25):** (a) an ISU-authed read the ISU cannot see returns EMPTY with no error - check siteAuth and ISU domain grants before blaming the query; (b) when the SAME data source is read on multiple pages of one flow, keep `authType` consistent across them - a delivered bug had page 1 fixed to `"sso"` while page 2 still ran `"isuAuth"`, so users selected rows on page 1 and page 2 rendered empty (misdiagnosed as "selections not carried forward").
- `errorPageConfigurations` routes HTTP errors to your own branded PMD: `[{"statusCode": "400", "page": {"id": "customErrorView"}}, ...]` - verified for 400/401/403/404/407/408/500/503.

## Common endpoint patterns

- Static WQL: the inline `wqlQuery: {query: "SELECT ..."}` block form errored at RUNTIME ("Property Error found: .data") in a delivered build session (2026-08-05) - the proven forms are the URL-encoded query on the `workday-wql` endpoint (`url: "data?query=<pathEncoded SELECT>"`, `baseUrlType: workday-wql`) or the externalized `queryId` form below.
- **Externalized WQL (preferred for reused/complex reads):** define the query once in `presentation/wqlQueries/<id>.wqlquery` (`{id, parameters[], query}`) and reference it from the endpoint with `wqlQuery: {queryId: "<id>", parameters: {p: "<% expr %>"}}` - no `string:pathEncode`, no `\"`-escaping, one definition many callers. Full pattern + parameterized/`deferred` forms in [efficiency.md](efficiency.md).
- Skip a round-trip with `"exclude": "<% ... %>"` on an endpoint - when true the call is not made; chain it to a precondition so a dependent lookup only fires when its input exists (see efficiency.md). Literal `"exclude": true` parks an endpoint permanently (delivered apps keep alternate/retired endpoints in source this way - check `exclude` before assuming a downloaded endpoint runs); on OUTBOUND endpoints, `exclude` expressions choose which POST fires per button. **TRAP:** `type: "hidden"` in a grid `cellTemplate` does NOT expose the cell's `.value` to `exclude` expressions (always reads empty/true, causing create endpoints to fire for ALL rows and duplicate records on save). Use `type: "text"` with `enabled: false` and `visible: false` for any hidden field whose value gates an `exclude` (pmd-gotchas #65). **Not `render: false`** - an unrendered widget is never built and reads empty at OK (#88, runtime-verified 2026-10-21).
- App Attributes in page expressions: `attrstore.<alias>` / `attrstore['name']` - endpoints' URLs, API keys, limits, feature flags all live in `attributes/default.attributes` (schema in model.md) and are tenant-editable without a code change.
- Error surfacing on outbound endpoints: `failOnStatusCodes: [{"code": 400}, ...]` declares which statuses fail the submit; `responseErrorDetail.errorSummary` (an expression with implicit `error`/`errors` variables) shapes the user-visible message. Verified in a delivered production app, 2026-08-05.
- WQL from pages can project nested related objects (`learningEnrollment{learner, cf_learnerPhoto} as learningEnrollment`) and query tenant calculated fields (`cf_*`) created against an Extend BO's WQL data source - `cf_` fields never appear in the `.businessobject`, only in WQL results. Newly verified SINGLE_INSTANCE targets usable from pages: `LEARNING_CONTENT`, `LEARNING_ENROLLMENT`, `PROJECT`, `FEEDBACK_TEMPLATE`.
- External/GenAI API calls from pages (absolute URLs, `authType: "noAuth"`, custom `headers`): see external-apis-and-genai.md.
- GraphQL from a page uses `.graphquery` files + a `workday-graph` provider - authoring depth (query vs mutation, when-Graph, combined mutations) is consolidated in [rest-api-catalog.md](rest-api-catalog.md).
- Dynamic type-ahead: deferred endpoint + `instanceList` with `onSearch`: `"<% const r = searchEp.invoke({'searchText': event.query}); r.data ?? [] %>"`. (The pod-style `searchEndPoint`/`searchResultValues` construct does NOT work as a page-body widget.) A search-driven `instanceList` still needs a `values` seed (`"values": "<% [] %>"`) alongside `onSearch`, or the build fails "Specify exactly one of instanceList, values, or instanceListLoopTag" (verified in a delivered build session, 2026-08-05).
- Deferred detail lookup: `endpoint.invoke({'param': v})` inside `onChange`; populate other fields via `widget.setValue()` / `widget.setVisible()`. **CAUTION - invoke args do NOT feed a declared `wqlQuery.parameters` binding** (the declaration always wins - pmd-gotchas #49): args passed to `.invoke()` are only visible to an endpoint that references them as BARE variables inside a `url` expression. For a same-page dependent lookup on a `wqlQuery` endpoint, bind the declared parameter to a live widget read instead (efficiency.md "Endpoint passes the parameter", form (b)) and call `.invoke()` with no args. **Deferred `.invoke()` supports GET and POST ONLY** - DELETE and PUT fail at runtime with UnsupportedOperationException (pmd-gotchas #62); use grid outbound endpoints or orchestrations for those methods.
- Current user: `/common/v1/userInfo` works for ANY signed-in user -> `data[0].workdayID/fullName/userName`. `workers/me` 404s for non-worker users (implementers) - avoid unguarded.
- Worker search WQL: `SELECT workdayID AS id, preferredNameInGeneralDisplayFormat AS descriptor FROM allWorkers WHERE fullName contains '<q>'`.
- Filter-bar -> grid refresh: filter `onChange` -> script-file function reads filters, computes rows -> `grid.setRows(newRows)`. Grids do NOT re-evaluate `rows` expressions reactively.

## Calling orchestrations from pages (`workday-orchestration` dataProvider)

The page<->flow bridge (verified in delivered production apps, 2026-08-05). Every flow - sync read, sync write, async - is launched as an HTTP call to `<flowName>/launch`:

1. AMD `dataProviders[]` entry (note the built-in `apiGatewayEndpoint` variable and backtick-`{{}}` templating inside dataProvider values):

```json
{ "key": "workday-orchestration",
  "value": "<% `{{apiGatewayEndpoint}}/orchestrate/v1/apps/{{site.applicationId}}/orchestrations/` %>" }
```

2. READ (sync flow returns data): a normal GET endpoint with `baseUrlType: "workday-orchestration"` and `url: "Get_Instances_x/launch?Reference_ID_Type=..."` - inputs ride as query params (flow reads `data.start.queryParams`); the page consumes the flow's EndSync body like any endpoint response.
3. WRITE: an `outboundEndPoints[]` entry with `httpMethod: "POST"`, `url: "Orch_PostDataToBO/launch"`, and an `onSend` returning the JSON body (flow reads `data.start.request.asJSON()`).
4. ASYNC flows launch exactly the same way (`POST orch_Async_x/launch`); the call returns immediately - do not read results from it. Flow-side contract details: orchestration.md.
5. **`/launch` is the ONLY page->flow bridge.** A deferred endpoint POSTing `/orchestrations/<flowName>` 404s even with a correct URL, and the `workday-orchestration` base URL has no trailing slash (endpoint URLs need a leading `/`) - pmd-gotchas #54.

## Cards & hub pages

A `.card` file is a PARAMETERIZED TEMPLATE, not a fixed home-page tile (verified schema from a delivered production app, 2026-08-05):

```json
{ "id": "applicationCard", "parameters": ["title","body","buttonLabel","buttonTask"],
  "header": {"title": "<% title %>"},
  "body": {"type": "simpleCard", "value": "<% string:toString(body) %>"},
  "footer": [{"label": "<% buttonLabel %>", "taskReference": {"taskId": "<% buttonTask %>"}}] }
```

- A hub page instantiates cards with a `cardContainer` widget on a VIEW page routed as its own task: `{"type": "cardContainer", "layout": "GRID", "cards": [{"type": "card", "cardId": "applicationCard", "parameters": "<% {'title': ..., 'buttonTask': ...} %>"}]}`.
- `dynamicCards` generates one card per data row: `{"on": "<% list %>", "as": "item", "template": {"cardId": ..., "parameters": ...}}` - delivered apps drive the list from a config BO (tenant-editable hub, no code change to add a tile). **Loop `as` variables (`"as": "item"`) work in STATIC expressions (`label`, `value`, `render`) but are NOT accessible inside event handlers (`onChange`, `onClick`) of child widgets** - workaround: set a static property from the loop var (e.g. `"label": "<% item.displayName %>"`) then read `self.label` in the handler; if display names are not unique, use a grid instead (pmd-gotchas #64).
- Card footers take `taskReference: {taskId}` (in-app navigation) OR `url` (external link).

## Pods - reuse mechanics (per Workday App Catalog samples `assetBarcoding` / `pmdWidgetDictionary`)

A `.pod` (`presentation/pods/<name>.pod`) is a reusable **endpoint+template seed** - a named block dropped into multiple pages instead of copy-pasting. Shape: `{podId, seed:{parameters:[...], template:{ ...widget/endpoint... }}}`, with `@@paramName@@` placeholders inside the template that the caller fills. Instantiate on a page with a `{type:"pod", podId:"<name>", parameters:{...}}` widget (header/footer pods take no parameters; a templated-grid pod takes `gridId`/`gridLabel`/`dataSource`, etc.). Used for repeated headers/footers, per-grid templates, and the deferred WQL-search endpoint block. The value is "reuse via pods" - reach for one whenever the same endpoint+widget block repeats across pages (shape in `pmdWidgetDictionary/pods/header.pod`, `assetBarcoding/pods/gridForBlindCount.pod`). **CAUTION:** a pod-provided endpoint that shares a name with an endpoint already in the page's `endPoints` array causes a runtime error - "The endPoint name(s): '<name>' exist on both the pod and pmd" - and the build does NOT catch it; scan for collisions before adding a pod to an existing page (pmd-gotchas #63).

## Custom i18n (Translation BO pattern)

**Native alternative first (per Workday App Catalog samples):** Extend DOES ship a platform-native string-bundle i18n mechanism - `presentationLabels/<locale>.properties` files (key=value per locale), read in a page as `<% presentationLabels.<Key> %>` (file-type detail in model.md). Locale file names are **hyphenated BCP-47** - `en-US.properties`, `fr-FR.properties`, `de-DE.properties`, `es-ES.properties` (canonical DevRel `vehicleRegistration/presentation/presentationLabels/`, `AWSStarterKit/presentationLabels/`, 2026-08-07). NOTE the mismatch with the custom pattern below: `userInfo.data[0].language` returns an **underscore** locale (`fr_CA`, `en_US`) - hyphen for the `presentationLabels` FILE name, underscore for the userInfo language VALUE. Do not "normalize" one to the other. Weigh it before hand-rolling the Translation-BO store below; the custom pattern still wins when translations must be TENANT-EDITABLE at runtime (admins maintaining rows, or a machine-translation pre-fill) rather than shipped in source.

The delivered custom pattern (verified in a delivered production app, 2026-08-05) builds a runtime-editable store:

- `model/Translation.businessobject` fields: `key`, `page`, `language`, `defaultText`, `translatedText`.
- Admin pages maintain the rows; a sync flow proxies a machine-translation API to pre-fill `translatedText` (API key in App Attributes, never in the page - see orchestration.md).
- Runtime chain on every page: `/common/v1/userInfo` -> `data[0].language` -> deferred WQL fetch of translations for (page, language) -> fall back to `en_US` when empty -> build a `pageVariables.translations` map in onLoad -> every label reads `pageVariables.translations.get('key') ?: 'Default text'`.

## Script / expression surface (beyond the basics in pmd-gotchas.md)

Verified in delivered production apps, 2026-08-05: backtick template literals with `{{expr}}` interpolation (also valid inside AMD dataProvider values); Elvis `?:`; optional chaining `?.`; `{:}` empty-map literal (populate with `.add(k, v)`); indexed lambdas `(x, i) =>`; string helpers `.splitByRegex()`, `.contains()`, `.substringBefore/After/BeforeLast/AfterLast()`, `.pathEncode()` (method form); `widget.isUpdated()` dirty check. Limits verified in a delivered build session (2026-08-05): closures have NO `reduce`; `while` loops DO work in `onSend` handlers; our build-verified surface found date functions limited to `date:getTodaysDate` / `getTodaysDateFormatted` / `getDateTimeZone` / `match` / `parse` with NO arithmetic. HOWEVER a canonical DevRel PMD `.script` (`pmdScripting/presentation/scripts/dateCalculations.script`) uses `date:add`, `date:after`, `date:month`, `date:year`, `date:extractValue`, `date:parseDateString` - see the sample-verified note below (Verify-before-promote #3). Reconciliation: `date:add` arithmetic appears supported in PMD `.script` FILES per canonical sample; our "no arithmetic" experience may have been inline-`<%%>`-scoped or release-dependent. Until you build-verify `date:add` in your target tenant, treat relative-date math ("due in 7 days") as safest in an orchestration - where `date.parse(s,"yyyy-MM-dd").plusDays(n)` is build+runtime verified (orchestration.md section Expression language). House debug convention: gate `console.info(...)` calls behind an `attrstore.debugFlag` App Attribute so admins toggle logging in-tenant without a code change - adopt on every app.

### Sample-verified script surface (per Workday App Catalog samples)

Additions the official samples show (sample-verified - below the build-verified surface above; build-verify before relying):

- **Direct widget property assignment** `widget.value = x` (alongside the verified `.setValue()`).
- **Field validation from script:** `widget.setError(msg)` / `widget.clearError()`, plus a page-level `onSubmit` handler to gate submission.
- **Counted range for-loop:** `for (var i: 1 to n) { ... }` (a counting-loop form; closures still have no `reduce`).
- **`console.debug/info/warn/error(...)`** all land in Analytics/Logs - filter the log stream with `wd_category is console` (complements the `attrstore.debugFlag`-gated `console.info` house convention above). All four severities are sample-confirmed (`pmdScripting/presentation/logging.pmd`, 2026-08-07).
- **`standardEditButtonsHidden`** - CONFIRMED: `"standardEditButtonsHidden": "<% true %>"` (a `presentation`-level property) DOES hide the EDIT OK/Cancel footer chrome (canonical `createAWorkEvent/.../registerConfirmation.pmd`, `generateWQL/.../queryBuild.pmd`, 2026-08-07). This CORRECTS the old "no prop suppresses it" gotcha (now fixed in pmd-gotchas.md #26/#28). Trade-off: once hidden, a custom `button`/`pageActionButton` must drive the commit - the reliable platform auto-commit is gone.
- **Date functions - `date:add` arithmetic** - CONFIRMED in a canonical PMD `.script`: `date:add`, `date:after`, `date:month`, `date:year`, `date:extractValue`, `date:parseDateString`, `date:format` (`pmdScripting/presentation/scripts/dateCalculations.script`, 2026-08-07). Note: the earlier-speculated method-forms `.between()`/`.withMonth()`/`.year()` do NOT appear in canonical - do not cite them. This partially contradicts our build-verified "no PMD date arithmetic" note (see the Script/expression surface note above) - `date:add` is the arithmetic entry point in `.script` files; still build-verify in your target tenant before moving relative-date math out of an orchestration.
- **`searchEndPoint` in the page body** - CONFIRMED as a page-body **picker/instance-list widget** (`searchEndPoint` + `searchResultValues`), canonical `capitalProjectPlanning/presentation/CapitalPlanningRequestCreate.pmd`. Refines the old "does not work as a page-body widget" note: it works on a picker widget bound to `searchResultValues` (the same widget also carries `selectedValuesAndDescriptors: [{id, descriptor}]` to preseed selection). 2026-08-07.
- **`textArea`** - native multi-line text input widget (sample-confirmed; use where a single-line text widget is too small).
- **`selectedValuesAndDescriptors`** - picker property to preseed selected instances as `[{'id':..., 'descriptor':...}]` without a round-trip (sample-confirmed on the picker above).
- BUILD-VERIFIED: **`bestEffort: "true"` endpoint property** - on a non-deferred inbound endpoint, lets it fail soft (endpoint result is undefined, page still renders). Use for page-load endpoints that may 404/error (e.g. `workers/me` under ISU login). `failOnStatusCodes` is for OUTBOUND/submit endpoints ONLY and has NO effect on page-load endpoints. Verified in UAP v2 build b39834766401d3acfe7496ceec484c88 (2026-08-28). NOT a fix on a DEFERRED `.invoke()` (pmd-gotchas #85): a flow that completes with a non-JSON answer shows the platform page error, and a flow that fails comes back empty with no error (corrected 2026-10-07).

## UX house patterns (proven on the current program; adapt per client)

- Confirm-before-commit: entry page stashes values to flow scope (outboundVariable-only outboundData, no POST); a confirm page reviews and runs the real POST on OK.
- Confirm/landing micro-pages must be `pageType: EDIT` (+ a no-op outboundVariable) to get OK/Cancel in the platform footer; a body button on a chrome-less micro page looks wrong.
- Read-only timestamps in grids: `readOnlyText` cellTemplate with `('' + x).substring(0,10) + ' ' + ('' + x).substring(11,16)` - a `date` cellTemplate renders as a picker even when disabled.
- **Grid cellTemplate default = `readOnlyText`, never `text`** - on an EDIT page (which any list page becomes the moment it hosts a filter bar), `text` cells turn into editable inputs users can type into; `readOnlyText` stays display-only, renders identically on VIEW, and is valid inside cellTemplates (gotcha #47; verified at ~91-cell scale, 2026-08-06). Reserve `text` cellTemplates for intentionally editable grids.
- Soft-delete: `active` BOOLEAN, "remove" = PUT active=false (DELETE on a referenced instance returns 500); all reads filter `r.active == true`; every PUT carries `active` forward (PUT is full-replace); backfill the flag on pre-existing rows after adding it.
- Grid on EDIT page shows an unavoidable leading gutter column; remove +/- row controls with grid-level `"enabled": false`. Actions columns: stack buttons vertically (`section horizontal:false`) so the auto-width fits the widest single button.

## Show / hide patterns (three distinct controls - don't confuse them)

- **`render`** (expr or literal) - the widget is not built into the tree at all when false. Use for mutually-exclusive widgets whose absence should collapse layout (per-row action buttons, alternate messages). This is the one to reach for in grid cell templates.
- **`visible`** (expr or literal) - widget exists but is hidden; toggle at runtime with `widget.setVisible(true/false)`. Use for progressive disclosure of a field/fieldSet that reveals on a choice.
- **`enabled: false`** - shown but read-only/greyed. Use for computed display fields and intro `richText`.

**State-machine actions in one grid cell** - each button's `render` keys off the row's state (and a computed helper), so exactly one action shows per state; a fallback `readOnlyText` explains when none is available:

```jsonc
{ "type": "button", "label": "Continue Room",
  "render": "<% expiryAssignment.status == 'In Progress' %>", ... },
{ "type": "button", "label": "Check In",
  "render": "<% expiryAssignment.status == 'Assigned' && ! anyInProgress() %>", ... },
{ "type": "readOnlyText", "value": "Finish room in progress first",
  "render": "<% (expiryAssignment.status == 'Assigned' || expiryAssignment.status == 'On Hold') && anyInProgress() %>" }
```

Drive visibility off ONE computed value (`anyInProgress()`, `activeAssignmentStatus(id)`) reused across every button rather than repeating the raw condition - the rule lives in one place.

**Progressive disclosure** - a `fieldSet`/field starts `"visible": false`; a checkbox/radio `onChange` reveals it and keeps validation in sync:

```jsonc
"onChange": "<% if (self.value) { expiryItemFS.setVisible(true); quantity.setRequired(true); }
                else { expiryItemFS.setVisible(false); quantity.setRequired(false); quantity.setValue(0); } %>"
```

Hidden value-holder fields (`"render": false` / `"visible": false`) are also used to stash looked-up ids/costs so the commit step reads them from fields instead of re-querying - pair with the compute-once pattern in [efficiency.md](efficiency.md). Always reset dependent fields on the hide branch (`setValue('')`) so stale values don't get committed.

**Cascading picker + clear-dependent pattern** - when a parent picker changes, blank all dependent widgets first, then populate them with the new value. Standard shape in `onChange`:

```jsonc
"onChange": "<% 
  dependentPicker.setValue('');
  dependentPicker.values = [];
  dependentGrid.setRows([]);
  if (! empty self.value) {
    const result = detailEndpoint.invoke();
    dependentPicker.values = result.data ?? [];
  }
%>"
```

Assigning `.values` is the supported way to refill a picker's OPTION LIST at runtime (donor: poc-task-tracker's `parentTaskDropDown.values = getTasksByMainTaskResponse.data`); `setValue` sets the SELECTION, not the list. The invoked endpoint must get its parameter from a live widget read in its own declared `parameters` (efficiency.md form (b)) - invoke args don't feed declared parameters (pmd-gotchas #49). Two more traps: wire the cascade to the PARENT's `onChange`, never the child's `onSearch` (onSearch fires on TYPING, not on opening the picker - gotcha #75); and if the selection must survive a page round trip, the picker needs BOTH `selectedValues` AND a `values` list containing that entry, which takes a second, non-deferred twin endpoint `exclude`-gated on the parameter being present (gotcha #76). Skip the blank-first step and stale selections from the previous parent quietly ride through to the POST. (Verified in a delivered build session, 2026-08-20.)

## Official platform limits & event-order facts (official-docs - Workday Education course manuals, crawled 2026-08-25; spot-verify load-bearing numbers in-tenant)

- Endpoint limits: max response 25,000,000 bytes per endpoint; 24 s timeout per endpoint; 60 s page-wide timeout. (Related but DISTINCT clock: the 25 s sync-orchestration-from-page cap in orchestration.md - the manual prints both numbers; they are enforced at different layers, do not merge them.)
- Event order: onLoad and onSend fire BEFORE PMD tag processing, so they CANNOT access widgets (widget events - onChange, onRowAdd, onRowRemove, onRowSelect, onSearch - have full widget access). Page load sequence: onLoad -> endpoint invocation (concurrent unless dependent) -> widget rendering -> onSend.
- onSubmit is SUPPRESSED while ANY error or warning is present on the page - clear them in onChange handlers first or the submit silently never fires.
- Grid write batching default: ONE API call per changed row (10 edits = 10 calls); set isArrayOutBinding for a single batched array submission.
- Script engine numbers: max 25 call frames; 5 s CPU per script execution (excludes endpoint/widget API wait time); 100 KB per PMD / script / pod / AMD file; max 2 levels of nested script-module includes; script-module FILES cannot read predefined app variables (queryParams, attrstore, ...) - pass them in as parameters.
- Page security: a maximum of THREE security domains can be used on a page (pairs with the `enabledForPageSecurity` note at the top of this file); both View AND Modify permission grant page access.
