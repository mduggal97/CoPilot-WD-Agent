# Practitioner enablement - onboarding, competency, certification

Getting a consultant productive and keeping their capability current. Vendor-neutral.

## Onboarding a new consultant

Ramp in three layers, fastest-payback first:
1. **The suite** - install the skills (README "Install" section: drop into `~/.claude/skills/`), then start at
   **wd-extend-lifecycle** for the lifecycle map + guided walkthrough, and read the phase skills for their role
   (a builder: wd-extend-dev / wd-integration-dev + wd-testing; a functional/PM lead: wd-discovery /
   wd-design-doc / wd-pm / wd-change-adoption). The suite is the single fastest way to make someone useful.
2. **The method** - how the practice delivers end to end (the delivery lifecycle + the quality-gate discipline).
3. **The environment** - tenant access, Workday Community account, and the tool setup
   (wd-extend-lifecycle `prerequisites.md`); pair this with the customer-technical-roles staged-access idea so
   they learn in a real (dev) tenant early.

Ramp mechanism: shadow one live engagement, then own a scoped piece with a reviewer, before running solo.
A short "first 30/60/90 days" checklist per role keeps ramp consistent instead of ad hoc.

## Competency model (skills matrix)

Define what each role should be able to do, and place each person against it:
- **Roles:** Extend developer, integration developer, functional/solution lead, PM/engagement lead (extend as
  the practice grows: Prism/reporting, security, change/adoption).
- **Dimensions per role:** the capabilities that matter (e.g. for an Extend dev: PMD/pages, orchestration/O4I,
  business-object modeling, security setup, wdcli/deploy, testing; for an integration dev: EIB, Studio/CLAR,
  Core Connector/DT, XSLT, migration). Mirror the wd-* skill boundaries so the matrix maps to real work.
- **Levels:** e.g. aware -> supervised -> independent -> can-lead/mentor. Keep it simple and honest.
- **Use it to** target enablement (close the gaps that block staffing), plan pairing (independent mentors
  supervised), and feed staffing (staffing-and-alliance.md reads this).

## Certification tracking

Track Workday certifications as a capability inventory that gates staffing and expires:
- **Which:** Workday Extend Pro, Integrations Pro, and the functional Pro certifications relevant to the
  practice's SKUs (HCM/Financials/Student/etc.).
- **Per person:** cert held, date earned, **recert due date**, and any prerequisite/eligibility. Recerts lapse
  quietly - a lapsed cert can affect partner status and eligibility to staff, so track the due dates like
  project milestones.
- **Prep:** point people at the official Workday learning paths; where the practice maintains its own recert
  study material, keep it current to the exam blueprint.

## Knowledge-sharing loop (close the loops)

Enablement is continuous, not a one-time onboarding:
- **Lessons learned** from each engagement roll into project memory and the practice's shared knowledge.
- **Reusable assets** harvested at closeout go into the reuse catalog (reuse-and-asset-catalog.md) so the
  next person inherits them.
- **Estimation actuals** feed wd-estimate calibration so quotes stay honest.
- Regular internal shares (new release capabilities, a solved gnarly problem, a new pattern) keep the whole
  team's competency rising, not just the person who did the work.

## Where this goes

Competency matrix + cert status -> staffing decisions (staffing-and-alliance.md) and enablement plans. Ramp
checklists -> per-role onboarding. Lessons/assets -> memory + reuse catalog + calibration.
