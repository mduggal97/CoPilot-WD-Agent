# Functional literacy - Payroll & Global Payroll Connect

Assumes shared primitives in [workday-functional-skus.md](workday-functional-skus.md). Source: Payroll for
Administrators; Creating Integrations Using Global Payroll Connect. GPC is integration-heavy and bridges
directly to our delivery work (see wd-extend-dev orchestration.md payroll-input notes + wd-integration-dev).

---

## Workday Payroll (US-centric core) - gross-to-net end to end
Calculates and settles employee pay: framework, taxes, inputs, calculations, accounting, and bank settlement.

**The mental model = the when/what/who framework:**
- **Period Schedule** (WHEN) - pay cadence with start/end/payment dates.
- **Run Category** (WHAT) - worker selection + taxation + components (one active "Regular" per pay group).
- **Pay Group** (WHO) - worker grouping; one per worker (unless multiple jobs).

**Building blocks:** **Pay Component** (earning/deduction/tax/withholding order) -> **Pay Component Groups (PCGs)**
-> **Pay Accumulations** (gross/taxable wages) -> **Pay Balances** (MTD/YTD/fiscal). **Related Calculations** compose
math (Hours x Rate). The **Calculation Engine** (numeric: Aggregate/Arithmetic/Conditional/Constant/Date/Instance/
Lookup/Step-based) drives it. Company Tax Setup / Worker Tax Elections; Withholding Orders + Deduction Recipients;
Payment Election Rules; Settlement Run; Banking; costing allocation hierarchy; ledger + suspense accounts.

**Core terminology:** Pay Component / Pay Component Group / Pay Accumulation / Pay Balance - Run Category / Period
Schedule / Pay Group - Continuous Calculation (auto-calc initial results; needs enablement + start/stop dates) - Retro
Processing - **NRPPT** ("No Retro Processing Prior To" date; bounds retro lookback) - Supported vs. Unsupported retro
events - Off-Cycle (Manual / Reversal / On-Demand) - Proration / subperiods - Arrears - Withholding Order / Disposable
Income - Forward Accrual - Settlement Run - Special Input (override company default, use sparingly).

**FDM/ties:** draws from HCM bio/job, Compensation, Benefits elections, Time hours, tax elections, manual input.
**Costing allocation priority: payroll-input override > worker-earning override > earning-level > worker-level >
supervisory-org default** - determines the GL hit. Worktags (Cost Center/Region/Program) classify journals; suspense
catches unclassified.

**Integration & reporting touchpoints:** input via manual task, batch, **EIB**, Worksheets. Settlement engine is
SHARED across Payroll, supplier invoices, expense reports, customer refunds. **Weekly Payroll Compliance Updates**
(Workday-delivered tax data). Reports: Payroll Register, Pay Calculation Results, Payroll Input Not Processed. BIRT for
custom check/advice layouts. (Payroll INPUT via REST `/payroll/v2/payrollInputs` is a common O4I target - see orchestration.md.)

**Gotchas:** (1) the Period Schedule / Run Category / Pay Group triad is the whole config mental model. (2) **NRPPT**
governs how far retro reaches and auto-advances on unsupported events - a frequent "why didn't retro fire?" cause.
(3) retro auto-calculates only for SUPPORTED events; tax-authority/benefit-dependent changes need manual adjustment,
and one unsupported change can block adjacent supported retro. (4) Continuous Calculation must be explicitly enabled.
(5) effective-dating a component definition does NOT auto-trigger retro. (6) payroll accounting entries generate as
DRAFT and can be regenerated without recalculating payroll.

**HC/Higher-Ed:** **Commitment Accounting** (budget encumbrance) in Payroll Accounting Setup is the classic
higher-ed/grant-funded/public-sector requirement; multi-worktag costing supports fund/grant/program allocation.

---

## Global Payroll Connect (GPC) - feed third-party / global payroll
Packaged connectors that feed Workday HR/pay data to third-party & global payroll vendors (and pull results back), so
Workday runs HCM while an external engine runs country payroll. **This is a payroll-INTEGRATION manual** - the key
delivery-relevant content is the interface-type landscape.

**The interface landscape (the core decision):**
- **PI (Payroll Interface)** - "top-of-stack," reports only net CURRENT values via Get Payees; simplest.
- **PECI (Payroll Effective Change Interface)** - full effective-stack; transmits changes in the sequence they
  become effective via the Data Initialization Service (DIS). The workhorse for global payroll. **Excludes contingent
  workers; no orchestration; no dynamic calculated comp plans; <=250,000 active employees.**
- **WECI (Worker Effective Change Interface)** - captures ALL personal/job/position data and changes, INCLUDING
  contingent workers (the gap PECI leaves).
- **GPC / Global Payroll Hub (GPH)** - unified UI to manage external pay groups across multiple vendors.
- **Data Changes on Demand (DCoD)** - vendor pulls worker data anytime via REST (JSON, field-level change detection).
- **Event Outbound Notifications** - auto-notify vendors of Hire/Termination.
- **External Payroll Results / Documents** - load vendor results/payslips/tax docs back into Workday.

**Constructs:** same when/what/who framework + PI Companies; Integration Attributes (Payroll Vendor, Country, Document
Retention - required); Field Attributes & Overrides (tree-structured; value mapping from reports/calc/custom fields);
Integration Maps; optional services (Transaction Log, Filename Sequence, Merge Files, Effective Stack Sync,
PECI-to-Excel); data-validation modes (Include/Omit/Abort).

**Core terminology:** Payee (contingent workers are NOT payees in PECI) - Effective Change (`peci:Effective_Change`
w/ sequence, event code, effective + entry dates) - change annotations (isAdded/isUpdated/priorValue/isDeleted) - All
Effective vs. Changes Only - Full Snapshot vs. Full Diff - Entry Date / Effective Date / **LSRD** (Last Successful Run
Date) - Primary vs. Ad-Hoc runs - Worker-Level LSRD - staffing event codes (HIR/TERM/LOA/RFL/PGI/PGO/PCI/PCO/ORG/DTA,
with -C/-R correction/rescind variants) - Effective Stack Sync (batch as often as every 6h) - EDI (Event-Driven
Integration).

**Gotchas:** (1) interface selection (PI vs. PECI vs. WECI) is the key decision - by vendor capability + data needs.
(2) first run uses All Effective/Full Snapshot for seeding; steady state is Changes Only driven by LSRD - wrong
initial mode corrupts baselines. (3) field overrides are EXPENSIVE (each = a separate service call) - prefer XSLT
transforms + calc fields tested in reports first. (4) ad-hoc runs deliberately skip status/LSRD/EDI updates - test
only, never production sweeps. (5) one vendor per pay group; one Event Outbound Notifications system and one DCoD
integration per tenant.

**HC/Higher-Ed:** relevance is organizational - large health systems and universities with international campuses or
outsourced payroll are the natural buyers.

---

## Cross-cutting (this domain)
- The **when/what/who framework** is identical whether payroll runs in Workday or is exported via GPC.
- **Worktags + costing allocation** is the connective tissue: Time Tracking assigns them, Payroll costs them, Payroll
  Accounting journals them.
- Time -> Absence -> Payroll is the natural data flow: submitted/validated time + approved absence become payable inputs.
- **EIB** is the common mass-load path for payroll input (and absence).
