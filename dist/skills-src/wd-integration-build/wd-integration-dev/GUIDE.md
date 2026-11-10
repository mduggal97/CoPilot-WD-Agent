---
name: wd-integration-dev
description: >-
  Build, review, and document TRADITIONAL Workday integrations - EIB (inbound/outbound), Workday
  Studio / CLAR assemblies, Core Connector, Connector with Document Transformation (DT), and the
  XSLT 3.0 behind them. Use for "build a Studio integration", EIB templates, Core Connector
  config, Document Transformation, XSLT/XTT/ETV flat-file output, Studio assembly vocabulary
  (assembly.xml, cc:, cloud:), MVEL, integration naming (INT IDs, ISU, ISSG, integration systems,
  security segments, calculated-field / sequence-generator names), build/design checklists, DART
  migration, code review of Studio or EIB source, or inventorying a tenant's SOAP web services
  (WWS) catalog (which operations an ISU can call, WSDLs). Small Studio or XSLT changes have
  migration and streaming landmines; consult before editing. Which web services a DOMAIN uses by
  design is wd-solution-playbooks; O4I / Orchestrate flows and Extend APPLICATIONS (PMD, pods,
  business objects, Model BPs, wdcli) are wd-extend-dev.
---

# Workday Traditional Integration Development

This skill is a thin index for TRADITIONAL integrations (EIB, Studio/CLAR, Core Connector, Document Transformation, XSLT). Each reference is self-contained and distilled from verified builds (not docs guesses). When a reference and Workday documentation disagree, the reference wins for the patterns it marks as build-verified.

**Scope boundary (read first):** O4I / Orchestrate flows (`.orchestration`, Maya format, the flow builder + validator engine) and Extend APP development (PMD pages/pods/cards, business objects, Model BPs, wdcli) are owned by the **wd-extend-dev** skill. This skill covers the pre-O4I integration toolbox. The two overlap in one place: an O4I integration tracked under an INT number follows the integration NAMING and build-gate conventions here, but its flow is authored with the engine in wd-extend-dev (see orchestration.md in the wd-extend-dev skill). If the task is "build/modify an orchestration flow" -> wd-extend-dev; if it is "build a Studio/EIB/CC/DT integration" or "name/migrate any integration" -> here.

## Auth for integration work

Before calling SOAP/WWS operations, fetching WSDLs with auth, or working with ISU
credentials, consult the **wd-auth** skill to verify the right auth mode and stored
credentials. For wdcli-based work (O4I builds via wd-extend-dev), wd-auth's preflight
check catches expired tokens and wrong-org state before they produce misleading errors.

## Flex Credits and API metering (Aug 2026 platform change)

As of the May 2026 platform policy update, **every non-Workday-built integration now counts toward the customer's annual API entitlement**, so integration design decisions are directly visible in the customer's cost model. The entitlement tiers, credit pricing, and the full what-counts / what-does-not-count lists live in the canonical owner - **wd-estimate `references/flex-credits.md`**; cite that rather than restating the numbers here.

**Design implication:** every integration build, IDD, and proposal should include an API consumption estimate. When a Core Connector can serve the use case, it is not just simpler -- it is free at the API layer. When choosing between a Studio augmentation and a standalone custom integration, factor in that the augmentation makes the entire connector's API calls metered. See `wd-estimate/references/flex-credits.md` for the full rate card and entitlement tiers.

**New integration patterns (forward-looking):** MCP (Model Context Protocol) and A2A (Agent-to-Agent) connectors are emerging alongside traditional EIB/Studio/XSLT. Sana Enterprise has 100+ enterprise connectors live (Jira, Salesforce, ServiceNow, Slack, Confluence, etc.) with 1000+ connector triggers coming in 26R2. These agent-to-agent flows may replace some traditional integration patterns -- consider them alongside the traditional toolbox at discovery and solutioning. The wd-extend-dev skill's custom-agents.md covers the MCP/Agent Action build model.

## Measure twice - know the requirements (esp. SECURITY) BEFORE you touch a script

Integrations carry the HEAVIEST security-config load in the suite - ISU, ISSG, integration security segments, per-operation domains, API-client/PGP credentials - and it is the #1 recurring miss. Before writing or modifying any integration, capture the requirement set in writing, derived from the design and the owning skills, never remembered or inferred from a sibling: functional + data (web-service operations, RaaS/WQL sources, transport) + **SECURITY** + tenant prereqs + NFRs. **The SECURITY section is mandatory and a blank/unresolved one is a HARD STOP - do not build until every ISU / ISSG / security segment / per-operation domain / API-client scope the integration needs is enumerated:** source it from `references/security-setup.md` (ISU/ISSG/segment naming + grants), the WQL `allWebServiceOperations` op-to-domain map (wd-extend-dev `references/tenant-ops.md`), wd-deployment `references/security-role-design.md` + `security-setup-section.md` Part 3, and the IDD WD Solution tab. Full gate: wd-extend-lifecycle `references/quality-gates.md` ("Measure twice - the pre-build requirements gate"). The tools to know exactly what's required already exist - use them up front.

**Automate-first (STANDING):** default to building/testing via API/wdcli/browser (plan-first + confirm-each-write, dev only); prompt only for the strictly-disallowed set (security ACTIVATION, credentials/MFA, prod, CAPTCHA/consent, permanent deletion). Canonical policy + disallowed list: wd-extend-dev `references/tenant-ops.md` ("Automate-first").

## Before building a domain connector

Before building a domain connector (payroll / benefits / comp / financials / time /
talent / student / HCM-core / etc.), open the matching **wd-solution-playbooks** domain
file for the web services, data sources, and named donors that domain uses - that skill
hands off to this one "at build," and its playbook saves you rediscovering the operation
names and donor integrations. Domain files live at `wd-solution-playbooks/references/`
(e.g. `payroll.md`, `benefits.md`, `compensation.md`, `financials.md`).

## Before ANY edit to an existing integration

1. **Confirm the local project matches what's deployed.** For Studio, check Git + the manifest timestamp before editing - another developer (often the client's) may have changed the assembly since you last pulled. Diff before you touch anything.
2. **Validate code against the CURRENT design (the IDD), not the original.** When requirements changed, re-read the latest signed Integration Design Document, enumerate every object the change touches (assembly steps, XSLTs, calc fields, ISU/ISSG, RaaS reports, transport), and plan the full update before writing. Partial updates that miss a transform or a security object are the most common defect source.
3. **Update comments/manifest when you update code.** A manifest-as-runbook that still describes the old behavior (or a stale `Sample` description) is a finding, not documentation.

Red flag: "too small to migrate carefully" - integration security objects (ISU/ISSG), PGP keys, and API Clients do NOT migrate tenant-to-tenant; a small change can still require full per-tenant re-setup.

## Coding standards (all integration + transform code)

Integration and transform code gets handed to client developers, so it carries the same bar as Extend code - including the **exemplar / north-star standard** (every transform is a reference specimen: correct-and-verified, efficient, readable, KT-commented, documented, reusable): descriptive names, knowledge-transfer comments in layman's terms (state the *intent* of each block, not a restatement of the code), a header + change-log block at the top of substantial XSLTs and Studio components, and a global logging/audit framework (global catch, named per-step catches, severity rollup). The suite-wide code-standards principle - and the exemplar bar - is owned by the wd-extend-dev skill's standards.md; the integration-specific naming that goes with it is integration-naming.md below.

**Author from the language, do not clone an example.** Write a transform from the minimal streaming XSLT skeleton + the idiom set in [references/xslt3.md](references/xslt3.md) (and a Studio assembly from the vocabulary in studio.md), reasoning from the requirement. The worked-example library (xslt3.md index, the CLAR corpus) is to LEARN idioms and VERIFY an unfamiliar shape - not a copy-source. Same author-from-primitives default as wd-extend-dev build-from-scratch.md.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| Integration naming: INT IDs, ISU/ISSG, integration systems, security segments, calc fields, sequence generators, Studio object names | [references/integration-naming.md](references/integration-naming.md) |
| Traditional integration build (EIB / Studio / Core Connector / Connector-with-DT) + per-type build gates | [references/integration-build.md](references/integration-build.md) |
| EIB deep-dive: inbound (operation selection, spreadsheet-template anatomy, validate-then-load, launching-user trap) + outbound (RaaS gates, transforms, transports, scheduling) + launch-from-integration + troubleshooting | [references/eib.md](references/eib.md) |
| Core Connector deep-dive: template config surface, integration services, field overrides, change detection (direct-only transaction log vs Full-Diff), DIS security exception, connector family map | [references/core-connector.md](references/core-connector.md) |
| REVIEWING someone's IDD or build (second-set-of-eyes QA scorecard): IDD-stage + Build/CLAR-stage checklists, Studio code-quality rubric, completion score | [references/integration-review.md](references/integration-review.md) |
| Studio anatomy: assembly.xml, `cc:`/`cloud:` vocabulary, MVEL, error-handling/audit framework, when-Studio-vs-O4I | [references/studio.md](references/studio.md) |
| Studio reusable patterns: boomerang, chained multi-Studio, DIS compare, EIB launcher, WWS import framework, shared-library CLAR | [references/studio-patterns.md](references/studio-patterns.md) |
| XSLT 3.0: streaming, iterate/accumulators/maps, merge strategies, XTT/ETV flat-file output, worked-example library index | [references/xslt3.md](references/xslt3.md) |
| Document Transformation: when-DT, DT integration anatomy, the O4I pre-formatter pattern, canonical-layout contract discipline (spec-as-code, packed columns, sample mode) | [references/document-transformation.md](references/document-transformation.md) |
| SOAP Web Services (WWS) catalog: inventory the services/operations an ISU can call, in-tenant report vs live WSDL crawl, retrieval gotchas | [references/wws-catalog.md](references/wws-catalog.md) |
| FUNCTIONAL testing of the integration (output-vs-IDD-mapping reconciliation, connectivity, full-volume, outbound parallel-run, integration UAT) - this skill owns build gates + DART; functional testing is owned by **wd-testing** | wd-testing references/integration-testing.md |
| Build-specs to regenerate the naming-standards / checklist / security-segment / WWS-inventory scripts if not on your machine | [references/scripts.md](references/scripts.md) |

Cross-skill boundaries:
- **O4I orchestration flows** (Maya format, node vocabulary, securityDomains rule, the flow builder + `validate.py` linter): orchestration.md in the **wd-extend-dev** skill.
- **Integration DESIGN docs** (the Integration Design Document (IDD) .xlsm, gap analysis, change control): the **wd-design-doc** skill. This skill owns the BUILD.
- **The machine side of integration security** (the ISU that RUNS the integration, domain grants, API clients, per-tenant setup): security-setup.md in the **wd-extend-dev** skill. This skill's security-segment worksheet plans the HUMAN side (who sees which integration systems).
- **Tenant promotion / DART migration / per-tenant re-setup** beyond the build: the **wd-deployment** skill (migration-checklist.md).

**Upstream reference:** Workday's Community "Integration Naming Standards" doc is **access-gated - do not bundle/redistribute it** (it is not shipped here). Reference it by link on Workday Community; regenerate the vendor-neutral naming master via `scripts/build_naming_standards_doc.py` (see integration-naming.md + scripts.md).

## File-format boundary

Use the xlsx/docx skills for Office file mechanics; keep firm deliverables in neutral formatting. This skill owns Studio/EIB/CC/DT/XSLT source code, integration naming, and integration coding conventions.

## Lifecycle neighbors

previous = wd-design-doc (build to the signed IDD); next = wd-testing (unit scenarios and DART/regression come from the design); sibling = wd-extend-dev (O4I orchestration engine + Extend app development). Tenant promotion / DART migration beyond dev = wd-deployment.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
