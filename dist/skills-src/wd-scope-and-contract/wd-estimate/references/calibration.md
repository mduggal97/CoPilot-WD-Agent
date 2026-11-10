# Estimation calibration - archetypes and program history

Estimates anchor on comparable delivered work. This table starts SEEDED with archetype illustrations drawn from delivered apps (complexity drivers are realistic; hours are mostly to-be-backfilled). Every project closeout (wd-post-go-live) appends actuals - an entry with recorded actuals outranks any multiplier math.

## App archetypes (complexity drivers from real delivered apps - genericized examples)

| Archetype | Real examples | Typical shape | Relative size |
|---|---|---|---|
| **Request + approval app** (form -> BP -> write-back) | a master-data request app (6 FDM objects, 5 Model BPs, SOAP write-on-approval); a two-app grant/award-forms split with Boomerang routing | 3-8 BOs, 12-25 pages, 1-5 Model BPs, 1-5 orchestrations | M-L; approval complexity and # request verticals drive it |
| **Tracking/recording app** (worklist + capture + reporting) | an inventory-expiry tracker (3-level BO chain, 20+ pages, live WQL joins, reporting page) | 3-5 BOs, 15-25 pages, 0-2 BPs | M; reporting + edge flows (cancel/pause/adhoc) are the hidden half |
| **Reconciliation app** (external data vs Workday, exceptions) | an AP statement reconciliation app (manual paste input, standardized output, comments-in-app) | 2-4 BOs, 8-15 pages | S-M; input-format handling and exception UX drive it |
| **Allocation/costing app** (grids, validations, effective dating) | a position-costing allocation app (3 BOs, 15 PMDs, 8 pods, RaaS validations) | grid-heavy pages, validation logic | M; validation rules and worktag edge cases drive it |
| **Prism + Extend reporting/attestation app** | a budget variance & projection app (hierarchy grain, thresholds, review workflow, multi-entity) | Prism pipeline + app on top | L; two platforms, two skill sets |
| **Integration-only (O4I), no UI** | an employment-end-date automation (category-based staffing writes); a vendor AP inbound integration | 1-6 orchestrations, subflows, error handling | S-M; source-data quirks and error/retry design dominate |
| **Marketplace app enhancement** | a company-credit-card app enhancement (section control, dynamic visibility, bank/card-provider REST integration); a user-access-provisioning enhancement (role pairing, filter roles); one recorded anchor: a costing-app enhancement (checkbox -> Program worktag on a costing allocation) ~ **40 h** | changes inside someone else's app | S-M but high care: co-ownership workflow, regression scope; (!) remaining example hours need owner backfill |
| **Full planning/budgeting tool replacement** | a capital-planning tool replacement (descoped) - swagged **1,400-1,900 h** (!) LOW CONFIDENCE (never delivered; one uncalibrated point - do not anchor large estimates on it) | many modules, conversion, heavy stakeholders | XL |

## Adjustment drivers (apply to the archetype base)

- +stakeholder groups beyond ~2 -> add design cycles (design phase scales with reviewers, not developers)
- +each external integration -> its own discovery/build/test lane (vendor lead times often gate the timeline, not effort)
- +data conversion -> separate workstream (profiling, load scripts, reconciliation, dry runs)
- +two-tenant-org delivery (firm org + client org trees) -> mirror/port overhead on every change
- +client developer co-ownership -> change-list workflow overhead but less firm build in later phases
- -strong PoC already exists -> Build shrinks, but never below the "additions + hardening + comments/KT" floor
- +record-accumulating BOs (a transaction / line / audit-log object at scale) -> add a **standard data-retention export/purge orchestration** LOE line - it is compliance table-stakes AND how the app stays under Extend's custom-object ceiling (wd-extend-dev model.md). Size it explicitly (~a small O4I orchestration pair); never fold it into a generic "orchestrations" line, or the estimate silently under-scopes a required inclusion.

## Phase distribution starting point (of an app's total dev-side hours)

Discovery 5-10% / Design 15-25% / PoC 10-15% / Build 25-35% / Unit Test 8-12% / UAT/E2E support 8-12% / Perf/Volumes docs 2-4% / Deploy/Cutover 4-6% / Hypercare 5-8%. PM adds ~10-15% on top across the term. Shift Design up for stakeholder-heavy apps; shift Build up for grid/validation-heavy apps.

## Actuals log (append at every closeout - the loop that makes this table honest)

| Project | Archetype | Estimated h (by phase) | Actual h (by phase) | Delta + why | Date |
|---|---|---|---|---|---|
| *(none recorded yet - first closeout populates this)* | | | | | |
