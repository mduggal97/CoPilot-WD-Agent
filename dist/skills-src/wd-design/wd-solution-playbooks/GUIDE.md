---
name: wd-solution-playbooks
description: >-
  Per-domain Workday TECHNICAL SOLUTION PLAYBOOKS - from a domain need to a concrete technical
  design. One playbook per area (HCM/staffing, recruiting, time/absence, talent/learning,
  compensation, benefits, payroll, financials/P2P, procurement/expenses, banking, projects/PSA,
  grants, student, analytics/Prism, adaptive planning), pairing the config spine (objects, setup
  order, BPs) with the technical surface: SOAP web services (WWS), RaaS/WQL sources, delivered
  connectors, EIB templates, and custom patterns with donors and gotchas. Use when designing or
  scoping in a domain: "what web services load this domain's data", "what are the config objects
  behind this domain", "how do we integrate with this domain", "Which web services / data sources
  does a DOMAIN use", or grounding an estimate in real domain constraints. Functional LITERACY is
  wd-discovery; the BUILD is wd-extend-dev / wd-integration-dev; security/tenant setup is
  wd-deployment; a tenant's full WWS catalog is wd-integration-dev.
---

# Workday Solution Playbooks - per-domain technical design cribs

One playbook per functional domain. Each follows the same shape so a solution design can
start from the playbook instead of a blank page:

1. **Configuration spine** - the domain's foundation objects, setup order, key BPs, and
   hard limits/landmines (doc-sourced from Workday Education course manuals, crawled
   2026-08-25; spot-verify load-bearing numbers in-tenant).
2. **Technical surface** - the SOAP web services (from the in-tenant WWS master inventory),
   REST/WQL/RaaS read paths, delivered connectors/EIB templates, and event/BP hooks.
3. **Solution patterns** - common custom-build shapes for the domain (Extend app, O4I,
   Studio, DT pre-formatter) with NAMED local donor examples where they exist.
4. **Design gotchas** - the domain facts that break naive designs.

## Reference map - read what you need

| Domain | Read |
|---|---|
| HCM core: orgs, staffing models, jobs/positions, hire | [references/hcm-core.md](references/hcm-core.md) |
| Recruiting (ATS): requisitions, candidates, offers, hire handoff | [references/recruiting.md](references/recruiting.md) |
| Time Tracking + Absence | [references/time-and-absence.md](references/time-and-absence.md) |
| Talent/Performance + Learning | [references/talent-and-learning.md](references/talent-and-learning.md) |
| Compensation + Advanced Compensation | [references/compensation.md](references/compensation.md) |
| Benefits | [references/benefits.md](references/benefits.md) |
| Payroll (US) + payroll input/integration | [references/payroll.md](references/payroll.md) |
| Financials: FDM, accounting, P2P, Accounting Center | [references/financials.md](references/financials.md) |
| Expenses & Procurement (Spend Management): expense, spend auth, corporate card, P2P, suppliers | [references/expenses-procurement.md](references/expenses-procurement.md) |
| Banking & Settlement: bank accounts, statements/recon, settlement run, payment types/formats | [references/banking-settlement.md](references/banking-settlement.md) |
| Projects/PSA + Revenue Management: project-to-bill, contracts, revenue | [references/projects-and-revenue.md](references/projects-and-revenue.md) |
| Grants Management: sponsored programs, awards, F&A, award billing | [references/grants.md](references/grants.md) |
| Student: foundation, records, admissions, aid, financials | [references/student.md](references/student.md) |
| Analytics / Reporting / Prism: reporting surface, data-source choice, Prism-in-Extend | [references/analytics-prism.md](references/analytics-prism.md) |
| Adaptive Planning (EPM): versions/levels/accounts/sheets - the WD <-> Adaptive integration + scoping (Extend does NOT build inside Adaptive) | [references/adaptive-planning.md](references/adaptive-planning.md) |

Analytics is a DELIVERY SURFACE (how you report on any domain's data), not a config domain, so
its playbook is the DOMAIN DESIGN bridge only: [references/analytics-prism.md](references/analytics-prism.md)
answers which surface fits a need, which data source feeds it (RaaS vs WQL vs LDQ), and the
config spine + gotchas. BUILD CRAFT (authoring a report, calc field, Prism pipeline, or WQL)
stays owned by wd-extend-dev `references/prism-and-reporting.md` (Prism) and
`references/report-writer-admin.md` (reporting) - the analytics-prism playbook cross-links them
as the build owner. Pair with wd-discovery functional-analytics.md for the literacy.

## How to use in a design

- At SOLUTIONING (wd-extend-dev solutioning.md): open the domain playbook FIRST - its
  technical-surface section answers "what can already read/write this" before you invent
  an integration.
- At DISCOVERY: pair with wd-discovery's functional-SKU literacy files (concepts +
  terminology live there; this skill assumes you know what the thing is).
- At ESTIMATE: the configuration-spine and gotcha sections surface scope the client will
  not mention (setup order dependencies, hard limits forcing batching, licensing gates).
- At BUILD: hand the named web services / donors to wd-extend-dev / wd-integration-dev.

## Provenance

Configuration facts are doc-sourced (public Workday Education course manuals) unless
marked otherwise; web-service names come from a live in-tenant WWS inventory
(build-verified list, operation counts as of the inventory date); donor examples are
named from the local example corpus. The suite provenance ladder applies: build-verified
knowledge in wd-extend-dev / wd-integration-dev WINS over anything here on conflict.

Before designing on any domain's native data, verify the tenant actually HOLDS it (a bare
dev tenant will not) - trust-but-verify (wd-extend-lifecycle/references/verify-in-tenant.md).

**Donor-citation bar (applies to every playbook's "Solution patterns" section).** Donors
fall into three tiers, and a citation must make its tier legible:
1. **Build-verified / official-catalog** - an Extend or O4I app whose source is on disk and
   deployed or catalog-shipped (e.g. `salesCommission`, `supplierInvoicesInbound`,
   `createAccountingJournal`, the deployed Payroll Input O4I template). Cite freely.
2. **Inventory-cited** - a Studio project named in the local Studio-to-O4I candidate
   inventory but not opened/verified this session. ALWAYS caveat: "(inventory-cited, not
   build-verified; open the project in the raw Studio export before quoting it)".
3. **Delivered-Workday reference** - a Workday-shipped INT00xx CLAR (a pattern to study, NOT
   a firm converter you can lift). Say so, and never present it as reusable firm IP.
When in doubt, under-claim: a donor that turns out not to be on the machine costs an estimate.

## Lifecycle neighbors

previous = wd-discovery (functional literacy + requirements); next = wd-extend-dev /
wd-integration-dev (build); siblings = wd-estimate (sizing), wd-deployment (security/
tenant setup), market-research (whether to build at all).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check
in wd-extend-lifecycle references/quality-gates.md - run it before presenting work as
final and report the result with the deliverable.
