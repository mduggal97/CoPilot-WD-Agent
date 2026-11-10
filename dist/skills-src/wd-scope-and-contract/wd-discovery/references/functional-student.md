# Functional literacy - Workday Student (higher-ed SIS)

Assumes shared primitives in [workday-functional-skus.md](workday-functional-skus.md). Source: Student,
Student Records & Advising, Student Recruiting & Admissions, Student Financial Aid, Student Financials
(for Administrators). This is the HIGHER-ED VERTICAL - highest-priority functional literacy for our practice.

**The single most important thing:** Workday Student is an SIS built on the SAME platform as HCM/Financials
(security groups, business processes, worktags, Report Writer). A Workday consultant fluent in HCM security transfers
directly. All five modules share ONE **academic foundation** configured once; foundation errors propagate everywhere.

**Deployment sequencing:** Foundation & Records first -> Recruiting/Admissions -> Student Financials (with core
Financials) -> Financial Aid (depends on enrollment AND charges; highest compliance risk, sequenced last). The four
big SIS-conversion streams: course catalog + academic records; prospect/application data; open AR balances; historical aid/awards.

---

## Student (Foundation) - the shared academic structure
The platform course - academic structure, configurable security, BPs, and reporting underpinning all four functional
modules. A hard prerequisite: nothing (aid, financials, records) works until the foundation is configured.

**Constructs:** **Academic Unit (AU)** (school/college/department org - itself a Workday organization type, so Student
plugs into the shared org model) + subtypes/hierarchies; **Academic Level** (undergrad/graduate/professional);
**Program of Study (POS)** (educational objective conferring a credential; standalone / addable-concurrent /
stackable-sequential); **Academic Calendars / Periods** (standard vs. nonstandard - intercession, express); Educational
Credentials; **Date Controls** (enrollment window, census, disbursement); Academic Policies.

**Core terminology:** Academic Unit / Academic Level / Program of Study - Academic Period (standard vs. nonstandard) -
Educational Credential - Date Control - Student Cohort - Report Writer (same 8 types as HCM/Fins - see functional-analytics.md).

**Gotchas:** (1) academic foundation is a hard prerequisite - four of five manuals open with a "foundation review."
(2) effective dating drives changes (not rigid catalog-year cloning). (3) POS stackable vs. addable determines
concurrent/sequential credential behavior - get it right early. (4) domain inheritance cascades down the AU hierarchy;
multiple-policy access is additive (most permissive wins). (5) BPs route to security GROUPS (staff-change continuity),
never named individuals.

**Higher-Ed:** the mandatory first build phase. Common pain: underestimating calendar/period modeling for nonstandard
terms (intercessions, express/module courses), which later breaks aid and charge calculations.

---

## Student Records & Advising - the academic-records backbone
Curriculum (courses/sections), academic requirements & degree audit, advising/cohorts, grading, transfer credit,
program completion, transcripts. Usually the LARGEST data-conversion and configuration lift.

**Constructs:** Course Definitions (catalog record) vs. Course Sections (registration-eligible offering); Course
Equivalency Groups, Cross-Listed Courses, Course Section Clusters (must-register-together), Reserved Capacity;
**Academic Requirements** / Requirement Groups/Areas / Restricted Requirement Groups (precedence when a course could
satisfy multiple); Academic Plan Templates (auto-assign); Student Cohorts; Grading Schemes; Eligibility Rules (shared
engine - prerequisites, co-reqs, restrictions).

**Core terminology:** Course Definition vs. Course Section - Versioning vs. Editing (preserve prior instances for
major change vs. override for minor) - Eligibility Rule - Course Equivalency Group - Cross-Listed Course - Course
Section Cluster - Reserved Capacity - Academic Requirement / Group / Area - Restricted Requirement Group - Academic
Plan / Template - Student Cohort (doubles as a security/data-access scope).

**Gotchas:** (1) version vs. edit on courses is a permanent data-integrity decision - versioning is default for
substantive change. (2) Eligibility Rules are a shared engine (prerequisites, reserved capacity, requirements) - model
once, reuse. (3) Cohorts serve double duty (advising + security constraint) - design with access in mind. (4)
Restricted Requirement Groups prevent a course double-counting - omitting them inflates degree-audit progress. (5)
cross-listing and section clusters are frequent registration/capacity bug sources.

**Higher-Ed:** the biggest config + conversion lift (full catalog + requirements + historical records); degree-audit
requirement modeling is the classic multi-institution pain point - plan iterative validation against legacy audits.

---

## Student Recruiting & Admissions - top of funnel
Prospect recruiting, multi-channel campus engagement, the admissions application lifecycle, an external applicant
site, and admissions decisioning. Often the first applicant-visible go-live (reputational risk).

**Constructs:** Student Classifiers (educational interests, tags); Recruiting Rating Scales; Recruiting Regions;
Admissions Counselors; Prospect Assignment Criteria; **Student Audiences** (dynamic saved-search groups that
self-update); Engagement Items (single comm asset); **Engagement Plans** (sequenced multi-channel campaigns); Student
Condition Rules; Message Templates; External Student Site.

**Core terminology:** Prospect - Prospect Stages (Lead -> Inquirer -> Pre-Applicant -> Applicant -> Pre-Matriculant ->
Student) - Educational Interest - Student Tag - Referral Source vs. Recruitment Source (why they contacted vs. how
recruited - distinct) - Recruiting Region - Admissions Counselor - Student Audience - Engagement Item / Engagement Plan
- Ad Hoc Messaging - External Student Site.

**Gotchas:** (1) the Campus Engagement Framework is SHARED across modules (used for FA/records comms too) - not
admissions-only. (2) Student Audiences are dynamic - "who receives this" isn't static; test carefully. (3) prospect
stage progression drives assignment + automation - mis-mapped stages break the funnel. (4) referral vs. recruitment
source is a real modeling decision institutions conflate. (5) the external site is a config deliverable with its own
security/branding.

**Higher-Ed:** academic foundation + POS must exist before admitting into programs. Common pain: reconciling legacy
CRM funnel definitions to Workday's fixed prospect stages + communication-preference/opt-out handling.

---

## Student Financial Aid - the Title IV engine
Federal program policies, ISIR processing, cost of attendance, merit/need packaging, disbursement, and compliance
(SAP = Satisfactory Academic Progress; R2T4 = Return of Title IV). Automation-first (nightly orchestration). Highest compliance-risk module (Title IV audit exposure).

**Constructs:** Federal Student Aid Program Rule Sets; Load Status & Class Standing Rule Sets; Calendar Policies +
Typical Attendance Patterns; Reaction Policies (COA/Merit/Need) + Reaction Reasons/Methods; Job Scheduler; Student
Cost Items + assignment; **Student Award Items** (calculations, precedence groups, fiscal limits, loan fees,
disbursement/proration); Financial Aid Action Item BPs; ISIR integrations.

**Core terminology:** **ISIR** (processed FAFSA data; primary input) - SAR ID (matching key) - **SAI** (Student Aid
Index; replaces EFC; drives need) - Financial Aid Action Item (info request via BP; can auto-hold) - Federal
Verification - Attendance Plan (projected enrollment; nightly-refreshed) - Load Status / Class Standing - **Cost of
Attendance (COA)** (Standard per-period vs. Pell full-year) - Student Cost Item - Student Award Item - Merit vs. Need
Packaging (two independent nightly strategies) - Payment Precedence Group - **Nightly Orchestration** (runs overnight, ~1 AM by default; fixed
sequential steps - **(!) reconcile: this file said 11 steps, wd-solution-playbooks student.md enumerates 18 jobs; verify the count against the current Student admin guide before citing either to a client**) - Reaction Framework (detects changes -> reprocessing) - TFA (Total Financial Assistance) - SAP /
R2T4 (Return of Title IV).

**Gotchas:** (1) automation-first - the nightly orchestration's STEP ORDER is fixed (it runs overnight, ~1 AM by default; the schedule itself is tenant-configurable - do not tell a client the time is immutable); you control
what data feeds each step. (2) Job Schedules create the FIRST instance; the Reaction Framework governs everything
after - mixing them up causes reprocessing errors. (3) Reaction Method (Auto vs. Review) + Manual Review Date
determine whether aid auto-adjusts or waits for a human. (4) merit and need packaging run independently. (5) Attendance
Plan accuracy is the linchpin; nonstandard/module course dates drive recalculation and are error-prone. (6)
pre-matriculation packaging is possible but gated on ISIR Progression Policy milestones.

**Integration:** heavy federal - **ISIR/CPS inbound, COD (Common Origination & Disbursement), NSLDS** exchanges with
the US Dept. of Education, school-code transmission. Monitor via Nightly Job Orchestration Results.

**Higher-Ed:** depends on both Records + Financials, so sequenced late; institutions often run PARALLEL aid cycles
before cutover; validate COD/NSLDS integrations before a real disbursement.

---

## Student Financials - the bursar / student-account module
Applies charges and payments, runs the calculation engine, manages sponsor contracts, waivers, refunds, and
collections - all posting to Workday Financials via worktags + account posting rules. The DEEPEST integration into
core Financials.

**Constructs:** **Student Financials Period Record** (per-student, per-period account; auto-created at matriculation,
spans anticipated start -> expected completion); Charge Items + Charge Assessment; Calculation Engine (tuition/fee
calcs); Account Posting Rules + Worktags + Costing Organizations (Company/Cost Center/Fund/Program/Grant/Gift...); 12
Student Financials BPs (Charge/Payment/Deposit/Refund events); Payment Plans; Waivers; Refund rules; Collections
policies; Sponsor Contracts (third-party billing).

**Core terminology:** Student Financials Period Record - Charge Item / Charge Assessment - Calculation Engine -
Worktag - Account Posting Rule - Payment Precedence (shared with Financial Aid) - Sponsor Contract - Waiver - Refund
(incl. Title IV credit balances) - Deposit - Collections / Past-Due Balance.

**Gotchas:** (1) sits on the **Financials FDM** - worktags/companies/account-posting-rules must align with the
institution's core finance chart (a JOINT config with the Financials team). (2) Period Records auto-generate at
matriculation from primary-program dates; program/date changes shift the record span. (3) inactivating a worktag value
affects only future transactions. (4) Account Posting Rules auto-derive related worktags from student/AU/transaction -
get derivation right or GL misclassifies. (5) payment precedence is shared logic with Financial Aid - coordinate both
modules' config.

**Higher-Ed:** bursar go-live is high-stakes (real money, refunds, sponsor billing); must be coordinated with core
Financials. Common pain: mapping legacy tuition/fee calc rules into the calc engine, converting open AR, aligning
student-account worktags with the finance chart. Sponsor/Title IV credit-balance refunds are complexity hotspots.

## SIS discovery question bank (Financial Aid + Academic Foundation)
> Folded in from a config-guide distillation sweep (2026-08-10). Vendor-neutral; no client specifics.

### -> wd-discovery functional-student.md (vendor-neutral SIS discovery question bank)

Consolidates the client-discovery question sets ending the Academic Date deck and the SAP guides into a tool-agnostic Financial-Aid + Academic-Foundation discovery bank. Vendor-neutral (no Workday task names); ask these of any SIS.

**Academic Foundation - Calendar & Periods**
- How many academic calendars does the institution manage, and in what format (annual / semester / quarter)?
- What period types are used and for what purpose (e.g. Fall, Spring, Summer; academic vs activity-pay/faculty-contract use)? Which period types link to each academic year?
- Does the academic structure require separate calendars per academic unit or program? Any unique/dynamic calendars (a program on a different cadence)?
- Are there mini/sub-sessions inside standard periods, and do they share or differ in start/end dates? How many weeks of instruction?
- What are the start/end dates for each academic year and period, and which units/levels link to each year?
- How does policy inheritance apply to calendars - which units/programs need inheritance "broken" for a unique calendar?

**Academic Foundation - Date Controls alignment**
- For advising, registration, records, student finance, and reporting: which student events are date-gated (last day to drop without a W, last day to drop, census date, fee calculation, open/close registration)?
- How do registration start/end dates align to the calendar? When does the initial enrollment window open and when can students first register?
- Are dates uniform across all levels / units / programs, or do populations differ? Are there priority-registration populations (athletes, international, disability, veterans)?
- Do any course sections carry their own dates instead of the period-level controls?
- What are the current-system limitations to model around (e.g. a cap on students per registration appointment)?
- Will any registration date have non-registration downstream impacts (notably financial aid)?

**Financial Aid - Date Controls**
- Which FA events are date-gated (disbursement, cost of attendance, packaging, student award, Pell)?
- How does the "actual enrollment usage" start align with registration appointments? Who determines enrollment, and by what process, to report actual enrollment by the census date?
- Who assesses students for disbursement-ready aid after the disbursement end date, and how?
- What gap is intended between award-display-start and the tuition due date, and does it differ for entering vs returning students?
- After the Pell recalculation date, will Pell be manually recalculated, and how often?

**Financial Aid - SAP finalization (when/where SAP is finalized in legacy + which populations need overrides)**
- In legacy, are ALL courses counted during SAP evaluation, or only courses that count toward the program of study? (Determines whether cumulative override measures must be converted.)
- When are SAP statuses finalized for the academic period / award year, and is evaluation run per period or per award year?
- When is the SAP assessment actually run in legacy?
- How are SAP statuses and cumulative measures evaluated and STORED in legacy (and can they be extracted)?
- Which student populations require SAP status revisions / overrides in legacy?

**Student Financials - Date Controls**
- Should registration soft-drop windows be defined (pros/cons), and how do anticipated payments factor in?
- How does the calendar drive whether/when late-course-add and late-registration fees are assessed?
- How do award-display-start dates align with payment-plan sign-up windows? What window length for payment-plan sign-up and for the soft-drop window?
- How do tuition deadlines and course start dates align to the payment-plan and soft-drop windows?

**Student Records - Date Controls**
- Is the conferral date printed on transcripts / shown in records?
- What are the grade-change and grade-entry processes, who is involved, and how are missed deadlines handled on the back end?
- Is there a need to verify attendance within a defined date range?
- Are program-declaration deadlines needed? How is residency-status change managed (and is a change window needed), given its tuition/FA impact?

(Vendor-neutral consolidation of discovery questions from Academic Date deck.pptx and SAP Data Conversion Guide.pptx.)
