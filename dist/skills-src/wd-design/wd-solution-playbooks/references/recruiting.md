# Recruiting (ATS): requisitions, candidates, offers, hire handoff - solution playbook

Workday Recruiting is the applicant-tracking layer that sits ON TOP of the HCM
foundation: job requisitions draw on headcount the staffing model governs, and the
whole funnel (prospect -> candidate -> application -> offer -> Ready for Hire) ends by
handing off to a Hire staffing event. Config facts below are doc-sourced (Workday
Recruiting product knowledge, 2026-08-25); verify in-tenant. Web-service names are from
the in-tenant WWS master inventory; the REST surface is build-verified from the suite's
rest-api-catalog.

## 1. Configuration spine

### Setup order

1. HCM foundation FIRST - supervisory orgs, staffing model, job catalog, and (Position
   Management) open positions or (Job Management) hiring restrictions must exist; a
   requisition cannot create headcount the staffing model does not allow. See
   [hcm-core.md](hcm-core.md).
2. Enable Recruiting; recruiting security groups (Recruiter, Hiring Manager, Interviewer,
   Recruiting Coordinator) and candidate-data privacy segmentation.
3. Job requisition setup - requisition types, job posting sites (internal Career + one or
   more External Career sites), job-board brokers (Indeed, LinkedIn RSC), evergreen
   requisitions, and the Create Job Requisition BP.
4. Candidate machinery - prospect stages, candidate pools, duplicate-candidate detection,
   the Job Application BP with its configurable STAGES (e.g. Review -> Screen -> Interview
   -> Reference Check -> Background Check -> Offer -> Ready for Hire) and disposition
   (decline) reasons.
5. Questionnaires (primary + secondary), assessments, and the interview framework
   (interview teams, scheduling, feedback).
6. Offer - offer letter templates (via Dynamic Document Generation / text), the Offer BP,
   and the compensation the offer proposes (flows into the Hire; see the compensation
   playbook).
7. Background check / screening - the delivered screening-partner integration
   (HireRight, Sterling, First Advantage, etc.) wired as an integration step inside the
   Job Application BP.
8. Onboarding handoff - Ready for Hire creates a pre-hire and launches the Hire event
   (HCM foundation governs what completes it).

### Key BPs

Create Job Requisition, Job Application (stage-configurable - the funnel spine), Move
Candidate to Linked Requisition, Interview, Reference Check, Background Check (integration
step), Offer, Ready for Hire (converts candidate -> pre-hire -> Hire), Create Prospect /
Convert Prospect to Candidate, Edit Job Requisition, Close/Freeze Job Requisition.

### Hard limits and landmines (doc-sourced - Workday Recruiting product knowledge, 2026-08-25; verify in-tenant)

- **Requisition needs headcount the staffing model owns**: Position Management requires an
  open/unfilled position; Job Management requires hiring-restriction headcount. Recruiting
  cannot conjure a position - the HCM foundation gates it (hcm-core.md staffing-model
  landmines apply unchanged).
- **A candidate is NOT a worker**: the candidate record is a distinct object. Only at
  Ready for Hire does Workday create a pre-hire, and only the completed Hire event makes a
  worker. Integrations keying on Worker/Employee ID find nothing until that conversion.
- Job Application BP stages/disposition reasons are configured per requisition type;
  declining a candidate requires a disposition reason. Stage configuration is where most
  client-specific complexity lives.
- Evergreen requisitions do not fill/close like standard reqs - they stay open and spawn
  linked hires; automation that "closes the req on hire" breaks on them.
- Candidate data is privacy-sensitive: candidate home-country data-privacy rules, GDPR
  purge/retention, and external-career-site data all apply. A report or extract can leak
  candidates a purge has already removed.
- Offer compensation flows INTO the Hire - do not double-write comp downstream; let Ready
  for Hire -> Hire carry it.
- "Enforce Required in Web Services" (tenant validation setting) governs whether
  red-asterisk required fields apply to web-service submissions - a candidate/requisition
  load that works in one tenant can reject in another on this checkbox alone (same trap as
  hcm-core.md).

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Recruiting** - the ATS event/read surface (present in the WWS master inventory;
  confirm the operation count against the current inventory extract). Named ops:
  Get/Put Candidate, Import Candidate, Get Job Requisitions / Put Job Requisition,
  Get Job Postings / Put Job Posting, Get/Put Prospect, Move Candidate, Get Job
  Applications, and screening/assessment result inbound ops. Reads back candidate,
  requisition, posting, and application data for extracts.
- **Staffing** and **Human Resources** carry the HIRE conversion - Ready for Hire launches
  a Hire event, which runs through the Staffing service (Hire Employee) exactly as
  hcm-core.md describes. Design the handoff around that event, not a naked candidate Put.

REST / WQL / RaaS:

- REST: **recruiting v4** (31 ops - interviews, jobPostings, prospects) is build-verified
  in the suite's rest-api-catalog (wd-extend-dev rest-api-catalog.md). Good for read-heavy
  candidate/posting/interview surfaces and micro-writes without SOAP.
- WQL / RaaS: candidate, job-requisition, job-application, and job-posting data sources
  back reporting and outbound extracts; RaaS custom reports remain the outbound workhorse
  (~2083-char URL guard - wd-extend-dev orchestration.md). Confirm exact data-source names
  in-tenant.

Delivered connectors and hooks:

- **Core Connector: Candidate (Outbound)** (candidate data out; delivered, confirm exact
  abbreviation in-tenant - integration-naming.md lists CCJR/CCJP/CCJPJF but no candidate CC
  abbrev), **CC: Job Requisitions (CCJR)**, **CC: Job Postings (CCJP)**, **CC: Job Profile
  and Job Family (CCJPJF)** - the delivered outbound catalog for recruiting
  master/transaction data (integration naming per wd-integration-dev
  integration-naming.md). Check these BEFORE designing a custom outbound.
- Delivered screening / job-board partner integrations (background-check vendors, Indeed,
  LinkedIn RSC) plug into the Job Application BP as integration steps - almost always the
  right answer over a hand-built vendor call.
- BP hooks: Job Application BP integration/service steps (background check, assessment),
  Offer BP, and Ready for Hire (which triggers the Hire staffing event and its
  Extend BP-triggered orchestrations - hcm-core.md).

## 3. Solution patterns + donors

- **Inbound ATS feed / candidate load** - external ATS -> O4I or EIB -> Import Candidate /
  Put Candidate. No build-verified recruiting-specific donor is on disk; reuse the generic
  O4I import-framework shape (submit -> poll -> Get Import Process Messages) whose
  build-verified donor is `supplierInvoicesInbound` (same framework, different payload -
  hcm-core.md, wd-extend-dev app-catalog registry). Delivered CC: Candidate Outbound covers
  the reverse direction (delivered-Workday reference - a pattern, not liftable firm IP).
- **Requisition / offer companion Extend app** - an Extend BO intake (custom requisition
  request or offer-approval form with its own BP) that then initiates Create Job
  Requisition / Offer via SOAP. Reuse the hcm-core.md "custom work-event app with its own
  BP" shape - build-verified donor `createAWorkEvent` (custom .businessprocess + wizard +
  hub); production-shaped sibling `workFromAlmostAnywhere`. No recruiting-specific
  build-verified donor exists; the pattern transfers directly.
- **Background-check / assessment trigger** - prefer the delivered screening-partner
  integration wired as a Job Application BP step. Only go custom when the partner is not
  supported, and then egress via O4I `SendHttpRequest` (external-API path - wd-extend-dev
  external-apis-and-genai.md / orchestration.md egress constraints), which moves candidate PII
  off-platform and needs data-governance review (wd-extend-lifecycle ai-data-governance.md).
- **Candidate -> hire handoff automation** - orchestrate Ready for Hire; the hire itself is
  an HCM staffing event, so sequence it with the hcm-core.md staffing-event chain (donor:
  `addAdditionalJob` catalog app - Create_Position -> staffing SOAP chain; order matters in
  Position Management).
- **Outbound candidate / requisition extract** - delivered CC: Candidate / CCJR first;
  custom shape mirrors the hcm-core.md O4I donor `employeeDemographicOutbound`
  (RaaS -> CsvFormat, sequenced filename).

## 4. Design gotchas

- Recruiting sits ON TOP of HCM foundation - ask the staffing model FIRST (hcm-core.md): a
  requisition needs headcount the model governs, and you cannot design a "create req" app
  that invents positions.
- Candidate is not a Worker - design the handoff around the Ready-for-Hire conversion
  event, not a Put Worker; anything keying on worker ID finds candidates only after the
  Hire completes.
- Background check is a BP integration STEP, not a free-standing API call - the delivered
  screening framework is almost always correct; a custom `SendHttpRequest` to a background
  vendor is a data-governance decision (candidate PII off-platform), not just a build
  choice.
- Candidate data privacy/purge is real: designing on candidate data means honoring
  retention/GDPR purge rules; extracts and reports can surface candidates a purge already
  removed.
- Offer comp flows into the Hire - do not double-write compensation downstream; let Ready
  for Hire -> Hire carry it (compensation playbook for the comp mechanics).
- Verify the tenant actually HOLDS recruiting data before designing on it (a bare dev
  tenant will not) - trust-but-verify (wd-extend-lifecycle/references/verify-in-tenant.md).
- Functional literacy (what a requisition / candidate / prospect IS, the ATS funnel
  vocabulary) lives in wd-discovery functional-hcm-talent-rewards.md (Recruiting section) -
  this playbook assumes it.
