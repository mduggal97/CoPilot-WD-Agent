# Functional literacy - Talent Acquisition/Development & Rewards

Assumes shared primitives in [workday-functional-skus.md](workday-functional-skus.md) (eligibility rules,
BP framework, comp basis). Source: Recruiting, Talent, Learning, Compensation, Advanced Compensation,
Benefits, and Creating Benefits Connector Integrations (for Administrators).

---

## Recruiting - the applicant tracking system (ATS)
Unifies internal/external sourcing and the hiring lifecycle from requisition through onboarding handoff, inside HCM.

**Process areas:** requisition management (job/evergreen/confidential; freeze vs. close); sourcing & candidate
marketing (prospects, pipelines, source-of-hire, referrals); career sites (internal Jobs Hub + external multi-country);
the dynamic Job Application BP + 9 subprocesses (Screen, Assess, Interview, Reference, Offer, Employment Agreement,
Background Check, Ready for Hire); dispositioning; OFCCP compliance snapshots.

**Core terminology:** Job Requisition (tracker for an unfilled position) - Evergreen Requisition (continuous-sourcing
req for seasonal/high-volume/hard-to-fill; feeds linked reqs) - Prospect (tracked, not applied) / Active Candidate
(applied) / Pre-Hire (created at Offer/EA/Background/Ready-for-Hire) / Worker (hired) - Candidate Pool (dynamic
<=50k / static <=25k) - Source of Hire - Disposition Reason - Ready for Hire (completion step that triggers HCM
staffing) - Confidential Requisition - Candidate Home (external portal).

**Ties/touchpoints:** reqs anchor to staffing models, job profiles, locations, compensation. Completing the Job
Application BP initiates HCM Hire/Change Job. Job-board integrations (Indeed/LinkedIn/Monster/Seek) with Workday as
system of record; inline assessment-vendor + background-check integrations; Workday Messaging SMS (160 char; limited
country support). OFCCP snapshot + requisition-aging/awaiting-action/source-of-hire reports.

**Gotchas:** (1) the Job Application BP is dynamic/parallel - a candidate can sit in multiple stages, but only one
Offer/EA progresses at a time; "Review" always initiates, "Ready for Hire" always completes. (2) Evergreen candidates
can NEVER be hired directly - move to a linked job req (matching job profiles; links can't be removed). (3) Closing a
req is permanent; freezing is reversible. (4) Only the PRIMARY job profile auto-populates a req. (5) Initiating Offer
or Background Check auto-creates the Pre-Hire record (surprises downstream data).

**HC/Higher-Ed:** evergreen reqs = high-volume/seasonal clinical hiring (nursing/per-diem/residents) and higher-ed
adjunct/student pools; OFCCP matters for federal-contractor hospitals/universities.

---

## Talent & Performance - capture, measure, develop talent
Goals, reviews, competencies, skills (Skills Cloud), potential, calibration - to drive visibility, alignment, and
workforce optimization.

**Process areas:** goal management (individual/cascaded, payout bands); performance & development reviews (Performance
Reviews, IDPs, Disciplinary, PIPs); worker talent data capture; competency & Skills Cloud; calibration (performance
and talent/nBox); talent pools & Manager Insights (ML).

**Core terminology:** Individual vs. Organization Goal - Goal Cascading (identical goal to many, optionally
edit-locked) - Review Category -> Type -> Template (three-tier structure controlling BP steps + layout) - Review
Section (reusable block: goals/competencies/feedback...) - Rating Scale / Section Rating / Overall Rating
(normalized composite) - Talent Review (HR-launched data-gathering event) - Potential (capacity for more; manager-only
visibility) - Skills Cloud (ML skills ontology w/ synonym de-dup) - Competency - Calibration (Performance = 1 rating;
Talent = performance + potential) - nBox (9-box perf vs. potential) - Talent Pool (static/dynamic, org-secured).

**Ties:** talent data hangs off Worker/Job Profile; skills feed Recruiting, Learning, Talent Marketplace, succession;
reviews/calibration roll up the supervisory hierarchy. Skills Cloud + Manager Insights need Skills Cloud + HCM ML
(Innovation Services / ISA).

**Gotchas:** (1) Workday ships NO default rating scales - every scale is a tenant build; Overall Rating normalizes
across differing section scales (mismatched scales silently skew composites). (2) Section weighting affects only the
Overall Rating, not section calcs. (3) Calibration rolls up strictly bottom-up (lower orgs finish first). (4) Talent
Calibration needs two ratings (perf + potential); Performance one. (5) deleting a maintained skill makes it a custom
worker skill; Skills Cloud auto-replaces with synonyms, changing report results. (6) Potential sections are
manager-gated - validate security before go-live demos.

**HC/Higher-Ed:** competency frameworks -> clinical competency tracking + faculty review cycles; nBox/succession ->
physician-leader / faculty succession.

---

## Learning - the embedded LMS
Employee-centric LMS delivering personalized, skill-aligned digital/blended/instructor-led development with catalog,
enrollment, and completion tracking. **Hard-depends on HCM** - sequence Learning after HCM.

**Constructs:** Standalone Lesson / Digital Course / Blended Course / Program / Topic (required browse category) /
Course Offering (scheduled instance). Media Files (<=10 MB; packaged <=4 GB), SCORM/AICC packaged content, Workday
Drive (storage) + Media Cloud (video + in-video Interactions). Certification / Equivalency / Expiry-Retrain rules.
Enrollment: Learning Campaign (<=100k workers), Mass Enroll, Facilitated/Role-based enroll, Waitlists.

**Core terminology:** Standalone Lesson / Digital Course / Blended Course / Program / Topic / Course Offering -
Learning Campaign (required-learning push to a saved-search audience) - Assessor (evaluates on-the-job) - Equivalency
Rule - Expiry/Retrain Rule - Waitlist - Packaged Content (SCORM/AICC).

**Gotchas:** (1) HCM is a hard prerequisite. (2) Training-room capacity fields are informational only - enrollment
limits control capacity. (3) completion fidelity differs by lesson type (external auto-completes on access; packaged
at launch/score). (4) ML recommendations are licensed (ISA), refresh only on a 24h weekday cycle. (5) Programs
auto-complete if all required items already done (unexpected instant completions at rollout).

**HC/Higher-Ed:** Certification/Equivalency/Expiry-Retrain -> healthcare mandatory/compliance training & license
recert (clinical CE, safety) and higher-ed required training; role/location mass-enroll suits multi-site systems.

---

## Compensation (Core) - the reward framework + staffing-time pay
Configures packages/grades/plans/elements and defaults/edits pay during Hire/Add Job/Change Job.

**Constructs:** Compensation Package (grades + plans) -> Grade (min/mid/max range, 3-5 segments) + Grade Profile
(localized variant) + Steps (tenure progression) -> Plans (Salary/Hourly/Period/Unit/Allowance/Commission/Calculated/
One-Time Payment) -> Elements & Element Groups (bridge comp to payroll earnings). Configurable **Compensation Basis**
(Total Base Pay, Total Salary & Allowances, Eligible Earnings Override) - consumed by Advanced Comp and Benefits.

**Core terminology:** Compensation Package/Grade/Grade Profile/Step - Compensation Element (link to payroll pay
component) - Compensation Basis (earnings def for bonus/stock/merit math) - Eligibility Rule - Compa-ratio - One-Time
Payment - Gross Up - Manage Basis Total (enter one total, system distributes across plans) - Propose Compensation
(Hire/Change/Offer) subprocess.

**Gotchas:** (1) hire defaulting precedence: **Offer > Requisition > Position > Eligibility Rules** - a position's
default comp OVERRIDES eligibility rules; job-profile grades override eligibility-rule grades. (2) multiple
eligibility rules OR automatically - order to exclude the largest population first + enable "Eligibility Rule
Performance Enhancement." (3) rules only fire if source fields auto-populate (data dependency). (4) Request Comp
Change is ad hoc and does NOT evaluate eligibility. (5) Manage Basis Total follows a fixed 6-step allocation order.

**HC/Higher-Ed:** Period Salary Plans (13th-month / academic-year pay) and Unit Salary Plans fit faculty/multi-period pay.

---

## Advanced Compensation - cyclical merit/bonus/stock reviews
Runs review campaigns with pooled budgets, planner grids, and performance-driven targets.

**Constructs:** Initiate Compensation Review Process (the campaign BP, mandatory fixed step order); Merit/Bonus/Stock
Plans (+ plan profiles); Compensation Matrix (Amount/Percent/Weighted); Scorecards (Company Funding vs. Plan Modifier);
Configurable Grid (planner entry surface + Grid Profiles + Validations); Pools (bottom-up vs. top-down; holdback/
overage); Participation Rule Sets (handle parallel events/terminations mid-review); Eligibility Waiting + Time
Proration rules; Vesting Schedules.

**Core terminology:** Pool / Holdback / Overage - Bottom-Up vs. Top-Down - Configurable Grid / Grid Profile -
Compensation Matrix - Net Attainment - Scorecard - Discretionary vs. Non-Discretionary - Merit Compounding -
Snapshot Dates (Organization / Compensation / Process Period End) - Prefill/Autofill.

**Gotchas:** (1) performance reviews must be COMPLETE before review initiation and period-end dates must align, or
matrix/scorecard data won't populate. (2) editing a rating in the grid does NOT update the underlying review. (3)
matrix + scorecard weights must total exactly 100%. (4) participants can redistribute but not increase the budget at
Distribute Pools. (5) the three Snapshot Dates each control a different facet (hierarchy vs. baseline comp vs.
eligibility/proration) - a frequent misconfiguration. (6) stock is annual-frequency only.

**Ties:** reads supervisory hierarchy for pool rollup; consumes Compensation Basis for percent targets; deep tie to
Talent (ratings/goals feed matrix/scorecard); awards flow to Payroll.

---

## Benefits - plans, eligibility, enrollment events
Configures benefit plans, eligibility, and enrollment events (life events, passive, open enrollment) governing
elections and coverage.

**Constructs:** Benefit Provider; Coverage Type & Coverage Target (participation levels + dependent validity);
Benefit Group (eligibility-rule cohort controlling plan access); Benefit Plan types (Health Care/HSA/FSA/Insurance/
Retirement/Additional); healthcare classifications PPO/HMO/EPO (US); Benefit Credits (38 credit types); Benefit Plan
Year Definition (active plans for a period); **Enrollment Event Type + Enrollment Event Rule** (the 6-tab framework
where nearly all enrollment behavior lives); Events and Reasons; Benefit Defaults (priority-based); Passive Event Rule;
Cross Plan Dependencies; Evidence of Insurability (EOI).

**Core terminology:** Coverage Type / Coverage Target - Benefit Group - Benefit Credit - Plan Year Definition -
Enrollment Event / Enrollment Event Rule - Passive Event (time-milestone-triggered, e.g. dependent age 26) - EOI /
Guaranteed Issue - Cross Plan Dependency - Benefit Annualized Rate (BAR) - Open Enrollment - Court-Ordered Coverage.

**Gotchas:** (1) a plan is invisible at enrollment unless it's in an ACTIVE Plan Year Definition. (2) the 6-tab
Enrollment Event Rule governs waiting periods, coverage begin/end, allowed changes, EOI, defaults. (3) **event
coordination**: overlapping events process earliest-first, later go on hold, then cascade; same-effective-date events
merge into a "hybrid" event by priority - a major source of unexpected results. (4) EOI timing is governed by TWO
settings (event rule + benefit group). (5) dependents with active enrollments can't be deleted; court-ordered coverage
errors on removal.

**Ties:** plans map to Payroll earnings/deductions; eligibility reads HCM worker data; credits can reference
Compensation (BAR). Benefits Connector is the outbound carrier feed (below); COBRA eligibility auto-populates.

**HC/Higher-Ed:** heavy US-healthcare content - PPO/HMO/EPO, HSA/FSA limits, Medicare (CMS Part A/B/D + ESRD), COBRA,
irrevocable beneficiaries (Quebec). Relevant to any employer running US group health.

---

## Creating Benefits Connector Integrations (Cloud Connect for Benefits, CCB)
Workday-maintained connector TEMPLATES that transmit benefits elections/eligibility to carriers and third parties.
This is the one integration-heavy manual in the rewards set - directly relevant to our delivery work.

**The benefits-vendor feed landscape:** primary carrier feed = **ANSI X12 834** (medical/dental/vision/life/
disability/retirement; segments/elements/loops); **Benefits Connector V2** (generic XML for vendors without a
dedicated template); **COBRA connectors** (initial rights + qualifying events); **payroll-integrated CCBs** (401k/FSA/
HSA deduction feeds).

**Constructs:** CCB Templates (834 V2 most common); Integration Services (Transformation, Loops, Transaction Log,
Filters, Sequence Generator, Delivery, Retention); Integration Attributes; Integration Maps (Workday value -> vendor
code); Integration Field Overrides (loop/segment/element refs); ISU + ISSG (one ISSG per product area); Change
Detection + Launch Parameters; Debug Service; Clone vs. Change Template.

**Core terminology:** Cloud Connect for Benefits (CCB) - End-to-End Connector - ANSI 834 - Segment/Element/Loop -
Change Detection (Newly Effective vs. Newly Entered) - Launch Parameters (Effective Date / From Effective Date /
Last Update) - Integration Map - Integration Field Override.

**Gotchas:** (1) never build on Deprecated/"Do Not Use"/DNU templates. (2) payroll-integrated CCB behavior FORKS on
payroll source - **Workday Payroll sends ACTUAL contributions; third-party payroll gets ESTIMATED** amounts from plan
config (a correctness landmine). (3) change detection distinguishes newly-effective vs. newly-entered and retro vs.
future - launch dates must match the vendor's cadence. (4) testing is "the most important part" - isolate Workday
DATA problems vs. integration-config problems. (5) Clone preserves config for safe iteration; Change Template forces
reconfiguration (expensive). (6) enrollment-event rules directly determine what qualifies for the file - benefits
config and connector output are tightly coupled.

**HC/Higher-Ed:** the 834 is the industry-standard US group-health enrollment feed; any healthcare/higher-ed employer
with multiple carriers runs several CCBs.
