# Extend Performance Testing Template - How to Complete It

Workday's **Extend Performance Testing Template** (v24.1, macro-enabled
`.xlsm`) is the companion to the Volumes Questionnaire. The questionnaire
drives whether testing is even *required*: Workday's ~**50K annual
transaction** threshold - over 50K, performance testing is required. Under
it, completing the template is still standard program practice.
(!) The ~50K-transaction figure is an approximation of Workday's current
guidance (Volumes Questionnaire instructions / Customer Care), NOT a fixed
platform constant - verify the current threshold per engagement before telling
a client testing is or isn't required. (Distinct from the 50,000-active-Extend-
workers gate on the Volumes Questionnaire - do not conflate the two.)

Save a **per-app copy** with the app name in the filename (e.g.,
`Extend Performance Testing Template v24.1 - <App Name>.xlsm`) in that app's
folder, from the blank master (see Engagement inputs for the current
master-template path).

For .xlsm file mechanics, use the **xlsx skill**; this reference owns the
content, classification rules, and template-specific editing traps.

## Tabs

Instructions / **Sample Use Cases** (worked example - mimic its style) /
**Use Case Testing** (the main tab) / **Addtl Integrations and Reports** /
Benefits.

## Use Case Testing tab - header block (F2-F5)

- **F2** = App Name
- **F3** = Reference ID (`<app>_<org>`; yellow-highlight if the app isn't in
  AppHub yet)
- **F4** = **the CURRENT design-doc version** - bump it whenever the design
  changes (e.g., set to v2.0 after a sign-off). If the source design has no
  version number, highlight F4.
- **F5** = BP TRX: `N/A` for a page-driven app with no BP; for BP-driven
  apps, list the custom Extend BPs (and their delivered parents where
  relevant).

## Single User Tasks (rows 12+)

One row per key **Extend code path** worth load-testing. Columns: A No,
B Name, C Start_Time, D End_Time (**C/D are yellow - filled DURING test
execution; leave blank when authoring**), E Workday Account, **F "Forecasted
Peak Production Hourly Workers"**, G Comments. During execution also capture
the tenant health baseline via tenant-ops (systemMetrics snapshot) and file
it with the times.

Pick the paths that matter: the write path(s), the read-heavy path, the
**high-volume path** (usually the line-item/child-record path), the
finalize/submit path, and the reporting path. Typical apps land at 5-10
tasks.

## (!) CRITICAL: column F is a VOLUME, not a headcount

Despite the label "...Hourly Workers," the Sample Use Cases tab fills F with
volumes like `250K`, `200K`, `2.5K`. Enter the **forecasted peak-hour
execution volume** - how many times that task runs in the busiest hour.

**Yellow-highlight every forecast** (they're estimates - the wd-design-doc
convention) and put the **basis in the G comment**. Good basis patterns:
- Volumes Questionnaire figure x peak concentration ("~35 txn/day, ~30% in
  the peak hour")
- Unit math ("100 bins/employee/day x ~50 specialists, ~30% in peak hr ->
  ~1,500/hr")
- Fan-out ("line approvals exceed requests - 1.5-2 approvers/txn")
- For batch rows: records per run, not per hour ("~500-3,000 records/monthly
  run - perf concern is bulk volume, not concurrency")

## Classification rules (the important judgment calls)

- **Interactive user tasks** -> Single User Tasks.
- **Admin/batch orchestrations the app runs** (data export, purge, monthly
  ingest) -> **also Single User Task rows** - they're executable code paths
  worth load-testing. Note "perf concern is bulk volume, not concurrency."
  A **BP-triggered orchestration counts as a task** the same way (e.g., a
  post-completion SOAP write).
- **Integrations the app itself owns** (its export delivery, its O4I write)
  -> **also** list on the **Addtl Integrations and Reports** tab under Custom
  Integrations, **cross-referenced to the task row**. An internal-only bulk
  op (e.g., purge) is a *task*, NOT an integration - don't double-list it.
- **External integrations the app DEPENDS ON** (data loads it reads, owned
  by another team) -> Addtl tab as a **DEPENDENCY / PRECONDITION with the
  real INT # from the current client Integration Tracker**, plus a precondition
  note on the dependent task rows. **Never list them as this app's use
  cases** - they have their own perf profile, tested separately.
- **RaaS reports the app calls per-interaction** -> Addtl tab Custom Reports,
  with a volume derived from the calling task (e.g., "entries x up to 10
  lines ~ 100-200/hr"). A pending/unbuilt report gets a row flagged "add to
  execution once built."
- **Standard Reports / Standard Integrations** sections (rows 18+/27+) =
  *delivered* Workday reports/integrations; `N/A` when reporting is an
  in-app PMD page and data access is in-app REST/WQL.

## Addtl Integrations and Reports tab columns

A No, B Name, C Integration/Report ID (the real INT# or report ID - yellow
if TBD), D/E times, F Account, **G Forecast (volume)**, H "used in a
dashboard?", I "dashboard interactive?", J Comments.

## Editing mechanics (template-specific traps; general .xlsm -> xlsx skill)

- Load with `keep_vba=True`, save `.xlsm`.
- **The task section is fixed at 5 rows** - to add tasks you must **insert
  rows**. The data rows have no merges/formulas/named ranges (safe), but the
  section headers `A18:H18` (Standard Reports) and `A27:H27` (Standard
  Integrations) are **merged** - openpyxl does not move merges, so use
  **unmerge-before-insert -> insert -> re-merge shifted**.
- **Copy styling from an existing task row (row 16)** onto inserted rows so
  borders and the yellow C/D time cells carry over.
- **OneDrive/Excel locks bite even on READ** - copy the file to the
  scratchpad first, edit there, copy back.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Blank master path** - the location of the blank
  `Extend Performance Testing Template v24.1.xlsm` for the program.
- **Perf Test Lead** - the named person who coordinates executed performance
  testing; route executed testing through this role.
- **Integration Tracker** - the program's Integration Tracker workbook, the
  source of the real INT # for each dependency row; a missing INT # gets a
  yellow TBD.
- **Completed examples to mimic** - the location of completed per-app copies
  that illustrate the key patterns to reuse: a first example with an external
  dependency pattern; a BP-driven app (F5 lists sub-BPs; BP-triggered
  orchestration as a task); a page-driven app with external-INT dependencies;
  an app with inserted rows and a custom-BP F5; an admin-purge =
  task-not-integration example; a Prism-ingest app with dependency precondition
  notes; and a combined file for a tightly-coupled app pair (with a scheduled
  daily-run row).

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
