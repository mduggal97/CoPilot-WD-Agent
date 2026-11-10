# Specialty tracks - the workstreams that ride alongside a core deployment

> Vendor-neutral. Each track below is a recognized shape of Workday-adjacent delivery
> work. This file gives the generic scoping/methodology shape per track; commercials go
> through wd-estimate / wd-contracts, productized go-to-market through
> bow-sales-enablement (the suite's Marketplace / Built-on-Workday go-to-market skill -
> part of this shareable suite despite the non-wd name prefix).

## Adaptive Planning

The FP&A layer downstream of Workday Financials/HCM: actuals flow in, plans and
forecasts flow out. Deliver it as its OWN workstream on a program (own lead, own design
sessions, own testing), not as a Financials appendix. Scope covers: planning-model
design (structure, dimensions, versions, calc logic per planning use case - workforce,
operating expense, revenue, capital, industry-specific models); integration patterns
(actuals in from Workday, plans published back, external data via extract/load); and
tenant operations (user provisioning, security model, tenant/instance administration).
Model design drives everything - agree the planning use cases and their owners before
touching the tool.

## Prism Analytics

Prism blends Workday data with external/legacy data into governed reporting datasets.
The methodology rule: **scope each reporting use case with a written requirements
document BEFORE any build.** Per use case, pin down:

- the business question and its consumers;
- every data source (Workday objects/reports and external files) with refresh cadence;
- the ingest and transformation flow, at FIELD level for the base data (name, source,
  type, notes);
- derived datasets and calculated fields with their logic;
- the published data source and which reports/dashboards consume it;
- security: who may see what, mapped to domains/roles before go-live, not after.

Typical use cases: point-in-time snapshots of Workday data for trend reporting, and
blending legacy-system history with live Workday data for continuous reporting across
the cutover boundary. Build mechanics and platform limits: wd-extend-dev
prism-and-reporting.md; functional literacy: wd-discovery.

## Release management and managed services (post-production offerings)

- **Release management** - Workday ships two feature releases a year; clients without a
  process absorb them badly. The generic package shape: a release-cycle project plan; an
  impact-analysis pass over Workday's release notes filtered to the client's footprint
  (tenant configuration, integrations, security); a new-features adoption shortlist; a
  regression + new-feature test plan (client supplies regression scenarios and a PM);
  and a lessons-learned close. The suite's release-regression workflow lives in
  wd-post-go-live; this track productizes it as a recurring service.
- **Managed services / production support** - ongoing operate-and-improve support,
  typically tiered (incident response, break/fix, minor enhancements, monitoring -
  integration monitoring is a natural add-on). Define severity levels, response targets
  (best-effort, never warranties - see wd-post-go-live), and a monthly service review.
- **Scoped mini-projects** - small fixed-outline engagements on a live tenant (an annual
  compliance cycle, open enrollment support, a new feature rollout, a clean-up). Each
  gets a one-page outline (outcome, activities, inputs, effort band) and standard
  contract paper (wd-contracts).
- **Health check / current-state assessment** - a structured review of a live tenant and
  its operating practices: configuration hygiene, security posture, integration
  inventory, adoption, backlog. Output is a findings-and-roadmap deck; it is also the
  natural entry point for the other post-production offerings.

## Operating-model co-design

A cloud ERP assumes consistent processes and clear role ownership - so Workday design and
the client's OPERATING model must be designed together, not sequentially. The track
covers: service-delivery structure (central shared services vs. distributed, tiered
support from self-service through specialist); how FDM choices (cost-center and
hierarchy design) drive routing, security, and reporting - and therefore org design;
security roles derived from real job responsibilities rather than legacy titles;
business-process ownership (who owns each BP definition and its change control); and the
service-management tooling in front of Workday (ticketing/portal feeding the support
tiers). The delivery rule: operating-model representatives sit IN the configuration
design sessions and validate BPs, roles, reports, and hierarchies before Test - retrofit
operating models fail. Decentralized institutions (higher-ed especially) need this track
most.

## Productized add-on packages

Repeatable rollout kits for a specific process or feature, sold to many clients. The
generic kit structure, whatever the subject: a work plan; announcement/invitation
communications; FAQs and quick-reference aids; role-based job aids for each task in the
process; a readiness/overview deck and workshop agenda for the affected population; and
a test script. Build once, genericize, parameterize per client. Marketplace-grade
packaging and go-to-market: bow-sales-enablement; delivery of the kit on an engagement:
this suite's normal lifecycle.

## Higher-ed / Student delivery notes

Workday Student programs carry extra structure worth naming:

- **The academic calendar is the timeline** - cutover windows are dictated by term
  boundaries and aid cycles, not preference; stabilization runs a full academic cycle,
  so plan hypercare accordingly (wd-post-go-live).
- **Mock-term UAT** - user acceptance is best run as a simulated term (admit -> enroll ->
  bill -> aid -> grade) with real client users in persona roles.
- **Financial-aid data is the conversion long pole** - regulatory data (ISIR - the
  Institutional Student Information Record, the US federal aid-application record - and
  other aid records) and its edge cases deserve their own conversion workstream and
  early reconciliation.
- **FERPA gates everything** - FERPA is the US student-records privacy law;
  education-record access needs the data-handling basis in the paper BEFORE tenant
  access (wd-extend-lifecycle references/ai-data-governance.md; design-time controls in
  wd-design-doc nfr-accessibility.md - despite the name, that file is the suite's
  combined non-functional-requirements and compliance reference, and carries the FERPA
  rows).
- **Decentralization is the norm** - schools and colleges run differently by design;
  expect the operating-model track (above) and heavier change management
  (wd-change-adoption), and use guiding principles to hold the line on standardization
  where it matters.
