---
name: wd-extend-dev
description: >-
  Build, modify, review, and deploy Workday Extend apps and O4I (Orchestrate for Integrations)
  orchestrations - and pull/list/report on Workday records. Use whenever the work touches an
  Extend app or O4I flow: PMD pages, pods, cards, scripts, business objects, security domains,
  Model BPs, wdcli commands (create/upload/deploy/download), PoC builds, code review or audits of
  Extend/O4I source, or "add a field / change a page / fix a bug". Also OWNS reading Workday data
  - "get me a list of employees", workers, orgs or any records via RaaS, WQL, or a custom report /
  calculated field. Even one-line PMD changes hide runtime landmines; consult before editing. Also
  covers limits, coding standards, UI design, Prism/reporting, custom agents, and GenAI calls.
  Traditional integrations (EIB, Studio/CLAR, Core Connector, Document Transformation, XSLT) and
  integration naming (INT IDs, ISU/ISSG) are wd-integration-dev; a domain's config objects and web
  services are wd-solution-playbooks.
---

# Workday Extend & O4I Development

This skill is a thin index. Read the reference file for the layer you're touching - each is self-contained and distilled from verified builds (not docs guesses). When a reference and Workday documentation disagree, the reference wins for the patterns it marks as build-verified.

## Before ANY wdcli command - the auth preflight

Before the first `wdcli app upload`, `app deploy`, `app download`, or `tenant token` in
a session, consult the **wd-auth** skill and run its preflight check (auth-preflight.md):
`wdcli whoami --ci` to verify the active org matches the target app, and confirm tenant
auth is live. This catches the wrong-org and expired-token failures BEFORE they produce
misleading errors. If any auth check fails, wd-auth surfaces the USER-ACTION block; once
the user signals done, re-check and proceed.

## Measure twice - know the requirements (esp. SECURITY) BEFORE you touch a script

Before writing OR modifying any artifact, capture the requirement set in writing - functional + data/integration + **SECURITY** + tenant prereqs + NFRs - derived from the design and the owning skills, never remembered or inferred from a sibling. **The SECURITY section is mandatory and a blank/unresolved one is a HARD STOP - do not build until every domain / ISU / ISSG / API-client scope / RaaS-report security the design implies is enumerated** (source it from `references/security-setup.md` + wd-deployment `security-role-design.md`/`security-setup-section.md` + wd-solution-playbooks for the domain's web services). Commonly-required security config is the #1 recurring miss - front-load it; the tools to know exactly what's needed already exist. Full gate: wd-extend-lifecycle `references/quality-gates.md` ("Measure twice - the pre-build requirements gate").

**Automate-first when you build/test in a tenant:** default to doing it via API/wdcli/browser (plan-first + confirm-each-write, dev only); prompt only for the strictly-disallowed set (security ACTIVATION, credentials/MFA, prod, CAPTCHA). The policy + disallowed list live in [references/tenant-ops.md](references/tenant-ops.md) ("Automate-first").

## Net-new vs modifying existing - two different defaults

- **Building NET-NEW: author from primitives, do not shop for a donor to clone.** Compose the artifact from the platform's minimal-correct skeletons - [references/build-from-scratch.md](references/build-from-scratch.md) has the smallest correct shape of every artifact (BO, VIEW/EDIT page, AMD/SMD, `.task`, FlowSync, Model BP) plus a "given a need -> what to author" decision path. Reach for an example only to SPARK an option or VERIFY an unfamiliar shape (a few must-clone exceptions like a flowVersion 3.3.0 scaffold are named there) - never as a copy-source. Then run the gotcha sweep + validator: that discipline is what makes authoring-without-a-donor reliable.
- **Modifying an EXISTING app: pull-latest + diff first** (below). That is a different rule for a different reason - not clobbering someone else's work - and it stays.

## Before ANY edit to an existing app - the workflow rules

Read [references/workflow.md](references/workflow.md) first when modifying an app that already exists. The short version:

1. **Pull latest, then diff.** `wdcli app download <refId> -d <dir>` and diff against your local tree before editing. Another developer (often the client's) may have changed the app since you last touched it - clobbering their work costs trust you don't get back.
2. **Change-list over direct edit when a client developer owns the code.** Deliver a list (page/file -> what to change -> why) instead of edit->build->deploy, unless the delivery lead explicitly asks for the edit.
3. **Validate code against the CURRENT design before executing changes.** When designs or requirements changed, re-read the latest design doc version, enumerate every code location the change touches (pages, scripts, orchestrations, BOs, AMD routes), and plan the full comprehensive update before writing anything. Partial updates that miss a page are the most common defect source.
4. **Update comments when you update code.** Comments that describe the old behavior are worse than no comments.

Red flag: "too small to sweep" is the #1 defect source - the pmd-gotchas sweep runs on every touched PMD, sized to the change, never skipped.

## Coding standards (all Extend + orchestration code)

Read [references/standards.md](references/standards.md) before writing code. Non-negotiables, because this code gets handed to client developers:

- Descriptive names - no single-letter variables where a real name conveys meaning.
- Knowledge-transfer comments in layman's terms ("explain it to your mother"): state the *intent* of each block, not a restatement of the code. Use `"_comment"` keys in PMD JSON, `//` in scripts.
- Header + change-log block at the top of every `.script` file and substantial page script (see standards.md for the format).
- Consistent naming: lowerCamelCase page ids, PascalCase BOs/BPs, verb-prefixed pages (`add...`, `approve...`), `DNU` prefix for do-not-use pages.
- Efficient by design - externalize reused WQL, compute derived values once into `pageVariables`, use set-based `list:` helpers over nested loops, and gate dependent endpoints with `exclude`. Patterns with real snippets in [references/efficiency.md](references/efficiency.md).

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **Approaching a NEW build - design the best-fit solution (canvass the toolbox, be forward-thinking, not reflexive)** | [references/solutioning.md](references/solutioning.md) |
| **Author an artifact FROM SCRATCH (compose from primitives, not a cloned donor)** - minimal-correct skeletons + "given a need -> what to author" | [references/build-from-scratch.md](references/build-from-scratch.md) |
| **Install wdcli + auth + common-errors (start here)** | [references/wdcli-setup.md](references/wdcli-setup.md) |
| wdcli commands, auth, build loop, org/tenant switching | [references/wdcli-workflow.md](references/wdcli-workflow.md) |
| Pages, widgets, layout, endpoints, AMD/SMD | [references/pmd.md](references/pmd.md) |
| Per-widget property catalog (~66 widgets, 9 families) + the GRID deep-dive (row access, paging, editable commit, export, validation module) | [references/widget-catalog.md](references/widget-catalog.md) |
| **Designing an ENGAGING UI (the craft layer above widget mechanics)** - dashboard question-first ordering, density budget, numeric alignment, state design, microcopy, accessibility numbers, the design self-review | [references/ui-design-principles.md](references/ui-design-principles.md) |
| PMD charts (Chart 2.0 - 13 types, data binding, dashboards) | [references/charts.md](references/charts.md) |
| Anything PMD that will actually RUN (always, before deploy) | [references/pmd-gotchas.md](references/pmd-gotchas.md) + run `scripts/pmd_preflight.py <app-root>` before every upload (codifies the lintable gotchas) |
| WQL language + invocation reference (grammar, data-source discovery, parameters, result shapes, verified examples) | [references/wql.md](references/wql.md) |
| Error handling & observability - page + flow + conventions (handlers, retries, rollback, coded message catalog, level-gated logging) | [references/error-handling.md](references/error-handling.md) |
| Efficient code: externalized WQL, compute-once, set-based helpers, `exclude`, show/hide | [references/efficiency.md](references/efficiency.md) |
| Business objects, fields, BO REST API, security domains | [references/model.md](references/model.md) |
| **Loading data IN / reading it OUT** - the hub: decision map by scale+channel, app-BO bulk-create + descriptor-snapshot pattern, native seed via EIB (+ the immutable-instance wall), read-out via REST vs delivered-WQL, landmines index | [references/data-loading-and-retrieval.md](references/data-loading-and-retrieval.md) |
| Custom BPs on a BO (approve/deny/send-back) | [references/model-bp.md](references/model-bp.md) |
| Orchestrations / O4I flows, SOAP/REST/RaaS/WQL calls, limits | [references/orchestration.md](references/orchestration.md) |
| O4I NODE SHAPES catalog (~45 node types: config keys + minimal JSON per node, from a 206-file census) | [references/orchestration-nodes.md](references/orchestration-nodes.md) |
| ISU, security domains grants, API clients, per-tenant setup | [references/security-setup.md](references/security-setup.md) |
| Workday R1/R2 release impact on in-flight builds; platform dev-tenant-lifecycle timing | [references/release-impact.md](references/release-impact.md) |
| **Migrate an app to a NEW developer tenant** (dev-tenant expiry/refresh, e.g. wcpdev -> custdev): Reusable Tenant Config + Object Transporter, MCBO config-data strategy, App Manager install runbook | [references/dev-tenant-migration.md](references/dev-tenant-migration.md) |
| Build-specs to regenerate `validate.py` / `workday_rest.py` if not on your machine | [references/scripts.md](references/scripts.md) |
| Prism / reporting / analytics as a build workstream (+ Prism administration facts) | [references/prism-and-reporting.md](references/prism-and-reporting.md) |
| Custom report authoring + calculated fields + report administration (report types, PBO lock, RaaS gates, hard-limits table, calc-field scopes/functions) | [references/report-writer-admin.md](references/report-writer-admin.md) |
| Data conversion / migration as a build workstream | [references/data-conversion.md](references/data-conversion.md) |
| Workday custom agents (DevCon 2026; verify GA) | [references/custom-agents.md](references/custom-agents.md) |
| External APIs / GenAI-LLM calls from pages or flows (page-direct vs flow-proxy) | [references/external-apis-and-genai.md](references/external-apis-and-genai.md) |
| **Audit/review an EXISTING app or integration** (health check, takeover, enhancement scoping) - sweep order + findings-report format | [references/app-review-audit.md](references/app-review-audit.md) |
| **Pre-build architecture review** (internal firm gate before build; reviewer != designer) - checklist + ADR-lite record | [references/architecture-review.md](references/architecture-review.md) |
| REST API catalog: local OpenAPI snapshot of all 51 public services (endpoint shapes, secured-by domains, release-refresh routine) | [references/rest-api-catalog.md](references/rest-api-catalog.md) |
| App Catalog sample registry - 50 official Workday samples: "which sample demonstrates X" + verify-before-promote list | [references/app-catalog-registry.md](references/app-catalog-registry.md) |
| **Live tenant ops** - check design facts against the tenant (RefIDs, worktags, BP events, drift), load test/demo/config data via API, implementer private-WS discovery, THE WRITE GATE | [references/tenant-ops.md](references/tenant-ops.md) |
| **Verify a tenant fact programmatically** ("to confirm X, read Y" cookbook: instance/field, worker/org, grant, BP event status, integration-run status + attachments, BO populated, native-data presence) - the HOW behind the suite trust-but-verify rule | [references/tenant-state-verification.md](references/tenant-state-verification.md) |
| **Load config via PRIVATE SOAP services** (custom reports, calc fields, ISU/ISSG, sequence generators, integration config - the advanced-load/iLoad surface) - API-client auth, WSDL fetch, WID discovery, Put + verify workflow, fault vocabulary | [references/private-ws-loading.md](references/private-ws-loading.md) |
| Healthcare & Higher-Ed domain cues - EDI/HL7/FHIR + Grants F&A/IPEDS/CDS + FERPA-vs-HIPAA (externally-sourced, verify-at-use) | [references/domain-patterns-hc-highered.md](references/domain-patterns-hc-highered.md) |

Traditional integrations (EIB / Studio / Core Connector / Document Transformation / XSLT) + integration naming (INT IDs, ISU/ISSG, build checklists) -> the wd-integration-dev skill. This skill owns the Extend app + the O4I orchestration engine; O4I built AS a tracked INT still uses this engine (wd-integration-dev cross-refs orchestration.md here). Traditional-integration DESIGN docs (the Integration Design Document (IDD) .xlsm) are owned by wd-design-doc.

**Official documentation endpoints (verified fetchable 2026-08-06; remember: build-verified reference patterns still outrank docs):**
- Extend developer docs: `https://developer.workday.com/documentation/...` - public, real content, fetch on demand (GA checks, API references).
- WWS SOAP directory (v-current): `https://community.workday.com/sites/default/files/file-hosting/productionapi/index.html` - public; 60+ services with per-service WSDL/XSD links (feeds orchestration SOAP ops + Studio `workday-out-soap` work). Operation-level index (500+ ops A-Z, each linking to its doc page): `.../productionapi/operations/index.html` - fetch this when you need one operation's request/response shape without downloading a whole WSDL.
- REST API directory (`.../file-hosting/restapi/index.html`) - login-gated shell. Hold a full local snapshot (e.g. 51 services) in your Extend workspace's `rest-api-schemas\` - see [references/rest-api-catalog.md](references/rest-api-catalog.md), including the per-release refresh routine (user re-exports after each R1/R2).

## Proof of Concept guidance

A PoC runs in parallel with design, so build it knowing things will change:

- Build broad rather than deep - every major screen and flow stubbed proves feasibility better than one perfect page.
- The coding standards apply from the FIRST generated line - PoC/prototype code carries the same KT-level comments and descriptive names as production code (standards.md), so the developer and architect can follow along from the first draft (verified in a delivered build session, 2026-08-05).
- Tag every assumption you bake in with a design open-item reference in a `"_comment"` (e.g., `"per 7/15 design, OI-06"`) so when the design answer lands you can find every affected spot by grepping the OI number.
- Structure for churn: keep logic in script files (reusable, diffable) rather than duplicated inline expressions.
- The PoC becomes the development base after design sign-off - PoC shortcuts you don't tag become production bugs.

## Reference apps

Learning a schema? Download a working example instead of guessing: a `_reference\` folder in your Extend workspace can hold known-good apps (e.g. a supplier-invoice template with reusable SOAP subflows, a Model BP family, an o4i-example, badge-scanning, inventory-kitting). A mature org has hundreds of apps - `wdcli app list -f json --ci` + name grep finds a schema example for almost any pattern. Keep a full third-party-style app's `source\` in the workspace as a reference for a complete build.

Donor-app pattern - **a prior task-tracker-style PoC**. Mine that kind of app for two reusable patterns: the **counter-BO task-ID sequence-generator** (a dedicated counter BO with a configurable zero-pad width, default 6 -> `T000001` - avoids race-prone row-count sequencing), and a **two-pass parent->child bulk-create** (create parents first, then children referencing them). Sequence-ID alternative (verified in a delivered production app): a **tenant Sequence Generator via SOAP `Increment_Sequence_Generator`** from a sync flow - tenant-native, migration-aware, no BO race; shape in [references/orchestration.md](references/orchestration.md). Prefer it when the client will accept a tenant setup step; the counter BO when the app must be self-contained.

## UX consistency

Users judge the app by consistency: same button placement (OK/Cancel left-aligned per the client's house preference), same confirm-before-commit pattern for destructive actions (micro-page confirms), same grid conventions (Actions column first, buttons stacked vertically to avoid clipping), same date/timestamp display format everywhere. When adding a page, copy the layout skeleton of the app's closest existing page rather than inventing a new arrangement.

Verified house conventions (delivered build session, 2026-08-05):

- Home page = TILES with descriptions (card container), not bare buttons.
- Every page navigates back to Home / its dashboard - no dead-end pages.
- Navigation buttons aligned consistently at the bottom (or top if the customer specifies) - never duplicated top AND bottom.
- Space pages with layout containers per the wireframes, not ad-hoc widget stacking.
- Action buttons sit directly above the grid they act on (e.g. Add Comment above Comment History), not grouped elsewhere on the page.
- **Every app with a home page ships a searchable tenant task** - users find the app by typing its name in Workday search, never by digging through App Manager (house standard, 2026-08-05). The mechanism is the source-side `.task` model file - a plain launcher that deploys with the app; ship one per landing route (see model.md; build+deploy verified 2026-08-06). The tenant-side "Create Custom Task" screen is a DIFFERENT tool - an instance-contextual launch that wants a Business Object (related-action entry) - use it only for that purpose, not as a substitute app launcher (wd-deployment R12). Either way, the task's security domain decides who can FIND it - grant it with the app's other domains.

## File-format boundary

Use the xlsx/docx skills for Office file mechanics. This skill owns Extend/O4I source code, wdcli, and coding conventions.

## Lifecycle neighbors

previous = wd-design-doc (build to the signed design); next = wd-testing (unit scenarios come from the design). Tenant promotion beyond dev = wd-deployment.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
