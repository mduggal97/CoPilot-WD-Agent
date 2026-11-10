# Workday release (R1/R2) impact on in-flight builds

Workday ships two feature releases a year (R1 ~March, R2 ~September). A multi-month Extend project WILL span one; plan for it rather than discovering it.

## During development

- **Watch deprecations:** scan release notes for PMD widget/property deprecations, orchestration node changes, and API version retirements affecting anything the app uses (grep the app source for pinned versions like `/soap/v46.1/` and API base URLs to build the checklist).
- **Preview-window testing:** when the client's preview/sandbox-preview tenant gets the new release ahead of production, run the app's critical paths there. What breaks in preview breaks in prod at release weekend.
- **New capabilities reassessment:** each release ships things that may simplify in-flight work (e.g., 26R1's `columnLayout`/`multiStepLayout` retired layout hacks; long-running API waits changed batch design). A quick "does this release change our design?" pass at release-note time is cheap; refactoring after go-live isn't. But treat DevCon/preview features as unverified until GA - don't design a client build around a preview feature without a fallback.
- **Freeze awareness:** clients often freeze tenant changes around release weekends; align deploy/promotion plans (wd-deployment) to the client's release calendar.
- **Refresh the REST schema snapshot:** each release, have the user re-export the full OpenAPI schema set from the Community REST directory and diff against the local snapshot (your Extend workspace's `rest-api-schemas\`) - new services, version bumps, and in-version field additions all land at releases. Routine and inventory in [rest-api-catalog.md](rest-api-catalog.md).

## Roadmap watch - checked per PURSUIT, not per release

wd-discovery's `solution-options.md` scores an **Evergreen risk** column ("will Workday deliver this natively, stranding the custom build?") and points here for the roadmap exposure - this section is what that pointer means in practice. At every pursuit/solution-options pass, check the named sources:

- **DevCon session notes** (most forward-looking; treat everything there as preview until GA)
- **Workday Community roadmap / What's-New pages** for the affected products
- **The R1/R2 release notes** for capabilities that just shipped

Standing question for the Evergreen column: **"has Workday announced this capability?"** - an announced native feature against a multi-year custom build scores itself. Current watch items: **Extend Pro packaging** (what lands in which SKU affects whether a client can even run the design); the **AI Gateway / delivered-agents surface** (native agents may absorb use cases that today look like custom GenAI builds - see custom-agents.md); and **Workday Everywhere** (surfacing Workday/Extend in Slack/Teams/Gmail/browser via the Everywhere plugin SDK) - an emerging *delivery surface* worth raising when a client asks "can users reach this from Teams?" (!) scope + GA not yet assessed for the suite; treat as a known option to weigh at solutioning (solutioning.md), not a documented build path - flesh out only if the practice takes on Everywhere work. (!) Extend Pro SKU/packaging implications are commercial, not just technical - confirm against current Workday commercial terms per pursuit; don't rely on conference-era packaging statements.

## Developer-tenant lifecycle (dev-tenant refresh / replacement)

Separate from feature releases, Workday periodically refreshes the DEVELOPER-tenant program itself - e.g.
an announced move from the older `wcpdev`-style developer tenants to a new developer-tenant line
(`custdev`). When this happens, existing Extend apps do **not** move automatically. The full runbook -
de-hardcode tenant IDs into App Attributes, Reusable Tenant Configuration + Object Transporter for
packageable artifacts, the MCBO configuration-data strategy, App Manager install, and reconcile/validate
- is in **[dev-tenant-migration.md](dev-tenant-migration.md)** (distilled from Workday's official
"Development Tenant Expiry Process" post). In short:

- **Package and re-deploy each app** (App Builder Save and Deploy; confirm you are authenticated to the
  new tenant / `wdcli whoami`).
- **Recreate the not-migratable objects** that never cross tenants - ISU/ISSG, API clients, PGP/x509
  keys, security, BP config (wd-integration-dev `integration-build.md` + `security-setup.md`); RTC
  auto-installs the OX-supported tenant config but not these.
- **Confirm the rollout DATES + regional (e.g. US) timing** before packaging.

(!) **As of 2026-08-12:** a dev-tenant refresh (`wcpdev` -> `custdev`) was announced on a Workday
developer call (~2026-08-11); **no formal retirement/rollout post yet** - status: announced, timing TBD.
Track to formal-post + dated status. Firm/engagement-specific affected tenants live in project memory,
not here.

## For live apps

Post-go-live regression at each release is wd-post-go-live's territory - it keeps the per-app critical-path checklist. During a build that spans a release, YOU own re-running unit scenarios (wd-testing) on the new release before resuming development on top of it.

## GA-status tracker (one place the "verify GA" caveats resolve to)

The build skills carry many "treat as preview until GA / verify GA before relying on it" caveats
(standards.md, solutioning.md, custom-agents.md, the roadmap-watch above). Keep ONE running register so
"is feature X GA in our target release?" resolves here instead of being re-litigated per app.

**Register schema** (one row per platform feature the practice's designs lean on):

| Field | Holds |
|---|---|
| Feature | the platform capability (e.g. a PMD widget, an orchestration node, an API surface, an AI/agent feature) |
| Status | preview / limited-GA / GA |
| GA release | the release it went (or is targeted to go) GA - or "announced, no date" |
| Affects | which apps/designs depend on it |
| Source | where the status came from (DevCon, Community roadmap/What's-New, R1/R2 release notes) |
| Fallback | the documented non-preview path if it is NOT GA in the target release (required - no preview dependency without one) |
| Last checked | date/release last verified (refresh every R1/R2) |

**How it stays current:** the practice's roadmap-intelligence intake (wd-practice-ops
`staffing-and-alliance.md`) feeds and refreshes this register; wd-discovery `solution-options.md` reads it for
the Evergreen-risk column; the verify-GA caveats in standards.md / solutioning.md / custom-agents.md point
here for the current answer. **Discipline:** check at each pursuit (solution-options) and re-verify every R1/R2
against the release notes; a design that depends on a not-yet-GA feature MUST carry a documented fallback.

Standing watch items to seed the register (from the roadmap-watch above, status "announced/preview,
GA-for-suite not yet assessed"): **Extend Pro packaging/SKU**, the **AI Gateway / delivered-agents** surface,
and **Workday Everywhere**.

**26R2 is beginning (detected 2026-08-27):** Workday 2026 R2 release notes are now appearing at
doc.workday.com (R2 ~September 2026). (!) PENDING maintainer action: re-export the full REST OpenAPI
schema set from the Community REST directory and diff against the current snapshot
(rest-api-catalog.md routine) - an interactive login step. Also re-verify the dated Admin Guide facts
in prism-and-reporting.md and security-questionnaire.md (both stamped Jul 2026) as the new guide
edition drops.

**Populated rows - Workday Build agent tooling (Workday newsroom 2026-06-02; re-verify each release):**
- **ASOR + Agent Gateway** (agent registry/governance + the gateway agents use to reach Workday; MCP + A2A
  support and OpenTelemetry alignment officially stated) - Status: **GA** (official Workday blog, announced
  Feb 2026) | Affects: any agent registration/governance design | Fallback: n/a (GA). The Agent Definition
  API v1.2 spec is public at github.com/Workday/asor. (official-docs - developer.workday.com research pass,
  2026-08-25; the three EA rows below were re-confirmed against the official sources on the same date -
  statuses unchanged.)
- **Developer Agent** (build agents in natural language; integrates with Claude Code/Cursor/Cline/Codex/
  Antigravity) - Status: **early access via Extend Professional** | GA: **projected H2 2026** | Affects: any
  agent-build engagement | Fallback: do not commit a client pre-GA - scope as EA/pilot. Detail:
  custom-agents.md "Workday Build".
- **Agent-Ready Tools** (MCP connectors; guard-railed HR/finance data with inherited security/BP/audit) -
  Status: **early access via Extend Professional** | GA: **projected H2 2026** | Fallback: use existing
  REST / AI-Gateway styles (external-apis-and-genai.md) until GA.
- **Agent Passport** (pre-deploy agent compliance validation - OWASP LLM Top 10 / NIST AI RMF / MITRE ATLAS) -
  Status: **early access H2 2026** | GA: **projected by end of 2026** | Fallback: manual security review as
  the agent go-live gate until GA.
- **Extend Professional entitlement** - the SKU that unlocks the above (and AI Gateway); **confirm the client
  has or plans Extend Pro during discovery** before scoping an agent build. **Sana / Sana Agents** = the
  broader-agentic-AI path (Workday's acquired platform), not a hand-built Extend artifact.
- **Workday Learning powered by Sana** - Status: **GA** (Workday newsroom 2026-07-22) | Features: AI-native
  learning, Personalized AI Tutoring, Interactive Course Creation, Automated Learning Operations | Affects:
  wd-solution-playbooks talent-and-learning.md (update any "Sana EA" or "Sana pending" references to GA).
  Note: this is the Learning module, not the Developer Copilot / Sana Agents path.
- **Adaptive Planning MCP Server** - Status: **Preview** (26R2, Preview Date 2026-08-15; UMSA opt-in
  required) | Exposes 7 MCP tools for Adaptive Planning data (dimensional query, modeled query, metadata
  search, sheet catalog, account formula); same security as Adaptive Planning APIs + audit logging; requires
  Tenant Setup - Security + Adaptive Planning API Access + Security Administration domains; OAuth for
  standalone, Workday registration for integrated instances | Affects: agent designs that need planning data;
  custom-agents.md "Adaptive Planning MCP Server" section. | Fallback: use Adaptive Planning REST APIs /
  RaaS reports directly until GA.
- **Adaptive Planning - FedRAMP Moderate** - Status: **GA** (Workday newsroom 2026-07-23) | Affects: federal
  agency clients; note for wd-solution-playbooks/wd-discovery when the engagement is a government entity.
- **AI Widgets for Extend** - Status: **GA** (Workday newsroom 2025-06-03 announcement; confirmed shipping
  in 2026 "next wave of agentic AI" blog; available with **Workday Extend Professional**) | Feature: embeds
  configurable AI prompts directly into Extend pages via a new PMD widget type - instant summarization or
  content generation scoped to page fields, without a separate external call or egress; developer defines the
  prompt and Extend Pro entitlement gates it | Affects: any Extend app that could benefit from in-page AI
  generation (job descriptions, commentary, summaries); adds to the Style 0 family in
  external-apis-and-genai.md | Fallback: custom richText + a flow-proxy Style 2 call to an external LLM
  if the client lacks Extend Pro. (doc-sourced - Workday newsroom/blog, 2026-08-28; verify exact widget
  name + PMD shape in-tenant before building - not yet in App Catalog samples)
- **Sana from Workday (platform) - GA** - Status: **GA** worldwide (Workday "next wave of agentic AI" blog,
  ~2026) | Three tiers: Sana for Workday (AI interface), Sana Self-Service Agent (summarizes HR/KB), Sana
  Enterprise (orchestrates AI agents across hundreds of enterprise systems - the broad agentic platform play)
  | Distinct from the Workday Learning powered by Sana row above - the Learning module is one GA product;
  this row covers the Sana PLATFORM layer | Affects: custom-agents.md Sana section; solution-playbooks when
  a client asks about broad agentic AI beyond a single Extend app; wd-discovery Evergreen risk column
  (Sana Enterprise could natively absorb use cases that look like custom agent builds). Fallback: n/a (GA).
  (doc-sourced - Workday blog 2026; re-verify per release)
- **Workday Data Lake + Data Connect - Early Access** - Status: **Early Access** (GA planned later 2026;
  announced Workday newsroom 2026-06-02) | Data Lake: curated unified HR/finance view blended with
  third-party sources and semantic definitions; single trustworthy foundation for developers | Data Connect:
  Apache Iceberg + pre-built connectors, bi-directional zero-copy access from cloud/analytics tools (no
  shadow DBs) | Live Data Query (LDQ): SQL via JDBC/Python, real-time access | AWS integration in early
  access alongside these | Affects: prism-and-reporting.md LDQ row (update "verify GA" caveat to
  "Early Access, GA planned 2026"); wd-discovery for engagements where the client wants a data warehouse /
  BI-layer exit from Workday without Prism | Fallback: Prism + RaaS for analytical reads until GA.
  (doc-sourced - Workday newsroom 2026-06-02; verify GA per release)
- **WWS SOAP version - 26R2 status** - Status: **v46.2 still current** (released 2026R1, July 10, 2026);
  no v47.x visible yet as of 2026-09-04 audit (26R2 formal release expected ~Sep 13, 2026 per second-Saturday
  cadence); community.workday.com/sites/.../versions/index.html confirmed v46.2 as latest | Implication:
  update this row when v47.x appears and flag any new SOAP services; also re-export the REST schema set at
  26R2 formal release (user-interactive step - reminder owned by rest-api-catalog.md routine).
  (public-verified 2026-09-04)
- **Studio Builder + Integration Runtime 2 (IR2)** - Status: **Work in progress** (DevCon 2026, NOT YET GA;
  verify per release before relying on it) | Feature: browser-based Studio IDE alternative on the Workday
  Developer Site; runs on IR2 (FedRAMP-compliant, ~40% faster than IR1, classpath separation, App Hub
  interop); IR1->IR2 migration = most integrations automatic / no customer input, minority via Studio Builder;
  classic Eclipse Studio + IR1 remain current | Affects: any engagement building or maintaining Studio
  integrations - when IR1 deprecation is announced, check every active Studio integration; Studio Builder is
  the migration tool for the minority that need manual IR2 adjustment | Fallback: classic Eclipse Studio /
  IR1 until GA. (doc-sourced - Workday/2026-DevCon-Hackathon, DevCon 2026; detail in
  wd-integration-dev/references/studio.md "Studio Builder and IR2" section)
- **Workday Open Developer Platform** - Status: **Pilot** (announced ~Workday Rising 2026, Sep 2026) |
  Feature: self-serve developer tenant access - any developer can join a waitlist at developer.workday.com
  to get a Workday tenant without an invitation; historically required customer/partner sponsorship |
  Affects: ecosystem growth signal (App Catalog sample acceleration likely over next 1-2 releases); note for
  wd-discovery when a prospect has community-built apps; for the practice, watch App Catalog for new
  community samples to mine | Fallback: n/a (not a build dependency; informational). (doc-sourced -
  Workday blog 2026; re-verify per release)

> **Status: partially populated (Workday Build agent tooling above, dated 2026-06-02).** Those rows carry real
> Status / GA / Fallback; the remaining watch items (Extend Pro packaging beyond agents, Workday Everywhere)
> are still unresolved. A "verify GA" caveat elsewhere is answered by a populated row if one exists, else it
> still requires a live check - and every populated row is dated, so re-verify against the current release
> rather than trusting the stamp. Add a row the first time a design depends on any other not-yet-GA feature.

**Refresh routine (each R1/R2):** re-verify the dated, doc-sourced numeric facts elsewhere in the suite
against the current Workday Admin Guide - notably the Prism limits in `prism-and-reporting.md` and the
session/TLS/auth facts in `wd-deployment/references/security-questionnaire.md` (both stamped "Jul 2026").
They go stale silently; this file owns the reminder to re-check them alongside the REST-schema refresh above.
