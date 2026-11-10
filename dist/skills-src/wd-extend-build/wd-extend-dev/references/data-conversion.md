# Data conversion / migration - as a BUILD workstream

Data conversion is not just a go-live event. The **execution** (freeze, final delta, day-of sequencing, rollback) belongs to wd-deployment `cutover-planning.md`; **this file owns the build** - the mapping, the loader, the reconciliation harness, and the iterative dry-run cycles you develop and harden *during* the build phase so cutover day is a rerun of something already proven, not a first attempt. Scope conversion as its own workstream with its own hours; a loader discovered the week before go-live is the classic slipped-date cause.

## 1. Field mapping - legacy source -> Extend BO

Start from the legacy current-state inventory (wd-discovery captures this; its `discovery-to-design.md` is where current-state feeds design). Build a mapping table - one row per **target BO field** - with:

| Column | What it pins down |
|---|---|
| Target BO.field | The Extend field (model.md field types) |
| Source system + field | Where the value comes from (or "derived" / "constant" / "not loaded") |
| Type / transform | Format conversion (date -> `MM/dd/yyyy`->ISO, currency -> `{value, currency}` with `value` as a STRING, code lookups) |
| Reference resolution | SINGLE_INSTANCE targets need a **WID or reference-ID** - how is the legacy code resolved to it? (This is the #1 conversion failure.) |
| Required? / default | Is the field mandatory on create; what fills a blank source |
| Notes / open item | Ambiguities go to the design doc's open-items list (yellow-highlight convention, wd-design-doc) |

Landmines the mapping table must resolve before you write a loader:

- **Reference fields.** A SINGLE_INSTANCE write accepts `{"id": <WID>}` (model.md). Legacy files carry human codes, not WIDs - the loader must look each up (WQL/RaaS against the tenant, or a pre-built code->WID crosswalk). Unresolved references are the most common load rejection. The crosswalk is buildable and re-verifiable per tenant live via tenant-ops (`refs <Reference_ID_Type>` returns the type's full RefID+WID set) - validate every legacy code before the first load (references/tenant-ops.md).
- **PUT is full-replace** (model.md). Any fix-up / second pass must send the COMPLETE payload, not a delta - bake the full field set into the loader from the start.
- **Nullable fields on pre-existing rows** - mirror the design-time field checklist in model.md; a field absent in the source loads null and every reader must be guarded (pmd-gotchas null discipline).
- **BOOLEANs** read `false` once touched by a PUT, not null - decide the intended default explicitly.

## 2. Decide WHAT converts (classify each BO)

Same three buckets cutover-planning.md defines - settle them at design time, not go-live:

- **Reference / config data** - almost always loads; small; the app is often unusable without it. Load first.
- **Open in-flight transactions** - hardest call. You generally CANNOT recreate a legacy approval mid-chain in an Extend BP: plan to **drain** the legacy queue before freeze, **re-enter** in Extend, or **load as new + relaunch** the BP. Decide per BO and record it.
- **Historical / closed records** - load only if the app itself needs them for reporting/audit; otherwise leave them in the legacy archive / client data lake (often the long-term system of record). Bias against bloating Extend BOs with history.

## 3. Build the load mechanism - pick one, know the tradeoffs

| Mechanism | Use when | Tradeoffs |
|---|---|---|
| **BO REST loader script** (PowerShell/Python) | Default. Small-medium volume, one-off or few reruns | Reads page at max 100/page (BO REST collection limit - pmd-gotchas.md #15), writes are **per-instance** (loop). Token via `wdcli tenant token <alias> --ci`; reuse the `workday_rest.py` helper (security-setup.md). Fast to build, fully diffable, but N writes = N round-trips. |
| **Orchestration load** (O4I) | Large volume, per-record transform/validate needed, OR the client team will rerun loads themselves | Bulk endpoints where available (`bulk=true` at 100/request; Submit-Extend-Data-style batching <=500). Stays inside the tenant, auto-authed via the ISU (orchestration.md auth). More to build; becomes a reusable client-owned asset. |
| **EIB** | Delivered / select-list data with an EIB path, or mass tenant-config the app reads | No custom code; limited to what EIB templates cover; not for arbitrary Extend BO shapes. |

Whichever you pick, the loader is **code that gets handed off** - apply standards.md: header + change-log block, KT-level comments, descriptive names, logic in reusable functions. A conversion script the client can't rerun is a defect.

## 4. Referential order - parents before children

Load **parent -> child** (a child's SINGLE_INSTANCE reference must already exist, or the write fails). For re-runnable loaders, **delete child -> parent** - deleting a parent still referenced by a child returns a 500 (model.md; prefer soft-delete where the app supports it). Write the loader so the order is explicit and configurable, and so a partial failure is safe to resume.

## 5. Reconciliation harness - build it once, reuse every cycle

Don't eyeball loads. Build a small reusable reconciler that runs after every load (dry-run and real) and emits a sheet:

- **Counts:** source-extract rows -> attempted -> loaded -> rejected, **per BO**, with every rejected row's reason and disposition.
- **Spot-checks / control totals:** sums of currency fields, distinct key counts, min/max dates - cheap checks that catch a transform that "loaded" but mangled values (WQL returning objects vs. strings, currency `value` string handling, timezone-shifted dates).
- **Key linkage:** confirm each loaded record maps back to its source key, so the load is auditable and reversible.
- **Sample-value check:** beyond counts and totals, pull a **sample of individual records** and compare their field values against the **source-of-record**. This catches a per-field transform that passes the aggregate totals but corrupts individual rows (e.g. a date shifted by a timezone, a currency `value` that lost precision).
- **Pass/fail verdict + variance notes (discipline reinforced by community data-engineering quality-pipeline skills):** every run records an explicit **PASS or FAIL** against the source-of-record, not just raw numbers. Any non-zero variance - a count gap, a control-total mismatch, or a failed sample-value check - must be **explained and dispositioned**: an understood, accepted variance is fine (e.g. rows intentionally not loaded); an *unexplained* one blocks sign-off.

Read-side counts can come from WQL/RaaS (orchestration.md "Reading data at scale") for volumes past the 100-row REST cap (pmd-gotchas.md #15). The reconciler is day-of evidence and the rollback baseline - keep its output.

> **Same harness reconciles a Prism/analytics load.** After any Prism dataset load, reconcile row counts + control totals + a sample of values against the source-of-record and record a pass/fail exactly as above - the Prism-side "test the pipeline as data" note points back here (wd-extend-dev/references/prism-and-reporting.md). This file owns the reconciliation methodology; that one owns the Prism build.

## 6. Iterative mock-conversion cycles

Conversion hardens by repetition, not by one big-bang attempt:

1. **Mock load** from a *representative* source extract (real shape, real edge cases - bad dates, missing codes, unicode), not a hand-cleaned sample. **Regulated-data rule (PHI/FERPA/PII):** a real extract goes ONLY into a **client-controlled non-prod tenant** (never a shared delivery-org dev tenant), and is **de-identified** unless the test genuinely needs true values (interval-preserving date-shift + synthetic identifiers per wd-extend-lifecycle `ai-data-governance.md` section 1); it must clear the tenant-ops WRITE GATE. This mirrors the wd-testing UAT rule (masked/synthetic unless the client security office approves in writing) - do not load real regulated data into a shared tenant to get "real edge cases."
2. **Reconcile**, triage every reject, fix the mapping or the loader, re-run.
3. Repeat until the reject list is empty or every remaining reject has an accepted disposition.
4. Each cycle also re-validates reference resolution against the tenant - WIDs differ per tenant, so a crosswalk built in one tenant must be rebuilt/verified in the next (security-setup.md per-tenant reality; new tenant = new S22 grants before any data call works at all, model.md).

Watch the release calendar (release-impact.md): if the build spans an R1/R2, re-run a mock cycle on the new release before trusting the loader for cutover.

## 7. Dry-run + sign-off (hand-off to cutover)

The **final** rehearsal is the full dry-run in IMPL described in cutover-planning.md - same scripts, same source format, same sequence as PROD will use. It must produce a clean reconciliation the **data owner signs off** (the loader doesn't sign off their own counts). What you hand cutover:

- The proven loader(s) + run instructions (token, tenant alias, order, rerun/rollback steps).
- The reconciliation harness + the signed dry-run counts (the go-live comparison baseline).
- The list of decisions made per BO (what converts, open-transaction disposition) and any residual data-fix items.

From there cutover-planning.md owns the freeze, final delta, day-of load, and rollback.

> **Feeds the wave go/no-go.** For a phased conversion, this file's reconciliation harness is the evidence source for the wave-by-wave readiness scorecard in wd-deployment `references/migration-readiness-gates.md` (Pass / Conditional Pass / Fail per gate); the dry-run + sign-off above is what its rehearsal gate consumes. Build owns the loader + counts; that scorecard owns the verdict.
