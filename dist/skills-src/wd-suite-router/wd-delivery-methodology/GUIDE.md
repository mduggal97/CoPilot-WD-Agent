---
name: wd-delivery-methodology
description: >-
  Vendor-neutral full-program Workday delivery methodology: the phase model for a complete
  deployment (HCM, Financials, Student, Adaptive Planning, Prism), role playbooks and workstream
  RACI, standing delivery norms (RAID, configuration workbook, governance and decision rights,
  tenant strategy, testing ladder), the configuration-guide format, and the specialty tracks
  (Adaptive, Prism, release management, operating model, higher-ed). Use for how a full Workday
  deployment runs end to end, which phase a program is in, what a role does, a RACI, program
  governance, a configuration guide, or scoping a specialty track. Boundaries: the
  Extend/Integration build lifecycle and routing are wd-extend-lifecycle; this project's
  plan/RAID/status is wd-pm (staffing hours: wd-estimate); OCM is wd-change-adoption; test
  scenarios are wd-testing; promotion/cutover is wd-deployment; hypercare is wd-post-go-live. A
  firm-private methodology skill, if installed, layers on top and wins on conflict.
---

# Workday Delivery Methodology (vendor-neutral)

> **Provenance:** authored locally 2026-09-01 as a vendor-neutral replacement for a firm-private
> methodology skill that was removed from this machine. Everything here is industry-standard
> Workday delivery practice and original generic content - no firm-proprietary methodology,
> artifacts, thresholds, accelerator tooling, or configuration IP. It is safe to share wherever
> the rest of the wd-* suite goes (still run the suite README sanitize sweep before packaging).

## What this is

The **full-program** delivery methodology: how a complete Workday deployment runs from first
handshake to steady state, across all product areas - **HCM** (Human Capital Management, the
HR core), **Financials**, **Student** (higher-ed administration), **Adaptive Planning**
(Workday's budgeting/FP&A product), and **Prism Analytics** (Workday's data-blending and
reporting product) - not just the technical track for **Extend** (Workday's platform for
building custom apps on the tenant) and integrations. Use it to:

1. **Orient** - name the phase a program is in and what that phase must produce.
2. **Staff** - explain what each delivery role does and build a workstream RACI.
3. **Run** - keep the standing norms (RAID - the single risks/actions/issues/decisions
   log, configuration workbook, confirmation sessions, guiding principles, governance,
   tenant strategy) that make delivery predictable.
4. **Extend** - scope the specialty tracks that ride alongside a core deployment.

**How this nests with the rest of the suite.** This skill is the WHOLE-PROGRAM lifecycle.
The wd-extend-lifecycle map (estimate -> contract -> discovery -> design -> build -> test ->
deploy -> post-go-live) is the Extend/integration TECHNICAL sub-track that runs INSIDE it.
They nest; they do not compete - the explicit phase-to-phase cross-map is in
[references/phase-model.md](references/phase-model.md). Answer a "which phase are we in?"
question in whichever vocabulary the user used.

## The phase model (the spine)

**Initiate -> Ready -> Plan -> Architect & Configure -> Test -> Deploy -> Support.**

Full phase detail, exit conditions, the delivery-model dimension (packaged fixed-scope
vs. tailored enterprise program), and the cross-map to wd-extend-lifecycle are in
[references/phase-model.md](references/phase-model.md).

## References (index)

- [phase-model.md](references/phase-model.md) - the phases, what each produces, exit
  conditions, delivery models, and the cross-map to wd-extend-lifecycle.
- [roles-and-raci.md](references/roles-and-raci.md) - the generic role model (delivery side
  and client counterparts), the workstream-RACI recipe, and counterpart staffing guidance.
  Feeds wd-pm when a real plan/RACI is built.
- [delivery-norms.md](references/delivery-norms.md) - the standing artifacts and rhythms
  every program keeps: RAID and decision discipline, configuration workbook, customer
  confirmation sessions, guiding principles, governance bodies, tenant strategy, the
  testing ladder, meeting norms.
- [config-guide-pattern.md](references/config-guide-pattern.md) - the FORMAT of a good
  per-area configuration guide, the reuse-before-build discipline, and how a firm builds
  its own guide library over time. Ships NO configuration content itself.
- [specialty-tracks.md](references/specialty-tracks.md) - Adaptive Planning, Prism
  Analytics scoping, release management and managed services, operating-model co-design,
  productized add-on packages, and higher-ed/Student delivery notes.

## How this relates to the rest of the suite

- Functional literacy (what each Workday module does): wd-discovery functional references.
- Build technique and gotchas: wd-extend-dev for Extend apps and O4I (Orchestrate for
  Integrations, Workday's orchestration engine); wd-integration-dev for traditional
  integrations - EIB (Enterprise Interface Builder, spreadsheet-driven loads/extracts),
  Studio (Workday's integration IDE), Core Connector (pre-built integration templates),
  and DT (Document Transformation).
- Plan/RAID/status for a real engagement: wd-pm. Staffing hours and pricing: wd-estimate.
- OCM (organizational change management) program planning: wd-change-adoption. Test
  methodology: wd-testing. Promotion/cutover: wd-deployment. Hypercare/closeout:
  wd-post-go-live. KT (knowledge transfer to the client): wd-kt.
- Reusable-asset catalog and practice operations: wd-practice-ops.
- Productized go-to-market for a many-customer app or package: bow-sales-enablement (the
  suite's Marketplace / Built-on-Workday go-to-market skill - part of this shareable
  suite despite the different name prefix).

**Firm layer.** A consulting firm using this suite typically has its own proprietary
methodology (branded phase names, role playbooks, configuration IP, accelerators). Keep
that in a SEPARATE private skill that references this one - never fold firm IP into this
file. When such a skill is installed, prefer its specifics and use this skill for the
generic frame.
