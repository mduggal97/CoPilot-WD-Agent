# Roles, counterparts, and the workstream RACI recipe

> Vendor-neutral. This is the standard role model of a Workday deployment and the recipe
> for turning it into a per-workstream RACI. When a real plan or staffing model is built,
> this feeds wd-pm (plan/RACI) and wd-estimate (hours by role and phase).

## The delivery-side role model

Every role owns deliverables PER PHASE - when writing a role description, organize it by
the phase model (phase-model.md) and state expectations, deliverables, and the norms the
role keeps (tracker hygiene, meeting notes, KT contribution).

- **Engagement / program manager** - owns the commercial relationship, forecast,
  escalation path, and delivery quality across workstreams; commissions the independent
  phase-exit quality reviews (reviewer from outside the workstream under review - see
  the QA thread in phase-model.md).
- **Project manager** - runs the plan, RAID, status cadence, and decision log day to day
  (wd-pm owns the artifacts).
- **Solution architect (functional)** - cross-area design authority; owns design
  coherence where modules meet: one FDM (Foundation Data Model - the shared set of
  organizational and accounting dimensions/worktags that drives routing, security, and
  reporting across every module), one security philosophy, one consistent style for BPs
  (business processes - Workday's configurable workflow definitions).
- **Technical architect** - cross-area authority for integrations, conversions,
  reporting, and Extend; owns the technical sub-track's architecture reviews.
- **Functional workstream leads** - one per area (HCM, Payroll, Financials, Student,
  etc.); own that area's design decisions, configuration, and confirmation sessions.
- **Technical workstream leads** - integrations lead, data-conversion lead, reporting
  lead; own build inventories, conversion-pass schedules, cutover sequencing for their
  objects, and defect triage in their lane.
- **Security lead** - owns the security workstream end to end: security strategy and
  role inventory in Plan, role-to-domain design in Architect & Configure (a domain is a
  Workday security object - a named bundle of securable tasks and data that roles are
  granted access to; design mechanics in wd-deployment security-role-design), security
  testing in Test, and cutover access changes in Deploy.
- **Change management lead** - impacts, readiness, comms and training plans
  (wd-change-adoption); impacts logged in the SAME RAID/tracker as everything else.
- **Consultants (functional/technical)** - execute deliverables, facilitate design
  sessions, load conversions, keep the tracker current.
- **Testing lead** - test strategy, event planning, entrance/exit criteria, defect
  process (wd-testing).
- **SMEs** - deep specialists on call (tax, benefits, financial aid, grants...); scoped
  by the workstream leads.

## The client counterpart model

The client mirrors the delivery team with counterparts - and this is where programs
succeed or stall:

- **Name a counterpart per workstream** (module leads, integration lead, data-conversion
  lead, testing lead, security admin) plus an executive sponsor and a client-side PM.
- **Counterparts have day jobs.** Agree their time commitment per phase up front, put it
  in the charter, and manage it like any other program dependency. A counterpart who
  cannot attend design sessions is a RAID risk, not a scheduling nuisance.
- **Write job descriptions for client project roles** when advising staffing: purpose,
  phase-by-phase time commitment, decisions they own, skills needed. Do this at Plan, not
  when the gap bites in Test.
- **Design for ownership transfer**: by the Test phase, counterparts should be able to
  explain their area's design to their own organization (wd-kt owns the enablement path;
  wd-extend-lifecycle customer-technical-roles.md owns the technical-counterpart access
  plan).

## The workstream RACI recipe

Build a RACI per WORKSTREAM - security, data conversion, integrations, reporting (or
fold reporting into the technical workstream), each functional area, change management,
testing - not one giant program grid nobody reads.

**Shape:** rows = STAGE + TASK (use the phase model's stages); columns = the roles above
plus the client counterparts; cells = **A** (Accountable - exactly one per row, a named
person) / **R** (Responsible) / **C** (Consulted) / **I** (Informed) / n/a; final column =
free-text comments for decisions and caveats.

**Rules that keep a RACI honest:**

- One named Accountable per task - "the team" is not an owner.
- If a row has no client-side letter, ask why - a program the client only watches is a
  program the client will not run after go-live.
- Estimate effort per role per phase alongside the RACI (hours/week x weeks) so the RACI
  and the staffing plan (wd-estimate) cannot drift apart.
- Revisit at every phase transition - roles shift weight (security is light in Initiate,
  heavy in Plan and Test).

**Worked pattern - a security-workstream RACI** (use the same shape for any area):
rows like "Plan / define security role inventory", "Plan / run security discovery
sessions", "Architect & Configure / build role-to-domain mapping in the build tenant",
"Test / execute positive and negative security tests", "Deploy / cutover access changes
and revoke implementation access"; columns = security lead, technical architect,
workstream leads, client security admin, client PM; each row one named A, comments carry
the decisions.
