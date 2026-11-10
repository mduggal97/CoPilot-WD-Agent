# Report Writer, calculated fields, and report administration

doc-sourced - Workday Education course manuals (public), crawled 2026-08-25; cite: "Workday Reporting"
+ "Creating and Securing Integrations" (building-custom-reports, calculated-fields chapters).
These are doc-tier facts: verify in-tenant before load-bearing use (labels, limits, and options can
shift by release).

**Scope:** authoring custom reports and calculated fields in the tenant, plus report administration
(scheduling, groups, bursting) and dashboards/worklets. Prism-side analytics -> `prism-and-reporting.md`.
The calc-field TYPE SELECTOR for Extend BOs -> `model.md` (this file is the tenant authoring how-to).
RaaS consumed as an integration source -> wd-integration-dev `integration-build.md` and its EIB docs.

## Object model in one breath

- **PBO** (Primary Business Object) = the report's main object; instances = rows. **RBO** (Related
  Business Object) relates 1:1 or 1:M. **CRF** (Class Report Fields) = fields available per object.
- **Report Data Source (RDS)** = a view/starting filter onto a PBO.
- **HARD RULE - the PBO is LOCKED once chosen.** You can swap data sources only WITHIN the same PBO.
  Wrong PBO = rebuild the report.
- Advanced reports reach RBO fields only **one level deep**; go deeper via calculated fields or
  (better) Document Builder.
- Discovery tools: **Business Object Details** (fields/RBOs/data sources/reports per object),
  **Data Sources**, **Report Fields**, **All Custom Reports**. Search prefixes: `rd:` custom reports,
  `rdt:` by tag, `field:` report fields, `cf:` calculated fields.

## Data source selection

| Category | Traits | Pick when |
|---|---|---|
| Standard | may carry built-in filter logic/prompts | manual's rule: "choose the data source that returns the smallest dataset that still includes all needed data" |
| Indexed | optimized for large-volume filter/group/facet/aggregation (Workers for HCM Reporting, Journal Lines for Financial Reporting, Trended Workers...) | performance matters; facets; matrix at volume. "Optimized for Performance" checkbox restricts to indexed fields; extend with non-indexed/calc fields via Create Data Source Extension -> Submit for Approval |
| Business View | blends component data sources | cross-source advanced/matrix/simple |
| Prism | user-created, blends non-Workday data | see prism-and-reporting.md |

## Report types - when each

Simple (limited, NOT shareable) | **Advanced** (RBOs, filters, charts, shareable, RaaS - the default
workhorse) | Matrix (group/summarize/drill) | Composite (multiple matrix subreports) | Search (facets)
| nBox | Trending | Transposed.

- Create via **Create Custom Report** or **Copy Standard Report to Custom Report** (only Report Writer
  standard reports are copyable - NOT XpressO; reports with deprecated sources/fields cannot be copied).
- **Hide Workday Delivered Report** suppresses a standard report you have replaced.
- Advanced-report tabs: Columns, Sort, Filter (PBO), Subfilter (RBO), Prompts, Output, Share, Advanced.

## Filters, subfilters, prompts

- **Subfilter (RBO) logic executes FIRST, then Filter (PBO).** The "RBO not empty" subfilter pattern
  removes PBO instances that have no related data.
- Filter condition = And/Or (+ parentheses in Advanced) + field + operator + Comparison Type:
  value in filter / value from another field / prompt user / **prompt user and ignore condition if blank**.
- Prompts come from: data-source built-ins, data-source-filter built-ins, field built-ins, calculated
  fields (Prompt for Value), Prompt Sets. Per-prompt options: Default Type (none / specify / determine
  at runtime), Required, Do Not Prompt at Runtime, Do Not Include in Subtitle, Control Prompt Values.
- Performance: filter EARLY (data-source filter > report filter > calc field); sorting simple field
  types beats object field types; prefer report filters/subfilters over calculated-field conditions.

## HARD LIMITS (memorize this table)

| Surface | Limit |
|---|---|
| Matrix report | 12,000 rows / 250 columns / 15 summarizations / 25 detail-data fields / drill on up to 2 dimensions / 5 drill-to links per summarization |
| Worklet | must load in **<30 seconds** or it will not render on landing pages; max **100 rows** shown (default 10) |
| Home page / Workbench | first 20 worklets / first 12 |
| Dashboard | **6 tabs x 6 worklets per tab**; up to 50 custom dashboard domains per tenant |
| Embedded analytics | max 5 worklets per BP step; initiation-step worklets only on the DEFAULT BP definition |
| Report group | 200 reports per group with Excel template; 200 sheets per workbook when bursting |
| RaaS integration payload | **2 GB** |
| Temporary reports | expire after 7 days by default |
| Mobile reports | 100-row cap |
| Discovery board | 10 visualizations per sheet (sheets unlimited) |

## RaaS (Report as a Service)

- Advanced report + **Enable as Web Service** (Advanced tab) -> consumable by integrations, BIRT,
  Prism, or an external URL. Formats offered at the endpoint include XML/JSON/CSV per output options.
- The consumer must have data source access - a RaaS call runs under the caller's security, so an ISU
  consuming RaaS needs the data source + field domains like any user (see wd-deployment
  `configurable-security-admin.md`, three-part report access test).
- 2 GB cap for integration consumption (limits table). RaaS-as-source patterns for EIB/Studio ->
  wd-integration-dev `integration-build.md`.

## Sharing, ownership, security

- Custom report creation requires the **Analytics Data: Report Fields and Values** domain; reports
  default to owner-only.
- Sharing modes: don't share / all authorized users / specific groups+users. The sharer needs the
  matching Report Definition Sharing domain(s); you can only share with users who can access the data
  source + filter. Only the owner or holders of **Manage: All Custom Reports** can edit/delete.
- **Cannot delete a report in use** (e.g. backing a worklet).
- **Transfer Ownership of Custom Reports** task - mover needs Custom Report Administration or Manage:
  All Custom Reports; the new owner needs data source access + the Custom Report Creation domain. Run
  **Custom Report Exception Audit** first. (Departing-owner cleanup pairs with scheduled-process
  transfer - see report administration below.)
- Access rule for RUNNING a report (three-part test) and troubleshooting order: wd-deployment
  `configurable-security-admin.md`.

## Calculated fields - authoring

- Evaluated at RUNTIME, never stored (Prism calc fields evaluate at publish - prism-and-reporting.md).
  Anchored to a business object; Global object fields are usable everywhere.
- **Two creation scopes:**

| Scope | Tasks | Securing domain | Use when |
|---|---|---|---|
| System-wide | **Create Calculated Field** / **Maintain Calculated Fields** / All Calculated Fields report | **Custom Field Management** | reused across reports/integrations |
| Report-level | **Create Calculated Field for Report** | **Private Calculated Fields Management** | one report only; keeps tenant-wide lists uncluttered |

  Convert either direction with **Convert Calculated Field (for Report)**.
- **Values follow the underlying fields' domains** - a calc field never widens data access.
- **Lookup Related Value requires a 1:1 PBO-RBO relationship** (use Extract Single Instance for 1:M).
- **Cannot delete a calc field in use** - deprecate with the **Do Not Use** label (Governance /
  Additional Info tab) and check the Where Used tab first. Governance tab also carries: Description,
  Category (drives prompt placement), Authorized Usage (restrict to Benefits Eligibility, Payroll...),
  Intermediate Calculation flag.
- Function catalog (by group): Numeric - Arithmetic Calculation, Convert Currency, Convert Text to
  Number, Count Related Instances, Date Difference, Numeric Constant, Sum Related Instances, Text
  Length. Text - Concatenate Text, Substring Text, Format Date/Number/Text, Text Constant, Lookup
  Translated Value. Date - Build Date, Date Constant, Increment or Decrement Date. Boolean -
  True/False Condition. Instance - Extract Single Instance (needs sort field/direction/occurrence),
  Extract Multi-Instance (Subset / Intersection / Except / Union), Lookup Related Value, Lookup Range
  Band, Evaluate Expression (Band), Aggregate Related Instance, Lookup Value as of Date, Prompt for
  Value, Lookup Field with Prompts, Lookup Organization (Roles), Lookup Hierarchy (Rollup), Lookup
  Date Rollup.
- Performance: chained calc fields hammer runtime; put the most-excluding condition FIRST; prefer
  Document Builder over calc-field chains for multi-instance navigation.

## Report administration

- **Schedule a Report** (single reports or report groups); monitor via **Scheduled Future Processes**
  and **Process Monitor**; edit/suspend/transfer via **Schedule Future Process**.
- Recurrence: now / once future / daily / weekly / monthly / **Dependent** (on another process outcome)
  / custom criteria. End dates extend at most **5 executions past Dec 31 of the following year**.
- Output options: xlsx / PDF / CSV, File Deletion Period, "Do Not Output an Empty Report",
  "Hide Prompt Values".
- **Shared scheduled output BYPASSES standard security** - the recipient sees the file exactly as
  generated (requires the Report Output Sharing domain). Treat output sharing as a data-disclosure
  decision, not a convenience.
- **Alerts:** **Configure Alert** = a custom report (the condition data) + recipients + message +
  schedule; channels via **Edit Tenant Setup - Notifications**.
- **Report groups:** run several reports as one unit (fiscal-close packs); members need Enable Save
  Parameters + one saved filter; **Maintain Excel Template** merges output to one workbook; prompt
  sets pass shared values.
- **Bursting:** prompt value type "Bursting Set" in a report group -> one output per instance of the
  bursting field (per company, per org), deliverable to security groups tied to the securing entity.
- Cleanup/maintenance: **Delete Temporary Report Definitions** (purge expired temps); **Reporting Mass
  Action** (swap a deprecated field across Advanced reports; audited via View Reporting Mass Action
  History); Maintain Report Tags / Mass Update Report Tags.

## Dashboards and worklets (basics)

- Make a report a worklet: Output tab -> **Enable as Worklet** + choose Available On (landing pages /
  dashboards / mobile / Embedded on Tasks). Worklet-capable types: advanced, matrix, nBox, transposed,
  trending, composite - NOT simple/search. Configure prompt defaults so no input is needed; use indexed
  sources to stay under the 30-second rule.
- Tenant-level worklet config: **Maintain Dashboards** (optional/required per security group, sizing,
  title overrides; needs "Setup: Tenant Setup - Worklets" domain).
- Custom dashboards: secured to a domain (Maintain Dashboards > Settings); custom worklets ALSO need
  the report shared to the audience - dashboard access does not imply report access.
- Embedded analytics on BP steps: report Available On "Embedded on Tasks" -> share -> Business Process
  > **Maintain Related Worklets** -> map worklet prompts to BP context.
- Discovery boards live in Workday Drive; Pivot Table exports to a matrix report, Table to an advanced
  report; curation via **Maintain Data Source list for Discovery Boards** + **Maintain Field Lists for
  Reporting** (each field needs "Enable in Discovery Boards").

## Authoring checklist

1. Confirm the PBO before anything else - it locks.
2. Pick the smallest data source that still has the data; prefer indexed at volume.
3. Push conditions into data-source filters/subfilters before reaching for calc fields.
4. Check every field's domain against the intended audience (silent-blank rule).
5. Enable as Web Service only if consumed programmatically; note the 2 GB cap.
6. Name and govern calc fields (Category, Do Not Use convention) - the tenant list is forever.

## Composite reports - official engine facts (official-docs - Workday Education course manuals, crawled 2026-08-25; spot-verify load-bearing numbers in-tenant)

- Config hierarchy: Report Settings -> Column -> Row -> Cell; style precedence cell > row > column > report. Subreports = Advanced, Trending, or Matrix, unified by a common control field (same related BO across subreports). Sharing a composite requires sharing EVERY referenced subreport too, plus data source + filter access.
- Expression engine: max 5 NESTED functions per expression; PEMDAS applies. Syntax uses cell/row/column refs: `Difference([C5],[C3])`, `Divide([C3],[C5])`, `Multiply([C3],[C4])`, `PercentIncrease([R3],[R5])`, `PercentRemaining([R3],[R5])`, `Sum([R2],[R3],[R5])`, `SumRange([C3],[C5])`. Multiply constants up to 12 digits / 6 decimals; Divide constants up to 10 digits (constant divisors cannot be decimals/negatives/zero - verify wording in-tenant). Column/row calc catalog = 7 types; cell level = 6 (no Sum Range).
- **Bulk Add Rows** is DISABLED once the report exceeds 200 rows. Up to 10 control-field columns (each subreport must contain every control field; only ONE control-field column works with row outlining). Cannot delete columns/rows whose cell references create dependencies more than 3 levels deep.
- Header/footer variables [V1]-[V4]: case-sensitive, max 4 per header/footer row (Report Time, Report Date Time, Report Name, promptable values, global values like Current User).
- Outlining: Last Level caps at 10 node levels or leaf, whichever comes first; Excel export of expansion hierarchies caps at 8 outline levels. Composite charts: Column/Bar/Line only; charts do not support column outlining, conditionally hidden columns/rows, or repeating column groups. Control-field columns render as TEXT (no numeric formatting).
- Delivered prompt sets for financial composites: "Financial Composite Reports for Company" and "... for Organization"; custom sets via **Create Prompt Set**.

## Worker Trending (official-docs - same source)

- Envelope: max 15 single-instance fields trendable (Worker / Worker BP objects); trending start date up to 72 months back; retroactive recalculation window configurable 1-6 periods; trended data auto-purged after 6 years.
- Setup chain (3 tasks): **Edit Tenant Setup - Reporting and Analytics** (Enable Worker Trending checkbox) -> **Maintain Trended Workers** (Trending Start Date + Trending Period = calendar month OR fiscal period, never both) -> **Create Worker Trending Data**. Purge via **Purge Worker Trending Data**.
- Data model: activity-derived metrics (Hire / Transfer In / Promotion / voluntary+involuntary Termination counts) + snapshot-derived (FTE, Compa-ratio, Ending Headcount, Manager Count, ...). Trending reports need a time period as a row or column grouping; matrix-compatible via Lookup Date Rollup.

## Worksheets gating, scheduling bounds, Discovery Board exports (official-docs - same source)

- Worksheets: report must be Advanced / Matrix / Composite with **Enable for Worksheets** checked (Advanced tab); Advanced reports additionally need Enable as Web Service; **matrix reports CANNOT be web-service-enabled**. One scheduled refresh per workbook; refresh is one-way (report -> workbook). SECURITY: viewers of a shared workbook see ALL data the workbook OWNER can see, regardless of the viewer's own security - treat workbook sharing as a data-disclosure decision.
- Scheduling recurrence bounds: daily 1-366 days; weekly 1-52 weeks (the 5-executions end-date rule is in report administration above).
- Extended data sources: max 20 fields per eligible data source via **Maintain Custom Data Source** (Create Data Source Extension + Submit for Approval).
- Discovery Board export map (completes the note above): Chart / Donut Chart / Pivot Table export to a MATRIX report; Table exports to an ADVANCED report; Area / Bar / KPI / Line / Scatterplot / Heatmap / Waterfall are board-only (no report export).
