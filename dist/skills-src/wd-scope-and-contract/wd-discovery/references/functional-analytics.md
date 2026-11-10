# Functional literacy - Analytics & Reporting

Assumes shared primitives in [workday-functional-skus.md](workday-functional-skus.md). Source: Workday Reporting,
Advanced Reporting for HCM, Advanced Reporting for Financials, Prism Analytics, BIRT Report Designer (for
Administrators). This cluster overlaps heavily with our delivery work - RaaS, WQL, Prism, and Extend all traverse
the SAME object model this teaches. Build depth is in wd-extend-dev `prism-and-reporting.md` (name-level pointer; skills stay separable).

**Keep the three layers straight (the one thing to remember):**
**Prism = prepare/blend data (platform)** -> **Report Writer = query + analyze + light-visualize (no-code)** ->
**BIRT = pixel-perfect printable forms (developer tool)**. Prism prepares; Report Writer both queries and visualizes;
BIRT presents. All three plug into the FDM object model; all reporting security flows through domain policies +
constrained security groups.

---

## Report Writer (Workday Reporting) - the no-code report engine
Build, secure, schedule, and visualize reports on LIVE Workday transactional data.

**8 report types:** Simple, Advanced (the workhorse), Matrix (pivot w/ drill; limits 12k rows / 250 cols),
Composite, Search, nBox, Trending, Transposed. Plus Discovery Boards (drag-drop ad hoc viz; <=10 viz/sheet),
charts/analytic indicators, worklets/dashboards (<=6 tabs x 6 worklets; worklets must load <30s), scheduling, alerts,
report groups, **bursting** (one output per prompt value, e.g. per company), Excel-template output.

**Constructs:** **Report Data Source (RDS)** - a view/starting-filter on a Primary Business Object; four kinds:
**Standard** (flexible, slower), **Indexed** (high-volume + facet filtering), **Business View** (curated multi-source
blend), **Prism** (from Prism tables). **Calculated fields** - runtime-evaluated, object-bound; families date/text/
conditional/aggregation/lookup/arithmetic (mirror Extend PMD calc fields).

**Core terminology:** Primary/Related Business Object (PBO/RBO) - Instance - Class Report Field - Report Data Source -
Indexed data source / Facet filter - Business View - Prompt / Optional prompt / Prompt set - Analytic indicator -
Worklet / Dashboard / Discovery Board - **Bursting** - Constrained vs. unconstrained security group.

**How it connects to delivery:** **RaaS = any Advanced report web-service-enabled = the outbound integration feed**;
**WQL** queries the same PBO/RBO/CRF model (understanding data sources = understanding WQL scope); Prism data sources
are the 4th RDS type consumed by Extend/O4I; bursting + Excel templates are common integration-adjacent outputs.

**Gotchas:** (1) custom reports are PRIVATE by default; sharing is explicit and needs access to BOTH the data source
AND its filters. (2) Indexed vs. Standard is a design-time perf decision (indexed unlocks facet filtering + matrix
scale, exposes fewer sources). (3) matrix hard limits (12k rows / 250 cols) force aggregation strategy early. (4)
worklets that don't render <30s silently drop off landing pages. (5) calculated fields are runtime (always current,
per-run cost) - heavy logic belongs in Prism (publish-time). (6) bursting is the native "one report, many recipients/
entities" before reaching for an integration.

---

## Advanced Reporting for HCM - trended workforce reporting
Report Writer applied to HCM, centered on **Trended Workers** (headcount/turnover over time) + composite reporting.

**Constructs:** **Trended Workers** data source (enable via Maintain Trended Workers; backfills up to 72 months,
monthly/fiscal periods, retro-change handling) - a workforce warehouse of **Snapshot data** (active workers as of
period end) + **Activity data** (staffing events by effective date). **Lookup Value as of Date** calc function.
Composite building blocks: control fields, column/row types, calc options.

**Core terminology:** Trended Workers - Snapshot vs. Activity data - Record date - Subreport - Control field -
Composite report - Dynamic Data row - Expansion hierarchy (<=8 Excel levels) - Prompt set - **People Analytics** (ML
narrative "Storyteller" on Prism) - Worksheets (Prism-built).

**How it connects to delivery:** Trended Workers is the in-platform answer to headcount/turnover dashboards we might
otherwise build via integration extracts - keep it in-platform. People Analytics/Worksheets ride on Prism.

**Gotchas:** (1) Trended Workers must be explicitly enabled + backfills up to 72 months - set the start date
deliberately at implementation. (2) Snapshot vs. Activity record-date semantics drive point-in-time vs. event-based
metrics (frequent "numbers don't tie"). (3) composite subreports must share matching control fields. (4) "Additional
Tools" surfaces WDSetup, Object Transporter (OX), Configuration Catalog, Worksheets, Prism, People Analytics.

---

## Advanced Reporting for Financials - financial statements via composites
Composite reporting to build formatted financial statements (income statement, balance sheet, budget-vs-actual) from
matrix/advanced subreports over financial data sources.

**Constructs:** indexed financial RDSs - **Journal Lines** (actuals) / **Plan Lines** (budget) / **Statistic Lines** -
for Financial Reporting; custom reporting time periods (fiscal, cumulative); composite column/row/cell types; delivered
"Financial Composite Reports" prompt set (Company, Period, Translation Currency); Deep Copy / Deep Delete; Reverse the
Sign (presentation only); hierarchies + outline structures; OfficeConnect (Excel add-in).

**Core terminology:** Composite report / Subreport - Control field (<=10; only one drives row outlining) - Journal/
Plan/Statistic Lines RDS - Reporting time period - Reverse the Sign (cosmetic sign flip) - Drillable total - Expansion
hierarchy - Repeating column group - Prompt set - Deep Copy/Delete - OfficeConnect.

**How it connects to delivery:** financial-statement composites are frequently the reporting layer clients want
instead of custom outbound integrations; OfficeConnect is the sanctioned live-Excel path (flag it before a client
asks for a "download to Excel" integration); budget-vs-actual multi-source composites overlap with Prism blending.

**Gotchas:** (1) Reverse the Sign is cosmetic - never a data fix (auditors care). (2) only ONE control field drives
row outlining though composites allow 10 control-field columns. (3) use Deep Copy to clone delivered statements
(with subreports). (4) Journal/Plan/Statistic Lines are separate indexed RDSs; budget-vs-actual = a composite
spanning them. (5) reporting time periods must match the client's fiscal calendar before statements tie.

---

## Prism Analytics - the data-preparation platform
An ETL/blend layer inside Workday: ingest large-volume Workday + non-Workday data, transform via visual pipelines,
publish governed data sources back into Workday reporting. NOT a report-writer - it FEEDS Report Writer/Discovery
Boards/dashboards. Highest overlap with an integration/Extend practice.

**Four-phase flow:** Acquire -> Transform -> Publish -> Report/Distribute (acquisition + publishing schedulable).

**Constructs (literacy):** **Tables** (materialized, schema-validated) / **Datasets** / **Derived Datasets** (run
pipelines); **Pipeline** of **Stages** (Filter, Group By, Join, Union, Manage Fields, Unpivot, Explode); **Prism
calculated fields** evaluated at PUBLISH time; acquisition via file upload / REST / sFTP / custom Workday reports /
S3 / Salesforce / Snowflake / Synapse; **WPA_ system fields**; publishing creates a **Prism data source (PDS)** with
domain + row-level (securing entity) + field-level security. (Exact ingest limits, field caps, publish-timeout, the
window-function list, and ALL build mechanics are owned by wd-extend-dev `prism-and-reporting.md` - not restated here,
to avoid drift.)

**Core terminology:** Dataset / Derived Dataset / Table - Pipeline / Stage - Join types - Union - Lineage - Relax
Sharing Rules - Data Change Task - Prism calculated field (publish-time) - Window function - **Prism data source
(PDS)** - Securing entity - Delete Published Rows vs. Unpublish - WPA_ fields.

**How it connects to delivery (highest overlap):** acquisition (sFTP/REST/S3/Snowflake/custom-report) IS the inbound
integration surface - often a lighter alternative to a full Studio/EIB inbound for "land external data for
reporting." **Publish-time calc fields** are the perf-correct place to push logic (vs. runtime report/Extend calc
fields). PDS-as-RDS ties back to Report Writer + WQL/RaaS; Extend/O4I can read Prism. Data Change Tasks + external IDs
mirror our integration upsert patterns.

**Gotchas (conceptual):** (1) Prism logic runs at PUBLISH time, not query time - the core perf argument for moving
heavy transforms here. (2) publishing is scheduled/async - downstream reports read the LAST publish, not live data.
(3) recommended pattern: a clean "PDS" derived dataset with no extra transforms as the publish target. (4) Delete
Published Rows (inactivates, restorable) vs. Unpublish (destroys the data source, breaks dependent reports) - very
different blast radius. (Hard numeric limits - upload size, field caps, publish timeout - live in prism-and-reporting.md.)

**HC/Higher-Ed:** the platform behind Accounting Center + People Analytics; classic use = high-volume operational
feeds enriched for reporting (patient/claims data; SIS/bursar/research).

---

## BIRT Report Designer - pixel-perfect printable forms
An Eclipse BIRT layout-authoring TOOL inside Workday Studio for formatted print output - invoices, offer letters,
payslips, POs. **Separation of concerns: Custom Report Writer owns the DATA; Report Designer owns the PRESENTATION.**
A Studio/Eclipse DEVELOPER task, not a business-analyst tool.

**Constructs:** source report must be **Advanced + Web Service Enabled** (emits XML/XSD/WSDL; max output 2 GB);
`.rptdesign` file; Data Source (binds XSD + XML sample); Datasets (per business object + per multi-instance field);
**Column Heading Override / XML Alias** (maps report fields to dataset fields); layout elements (Tables/Grids/Labels/
Text/Dynamic Text/Images); parameter bindings (PrimaryRowNumber/SecondaryRowNumber); Deploy wizard -> **Business Form
Layout** object attached to the report.

**How it connects to delivery:** the web-service-enabled source report = **RaaS** - BIRT sits on the exact XML/XSD/
WSDL our integrations consume (same enablement step, different consumer). Overlaps with Document Transformation / print
in traditional integrations - when a client wants "a nicely formatted PDF from a report," BIRT is the native answer
vs. an XSLT/DT integration. Multi-dataset parameter binding mirrors parent/child handling in XSLT/Studio.

**Gotchas:** (1) data logic stays in the Report Writer, layout in BIRT - refactor the source report, don't compute in
the design. (2) source report must be Advanced + web-service-enabled (same RaaS switch). (3) 2 GB output ceiling +
per-row PDF explosion are real limits. (4) XML Alias / Column Heading Override mismatches are the #1 breakage - field
renames silently invalidate the design until datasets are refreshed. (5) report changes require a dataset refresh +
re-deploy cycle (a maintenance tax the client dev team owns). (6) staff a Studio/Eclipse developer, not a BA.
