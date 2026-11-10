# Workday Functional SKUs - domain literacy for delivery

**Why this exists.** Our practice is deep on TECHNICAL delivery (Extend, orchestration, integrations,
Prism). This reference set builds the complementary FUNCTIONAL literacy - what each Workday SKU does,
its process areas, its configuration building blocks, and the vocabulary a client speaks - so we can
run discovery, scope, and design in the client's functional language, not just the build layer.

Source: official Workday Education course manuals (doc.workday.com/en-us/workday-education.html),
mined 2026-08-07. Tier = doc-sourced (official Workday narrative); cite the manual. Vendor-neutral -
no client specifics. Use this to ASK better discovery questions and RECOGNIZE what a client means, not
as configuration how-to.

## How to use
- Heading into discovery/design for a functional area, read that domain file first to speak the language.
- When a client names a term you don't know, find it in the domain file's terminology block.
- The "Integration & reporting touchpoints" in each SKU is the bridge to our delivery work - it tells
  you where EIB / Core Connector / Studio / Orchestrate (O4I) / RaaS / WQL / Prism / Extend commonly attach.

## Domain files (index)
- [functional-hcm.md](functional-hcm.md) - HCM Foundation, Security, Time Tracking, Absence
- [functional-hcm-talent-rewards.md](functional-hcm-talent-rewards.md) - Recruiting, Talent/Performance, Learning, Compensation, Advanced Compensation, Benefits, Benefits Connector
- [functional-payroll.md](functional-payroll.md) - Payroll, Global Payroll Connect (PECI/PI/WECI)
- [functional-financials.md](functional-financials.md) - Financial Management, Financial Accounting, Accounting Center, Consolidation, Procure-to-Pay, Customer Accounts & Contracts
- [functional-student.md](functional-student.md) - Student (SIS): Foundation, Records & Advising, Recruiting & Admissions, Financial Aid, Student Financials
- [functional-analytics.md](functional-analytics.md) - Report Writer, Advanced Reporting (HCM/Financials), Prism Analytics, BIRT Report Designer

## The one-platform model (shared primitives - learn once, reused everywhere)

Every Workday SKU is built on the same platform primitives. Learn these once; each domain file assumes them.

- **Tenant** - the customer's uniquely configured Workday instance. Metadata (Workday-owned) vs. tenanted
  data (customer config + transactions). Preview tenants get features ~5 weeks early; weekly service
  updates vs. two feature releases/year (R1, R2) drive an adoption cadence.
- **Foundation Data Model (FDM)** - the dimensional backbone shared by HCM, Financials, and Student.
  - **Company** = the internal legal entity; "the level at which you hold a balanced set of books."
  - **Organization types**: Supervisory (HCM management hierarchy), Cost Center, Location, Region,
    Pay Group, Matrix, plus sector types **Fund, Grant, Program, Project, Business Unit, Gift** (the fund/
    grant structures that matter for higher-ed and nonprofit/health).
  - **Worktags** = keyword labels representing business dimensions, stamped on transactions for
    multidimensional reporting. Every organization is automatically a worktag; worktags are NOT organizations.
    Caps: ~15 custom worktag types; up to 10 custom org worktags financial-enabled (canonical numbers owned by wd-solution-playbooks `financials.md` - reconcile there if these drift). **Related/defaulted
    worktags** auto-populate from a chosen object; "last one in wins" on conflicts (validate defaulting order).
  - **Organization hierarchies** roll up for reporting/security/role inheritance but **hold no transactions** -
    posting happens at the org/company level. Don't conflate hierarchy with posting.
  - **Account Posting Rules** translate operational transactions (charges, invoices, payments, external
    feeds) into GL journals with the right ledger account + worktags. This is the bridge from any module to the ledger.
- **Configurable Security** - authorization model (distinct from authentication/SSO).
  - **Domain** (secured tasks/reports/data) with a **Domain Security Policy** (View/Modify; Get/Put for
    integrations). **Business Process Security Policy** (per BP type: initiate/approve/cancel/rescind/delegate).
  - **Security groups** (~24 types): membership is Workday-assigned (All Users, Employee As Self - uneditable),
    manually assigned (user-based, unconstrained), or **derived** (role/job/org/location/segment).
    **Constrained** (limited to the member's orgs/data) vs. **unconstrained** (all data).
  - A user's access is the **UNION** of all their groups - one unconstrained group silently overrides careful
    segmentation. **Nothing takes effect until "Activate Pending Security Policy Changes" runs** (the classic
    "I changed it but it didn't work"). Some domains enforce group-TYPE (self-service domains accept only
    self-service groups).
  - **ISU (Integration System User) + ISSG (Integration System Security Group)** is the core pattern for
    EVERY integration; ISSG grants Get (outbound) / Put (inbound) on the needed domains. **Inbound EIBs are
    special - they typically assess the LAUNCHING user's security, not an ISU** (a frequent delivery surprise).
- **Business Process (BP) framework** - the "what/who/when" workflow engine used for every transaction
  (Hire, Change Job, Termination, Charge, Payment, Enrollment, Admissions decision...).
  - Definition approaches: Default (one shared, recommended) / Organization-specific / Rule-based (one condition
    rule per definition, evaluated at initiation). Workday uses the definition **effective at initiation**, not
    the event's effective date.
  - ~23 step types (Initiation, Action, Approval, Approval Chain, Consolidated Approval, To Do, Checklist,
    **Integration step** = the hook to trigger an EIB/Studio/O4I mid-workflow, Report, Service, Review Documents...).
  - Condition rules: Entry / Validation / While-Running / Exit. **Denial of ANY approval/review step denies the
    ENTIRE BP.** Data is **Proposed** (uncommitted) until the single **Completion step** succeeds - important for
    integration timing. Correct (in-flight) / Rescind (completed) / Cancel (in-progress).
- **Report Writer** - the no-code report engine on the live object model (Primary/Related Business Objects,
  Class Report Fields, Report Data Sources, calculated fields). RaaS = a web-service-enabled Advanced report =
  the outbound data feed. Full detail in [functional-analytics.md](functional-analytics.md). WQL traverses the
  SAME object model - understanding data sources IS understanding WQL scope.
- **Eligibility Rules** - a shared criteria engine reused across Compensation (which comp components apply),
  Benefits (groups/plans), Absence (accrual/leave), Student Financial Aid (COA/award), and Time. Same rule
  builder, different data domain. Multiple rules on one target are OR'd; rules only fire if their source fields
  auto-populate (data dependency is the #1 failure mode).
- **Calculation Engine** - numeric/Boolean/date/step-based calcs recurring across Absence, Time Tracking,
  Payroll, and Student Financials. One skill, many modules.
- **EIB (Enterprise Interface Builder)** - the spreadsheet-driven mass-load/extract path common to Absence,
  Payroll input, Compensation one-time payments, journals, contracts, invoices. First reach for bulk data moves.

## Deployment sequencing (typical, cross-SKU)
Foundation (FDM: companies, orgs, worktags, security) first -> HCM Core (supervisory orgs, staffing, job
profiles) -> Compensation/Benefits/Time/Absence -> Payroll (hard-depends on HCM + Comp + Time) -> Financials
(FDM + P2P + revenue) in parallel. **Student**: academic foundation first, then Records, then Admissions,
then Student Financials (with core Financials), then Financial Aid (depends on enrollment AND charges - highest
compliance risk, sequenced last). **Learning** hard-depends on HCM. Reporting/Prism build in parallel with each.

## Vertical lens - Healthcare & Higher-Ed (our practice)
- **Higher-Ed / research / nonprofit fund accounting**: the FDM sector worktags **Fund, Grant, Program, Project,
  Gift** are the load-bearing structures; **Commitment Accounting** (payroll budget encumbrance) is the classic
  grant-funded/public-sector payroll requirement.
- **Workday Student** is the higher-ed SIS - a full vertical on the same platform ([functional-student.md](functional-student.md)).
  Federal integration surface (ISIR/CPS, COD, NSLDS) makes Financial Aid the highest-compliance, latest-sequenced module.
- **Healthcare workforce**: 24/7 shift staffing drives Time Tracking (shift differentials, min-rest, consecutive-day,
  meal/break attestation, geofenced clock-in), Absence (FMLA/STD/LTD cascades, intermittent leave), and high-volume/
  seasonal Recruiting (evergreen requisitions). **Benefits + Benefits Connector (834 EDI)** is the standard US
  group-health enrollment feed; PPO/HMO/EPO, HSA/FSA, COBRA, Medicare coordination all surface.
- **Accounting Center** (Prism-based) is the classic bridge for high-volume operational feeds - patient billing/
  claims (health) and bursar/SIS/research (higher-ed) - enriched into GL journals.
- Demo tenants seen in the manuals: **AMU = Alma Mater University** (Higher-Ed), **GOV = Green Oak Valley** (public sector).

## Cross-references into the technical suite
(Name-level pointers - skills stay separable, so no deep relative links.)
- FDM/worktag depth for build: wd-extend-dev `domain-patterns-hc-highered.md`.
- RaaS/WQL/Prism build mechanics: wd-extend-dev `prism-and-reporting.md`, `orchestration.md`.
- Payroll-input / WWS-import integration shapes: wd-extend-dev `orchestration.md`; traditional integration build: wd-integration-dev.
