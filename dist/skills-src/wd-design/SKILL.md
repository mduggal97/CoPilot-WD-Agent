---
name: wd-design
description: "Use for Workday Extend and integration design work: writing or reviewing a design document or integration design document (requirements, field specifications, object model, open items, change control, design sign-off), wireframes, swimlane process flows, flowcharts, sequence and state diagrams, system-level integration landscape diagrams, and per-domain technical playbooks that name the configuration objects, web services, report sources and connectors behind HCM, recruiting, time, absence, compensation, benefits, payroll, financials, procurement, projects, grants, student, analytics and planning."
---

# Design documents, visuals and domain playbooks

This skill bundles several skills from the Workday Practice Delivery suite.
Each one lives in its own folder with its full method in `GUIDE.md`.

## How to use this skill

1. **Pick the one member skill** below that owns the task.
2. **Read that member's `GUIDE.md` first.** It is the full method. Do not answer from the summary here.
3. **Open only the reference files the guide points to.** Paths inside a guide are relative to that member's folder.
4. **Follow the guide's quality check** before presenting work as final, and report the check result with the deliverable.
5. **Never invent Workday facts.** If the guide and its references do not cover it, say so.

## Reading a guide written for another tool

The guides were written for Claude Code, which runs on the user's own machine. Translate as you read:

- **"SKILL.md" of a named skill** means that skill's `GUIDE.md`.
- **"Invoke skill X" or "route to X"** means open X's guide. Find X in the suite map below.
- **`../<skill>/references/<file>`** points at another member's folder, possibly in another skill.
- **`scripts/...` files are not included here.** Describe what the script does and produce the result by hand, or hand the step off.
- **You cannot run `wdcli`, call a live Workday tenant or Smartsheet, drive a browser, or touch local folders.**
  - Do the design, plan, draft, payload or row values here.
  - Then name the boundary plainly and give the exact steps under a heading **"Finish this on your machine"**.
  - Never say or imply that a live action ran.
- **Never ask for, accept or repeat a password, token or API key.**

## Member skills

### wd-design-doc

**Use for:** Author, update, and quality-check Workday Extend and Integration design documents in Excel - the 16/17-tab Extend template, client variants (e.g. a client-mandated 16-tab format), the BoW/Marketplace 10-tab template, the Integration Design Document (IDD), or a customer-specific template. Use this skill whenever the task involves a design document, design doc, functional/technical spec workbook, requirements tab, field specifications, object model tab, open items list, design gap review, design sign-off, or updating a design after a decision. Also owns the yellow-highlight open-items convention and design change control used across the whole delivery - consult it whenever those come up, even from other skills.

**Start here:** `wd-design-doc/GUIDE.md`

**Reference files:**

- `wd-design-doc/assets/idd-readme-content.md` - Canonical IDD "READ ME" content (authored as CELLS, not a text box)
- `wd-design-doc/assets/brands--_example-customer.json`
- `wd-design-doc/assets/brands--neutral.json`
- `wd-design-doc/references/16-tab-spec.md` - The 16-tab Extend design doc - structure, styles, build method
- `wd-design-doc/references/bow-template.md` - BoW / Marketplace design doc - the 10-tab template
- `wd-design-doc/references/change-control.md` - Design change control - after sign-off
- `wd-design-doc/references/document-quality-gates.md` - Design-document quality gates - brand- and template-agnostic
- `wd-design-doc/references/formatting-checklist.md` - Professional formatting checklist (all templates)
- `wd-design-doc/references/gap-analysis.md` - Design gap analysis - finding the holes before the client does
- `wd-design-doc/references/idd-template.md` - Integration Design Document (IDD) - the .xlsm template for integrations
- `wd-design-doc/references/layout-engine-findings.md` - Layout engine - build outcomes (2026-08-11)
- `wd-design-doc/references/layout-engine.md` - Layout engine: content / layout / brand, calibrated from a reference
- `wd-design-doc/references/nfr-accessibility.md` - Non-functional requirements (NFRs) - the design-time checklist
- `wd-design-doc/references/scripts.md` - Scripts this skill uses - bundled vs. regenerate-on-demand
- `wd-design-doc/references/template-builder.md` - Template builder & rebrander - get a fresh template, or rebrand it for a customer
- `wd-design-doc/assets/templates--idd.json`
- `wd-design-doc/assets/templates--layouts--payroll-input-inbound-o4i.json`

### wd-design-visuals

**Use for:** Create and update Workday Extend/Integration design visuals - Balsamiq wireframes (.bmpr), wireflow diagrams, swimlane process flows (draw.io), flowcharts, and app-level sequence & state-machine diagrams (incl. Mermaid input) - in multiple output formats (bmpr, drawio, SVG, PNG, HTML, PDF embed). Use this skill whenever the task mentions wireframes, mockups, screens, wireflow, process flow, swimlane, flow diagram, flowchart, sequence diagram, state machine, Mermaid, Balsamiq, draw.io/drawio, or embedding diagrams into a design document. Even "add one screen to the wireframe" goes through this skill - arrow geometry and layout conventions are easy to break.

**Start here:** `wd-design-visuals/GUIDE.md`

**Reference files:**

- `wd-design-visuals/references/balsamiq-bmpr.md` - Balsamiq .bmpr generation - file format, layout conventions, arrow geometry
- `wd-design-visuals/references/balsamiq-cloud-roundtrip.md` - Balsamiq round-trip - getting the clean PDF into the doc
- `wd-design-visuals/references/output-formats.md` - Output formats - choosing and producing each
- `wd-design-visuals/references/process-flow.md` - Process flows - the 3-lane swimlane template + integration variant
- `wd-design-visuals/references/scripts.md` - Scripts this skill uses - regenerate-on-demand build-specs

### wd-systems-diagrams

**Use for:** Turn an integration inventory into system-LEVEL landscape diagrams - an executive integration landscape and per-workstream deep-dives - rendered as SVG, Draw.io, and PPTX. Use when the user says "systems diagram", "integration landscape", "architecture diagram", "draw.io of integrations", "exec integration overview", "broader landscape", "map our integrations", or wants a stakeholder-ready picture of how Workday (or any hub ERP) connects to external systems across a program. Runs a proven headless diagram-generation engine (no GUI/server needed) from an Excel/CSV tracker or a live Smartsheet. NOT for app-level Extend page flows or wireframes - that is wd-design-visuals.

**Start here:** `wd-systems-diagrams/GUIDE.md`

**Reference files:**

- `wd-systems-diagrams/references/diagrams-and-brand.md` - Diagram modes, brand palette, formats & layout constants
- `wd-systems-diagrams/references/input-schema.md` - Input schema - Integration Tracker
- `wd-systems-diagrams/references/sample-integration-tracker.csv`
- `wd-systems-diagrams/references/scripts.md` - Scripts this skill uses - regenerate-on-demand build-spec

### wd-solution-playbooks

**Use for:** Per-domain Workday TECHNICAL SOLUTION PLAYBOOKS - from a domain need to a concrete technical design. One playbook per area (HCM/staffing, recruiting, time/absence, talent/learning, compensation, benefits, payroll, financials/P2P, procurement/expenses, banking, projects/PSA, grants, student, analytics/Prism, adaptive planning), pairing the config spine (objects, setup order, BPs) with the technical surface: SOAP web services (WWS), RaaS/WQL sources, delivered connectors, EIB templates, and custom patterns with donors and gotchas. Use when designing or scoping in a domain: "what web services load this domain's data", "what are the config objects behind this domain", "how do we integrate with this domain", "Which web services / data sources does a DOMAIN use", or grounding an estimate in real domain constraints. Functional LITERACY is wd-discovery; the BUILD is wd-extend-dev / wd-integration-dev; security/tenant setup is wd-deployment; a tenant's full WWS catalog is wd-integration-dev.

**Start here:** `wd-solution-playbooks/GUIDE.md`

**Reference files:**

- `wd-solution-playbooks/references/adaptive-planning.md` - Adaptive Planning (EPM): versions, levels, accounts, sheets - integration + scoping playbook
- `wd-solution-playbooks/references/analytics-prism.md` - Analytics / Reporting / Prism: the delivery-surface design bridge - solution playbook
- `wd-solution-playbooks/references/banking-settlement.md` - Banking and Settlement: bank accounts, statements, the settlement run, payment formats - solution playbook
- `wd-solution-playbooks/references/benefits.md` - Benefits - solution playbook
- `wd-solution-playbooks/references/compensation.md` - Compensation + Advanced Compensation - solution playbook
- `wd-solution-playbooks/references/expenses-procurement.md` - Expenses & Procurement (Spend Management): expense, P2P, suppliers - solution playbook
- `wd-solution-playbooks/references/financials.md` - Financials: FDM, accounting, P2P, Accounting Center - solution playbook
- `wd-solution-playbooks/references/grants.md` - Grants Management: sponsored programs, awards, F&A, award billing - solution playbook
- `wd-solution-playbooks/references/hcm-core.md` - HCM core: orgs, staffing models, jobs/positions, hire - solution playbook
- `wd-solution-playbooks/references/payroll.md` - Payroll (US) + payroll input/integration - solution playbook
- `wd-solution-playbooks/references/projects-and-revenue.md` - Projects/PSA + Revenue Management: project-to-bill, contracts, revenue - solution playbook
- `wd-solution-playbooks/references/recruiting.md` - Recruiting (ATS): requisitions, candidates, offers, hire handoff - solution playbook
- `wd-solution-playbooks/references/student.md` - Student playbook - foundation, records/advising, recruiting/admissions, financial aid, student financials
- `wd-solution-playbooks/references/talent-and-learning.md` - Talent/Performance + Learning - solution playbook
- `wd-solution-playbooks/references/time-and-absence.md` - Time Tracking + Absence - solution playbook

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, wd-suite-feedback, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design** (this skill): wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: the Marketplace sales-enablement and product go-to-market skills. If a guide points to `bow-sales-enablement` or `product-gtm`, say that content is not included.
