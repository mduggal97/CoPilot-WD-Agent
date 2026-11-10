# Extend Volumes Questionnaire - How to Complete It

Workday's **Extend Volumes Questionnaire** is a macro-enabled `.xlsm` that
must be completed for **every** Extend application at production readiness.
It goes to a **Workday Customer Care case**. Same template for all apps; save
a per-app copy named `<App Name> - Extend Volumes Questionnaire_<yyyymmdd>.xlsm`
in that app's folder.

For .xlsm file mechanics (openpyxl usage, saving, locks), use the **xlsx
skill**; this reference owns the content and rules.

## Sheets

| Sheet | What it is | Do you edit it? |
|---|---|---|
| Instructions | Boilerplate | No |
| **Deployment Information** | App identity, contacts, tenants, dates, Prism/Accounting Center flags | Yes - per app |
| **Extend** | The core volume tab: users, transactions, custom objects, APIs, orchestrations, attachments, retention | Yes - per app |
| **Recommendations** | **FORMULA-DRIVEN - never overwrite.** C2 = `=SUM(Extend!C5)`; C3 = `=IF(...Extend!C5>=Values!B1...)` | **No** |
| Roles and Responsibilities | Generic RACI, same for all apps | No |
| Values (hidden) | Holds the threshold: **B1 = 50000** active Extend application workers | No |

**Threshold logic:** if Extend!C5 (user access count) is under 50,000, the
Recommendations tab concludes "does not exceed thresholds" (and performance
testing is generally not *required*). Let the formulas do this - a file with
the conclusion hardcoded gets bounced.

## Editing rules (content-level; mechanics -> xlsx skill)

- Load with openpyxl **`keep_vba=True`** and **WITHOUT `data_only`** (with
  `data_only` the formulas are replaced by cached values on save -
  destroying the Recommendations tab). Save as `.xlsm`.
- **Write input cells only.** Never touch Recommendations or Values.
- Apply the **yellow-highlight convention from wd-design-doc**: yellow-fill
  any cell whose value is unknown/estimated pending a follow-up, with a note
  saying what's needed and from whom; unhighlight once answered. Confirmed
  program-standard values (see Engagement inputs below) do NOT get highlighted.

## Per-app cells to fill

**Deployment Information tab:** app Name, Reference ID, Purpose, Business
objectives, Criticality, outage tolerance, IMPL tenant(s), Production /
First-Use dates, project timeline + tenant build dates, contacts, and the
**Prism section** (deploying Prism? transformation? - Yes/Yes with an
explanation if the app reads Prism-published datasets; Accounting Center
usually No).

**Extend tab:** user access counts (C5 = the threshold driver), user volume
intervals, transaction volumes (Day/Week/Month/Year), custom objects, peak
windows, bulk actions, **Workday APIs used**, WQL, orchestrations,
attachments, reporting, integrations, retention/archival (C21/C22/C24), and
the design-doc link.

## (!) The common gap: the API inventory

The single most common omission is an incomplete "Workday APIs used" answer.
Enumerate **every** surface, not just the obvious one:

- **SOAP** web-service operations (e.g., Assign Costing Allocation,
  Put_Sponsor, Increment Sequence Generator) - writes especially
- **RaaS** custom reports the app or its orchestrations call (e.g., Related
  Worktags defaulting)
- **WQL** reads (pickers, validations, Evaluate-Expression calc fields)
- **REST** - generated Extend BO endpoints, delivered Custom Object REST,
  businessProcess/orchestrate endpoints
- **Orchestrations** - page-triggered, BP-triggered, and scheduled (name
  them; note cadence for scheduled ones)
- **Attachments** (file sizes, retention)
- **Prism** dataset access, if applicable

Precedent: a costing app's correct answer was SOAP (2 operations) + WQL +
REST + RaaS - a first pass listing only WQL/REST would have been the classic
gap.

Also state **bulk behavior** explicitly when present (e.g., "bulk=true, 100
per request," "orchestration batch-creates 100-500 records/run," "EIB for
mass migration") - batch writes are what the reviewer is sizing for.

## Volumes need a basis

Never enter a bare number. Derive each volume and keep the derivation
(design-doc discovery answers, legacy baseline, headcount x frequency,
straight-line split of an annual figure). Estimates get yellow-highlighted
with the basis and the person to confirm with; if the customer has ruled
"estimated counts are fine, just annotate," note "(est.)" instead of
highlighting (example: a client ruling that user counts may be estimated). Where the
tenant already holds the population, derive the number live via tenant-ops
(WQL count / RaaS, aggregates only) and cite the query as the basis - a
measured count beats a highlighted estimate.

## Update the program capacity ledger

Every submission (initial or re-cert) writes its declared volumes, worker
counts, and orchestration schedules back to the **program capacity ledger**
(wd-pm `references/program-mode.md`) - Workday reviews each app alone; only
the ledger sees the tenant-wide sum and the overlapping orchestration windows.
Post-go-live volume sanity checks compare actuals against the **ledger**, not
just this app's own questionnaire: an app within its own envelope can still be
the row that tips the program's total or collides with another app's nightly
window.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live. Reuse them across all of the program's apps:

- **Program contacts (by role)** - Integration Lead, PM, Reporting Lead, Data
  Lead, and Perf Test Lead (name + email) for the Deployment Information tab,
  plus the Customer/legal-entity name and Deployment Phase (e.g., Initial
  Deployment).
- **Reference ID pattern** - the org suffix appended to app reference IDs
  (Reference ID = `<appNameCamelCase>_<orgSuffix>`); assume it even before the
  app is created. Once known it's a program-standard value - no highlight.
- **Tenants** - the DEVELOPMENT-level tenant alias (build/unit testing) and the
  IMPL tenant alias(es) (E2E); program-standard once set, no highlight.
- **Dates** - Move-to-Production and First-Use dates and the tenant build-date
  timeline (watch for stale dates in older design text; the memory value
  supersedes).
- **Headcount bases** - the Foundation vs. Config employee counts (and any
  E2E/Parallel/Gold counts) that derive volumes; reuse from a completed
  reference file for the program.
- **Retention / archival (C21/C22/C24)** - where aged custom Extend business
  objects and Prism tables go long-term (e.g., a client data lake as the
  system of record for aged records) and on what export schedule; keep any
  not-yet-pinned interval lightly highlighted.
- **Blank master + completed examples** - the location of the blank
  questionnaire template and completed per-app copies to mimic for shared
  program data (including a first Prism = Yes/Yes example and a combined file
  for a tightly-coupled app pair, where available).
- **Volume posture vs. the 50,000-active-worker threshold** - whether the
  program's apps run under Workday's Volumes-Questionnaire threshold.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
