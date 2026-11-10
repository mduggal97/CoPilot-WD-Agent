# UET (Unified Engagement Tool) - fill procedure

Verified against the Oct-2025 UET version (a sample workbook; see Engagement inputs). The workbook is ~60 sheets, but almost all are hidden calculation/validation/DBI layers - **never touch hidden sheets or formula cells**. Work only the visible input sheets, in this order (the Start tab's own instructions confirm the sequence).

The file is `.xlsb` - openpyxl cannot read it. Use Excel COM (pywin32/PowerShell) read-only for inspection; for FILLING, prefer guiding the user through manual entry or COM with extreme conservatism (input cells only, save-as under a new name, never overwrite the template).

## 1. Start - opportunity setup

- Opportunity Name / Industry / Client Name (as they appear in Salesforce - the UET expects Salesforce-consistent values)
- Contract Arrangement Type (e.g. Hourly; drives which additional inputs unhide - `*`-marked rows apply to hourly/rate arrangements)
- Opportunity Currency, Project Company
- Internal team: Managing Director, Project Director, Project Manager
- Contract Start Date (**must be a Monday**) / End Date (term limits apply, e.g. E&I cannot extend beyond a published cap) - Term months/weeks compute automatically
- Rate card approach: Standard / Plan / **Custom Rates** (custom -> fill the Custom Bill Rates Table next); Lead Cost Center for plan/auto rates (the Extend offering's lead cost center - see Engagement inputs)
- Multiyear Bill Rate Escalator %, Included Expenses %, Expense Hourly Rate
- Contingent workers / vendors: only via their buttons if used

## 2. Custom Bill Rates Table (only for Custom Rates)

Rates by `Level_Country` row (Executive/MD/Principal/Senior Director/Director/Senior Manager/Manager/Senior Associate/Associate/Senior Analyst/Analyst - per country block USD/INR/CAD): enter the **1st Twelve Months Bill Rate**; later periods auto-populate from the escalator. Only fill levels you'll actually staff.

## 3. ResourceEffort - where the LOE lands

One row per resource (person or TBD role). Two zones per row, left->right:

- **Costing info**: Offering (Extend work = `Workday Extend: Extend Services`), Resource Cost Center (the Extend offering's cost center - see Engagement inputs), Costing Level & Location + Billing Level & Location (e.g. `Senior_Manager_USD`), Billable/Investment. Contribution Margin and Staffing Mix Target compute per row - a deeply negative margin (e.g. MD at custom rates) is a pricing decision to surface, not hide.
- **Staffing info**: Digital Proposal Role, Project Role (`Developer`, `Developer Lead`, `Functional Consultant`, `Project Manager`, `Subject Matter Expert`, `Change Management Lead`), Worker Name (blank if unknown - but the Review tab will warn on missing role assignments), Supervisory Org (required for expected-capability HC), Resource Pool, Restrict-to-US flag, Memo (use it: `"Senior Manager - <name or TBD>"`), Skills.
- **Weekly hours grid** (columns to the right): hours per resource per week across the term. Workflow per the sheet's instructions: complete costing info -> click **"Estimate Hours"** (macro establishes totals) -> manually shape the Actual Forecast per week -> **"Edit Staffing Info"** for staffing details. Remove hours forecast past the contract end date (the sheet flags this).

Translate your phase x role LOE into this grid: each role's phase hours spread over that phase's weeks. Keep a side table (plain Excel/markdown) showing LOE by role x phase - that's your durable estimation artifact; the UET grid is its projection.

## 4. PricingDetermination - levers

Review Revenue / Contribution Margin (Actual vs Target) summaries; apply levers: Contingent amount, Fee Cap (required for capped/Fixed-Not-to-Exceed arrangements), Expense Cap, Non-Billable Expenses. Adjustments show as Unadjusted Revenue - Adjustment. Note reasoning in "Additional Pricing Inputs/Notes" - it carries to Review.

- **Prism cost driver (when the scope includes Prism):** every physical row of a published dataset / analysis-enabled table counts against the client's **Prism reportable-rows entitlement** (visible at Data Catalog > Prism Usage). Pipelines that pre-aggregate reduce both runtime and entitlement consumption - a scoping lever worth pricing into the design effort, and a talking point when the client's entitlement is tight. (Per Workday Admin Guide (Reporting & Analytics), Jul 2026.)

## 5. Review - final check

Summary + warnings. Resolve every warning (e.g. **"Warning: Missing Project Role Assignments"**) or note why it stands. Check: TCV, margin actual vs target, MD hours, % global resource hours. This tab is what pricing leadership reads - it must be clean.

## When building from a donor workbook (copying a prior opportunity)

- **Donor-cleanup sweep is mandatory and includes FORMATTING**: after clearing the prior opportunity's ResourceEffort rows, sweep the whole used range for leftover data rows AND leftover cell fills/formats with no data (both shipped once, 2026-08-03). Cleared rows must look like clean empty rows.
- **Trace required fields, don't guess at them**: scan formulas on all other sheets (including hidden calc/DBI sheets - read-only) for references into ResourceEffort's input columns; that trace defines which inputs drive downstream calculations. Fill the derivable ones (flag as assumptions); anything needing the user (named resources, pricing policy) goes on an explicit **"Fields you must complete"** checklist - in chat, in the assumptions doc, and in the project next-steps. Never leave a formula-driving input silently blank.

## Financial-workbook audit conventions (workbooks WE author)

For financial workbooks the firm authors from scratch - the LOE side table above, pricing models, value calculators, anything pricing leadership or a client will audit - apply these conventions (pattern from a community skill-craft survey, 2026-08-06 - rebuilt for this suite):

- **Cell color semantics**: blue = hardcoded input, black = formula, green = cross-sheet link. A reviewer can then see at a glance what is assumption vs. derivation vs. plumbing - and which cells are safe to change.
- **Live formulas ONLY for derived values.** A pasted number where a formula belongs is a defect: the delivered value silently detaches from the delivered assumptions, and the next input change lies.
- **A dedicated CHECKS tab** surfacing reconciliation booleans - totals tie across tabs, rates x hours = revenue, side-table LOE matches the grid - each a visible TRUE/FALSE at a glance. Any FALSE blocks delivery.
- **Recalculate headlessly before delivery** so delivered values match delivered formulas - never ship stale cached results. The suite's LibreOffice recalc path lives in bow-sales-enablement's build kit (`assets/wave2-build-kit/xlsx_helpers/recalc.py`; toolchain setup in wd-extend-lifecycle `references/prerequisites.md`); on a machine with Excel, a COM open-recalc-save works too.

These conventions **complement, never override, an existing template's own formatting**: inside the UET itself, the formula-preservation rule above wins (never touch hidden sheets or formula cells). Apply the full set only to workbooks whose format we own. Shared surface: bow-sales-enablement's Spend Snapshot (`references/spend-snapshot.md`) runs the same discipline - blue inputs, formulas-only calc cells, recalc-to-zero-errors gate.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Donor/sample UET workbook** - the prior-opportunity workbook you copy from (if any), used only as a structural donor (run the donor-cleanup sweep above before reuse).
- **Opportunity & Client name** - as they appear in Salesforce (the UET expects Salesforce-consistent values).
- **Industry** - the client's industry classification.
- **Internal team** - Managing Director, Project Director, Project Manager for this opportunity.
- **Project Company** - the firm legal entity / project company on the opportunity.
- **Opportunity currency** - the currency for the estimate.
- **Extend offering + lead cost center** - the offering code for Extend work and its lead/resource cost center.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
