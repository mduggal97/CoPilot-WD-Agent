# PMD charts (Chart 2.0) - widget vocabulary

Sample-verified from the official Workday App Catalog `chartDictionary` sample (28 PMDs, one per chart type + feature) plus real usage in `workFromAlmostAnywhere`, `sentimentAnalysisWithTheAIGateway`, `salesCommission`. Tier = sample-verified (official sample source; above doc-sourced, below our own build-verified). Charts were a blind spot in the rest of our PMD notes - this is the reference.

## The 13 chart types (all "Chart 2.0", `type: "<name>Chart2"`)

`lineChart2` / `clusteredBarChart2` (+`barOrientation: VERTICAL|HORIZONTAL`) / `stackedBarChart2` / `percentBarChart2` / `comboChart2` (bars+lines) / `dualAxisChart2` (two measurement axes) / `donutChart2` / `bubbleChart2` / `scatterChart2` / `stackedAreaChart2` / `overlaidAreaChart2` / `percentAreaChart2` / `waterfallChart2` (+`accentFirstMark`, `appendEndMark`).

(There is a legacy Chart 1.0 family, e.g. `clusteredColumnChart` - superseded by the `*2` types; don't use it in new work.)

## Universal data binding

Every chart takes a row list and reads fields per row:
```
"data": "<% listOfRowMaps %>",     // the data source (endpoint.data, a pageVariable, a computed list)
"dataVariableName": "row",         // the per-row loop variable
```
Then each dataset is `{name: "<legend label>", value: "<% row.field %>"}` - the `value` is a per-row expression.
- **Multi-series:** `measurementDataSets: [ {name, value}, {name, value}, ... ]` (plural).
- **Single-series** (waterfall, bubble): `measurementDataSet` (singular).
- **Category axis:** `categoryDataSet: {value: "<% row.category %>"}`; optional **`secondaryCategory`** for grouping - swap primary/secondary to pivot which field clusters.

## Per-dataset props

`chartMarkType: BAR|LINE|POINT` (combo - mix marks per series) / `axisPosition: LEFT|RIGHT` (dualAxis) / `chartMarkLabel` (value labels drawn on the marks) / `hideInTooltip` / `numberFormatOptions: {formatType: PERCENT|SCIENTIFIC, precision, showTrailingZeros, signType: PARENTHESIS, numberFormatCode}`.

## Chart-level props

- `title` / `subtitle` - expressions.
- `legendPosition: TOP | BOTTOM(default) | LEFT | RIGHT | HIDDEN`.
- `accessibilityMode: true` - pattern fills for color-blind safety (recommend ON for client-facing dashboards; ties to the nfr-accessibility pass).
- `animateOnLoad`, `showOutline`, `hideChartControls`.
- `measurementAxisOptions: {axisTitle, axisMinimum, axisMaximum, axisIncrement, hideAxisValues, hideAxisTitle, comparisonLineValue + comparisonLineLabel}` - the comparison line is a horizontal reference/target line.
- `categoryAxisOptions: {axisTitle, axisValueOrientation: VERTICAL, hideAxisValues}`.
- `targetLineDataSet` - per-category target ticks (can carry its own `chartMarkLabel`).

## Type-specific datasets

- **Donut:** `sliceSizeDataSet`, `sliceColorDataSet`, `sliceDetailDataSet` (extra tooltip line), `showLabelLines`, `showPercentLabels`, `hideLabels`, `colors`.
- **Bubble:** `measurementDataSet` + `categoryDataSet` + `bubbleSizeDataSet` + `bubbleColorDataSet`.
- **Scatter:** `horizontalAxisPositions` / `verticalAxisPositions`, `chartMarkLabel`, `showRegressionLine`, and **`quadrantOptions`** = a 9-box: `{horizontalOriginPosition, verticalOriginPosition, upperRight/upperLeft/lowerLeft/lowerRightQuadrantColor: POSITIVE|NEGATIVE|NEUTRAL}`.

## Behavioral facts (verified in the dictionary's feature pages)

- Charts are legal **view-only widgets on EDIT pages** (`featureEditPage.pmd`) - a chart on a filter-bar dashboard is fine.
- A misconfigured chart renders an **empty-state placeholder, not a crash** (`featureEmptyState.pmd`) - unlike most PMD null landmines.
- Charts work inside `panelList`, horizontal fieldSets (dashboard grids), and **cards** - a `chartCard` hosts a full chart in a card body; `workFromAlmostAnywhere/presentation/cards/daysChart.card` puts a donut in a Workday-Home card with a dynamic `indicator` badge.
- **Podium / ranking trick** (`podiumChart.pmd`): to draw a 1-2-3 podium, invert the values (`5 - rank`) so #1 is tallest, then `chartMarkLabel` shows the *real* value, `hideInTooltip` + `hideAxisValues` suppress the inverted numbers.

## Where to reach for one

Read the matching `_reference/app-catalog/chartDictionary/presentation/*Chart2.pmd` for a copyable, minimal instance of any type; the `feature*.pmd` files each isolate one capability (axes, legend, tooltip, number formatting, accessibility, empty state, edit-page). See [app-catalog-registry.md](app-catalog-registry.md) for the full sample index.
