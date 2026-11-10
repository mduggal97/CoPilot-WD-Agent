# PMD widget catalog - per-widget property reference + Grid deep-dive

Scope: the WIDGET-LEVEL reference. Page architecture, endpoints, flows, and show/hide patterns stay in
[pmd.md](pmd.md); runtime landmines in [pmd-gotchas.md](pmd-gotchas.md); Chart 2.0 in [charts.md](charts.md).

Provenance tiers used below:
- **sample-verified** - from the official Workday App Catalog `pmdWidgetDictionary` (62 demo PMDs, every
  widget with a live page) and `pmdScripting` samples under `workday-extend/_reference/app-catalog/`.
  Cited as `(sample: <file>)`. Build-verify before first production use.
- **build-verified** - from delivered production apps in our own source tree. Cited as
  `(build-verified: <app area>)`.

Legend: REQ = required (the demo never omits it / build fails without it). All snippets ASCII.

## Text / display widgets

| type | key properties (prop -> example -> note) | when to use | demo |
|---|---|---|---|
| `text` | `value` REQ (expr ok); `label`; `enabled: false` = display-only | one-line value; display mode = `enabled:false` | simpleTypes.pmd |
| `readOnlyText` | `value` REQ; `label` | always-display text; THE default for grid cells (gotcha #47) | simpleTypes.pmd |
| `richText` | `value` REQ (HTML: `<b> <br> <h1 style=...>`); `enabled:false` = rendered display, `true` = rich input | formatted copy, instructions, banners | simpleTypes.pmd |
| `title` | `label` REQ (expr ok: `"Redirect: <% queryParams.id %>"`) | the page header; one per page | redirectQuery.pmd |
| `number` | `value`; `minimumValue`/`maximumValue`; `totalDigits`/`fractionDigits`; `onChange` | numeric display/input with bounds | queryBuild.pmd |
| `currency` | `value`; `currencyCode: "USD"`; `showCurrencySymbol` (never shown on EDIT widgets); `totalDigits`/`fractionDigits`; min/max | money fields | simpleTypes.pmd |
| `hidden` | `value` REQ; `valueOutBinding` (incl. multipart form `postAttachment::data:file` with value `cid:filedata`) | invisible value carrier for payloads and grid rows | bpExtender.pmd |
| `image` | `imageUri` REQ (URL or `data:<type>;base64, <b64>`); `userPhoto: true` shrinks; `render` | show an image; resize options are very limited | images.pmd |
| `labeledImage` | `charm: "FOLDER"` (25+ charm ids: SEARCH, EMAIL, LOCATION, JOB_REQ...) OR `imageURL`; `label` | icon + label rows | labeledImage.pmd |
| `labeledThumbnail` | `title`, `subtitle`, `imageEndPoint: {url, authType}` | thumbnail card-row with text | labeledThumbnail.pmd |
| `progressIndicator` | `value` REQ, `maximumValue`, `isPercentage`, `label` | progress bar; NOT reactive - wrap in `dynamicSection` and reassign `.data` (gotcha #38) | progressIndicator.pmd |

## Input widgets (EDIT pages only)

| type | key properties | when to use | demo |
|---|---|---|---|
| `textArea` | `value`; `label`; `helpText`; `required` | multi-line text (`multiline:true` on `text` is a silent no-op - gotcha #50) | simpleTypes.pmd |
| `date` | `value` (`date:getTodaysDate(...)`); `datePrecision: DAY\|SECOND`; `dateFormat`; `displayTimeZone` | dates/timestamps; outbound needs `.format('yyyy-MM-dd')` (gotcha #14) | simpleTypes.pmd |
| `time` | `value: "01:23 AM"` | time-of-day, distinct from `date` | simpleTypes.pmd |
| `checkBox` | `value: "true"`; `label`; `helpText` | boolean; as a submit gate prefer radioGroup (gotcha #25) | simpleTypes.pmd |
| `numericStepper` | (no dictionary demo; build-verified widget - pmd.md cheat-sheet) | +/- integer input | - |
| `fileUploader` | `fileTypes: "pdf,docx,..."`; `validations: [{errorMessage}]`; `singular`, `compact`; `valueOutBinding: "ep:filedata:"`; pair outbound endpoint with `multiPartFileLast: true` | file upload into an `.attachment` BO or flow | resume.pmd, bpExtender.pmd |
| `fileUploaderRow` | child of `fileUploader.children[]`: `attachment` (an attachmentList), `fileName`, `fileType`, `allowRemove` | pre-seed an uploader with existing files | fileUploaderRow.pmd |
| `attachmentList` | `attachmentURL`, `attachmentName`, `attachmentUriTemplate: "[Target]"`, `attachmentAuth`, `instanceList: [{action:"attachment", descriptor, mimeType, iconId}]` REQ | list/download attachments; crashes the page without `instanceList` (gotcha #41) | attachmentList.pmd |
| `superEdit` | `children: [widget]` | pencil-icon reveal of an inline edit control | superEdit.pmd |

## Selection / picker widgets

| type | key properties | when to use | demo |
|---|---|---|---|
| `dropdown` | one of: `instanceList: [{id, descriptor}]` (hardcoded) OR `values: "<% list %>"` + `idKey`/`displayKey`; `selectedValues: "<% ['id2'] %>"` preselects; `onChange`; value reads as a LIST of ids (`x.value[0]`) | single-select from a bounded list | dropdown.pmd |
| `instanceList` | `values` REQ (seed `"<% [] %>"` when search-driven); `idKey`/`displayKey`; `widKey` (enables Workday related-actions hover); `multiSelect`; `searchEndPoint: "<% endpoints.x %>"` + `searchResultValues` (type-ahead; `instanceListQuery` is the implicit search-text var in the endpoint URL); `selectedValuesAndDescriptors`; `guide` | THE type-ahead picker; related-action instances | instanceList.pmd, relatedAction.pmd, queryBuild.pmd |
| `checkBoxList` | `values` REQ; `idKey`/`displayKey`; `maxSelectable: 2` | bounded multi-select with a selection cap | instanceList.pmd |
| `radioGroup` | `instanceList` OR `values`; `selectedValues`; `hideDisplayOption` | mutually-exclusive choice; reliable submit gate via `.selectedEntries[0].id` | personalInformation.pmd |
| `snapSlider` | `instanceList` REQ (ordered scale points) | Likert / rating scales | snapSlider.pmd |
| `multiSelectCalendar` | `calendarStartDate`; `eventData: {on, as, template: {startDate: "<% date:parse(x) %>", endDate, style, title, editTask: {render, task}}}`; `sidebar: {task, position}`; `submitButton: {label, datesQueryParamName, task}` | month calendar with clickable events + date multi-select; sidebar/editTask targets are plain pages (`sidebar.pmd`, `popup.pmd` = micro EDIT page reading `queryParams`) | calendar.pmd |
| `monikerLevel` | entries of `instanceList.monikerLevels[]`: `{levelValues: "<% ep.data %>", endPoint: "<% endpoints.x %>"}`; parent selection feeds the next level via `promptSelections[n]` in the endpoint URL | hierarchy drill (org chart) inside a picker | monikerLevel.pmd |

## Layout containers

| type | key properties | when to use | demo |
|---|---|---|---|
| `section` | `children[]` REQ; `horizontal`; `columnWidthRatios: [0.5, 0.25, 0.25]` (horizontal only; a `title` CANNOT be used on the same section as columnWidthRatios - stated in the demo itself); `title`; `visible`/`render`/`id` | the general container; ratio columns | sections.pmd |
| `fieldSet` | `children[]`; `title`; `horizontal`; `collapsible: true` | labeled/collapsible field group | personalInformation.pmd |
| `tabs` | page-level `presentation.tabs[]` (>=2), each a `section` with `label`; a `body` with >=1 child is REQUIRED and always renders ABOVE the tabs | stacked views on one page | tabs.pmd |
| `areaLayout` | `body {type, layout: "left", primaryArea: [], secondaryArea: []}` | main content + side rail | areaLayout.pmd |
| `basicFormLayout` | `body {type, sections: [{type: "layoutSection", children: []}]}` | stacked form sections; `layoutSection` ships today | basicFormLayout.pmd |
| `hub` | `body {type, label, initialTask: {taskId}, navigationTasks: [{type: "group", icon, label, items: [{label, task}]} \| {icon, label, task}], additionalLinks: {title, links: [{type: "task"\|"external", ...}]}}`; sub-page id `home` collides with the platform Home shell (gotcha #51) | left-nav multi-page app shell | projectHub.pmd |
| `listDetailHub` | `body {type, label, items: "<% list %>", itemVariableName, icon, navigationTemplate: {icon, label, task: {taskId, parameters}}, additionalLinks}` | master/detail generated per data row | ticketsListDetail.pmd |
| `cardContainer` | `cards: [{type: "card", cardId, parameters: "<% {...} %>"}]`; `layout: "GRID"\|"MASONRY"`; `dynamicCards` for data-driven tiles (pmd.md Cards section) | hub/dashboard tiles | home.pmd, projectStatus.pmd |
| `dynamicSection` | `data` REQ (reassign `<id>.data = {...}` to force re-render), `dataVariableName`, `children[]` | the reactive escape hatch - re-render children on demand | queryBuild.pmd, progressIndicator.pmd |
| `editWizard` | `body {type, title, subtitle, summarySettings: {enabled, label}, editTasks: [{label, render, task: {taskId}}]}`; `enableSaving` adds draft autosave (pmd.md 26R1 section) | multi-step wizard over existing EDIT pages | editWizard.pmd |
| `pod` | `{type: "pod", podId}` instantiates `presentation/pods/<name>.pod` (`{podId, seed: {parameters, template}}`, `@@param@@` placeholders) | reuse a repeated widget/endpoint block | pods/header.pod |
| micro pages | page-level `"micro": true` (+`pageType: edit` ok) and `"microConclusion": true` | modal pop-up / flow-end confirmation pages | micro.pmd, microConclusion.pmd, popup.pmd |

Layout scale evidence (build-verified): one delivered production app (a ~30-page logistics app) runs
`cardContainer` x29, `layoutSection` x16, `basicFormLayout` x6, plus a `hub` shell - these containers are
production-safe at app scale, not just demo toys. 26R1 `columnLayout`/`multiStepLayout` remain doc-sourced
only - see pmd.md "Layout tags (26R1)".

## Action widgets

| type | key properties | when to use | demo |
|---|---|---|---|
| `button` | `label` REQ; `action: PRIMARY\|AUXILIARY\|LINK` (omit = secondary); `taskReference: {taskId, parameterBindings}` (`parameterBindings` OVERRIDES a `parameters` map - stated in the demo); OR `workdayTaskReference: {wid}` to launch a DELIVERED Workday task/report by WID | navigation + delivered-task launch | buttons.pmd, linkToDelivered.pmd |
| `pageActionButton` | `label`; `onClick` script REQ; `visible` | in-page action, no navigation/flow (recompute, invoke, setRows) | buttons.pmd, queryBuild.pmd |
| `buttonGroup` | `children[]` of buttons; `action` | cluster of related buttons | buttons.pmd |
| `dropDownButton` | `values: [{label, taskReference}]`; `action` | one button, menu of destinations | buttons.pmd |
| `editButtonBar` | `editButtons: [{type: "editButton", buttonType, ignoreRequiredFields: "true"} \| {type: "dropdownEditButton", buttonType, dropDown: {dropdown}}]` | custom EDIT-page submit bar; prefer platform OK/Cancel by default (gotcha #28); `ignoreRequiredFields` lets a save bypass required checks | buttons.pmd |
| `externalLink` | `descriptor` REQ; `url` (absolute, or tenant-relative `<% '/' + tenant + '/d/home.htmld' %>` - still opens a new tab) | link out of the app | buttons.pmd |
| `guide` | attached to a widget as `"guide": {type, id, title, text}` | contextual help popover on a field | queryBuild.pmd |
| `congratulationsPopup` | `textCongrats`, `textSubmitted`; `render` | native success popup - prefer over a micro-conclusion page for simple "done" | congratulationsPopup.pmd |

## List / repeat widgets

| type | key properties | when to use | demo |
|---|---|---|---|
| `panelList` | `children[]` = one template panel rendered per row; `doNotAdd`/`doNotRemove` hide the user +/- controls; read answers via `panel.children[i].childrenMap.<id>.value` (pmd.md) | dynamic repeating form sections | educationAndEmployment.pmd, references.pmd |
| `loop` | `on: "<% list %>"`, `as`, `children[]` (template per row) | render a widget-set per instance in the body | loops.pmd |
| `instanceLoop` | inside `instanceList.instanceListLoopTag`: `{templateInstance: {id, descriptor, wid}, on, as}` | build picker instances from data with related-actions | loops.pmd |
| `templatedListItem` | `title` (an instanceList with `taskReference`), `subtitles: []` | home-style link list rows | templatedListItem.pmd |

## Cards (.card files - parameterized templates; see pmd.md "Cards & hub pages")

Card shell: `{id, parameters: [names], header: {title, subtitle, icon: "wd-accent-*", indicator: {label, color-expr}}, body, footer: [{label, taskReference | workdayTaskReference | url}]}`.

| body type | key properties | demo |
|---|---|---|
| `simpleCard` | `value` (text body) | cards/ticket.card |
| `pillCard` | `pills: [{label, taskReference}]` | cards/pill.card |
| `listCard` | `on`/`as`/`limit`; `template: {label, value, secondaryValue, secondaryValueWidth, indicator}` | cards/features.card |
| `chartCard` | `chart: {<full Chart 2.0 definition>}` (see charts.md) | cards/ticketStatusChart.card |
| `imageCard` | `endPoint: {name, url}` | cards/imageCardExample.card |

Home-hub cards use `.carddefinition` files with their own `endPoints` (sample: cards/listCard.carddefinition).

## Media / misc

- `video` - `mediaId` REQ (Workday Media Services must be enabled on the tenant; media access controls
  are honored) (sample: splashPage.pmd, projectHome.pmd).
- `applicationException` - declarative page-level error/warning banner; shape in pmd.md.

## Icon names (`wd-accent-*` and `wd-icon-*`) - the registry and a silent failure

- **[BV] An unknown/misspelled icon name renders BLANK - silently, no build error.** Icon names are unvalidated at build, so confirm every name exists in its package before shipping.
- **`wd-accent-*`** names (card headers, `labeledImage`, accent tiles) resolve against the CLASSIC Canvas accent icon set - the npm package `@workday/canvas-accent-icons-web` (~250 icons). It is NOT the newer "expressive" gallery - many expressive names render blank in-tenant.
- **`wd-icon-*`** names (hub `navigationTasks`, system chrome) come from the SYSTEM icon set - `@workday/canvas-system-icons-web` (a different, larger set). Do not assume a name in one set exists in the other.
- **Get the valid list from jsdelivr:** fetch the package's icon manifest, e.g. `https://data.jsdelivr.com/v1/packages/npm/@workday/canvas-accent-icons-web` (and `.../@workday/canvas-system-icons-web`) - the SVG filenames ARE the valid names (strip `.svg`).

## BP / history widgets (the bpExtender family)

`bpExtender` lives at a page-level `"extender"` key (SIBLING of `body`, inside `presentation`) and renders
the standard Workday BP chrome on an Extend page (sample: bpExtender.pmd):

- `bpButtons: [{type: "bpButton", buttonType: PRIMARY|AUXILIARY, label, id}]` - the BP action buttons.
- `attachment` - a `fileUploader` (multipart via an outbound endpoint with `multiPartFileLast: true`).
- `comment` - a `textArea` bound out via `valueOutBinding: "submitStep.comment"`.
- `commentHistory` / `processHistory` - each a `bpTemplatedList` (`on`/`as`/`template`) whose template is a
  `commentHistory` (`author`, `text`, `date`) or `processHistory` (`actionEvent`, `workflowStep`, `status`,
  `completedDate`, `user`, `delegationMessage`) widget.

Helper-orchestration pattern (sample-verified): the page's endpoints all hit ONE sync helper flow
multiplexed by a query param - `bpExtenderHelper/launch?action=commentHistory|processHistory|claim|echo|attachment`
on the `orchestration` dataProvider - plus a second helper flow for the multipart file upload
(`bpExtenderHelperFileUploader/launch`). Outbound responses are snapshotted to flow scope with an
`outboundVariable` (`"<% updateClaim ?? {:} %>"`) so the confirm page can render them
(sample: bpExtender.pmd + bpExtenderConfirm.pmd + orchestration/bpExtenderHelper.orchestration).

## GRID DEEP-DIVE (consolidated)

### Core shape

- Data prop is `rows` REQ (`"<% endpoint.data %>"`) - `value` on a grid FAILS the build (pmd.md).
- `rowVariableName` REQ - and must not be a JEXL word-operator (`lt`, `eq`, `or`...; pmd.md).
- `columns: [{type: "column", columnId REQ, label, cellTemplate: {<widget>}, sortableAndFilterable, render}]`.
  Column `label` and `render` take expressions - a runtime-shaped grid (labels + column count driven by
  data) is legal (sample: queryBuild.pmd builds an 11-column grid over unknown WQL fields via
  `queryResult[data.fieldList[n]]` bracket access).
- Grid-level props seen in samples: `gridType: "LIST"` (read-style) or `"EDIT"` (+`addButtonLabel`,
  build-verified: delivered user-provisioning app); `doNotAdd`; `doNotRemove` (sample: gridsEdit.pmd) AND
  `doNotRemoveRow` (sample: gridEvents.pmd; build-verified in a delivered production app) - both spellings
  appear, the build-verified one is `doNotRemoveRow`; `showRowMover: true` (drag row reorder);
  `enabled: false` (kills the +/- row controls); `selectionEnabled`; `maxRowSelection`;
  `excelExportEnabled`; `pagingInfo`.
- Column `width` is invalid (silent WARN, gotcha #30). Stack per-row action buttons vertically instead.

### Cell types and the null-safe idiom

- Default every display cell to `cellTemplate: {type: "readOnlyText"}` - on an EDIT page a `text` cell
  becomes a live input (gotcha #47). ANTI-GOTCHA FLAG: the dictionary demos use `text` +
  `enabled: false` cells throughout (grids.pmd, gridsEdit.pmd); that renders read-only too, but our house
  rule stays readOnlyText - identical render, no enabled-flag to forget.
- Null-safe cell idiom (build-verified at 29-grid scale in a delivered production app):
  `"value": "<% empty row.lotNumber ? '-' : row.lotNumber %>"` - guards gotcha #7 NullOperand crashes.
- Editable cells: `number`/`text`/`dropdown` cellTemplates with per-cell `onChange`
  (sample: gridEvents.pmd quantity column; gridsEdit.pmd Row Mover priority dropdown).
- Buttons in cells: `cellTemplate: {type: "button", taskReference: {taskId, parameterBindings}}` passes
  row values as queryParams (sample: grids.pmd "Go" column).

### Hidden carrier columns (pass ids/WIDs through selection)

Two build-verified shapes plus the sample shape:
1. Whole-column hidden: `{columnId: "idColumn", cellTemplate: {type: "hidden", value: "<% row.id %>", visible: false}}`
   (sample: gridEvents.pmd). **CAUTION (gotcha #65):** a `type:"hidden"` cell's `.value` is INVISIBLE to
   outbound-endpoint `exclude` conditions - fine for selection READ-BACK (shapes here), but if the value
   gates an `exclude`, use `type:"text"` + `enabled:false` + `visible:false` instead. **Never `render:false`** - an unrendered widget is never built and reads empty at OK (gotcha #88, runtime-verified 2026-10-21).
2. Hidden widget nested in a cell `section` next to the visible widget:
   `{type: "hidden", id: "receiptslineWID", value: "<% row.eventTarget_01?.id %>"}` - read back in `onSend`
   as `row.childrenMap.<columnId>.<hiddenWidgetId>.value` (build-verified: delivered production app).

### Selection + reading selected rows

- `selectionEnabled: true` adds checkboxes; `maxRowSelection: 1` = single-select, `10` = capped multi
  (samples: gridEvents.pmd, pmdScripting pageEvents.pmd).
- `onRowSelect` is the grid-level selection event: `"onRowSelect": "<% gridEvents.selectRow(); %>"` - must
  call a script-FILE function (gotcha #2). In the script: `grid.selectedRows` (property) - test
  `.isEmpty()`, read `selectedRows[0].childrenMap.<columnId>.value` (sample: gridEvents.script).
- `grid.getSelectedRows()` (method form) works in outbound `onSend` - loop rows and read
  `row.childrenMap.<columnId>.<widgetId>.value` into the payload (build-verified: delivered production
  app; also pmd.md). Multi-select bulk-ops pattern: iterate selected rows into a list of maps, hand the
  list to a flow via `outboundVariable` scope.

### Editable-grid commit (the durable write paths)

Script-side `.invoke()` POSTs in `onSubmit` are TRANSACTIONAL and roll back (gotcha #52). The two
framework-managed paths that persist:
1. **Grid `outboundFields`** - per-row commit binding on the grid itself:
   ```jsonc
   "outboundFields": [{ "outboundEndPointName": "postCategory",
     "values": [{"outboundPath": "categoryName", "value": "<% catName.value %>"},
                {"outboundPath": "sortOrder",   "value": "<% catSort.value %>"}] }]
   ```
   with `gridType: "EDIT"` + `addButtonLabel`; the platform OK fires the outbound per added/edited row
   (build-verified: delivered user-provisioning app).
2. **`onSend` outbound endpoints** reading `getSelectedRows()` / widget values (pmd.md outbound section).

### Grid events summary (sample: pmdScripting gridEvents.pmd + gridEvents.script)

| event / API | where | evidenced use |
|---|---|---|
| `onRowSelect` | grid-level | toggle a detail section, deferred `endpoint.invoke({id})` per row |
| `onChange` | cell-level (inside cellTemplate) | recompute a sibling cell: `selectedRows[0].childrenMap.totalCostColumn.value = q * c` |
| `grid.selectedRows` | script property | read/write cell widget values via `.childrenMap` |
| `grid.setRows(list)` | script | THE refresh path - grids do not re-evaluate `rows` reactively (gotcha #39) |
| `grid.rows = list` | script file | direct assignment also works (sample: pageEvents.script) |
| `grid.rows` (read) | script file | iterate rows for validation; per-row cells via `row?.get('<columnId>')?.children[0].value` |

### Cascading clear

Parent picker changes -> `grid.setRows([])` first, then repopulate. Full pattern lives in pmd.md
"Cascading picker + clear-dependent pattern" - do not re-derive it here.

### Pagination and scale

- Sample-verified scroll paging (sample: gridsView.pmd "Paginated Grid"): endpoint URL reads implicit
  `pagingVariables`: `var limit = pagingVariables.limit ?: 100; var offset = pagingVariables.offset ?: 0;`
  and the grid takes
  `"pagingInfo": {"endPoint": "<% endpoints.workersPagedEndpoint %>", "rowCount": "<% ep.total %>", "data": "<% ep.data %>"}` -
  additional pages load as the user scrolls.
- Build-verified simpler cap: a delivered user-provisioning app populates a search grid only via a Search
  button and truncates client-side - `searchGrid.setRows(gridRows.subList(0, 100))` - pairing with the BO
  REST `limit` max of 100 (gotcha #15).
- No sample or build evidence exists for grid behavior beyond scroll-paging (virtualization thresholds,
  hard row caps) - plan for <=100-row pages or `pagingInfo`, and say so in designs.

### Export

- `"excelExportEnabled": true` on the grid = native Excel export, confirmed on a VIEW page alongside
  `sortableAndFilterable` columns (sample: gridsView.pmd). For FORMATTED workbooks (styling, multi-sheet)
  use the Excel-generation orchestration pattern - see [orchestration.md](orchestration.md).

### Reusable grid-validation module (build-verified: delivered costing app)

`presentation/scripts/gridColumnValidator.script` - include via `"include": ["gridColumnValidator.script"]`,
call `gridColumnValidator.areColumnsBlank(gridWidget)`:

```
const areColumnsBlank = function(gridWidget) -> boolean
  // true when ANY row has ALL of the watched columns blank (i.e. validation FAILS);
  // empty/missing grid returns false (treated as valid).
  // Row access idiom: row?.get('<columnId>')?.children[0].value over gridWidget.rows
{ "areColumnsBlank": areColumnsBlank }
```

Use it as an `onSubmit` submit gate (NOT a `validations` entry on the grid itself - a grid never evaluates one, pmd-gotchas #24) on worktag-style "at least one of these columns"
rules. Note the third row-access idiom it demonstrates (`row?.get(columnId)?.children[0].value`) alongside
`childrenMap.<columnId>.value` and `childrenMap.<columnId>.<widgetId>.value` - which one applies depends
on whether the cellTemplate is a bare widget or a section wrapper.

## Anti-gotcha reconciliation flags (dictionary vs our build-verified notes)

1. **`headerSize`**: queryBuild.pmd carries a PRESENTATION-level `"headerSize": "STANDARD"`. Our
   build-verified rejection (gotcha #50) was `headerSize` ON THE `title` WIDGET. Possibly two different
   properties - treat the presentation-level form as unverified and omit both until build-verified.
2. **`text` cells with `enabled:false`** render read-only in every dictionary grid demo - a working
   alternative to gotcha #47's readOnlyText rule, but keep readOnlyText as the house default (no flag to
   forget when a page later turns EDIT).
3. **`doNotRemove` vs `doNotRemoveRow`** - both appear in official samples (gridsEdit.pmd vs
   gridEvents.pmd); delivered production code uses `doNotRemoveRow`. Prefer `doNotRemoveRow`.
4. **`bestEffort: "true"`** BUILD-VERIFIED: on non-deferred inbound endpoints, lets the endpoint
   fail soft (result undefined, page still renders). Use for any page-load endpoint that may
   404/error. `failOnStatusCodes` is OUTBOUND-only - no effect on page-load. Verified in UAP v2
   build b39834766401d3acfe7496ceec484c88 (2026-08-28).
   NOT a fix on a DEFERRED endpoint (pmd-gotchas #85): a flow that completes with a non-JSON
   answer shows the platform page error; a flow that fails comes back empty with no error
   (corrected 2026-10-07). Fail soft in the flow.
5. **`onSubmit` + `setError` as a submit gate** is the sample-blessed validation pattern
   (pmdScripting pageEvents.pmd) - fine for pure validation, but remember gotcha #52: any script-side
   `.invoke()` WRITE in `onSubmit` rolls back regardless.
