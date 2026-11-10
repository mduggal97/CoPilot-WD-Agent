# Talent/Performance + Learning - solution playbook

Two adjacent domains that share the worker profile: Talent/Performance (goals, reviews,
competencies, feedback, calibration, succession, skills) and Learning (catalog, courses,
enrollments, campaigns, certifications). Config facts below are doc-sourced - Workday
Education manuals, 2026-08-25; verify in-tenant. Web-service names are from the in-tenant
WWS master inventory.

## 1. Configuration spine

### Talent/Performance setup order

1. Rating scales - Workday delivers NONE; the client builds them. A scale can be
   inactivated but never deleted, and must be applicable to all templates in a review
   category. Recommended: ONE scale per template (multiple scales normalize badly).
2. Competency framework - categories -> classes -> competencies -> proficiency rating
   scales -> job family / management level associations -> competency precedence.
   A competency can only attach to a class if the class maps to a category.
3. Goals setup - categories, units, payout bands, periods, completion statuses, goal
   templates + template rules. Goals cascade to employees, talent pools, or orgs.
4. Employee review templates - 4 review categories (Performance Review, Individual
   Development Plan, Disciplinary Action, Performance Improvement Plan); review types;
   sections; employee review rules ("Applies To" population - blank = everyone).
5. Feedback - badges -> Maintain Feedback Setup -> question tags -> question library ->
   feedback templates (Get Feedback on Self / on Worker / Performance Review / Anytime).
6. Calibration - nBox report -> calibration program -> BP wiring (Launch Calibration
   needs the Calibration Participation Details step + Shared Participation step type).
7. Worker talent data - skills (Skills Cloud), education, certifications, career
   interests; talent pools; succession plans; talent review templates + rules.

### Talent hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- Review template cap: up to 14 sections per template; each section usable ONCE; no
  section is required. Ratable sections limited to Accomplishments, Competencies,
  Goals, Questions, Responsibilities. Fields in a section can be relabeled, never
  reconfigured. Once a template is assigned to a review type, the type cannot be deleted.
- Goal carryover vs consolidate status filters: Carryover requires dates and only moves
  goals in Not Started / In Progress status; Consolidate moves NS / IP / Complete and the
  source reviews' dates must fall inside the current review's dates. Load Relevant Goals
  skips goals whose completion status maps to Not-Applicable.
- Reviews run against the PRIMARY job only. One in-progress review per template
  section-set + date range per employee.
- Calibration is hierarchical-submission: every lower-level org must submit before the
  higher-level manager can; the controller finalizes last. nBox data refreshes via a
  periodic background process (data source: Indexed In Progress Worker Calibration
  Placements) - it is NOT real time. Calibrated ratings are excluded from printouts.
- Skills Cloud is an ISA gate AND irreversible: requires an Innovation Services Agreement
  or Universal Main Subscription Agreement, and once enabled it cannot be disabled.
  Mass Populate Worker Profile Skills cannot be undone. Talent Marketplace, Career Hub,
  and Manager Insights Hub all stack additional agreements on top of Skills Cloud.
- Deleting an in-use skill or school from setup converts it to a "custom" entry on
  worker profiles; Workday never re-adds custom items to the setup table.
- Pay for Performance uses only the MANAGER's overall rating and requires review dates
  inside the compensation period (this is the talent->comp handshake; see the
  compensation playbook).

### Learning setup order

1. Learning catalog(s) -> topics (required for all content) -> courses (digital or
   blended) -> course offerings (required for instructor-led / training-activity
   lessons) -> programs. Standalone lessons live outside courses.
2. Instructors/assessors (internal + external), locations, virtual classrooms.
3. Content rules - prerequisites, equivalencies, certifications, expiration (Date /
   Duration / Recurrence / Advanced per learner group), retrain windows.
4. Security - learning security segments and categories; enrollment BPs.
5. Enrollment machinery - Enroll in Content / Drop Learning Enrollment BPs, waitlists,
   campaigns + audiences, mass enroll variants.

### Learning hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- Content is never deletable, only inactivated; blended-course effective dates cannot be
  edited after creation; digital courses have NO versioning - edits apply immediately.
- Segment lockout trap: once ONE topic is segmented, access to all other topics stops
  until a second segment exists. A segment applies to a catalog OR a topic, never both;
  topic segments override catalog segments; a course/program security category overrides
  both.
- Teams/Zoom virtual classrooms each require an ISU: Teams needs an ISU + Integration
  System security group (Client ID / Secret / Tenant / Mailbox); Zoom needs a
  server-to-server OAuth app in Zoom plus an ISU.
- Surveys cannot be loaded via web service and cannot be used as assessments.
- External content marks Completed on first click (no progress tracking); Cloud Connect
  imported content needs an extra Cloud Connect subscription to track.
- Campaign audiences: up to 100,000 workers; dynamic talent pools return NO audience
  (static only); campaign content is invisible on My Transcript until the learner
  enrolls/starts.
- Completion is one-way: cannot amend results once status = Completed; instructor-led
  completion goes through Manage Grading and Attendance, not Manage Enrollment Completion.
- SCORM 1.2 / SCORM 2004 / AICC 2.x only; packaged content is incompatible with
  standalone lessons; SCORM load requires domain Put access. Learning cannot deploy
  before HCM.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Talent** - 124 operations. Worker-profile writes (Manage Skills / Certifications /
  Education / Work Experience / Competencies), setup Puts (Put Skill, Put Competency,
  Put Talent Pool, Put Succession Strategy), succession (Get/Manage Succession Plans and
  Pools), calibration (Get Calibration Programs/Values, Import Calibration Values,
  Put Calibration Program), development items, mentorships, Give Feedback, Assess Talent.
- **Performance Management** - 47 operations. Start Performance Review, Get Employee
  Reviews / Review Templates, Update Employee Review Rating + Bulk Import Update Employee
  Review Rating (the manuals' "EIB loads review ratings" path), Import/Load Employee
  Reviews (historical conversion), Manage Goals, Put Organization Goal, Get Rating Scales,
  Check-Ins (Get/Put Check-In and Check-In Topics), feedback questions/badges.
- **Learning** - 111 operations. Put Learning Enrollment (carries the Manual Expiration
  Override flag), Enroll In Learning Content / Enroll in Assigned Content, Cancel Learning
  Enrollment, Waive Learning Assignment, Import Learning Enrollment (bulk), Manage
  Learning Course / Program / Lesson / Course Offering, Put Learning Course Offering,
  content rules (Get Learning Certification Rules, Manage Learning Prerequisite /
  Equivalency Rule), Extended Enterprise learner ops, Get Virtual Classroom Attendance
  Records, Put Learning Topic / Catalog / Security Segment.

Other read/write paths:

- WQL/RaaS: learning data sources named in the manuals - Learning Enrollments and
  Learning Assignments Records, Learning Enrollment Event, Learning Course Offering
  Management Event, Learning Equivalency Record, Media Tracking. Talent: nBox uses
  Indexed In Progress Worker Calibration Placements; "Has On-Hold Compensation Review
  Event due to Leave" is a Worker report field.
- Extend BO references: LEARNING_CONTENT and LEARNING_ENROLLMENT are build-verified
  SINGLE_INSTANCE targets on Extend business objects, and page WQL can project nested
  related objects off a learning enrollment (per wd-extend-dev model.md and pmd.md) -
  this is what makes native enrollment-tracking Extend apps possible.
- Delivered connectors: Cloud Connect for Workday Learning (e.g. LinkedIn Learning
  content import); SAML SSO links for external content. Skills Cloud / ML sliders are
  platform services, not integrations you build.
- EIB shapes: review-rating loads (Bulk Import Update Employee Review Rating),
  historical review conversion (Load Employee Reviews), bulk enrollments (Import
  Learning Enrollment).
- BP hooks: Start Performance Review, Manage Goals, Get/Give Feedback BPs, Enroll in
  Content, Drop Learning Enrollment, Manage Course Offering (supports an Integration-type
  step - the documented Zoom hook), Mass Enroll, Campaign Event.

## 3. Solution patterns + donors

- **Enrollment-tracking / compliance-training Extend app** - Extend BO with
  LEARNING_CONTENT + LEARNING_ENROLLMENT single-instance fields, page WQL joins the
  learner, orchestration enrolls via Enroll In Learning Content or Put Learning
  Enrollment. Donor: the learningEnrollments O4I sample (boomerang: fetch workers meeting
  a condition -> enroll in a course) in the wd-extend-dev app-catalog registry.
- **Multi-rater / custom review step inside the native review BP** - donor: multiRater
  (custom BP embedded in a NATIVE BP via allowedParentProcesses, 8 Performance_Management
  SOAP flows). The pattern for anything the delivered review framework cannot host.
- **Mass launch of talent events** - donor: crisisCheckin (Model BP mass launch via
  async fan-out) for check-in / attestation / survey-style talent touchpoints.
- **Skills and sentiment AI** - donors: skillsMiningWithTheAIGateway (skills-cloud
  extract from free text), sentimentAnalysisWithTheAIGateway, and
  employeeRecognitionWithTheAIGateway (aggregate feedback -> batch sentiment); the
  non-AI employeeRecognition twin shows worker search + home cards.
- **Review-rating conversion / bulk load** - EIB or Studio against Bulk Import Update
  Employee Review Rating / Load Employee Reviews; route via wd-integration-dev.
- **Campaign-plus-audience automation** - custom report audience + Create Scheduled
  Distribution beats building an Extend scheduler; only go custom when the 100K audience
  cap or dynamic-pool gap bites.

## 4. Design gotchas

- Anything "skills-based" you design gates on Skills Cloud + an ISA the client may not
  have signed - surface it at estimate time; enabling is irreversible.
- Do not design goal-edit automations that touch goals attached to reviews - they cannot
  be deleted, and in-progress-review goals cannot be archived.
- Calibration writes ratings on a delay (background nBox refresh + hierarchical
  submission) - a dashboard reading review ratings mid-cycle will show pre-calibration
  values.
- Learning "completion" is not a safe external trigger for external content (Completed
  on first access) - use packaged content or graded activities when a downstream system
  pays or certifies on completion.
- A learning app that creates offerings must respect segmented security: writes via
  Put Learning Course Offering land in whatever catalog/topic segment applies, and the
  segment lockout trap can hide content from the very population you built for.
- Surveys have no web-service load path - if a solution needs programmatic
  question/response data, model it as an Extend BO form, not a Workday Learning survey.
- Multi-Rater (Get Additional Reviewers) exists only inside performance reviews and
  development plans and cannot run standalone - external 360 tools integrate via
  Performance Management WWS instead.
