# Payroll (US) + payroll input/integration - solution playbook

US-centric gross-to-net payroll plus the payroll-input / payroll-integration surface.
Config facts: (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant).
Web-service names: (from the in-tenant WWS master inventory).

## 1. Configuration spine

### The who/what/when triad (anchor model)

Every payroll run is defined by three objects:

- **Period Schedule** - WHEN (start/end/payment dates; sharable with Absence + Time Tracking only if dates match)
- **Run Category** - WHAT (workers-to-process criteria, gross/net accumulations - BOTH required, taxation rules)
- **Pay Group** - WHO (payroll-only org type; ONE country per pay group)

Setup order (foundation first): Edit Tenant Setup - Payroll -> Create Period Schedule
(or EIB via Put Period Schedule) -> pay accumulations + pay component groups -> run
categories -> **Maintain Payment Election Rules (one per run category - REQUIRED;
missing rule = processing error, payroll cannot complete)** -> Create Pay Group ->
assign workers (Company FIRST, then pay group - hard prereq; Company is the tax-ID holder).

Key constraints: only ONE run category per pay group can be Regular (on-cycle); one
active Pay Group Auto Assignment rule per pay group; Override First Processing Period
CANNOT change after the first pay calculation; pay run groups must share period schedule
and country.

### Processing cycle (run-time order)

Add Payroll Input -> Run Retro Pay Calculation + Complete (retro MUST complete before
the regular complete) -> Run Pay Calculation (creates gross-to-net AND accounting in one
pass) -> review -> Run Pay Complete -> Create Settlement Run -> post-settlement
integrations (ACH, positive pay, check print, hosted tax filing).

- Smart Calculation is CONFIG-BLIND: it picks up worker changes only, NOT config changes
  (pay component edits, posting rules). Use "Based on Result Status" to recalc after
  config changes; Preview Smart Calculation Run shows what it detected.
- Off-cycle ENFORCED sequence: (1) Manual, (2) Reversal, (3) On-demand, (4) On-cycle.
  All off-cycles complete before the on-cycle completes; settle off-cycles separately.
  Only one off-cycle entry of the same type In Progress per worker.
- Cancel Pay Complete allowed ONLY when: on-cycle complete, no retro in progress or
  complete for the period, settlement not complete, no post-processing (tax integrations)
  has run. It sits in its OWN domain (Process: Run Batch Cancel Complete).

### NRPPT (No Retro Processing Prior To)

The NRPPT date bounds how far back retro searches. Initially set to day 1 of the first
Workday pay period on the first retro calc; auto-moves forward on unsupported events or
max lookback. Pay group or company moves generate an UNSUPPORTED event and push NRPPT
out. Change paths: Change No Retro Prior to Date BP (one worker), the group task (sets
day after last completed period), or the Change No Retro Processing Prior To web service
(per-worker dates - the integration path).

### Payroll input semantics

- Payroll input NEVER causes proration; an override for a subset of days overrides the
  whole subperiod/period.
- Overriding a pay component that was itself established via an ongoing/one-time
  override ADDS instead of overriding - use Adjustment.
- Batch ID enables Delete by Batch ID (works even with In Progress results) - design
  inbound integrations to stamp it. One-Time needs Start AND End date; Ongoing start only.
- Minimum Net Amount on the run category is NOT enforced until Maintain Deduction
  Priorities is configured. Run Retro Pay Calculation never creates or recoups arrears.

### Payroll accounting (13-step sequence, shared FDM tasks)

Run in order - each step depends on the ones above it:

1. Maintain Ledger Account Types
2. Create Account Set (parent = Chart of Accounts, child holds accounts)
3. Edit Default Ledger Accounts (on the posting rule set)
4. Edit Posting Rule
5. Create Fiscal Schedule
6. Maintain Fiscal Schedule Posting Intervals
7. Create Initial Fiscal Year
8. Create Next Fiscal Year
9. **Edit Company Accounting Details** (fiscal schedule + account set + posting rule set) - **LOCKED after the first posting**, so get it right before go-live
10. Maintain Ledger Types
11. Create Ledger
12. Create Ledger Year and Ledger Periods
13. Mass Update Ledger Period Status (the period MUST be open to generate results)

- Suspense accounts best practice (identifier convention 99999.n): Earning Suspense
  (Expense), Deduction Expense (Liability), Net Pay Suspense (Liability). Without them,
  unassigned transactions STOP the payroll cycle.
- Run Pay Accounting regenerates accounting only. RECALCULATE payroll when an earning
  definition, balancing worktag, posting rule, or worker default org changed; re-run
  accounting only for wrong account posting or an unopened ledger period.
- Costing allocation override priority (highest first): payroll input worktags >
  worker-earning > earning > worker > supervisory-org default (Multiple Jobs adds
  position-level layers). Allocations apply per PERIOD END DATE unless Enable Mid Period
  Costing; forward accruals always use period-end allocations.
- Worktag enablement for costing: Maintain Worktag Usage > Payroll Costing Allocation
  (up to 10 Primary Worktag Types).
- Intercompany payroll: tenant-setup enable is IRREVERSIBLE once payroll/commitments
  run; requires Edit Company Intercompany Profile + a SHARED account set across the
  related companies.

## 2. Technical surface

(from the in-tenant WWS master inventory)

- **Payroll service - 120 operations.** Inbound writes: Import Payroll Input (bulk file),
  Submit Payroll Input + Put Payroll Input (singular), Import Payroll Off-Cycle Payment
  (manual + on-demand; NOT reversals), Import Payroll History Payment, Put Period
  Schedule, Assign Pay Group, Assign Costing Allocation, Change No Retro Processing
  Prior To, Put Payment Election Rule, Put Payroll Deduction Recipient, Put Advanced
  Lookup Table, tax-election Puts (Federal W-4, USA State and Local, TD1, FICA/FUTA).
  Reads: Get Payroll Results, Get Payroll Balances, Get Payroll Payslips, Get Payroll
  Inputs, Get Period Schedules, Get Worker Costing Allocations, tax-filing Gets
  (Periodic/Quarterly/Monthly Worker Tax Filing Data, EFW2 year-end).
- **Payroll Interface service - 30 operations** (third-party payroll pattern): Put/Import
  External Payroll Input, Put/Import External Payroll Results, Put External Payroll
  Actuals, Put External Pay Group, Put External Payroll Earning/Deduction, Get Payees.
- Country services: Payroll GBR 63 ops, Payroll CAN 41, Payroll FRA 20, Payroll AUS 8.
- **Settlement Services - 48 operations**: Submit Settlement Run, Put Scheduled
  Settlement Run, Import/Put Payment Acknowledgement Message, Get Payments, Put Bank
  Routing Rule, Submit Payment Return, Submit Stop Items, Submit Escheatment Items.
- **Cash Management - 113 operations** (bank side): Put Bank Account, Put Financial
  Institution, Import Bank Statement, Import Intraday Bank Statement.
- REST: **POST /payroll/v2/payrollInputs** - the REST alternative to the SOAP
  Import/Submit_Payroll_Input path, callable natively from an O4I flow (payroll v2 also
  exposes payGroups, payGroupDetails, jobs, taxRates - see wd-extend-dev
  rest-api-catalog.md).
- House Import-vs-Submit rule (wd-integration-dev eib.md, owner-confirmed): `Import_*` =
  bulk/file convention, asynchronous, results land in an Import Process (harvest via
  Get_Import_Processes + Get_Import_Process_Messages); `Submit_*`/`Put_*` = singular
  transaction, synchronous errors (BP-triggered integrations). Prefer Import for files.
- Import_Payroll_Input payload facts (verified from working sources + public v46.1
  operation pages): wrapper carries Default_Batch_ID + many Payroll_Input_Data (24
  children); Earning_Reference|Deduction_Reference is a CHOICE; Start_Date required,
  End_Date optional; Worktag_Data accepts ~47 typed references with NO single ID-type
  convention (Fund_ID vs Cost_Center_Reference_ID); custom worktags are asymmetric -
  element Custom_Worktag_01_Reference but ID type Custom_Worktag_1_ID; element ORDER is
  not consistent across working integrations - pin one known-good sequence.
- Delivered/hosted: tax filing (ADP, MasterTax, Ceridian), e-IWO child support, bank
  settlement integration systems per bank + payment type, EIB templates generated per
  web service.

## 3. Solution patterns + donors

- **Payroll Input Inbound O4I TEMPLATE (deployed; the house canonical solution).**
  Template integration: delimited file -> header-driven CSV-to-JSON -> map the canonical
  **27-column layout** to Import_Payroll_Input elements -> ONE bulk request per file ->
  harvest Workday's results. Design decisions worth reusing: Cost_Center gets its own
  column, all other worktags PACK into Additional_Worktags as TYPE=VALUE;TYPE=VALUE
  (new worktag type needs NO header change; delimiter attribute must not be ; or =);
  **47-type worktag map**; Workday validates - the O4I does structural gates only and
  harvests the import messages; config ships as packaged App Attributes (a pure
  INTEGRATION app reads attrstore - build-verified); sample mode emits the layout +
  mapping guide as a self-documenting artifact.
- **Pre-formatter**: Document Transformation is the house standard for condensing the
  client file to/from the canonical layout (column condensing belongs in the
  pre-formatter, not the O4I - O4I has no name-based CSV column accessor). DT example
  scripts ship with the template; see wd-integration-dev document-transformation.md.
- **WWS import framework in O4I**: donor `supplierInvoicesInbound` (official catalog) -
  submit -> poll Get_Import_Processes -> harvest Get_Import_Process_Messages -> audit
  file. Same framework applies to Import_Payroll_Input.
- **REST payroll input from a pipeline**: donor `salesCommission` (official catalog) -
  Prism -> DCT execution -> POST /payroll/v2/payrollInputs, plus TriggerIntegration and
  BP approvals. The Prism-to-payroll shape for computed pay (commissions, incentives).
- **Studio donors by INT pattern** (local Workday-delivered CLAR corpus - these are DELIVERED
  Workday reference integrations, NOT firm-built converters; treat as pattern shapes to study,
  and confirm the exact CLAR is on your machine before quoting effort): INT0021
  Payroll-Results-to-GL outbound (also INT0012/INT0030/INT0050 ERP-specific variants and
  INT8920/INT9020 payroll-results outbound), INT0018 Payroll-Garnishments outbound
  (INT0028 garnishments EFT variant), INT0043 timesheet-payroll inbound, INT0014
  currency-exchange-rate inbound, INT0036 commission-upload inbound, INT0023 external
  US-payroll data inbound. These are the reference shapes when converting or estimating
  the classic payroll INT set. IMPORTANT scoping caveat (reconciles with financials.md): the
  estate audit found **no journal/payroll OUTBOUND donor among the firm-built projects** - a
  true GL/third-party export is usually NET-NEW O4I work, not a conversion. The INT0021 family
  here is the DELIVERED-Workday outbound reference, useful as a shape but not a firm converter
  you can lift.
- **Bank/settlement**: INT553/INT554/INT555 bank REST API outbound family (real-time
  request/response - see the wd-integration-dev studio.md donor registry), INT060-style
  prenote status update, INT540-style remittance emails, INT003-style settlement-date
  update. Statement inbound is plain Import Bank Statement / Import Intraday Bank
  Statement EIBs.
- Third-party payroll (Payroll Interface): use the External Payroll Input/Results ops
  above; delivered PECI/WECI connectors exist but their manual is not in the public
  education catalog - treat connector specifics as verify-in-tenant.

## 4. Design gotchas

- Payment election rule missing for a run category = payroll cannot complete. Check it
  in discovery for every new run category an app or integration introduces.
- Payroll input never prorates, and override-on-override ADDS - integrations that
  "correct" prior inputs must send Adjustments or delete by Batch ID and reload.
- Reversals CANNOT be loaded via web service (UI-only) - do not design an inbound feed
  that assumes reversal rows.
- Smart Calculation config blindness: after any config change your solution makes
  (posting rule, earning definition), the recalc must run Based on Result Status.
- Edit Company Accounting Details locks after the first posting - accounting-structure
  decisions are effectively one-way once payroll posts.
- Missing suspense accounts stop the payroll cycle on the first unassigned transaction.
- Get/Put Company Tax Details is secured to the Setup: Tax domain - a payroll ISU often
  lacks it; grant explicitly.
- EIB error signature (doc-sourced): "Invalid ID Value ... Company_Reference_ID" = bad
  reference ID in the sheet; the same message WITHOUT "ID" = the LAUNCHING USER lacks
  security for that company.
- Worktag ID types follow no convention and custom worktags are zero-padded on the
  element but not the ID type - generate the map from a single source of truth, never
  hand-type 47 branches.
- NRPPT pushes out on pay group/company moves - mid-year org changes silently shorten
  the retro window an integration may rely on.
- Currency conversion happens AFTER net pay validation; pay balances, arrears,
  commitments, and fringe actuals are NOT converted.

Cross-refs: wd-integration-dev (eib.md, document-transformation.md, studio.md donor
registry), wd-extend-dev (orchestration.md, rest-api-catalog.md, app-catalog-registry.md),
financials.md in this skill (FDM + journal side), wd-discovery functional-payroll.md.
