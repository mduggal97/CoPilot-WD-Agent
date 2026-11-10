# Pre-sales qualification + SOW handoff

## Qualification checklist (before investing in a full estimate)

Cheap to ask now, expensive to discover in delivery week 3:

- **Does the client own Workday Extend / Innovation Services?** (No Extend SKU = no project; procurement of it adds months.) Which capacity tier - are they near usage limits?
- Tenant landscape: do they have a dedicated dev/impl tenant the firm can use? Who grants access, and how long does that take?
- Is there an incumbent tool/process (discovery is cheaper) or greenfield (design is longer - wd-discovery's hard path)?
- Who is the economic buyer, who signs the SOW, and what deadline is driving them (fiscal year, contract expiry of the legacy tool)?
- Is a competing partner quoting? (Shapes how assumptions vs price are balanced.)
- Client-side capacity: will SMEs be available for design sessions? A client who can't staff discovery stretches every phase.
- Security/compliance constraints (PII in the app? SOC/audit needs?) that change the design floor.

## SOW handoff - translating the estimate into contract language

The estimate's assumptions become the SOW's protective structure. For each section, the estimate provides the content:

- **Scope**: the enumerated apps/integrations and, per app, the archetype-level description (objects, page groups, BPs, integrations) - specific enough that "add another request type" is visibly out of scope.
- **Assumptions** (lift directly from the estimate's assumption list): volumes assumed, # of design cycles included, environments provided by client and when, client staffing (SME availability, security-admin turnaround), data conversion scope (or its exclusion), # of UAT defect-fix rounds included.
- **Exclusions** (state them; silence reads as inclusion): legacy-system changes, historical data conversion beyond N months, integrations not enumerated, post-hypercare support, Workday-side subscription/SKU costs, report development beyond the listed set.
- **Client responsibilities**: tenant access + security grants within X business days, SME availability for scheduled sessions, UAT execution, sign-offs within Y days (schedule protection), test data provision.
- **Change-order baseline**: changes to signed scope go through the change process (delivery-side mechanics: wd-design-doc change control); material changes re-priced from the estimate model.
- **Milestones/payment**: tie to the gates (design sign-off, UAT complete, go-live) matching the estimate's phase structure.

A SOW template exists in your client-docs tree (location - see Engagement inputs; wd-contracts owns the template pointer) - use the docx skill for mechanics, this content model for substance.

## RFP response shape

When responding formally: executive summary (their problem, our fit) -> understanding of requirements (play back the RFP + smart questions that show depth) -> **methodology & tools** (see proposal-content.md - the depth buyers want) -> approach & timeline (phases + gates; AI-accelerated timeline framing per proposal-content.md) -> team & roles -> relevant experience (prior program apps by archetype, anonymized as needed) -> pricing (from the UET) -> assumptions & responsibilities (from above), with professional visuals throughout (proposal-content.md). Firm response documents = neutral formatting via the docx/pptx skills; drafting the resulting SOW/SaaS agreement = the wd-contracts skill; this skill owns the content.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **SOW template location** - where the confirmed SOW template lives in your workspace (wd-contracts owns the canonical template pointer and drafting).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
