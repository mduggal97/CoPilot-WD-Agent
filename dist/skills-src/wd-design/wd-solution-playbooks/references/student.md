# Student playbook - foundation, records/advising, recruiting/admissions, financial aid, student financials

Workday Student is an SIS on the same platform as HCM/FIN (same security, BPs, worktags, Report
Writer). All five modules share ONE academic foundation; foundation errors propagate everywhere.
Functional literacy lives in wd-discovery functional-student.md; FERPA/industry cues in
wd-extend-dev domain-patterns-hc-highered.md. This file is the design crib.

## 1. Configuration spine (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

**Foundation order (condensed):** Academic Unit subtypes > Academic Units (+ designate Institution)
> Academic Levels > Configure AU for Level (admit/offer courses/offer programs/recruit flags per
level) > Academic Period Types > Academic Calendar > Initial/Next Academic Year > Period Date
Controls > Calendar Policy > Programs of Study (+ credentials, program areas). 13 academic policies
(Calendar, Academic/Class Standing, Load Status, Enrollment Access and Grading, Course Unit Type/
Repeat/Attempt Limit, Federal Student Aid Program, SAP, COA Reaction, Payment Plan, Transfer Grade
Mapping) attach to AU/AL and inherit downward. AU Hierarchies are a SEPARATE rollup object - they
do not replace the parent-subordinate structure.

**Periods:** standard academic periods must be contiguous and non-overlapping; nonstandard
(intersessions) may overlap. Every calendar needs at least one standard period. All periods in an
award year must share the same academic year type.

**NO catalog year.** Workday Student uses pure effective dating. Academic requirements attach at
the program-of-study DECLARE date (not enrollment date) and are versioned by effective date.

**Registration bypasses the BP framework.** Registration activities complete instantaneously -
there is no BP to hook. Hard cap: 3,000 students per 15-minute registration appointment window.
Registrations ALWAYS roll up to financial aid period records by course-section START date.
Financial aid load status for past periods never updates retroactively.

**Nightly orchestration - FIXED 18-job order** (cannot be reordered; default start 1:00 AM
tenant-local - **(!) reconcile: wd-discovery functional-student.md says the SCHEDULE is
tenant-configurable and counts 11 steps vs the 18 jobs below; verify count + schedule mutability
against the current Student admin guide before citing either to a client - do not assert "start
time fixed" until confirmed**). The sequence is a design constraint - anything you build that
depends on a job's output must run AFTER it in the chain:

1. FA Date Based Processing
2. Update Completed Activity Registration Records
3. Process Academic Progress
4. Refresh Attendance Plan
5. Return of Title IV Evaluation
6. Assign Student Charges *(schedulable)*
7. ISIR Progression
8. ISIR Action Item Evaluation
9. Refresh SFPR
10. Assign Cost of Attendance *(schedulable)*
11. Merit Packaging *(schedulable)*
12. Need Packaging *(schedulable)*
13. Packaging Communications *(schedulable)*
14. Recalculate Sponsor Contracts
15. Disburse Payments *(schedulable)*
16. Recalculate Payment Plan Installments *(schedulable)*
17. Holds / Soft Drop / Aging Group Removal
18. Charges and Installments Aging

Only the 7 marked *(schedulable)* can be run on your own schedule; the other 11 run on Workday's
terms as part of the nightly chain.

**ISIR:** one active ISIR transaction per student per primary POS - hard rule. Configure ISIR
Progression Policy sets the activation trigger (admitted/confidential, admitted/public, or
matriculated); award-year-specific, defaults to the prior year's policy. Matching: SAR ID primary,
SSN + Name ID secondary, plus transaction number + federal school code.

**Federal school code chain:** OPEID > AU/AL combination > COD Routing ID > campus locations
(Create OPEID, Maintain COD Routing ID Policy, Maintain Federal School Code Policy).

**Money rules:** sponsor contracts have HIGHER payment precedence than student award items (nightly
recalc is opt-in via Maintain Institutional Student Financial Options). One award package per
student per award period; award item effective dates must align to award-year start (07/01).
Precedence groups are configured ONCE per institution. Refund payments are cancelable only within
48 HOURS of settlement completion - after that they must be RETURNED. Worktag limits: max 15 custom
worktag types per tenant; max 10 custom organizations as financial worktags.

**Fast Path admissions is all-or-nothing:** auto-admit fires only if ALL programs on the
application are Fast Path-enabled; one non-enabled program reverts the whole application to
selective evaluation.

**Calc engine (FA + SF share it):** Logic calculations CANNOT mix AND and OR in one calc; lookup
tables max 10 columns; a business object supports up to 100 custom fields; rounding percentages
only in half-percent (0.05%) increments. Performance: most-common condition first (Conditional/OR),
least-common first (AND).

**Deceased Student Event automation (6 actions):** Apply Student Hold, Set Student to Private,
Discontinue Academic Records, Withdraw Student Applications, Write Off Student Charges, Disable
Workday Account - plus a National Student Clearinghouse enrollment update.

**Key BPs.** Registration is the notable EXCEPTION - it bypasses the BP framework entirely
(instantaneous, no step to hook). Everything else routes through BPs worth knowing at design time:
**Admissions Application Event** and admission-decision BPs (recruiting/admissions), **Student Record
change** + **Academic Progress / Award** events (records/advising), the **Financial Aid Award** and
disbursement BPs (aid), and **Student Charge / Payment / Refund** BPs (student financials). The
**Deceased Student Event** above is the highest-impact multi-action BP. Because registration has no
BP, an Extend/O4I solution that needs a registration-time hook must poll or run on the nightly chain,
not subscribe to a BP event.

## 2. Technical surface (from the in-tenant WWS master inventory)

Ten SOAP services cover the suite. TWO are INVISIBLE to name-probe discovery and appear only in the
in-tenant WWS report: **Student Core** and **Student Transfer Credit** - a name-probe inventory
will miss them entirely.

| Service | Ops | What it covers |
|---|---|---|
| Student Records | 150 | Curriculum (Submit Course Section, Put Publish Course Section, meeting patterns), registration (Import Student Course Registrations, Put Student Course Registered/Dropped Registration), grades (Submit Grades for Registrations, Import Student Grade Updates), lifecycle (Import Student Matriculations / Withdrawals / Leave of Absences / Dismissal Events / Suspensions), POS (Submit Add/Change/Remove Program of Study, Submit Program Completion), transcripts (Put Transcript Order, Get Completed PDF Transcript Orders) |
| Academic Foundation | 85 | Shared spine: Get Students, Put Program of Study, Import Education Test Results, Import Student Personal Information / Student IDs, Put Student Hold Assignment/Reason, educational institutions + grading schemes, residency, immigration, veterans |
| Financial Aid | 77 | The federal chain: Import ISIR Transaction, Import COD MPN / Counseling / Origination Status / Disbursement Status / IBT, Import NSLDS Transactions, Import School Account Statement (SAS) File, Import External Awards, Import CSS Profile, Import Legacy Financial Aid Packages (conversion), Put Student Award Item, Put/Get Student Loan Applications, Get ISIR Transactions |
| Student Finance | 75 | Charges/payments/waivers/deposits/sponsors, 1098-T (Get/Import 1098-T + Legacy Data), Get Student Account Summary, Import Student Historical Transactions (conversion) |
| Student Core | 55 | NAME-PROBE INVISIBLE. Person-adjacent: Submit Student Hold, Submit Deceased Student, Submit Student Residency, student documents (Add/Edit/Delete), immigration, privacy preferences, friends/family (FERPA proxies), accommodations, appointments |
| Admissions | 50 | Import Student Applications (Common App shape), Import External Student Transcripts (SPEEDE), Import Student Application Admission Decision, Submit Student Application Withdrawal, application GPAs, evaluation views |
| Academic Advising | 42 | Academic requirements + overrides (Submit Academic Requirement Override), cohorts (Import Student Cohort Memberships), transfer credit rules, Get Academic Progress for Student |
| Student Recruiting | 41 | Prospects/recruitments (Import Student Recruitments - Submit Student Prospect is DEPRECATED), campaigns, events + registration/attendance records, recruiting regions |
| Campus Engagement | 19 | Engagement plans, student audiences, student notes, Complete Action Item Event |
| Student Transfer Credit | 8 | NAME-PROBE INVISIBLE. Preliminary + assigned transfer credit (Put/Delete/Bulk Import) |

**The Submit/Import twin rule (Student Finance):** every Student Financials transaction has a SOAP
twin of its UI task - a Submit_* (single, fires the BP) and an Import_* (bulk background, no BP):
Submit/Import Student Charge (current form: Submit Charge for Student / Import Charges for
Students), Student Payment, Student Waiver Payment, Student Deposit, Acceptance/Application Fee
Payment, Student Credit Memos, Student Sponsor Payment, Pending Student Sponsor Refund. This is the
primary SIS-coexistence surface; ISU needs Get/Put domain grants.

**Other paths:** RaaS on web-service-enabled custom reports (key data sources: Student
Applications RDS + Student Application Originals RDS for unsubmitted apps, Academic Records, FAPR,
SFPR, Student Charges/Payments/Awards). Transcripts render via BIRT (unofficial layouts authored in
Studio's BIRT designer; official via delivered business form layout). Packaged integrations:
Common App inbound template, SPEEDE transcripts, test scores (ACT, AP, GMAT, GRE, PERT, SAT,
TOEFL), ISIR File Inbound + ISIR Correction Outbound, COD inbound/outbound, TSM and FAH NSLDS
templates, 1098-T Outbound direct to IRS FIRE (Workday-managed), National Student Clearinghouse.

## 3. Solution patterns + donors

- **SIS-coexistence inbound (config-surface exemplar): INT165 pattern** - SIS work-study Studio
  inbound; the campus variant externalizes config into 26 launch params + 65 integration attributes.
  The model for per-campus behavior WITHOUT code forks.
- **Legacy FA feed: INT041 pattern** - Banner financial-aid / federal work-study award inbound
  built on Import_* web services (18 XSLT maps + value translation). Base donor for any
  Banner/Colleague-era aid or employment feed.
- **Conversion streaming/merge: STUDC* family** - STUDC009 education-test-results streaming and
  STUDC005 student-course-registrations streaming (with Convert_Student_Import_Template_Streaming
  as the template shell), plus the MergeStudentData v1-v5 evolution and transcript-aggregation
  merge stage. Pattern: stream huge conversion files, merge per-student fragments, then bulk
  Import_*. (MergeStudentData/transcript-aggregation donors are corpus-cited; not present in the
  80-item O4I candidate inventory - locate in the raw Studio export before reuse.)
- **Boomerang: INT051b pattern** - bookstore-credit boomerang: read registrations/charges out,
  compute an external credit, post back via Submit Student Payment. Same shape fits any
  auxiliary-services credit (dining, housing, library fines).
- **Account/SSO: INT024 pattern** - login accounts SSO Active Directory inbound; pairs with
  admissions "Create External Account for Student Applications" service step + Maintain Delay
  Student External Account Creation Policy.
- **External-student + temp-data: INT022 pattern** (external student inbound) and **INT228
  pattern** (temporary SSN inbound) - the Colleague/temporary-financials coexistence family.
- **Admissions portfolio outbound: INT222 pattern** - application-attributes update to an external
  review platform (Slideroom-class).
- **Analytics: Prism** - student Prism donor exists (MV_INT_Stu_Prism); Prism is the sanctioned
  path for blended retention/enrollment analytics rather than heavy custom reports.
- **Extend apps:** student-facing self-service gaps (case management, forms) work on the same
  Extend patterns as HCM but must respect FERPA segmentation - see wd-extend-dev
  domain-patterns-hc-highered.md before designing any student-data egress.

## 4. Design gotchas

- **No BP hook on registration.** You cannot add an approval or integration step to the act of
  registering - react via nightly jobs, date controls, holds, or the mass-drop BPs instead.
- **Section START date drives aid rolldown.** A late-starting section lands in a different FA
  period record than the term it "belongs" to; module/pod scheduling designs must check this.
- **One active ISIR per primary POS** - external aid tools that push ISIR corrections must respect
  progression status (Active/Inactive/Pending Review/Ready to Transmit/Transmitted).
- **Fast Path is all-or-nothing** per application; mixed-program applications silently go selective.
- **Declare date, not enroll date,** anchors academic requirements; conversion must set POS declare
  dates deliberately or degree audits evaluate against the wrong requirement version.
- **Submit vs Import:** Submit fires the BP (approvals, notifications); Import is background bulk
  and skips routing. Pick per volume AND per governance need (rule shared with wd-integration-dev).
- **Submit Deceased Student triggers 6 automated actions** incl. charge writeoff and account
  disable - never sync a deceased flag casually from HR/advancement systems.
- **48-hour refund window;** after settlement +48h refunds are returned, not canceled - reconcile
  external refund tools against this.
- **Due date rules do NOT apply** to charge items inside a Workday payment plan; Override Revenue
  Company locks once transactions exist; course fees attach only if defined BEFORE sections are
  created; charge item and course must share an AU (or superior).
- **SFPRs are not created for applicants** - applicants lack charges, anticipated aid, sponsor
  contracts, and COD outbound; pre-matriculation designs cannot assume the financials spine.
- **FERPA surface:** directory-information config, segment-based security (notes, holds, docs,
  questionnaires), third-party proxies capped at 7 tasks. Any custom read of student data needs the
  privacy-preference check designed in, not bolted on.
- **Calc-engine ceilings** (no AND/OR mix, 10-col lookups, 100 custom fields/BO) push complex aid
  logic to pre-computation outside Workday sooner than clients expect.
- **Comms limits:** SMS US/Canada only; push notifications unavailable for Recruiting/Admissions;
  rich text is STRIPPED in Student questionnaires; max 5 recommenders; 70 merge fields.
- **Verification assignments reset daily at midnight** tenant-local; unreconciled duplicates HALT
  admissions processing - build duplicate reconciliation into any application-load design.
- **Purge is irreversible** (Purge report tag); historical-student documents tied to an active
  student cannot be purged.
- **Inventory blind spot:** Student Core and Student Transfer Credit do not answer a WSDL
  name-probe - refresh the surface from the in-tenant WWS report, not from public probing.
