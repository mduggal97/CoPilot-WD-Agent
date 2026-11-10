# Workday-native custom agents - the build model (DevCon 2026, forward-looking)

> **Verify GA / current capability before proposing this to a client - this is DevCon 2026 PREVIEW material, not confirmed generally available.** Treat every artifact shape, endpoint, and auth detail below as unverified until you have re-checked it against the then-current Workday release (same caution release-impact.md applies to any preview feature: design a fallback, don't build a client commitment on a preview). Full verified build notes live in your Extend workspace's **`CLAUDE.md` -> "Custom Agents on Workday"**; this file is a seed index folding in the DevCon memory.

Workday's custom-agent platform is a build surface that sits **on top of** the Extend stack you already build - it consumes BOs, orchestrations, and pages rather than replacing them. Source of truth for the samples: the official **Workday/2026-DevCon-Hackathon** repo (sample apps `ttsecretsanta_ynzjmg`, `peerRecognition_dcmjng`), plus the official **Workday/asor** Agent Definition API docs (v1.2, 2026.05 - official-docs tier, several pieces PREVIEW-flagged; verify GA/preview before committing).

> **Four distinct AI/MCP surfaces - do not conflate them.** (1) **Workday-native agents** - the subject of this file: agents defined in ASOR, executed through the **Agent Gateway**, built from `.agent`/`.agentskill` artifacts. (2) **Workday ML AI Gateway** - first-party in-platform models at `/ml/...` (sentiment, skills, docint, forecasting), no LLM, no egress; see [external-apis-and-genai.md](external-apis-and-genai.md) "Style 0". (3) **External LLM** - OpenAI/Azure/etc. called out of the tenant, or an external chat/LLM reaching in over MCP; also [external-apis-and-genai.md](external-apis-and-genai.md). (4) **Adaptive Planning MCP Server** - a SEPARATE MCP server for Workday Adaptive Planning data (not the main Workday tenant's Agent Gateway MCP), see "Adaptive Planning MCP Server" section below. This file is surface (1) and (4) only; surfaces (2)/(3) are in external-apis-and-genai.md.

## Adaptive Planning MCP Server (26R2 Preview - 2026-08-15; verify GA before relying on it)

A standalone MCP server exposing Adaptive Planning planning data to external AI agents. Distinct from
the Agent Gateway MCP (which covers HCM/Finance via ASOR-registered agents) - this is an Adaptive
Planning-specific endpoint.

**Status:** Preview, 26R2 (Preview Date 2026-08-15). Requires UMSA opt-in (Universal Main Service
Agreement). Re-verify GA per release-impact.md; do not commit a client to this path pre-GA without a
fallback. (doc-sourced - doc.workday.com 26R2 release notes, 2026-08-27)

**Seven tools exposed** (availability varies by user permissions):

| Tool | Purpose |
|---|---|
| data-dimensional-query | Retrieve multidimensional financial data |
| metadata-search-by-term | Search planning metadata by keyword |
| metadata-search-by-ids | Look up metadata details for specific IDs |
| data-modeled-query | Retrieve rows from modeled planning sheets |
| sheet-get | List all planning sheets visible to user |
| sheet-get-definition | Retrieve sheet structure and schema |
| model-account-get-formula | Get formula overview for accounts |

**Security + access:**
- Tool calls use the same security model as public Adaptive Planning APIs - permissions are enforced, access scoped to what the authenticated user can see.
- All tool calls are recorded in audit logs.
- Authentication: OAuth for standalone Adaptive Planning; Workday registration for Workday-integrated (HCM+Fin+Planning) instances.
- Required system domains (Workday-enabled instances): Tenant Setup - Security, Adaptive Planning API Access, Security Administration.

**Design implications:**
- An external AI agent (e.g. Claude Code + MCP) or a custom Workday agent can connect to this MCP server to read planning data without raw API calls.
- The 7 tool surface is read-only (query/metadata) - write-back to Adaptive Planning plans is NOT part of this MCP surface (use Adaptive Planning REST APIs or EIB for writes).
- GA tracker entry: release-impact.md "Adaptive Planning MCP Server".

## Flex Credits and Extend API entitlements

Customer-built Extend apps count toward API entitlements, but the Extend SKU adds an API entitlement multiplier, and agent usage in production meters by the per-agent Rate Card. See **wd-estimate `references/flex-credits.md`** for the full commercial model - entitlement tiers, the multiplier and its worked example, the agent Rate Card, overage pricing, and the non-production rule.

**Design implication:** when an Extend app calls Workday APIs (BO REST, WQL, SOAP, RaaS), those calls count toward the customer's entitlement. Factor API volume into the design doc and proposal. Agent Actions exposed as MCP tools are metered by the agent's Rate Card, not by raw API calls -- so wrapping logic in an Agent Action can be commercially advantageous vs. raw API consumption.

## Developer Agent - 50+ skills (Aug 2026 Workday AI Vision briefing)

The Developer Agent provides **50+ skills across 7 categories** for building on Workday via natural language. It works with Claude, Cline, Codex, Cursor, Google Antigravity, and MCP. Skills visible from the Aug 2026 briefing (4 per category shown; 22+ more exist):

| Category | Skills |
|---|---|
| **Agents** | Build Agent Skills, Register with ASOR, Apply Agent Stamps, View Registered Agents |
| **Apps** | Create Business Object, Create Business Process, Create Page, Create Page Scripts |
| **Orchestrate** | Discover Integrations, Configure Integration Security, Surface Insights, Discover Actions |
| **Data Cloud** | Query Live Data, Access External Data, Blend Data Sources, Transform Dataset |
| **APIs** | Search API Docs, Generate WQL, Configure Report as a Service, Create API Clients |
| **DevOps** | Deploy Apps, Manage Tenants, Analyze Usage, View Metrics |
| **Knowledge** | Search for Content, Find Tutorials, Clone from App Catalog, Read Product Updates |

The Developer Agent is currently in Early Adopter; GA projected Oct 2025 per the agent GTM roadmap (verify against the current release). It is entitled through Extend Pro (= Extend Core + Developer Agent access). **RECONCILIATION (official-docs - developer.workday.com / Workday newsroom, 2026-08-25):** the official statement is early access via Extend Professional with **GA projected H2 2026** - the "Oct 2025" GTM-roadmap date above is superseded by the official newsroom timing; keep the official date.

## Workday Build - building agents in Extend Professional (Workday newsroom 2026-06-02; dated - verify GA)

**Workday Build** is Workday's platform for developers to build custom AI apps and agents that run on Workday;
the agent-building tools are entitled through **Workday Extend Professional ("Extend Pro")** - **early access
now, GA projected H2 2026** (Agent Passport GA projected by end of 2026). Treat as preview until GA: verify per
tenant/SKU and design a fallback before any client commitment. Workday frames **three ways to build an agent**:
**(1) bring your own tooling, (2) build in the Developer Agent, or (3) use Sana Agents** for a broader scope of
agentic AI.

- **Developer Agent** - build AI apps/agents in **natural language**; it plugs into the agentic dev tools a
  developer already uses - **including Claude Code** (also Cursor, Cline, Codex, Google Antigravity) - and
  wires up the data, services, and documentation itself (e.g. "an agent that alerts finance when a department
  is trending over budget"). **For a consultant using THIS skill suite in Claude Code, Developer Agent is the
  native on-ramp to Workday agent-building** - the same Claude Code session can drive it.
- **Agent-Ready Tools** - a new class of enterprise connectors built for autonomous agents, exposed over
  **MCP (Model Context Protocol)**, giving agents guard-railed access to HR/finance data with **inherited
  security, delegation, business-process controls, and audit trails** (plus custom agent actions via a large
  Pipedream connector library - status: ANNOUNCED, not shipped; see "Pipedream status check" in the
  "Core MCP Tools + the MCP Explorer" section below, current as of 2026-09-11). This is the GOVERNED way
  an agent reaches Workday data - contrast the raw AI Gateway / external-LLM styles in
  external-apis-and-genai.md.
- **Agent Passport** - pre-deployment **compliance validation**: standards-based "stamps" showing which
  security/compliance tests an agent passed (**OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS**; Cisco is the
  first attestation partner). Treat it as the go-live gate for a custom agent.
- **Sana / Sana Agents** - Sana (an AI knowledge/agent platform Workday acquired, ~$1.1B) is the
  **broader-scope agentic-AI** path in the three-choice model. If a client says "Sana," this is it: Workday's
  platform layer for agentic AI, not something you hand-build in Extend - reach for it when the scope is bigger
  than a single Developer-Agent/ASOR agent. **Status update (doc-sourced, Workday blog 2026-08-28 audit):**
  Sana from Workday is now GA worldwide in three tiers - Sana for Workday (AI interface), Sana Self-Service
  Agent (HR/KB summaries), and Sana Enterprise (orchestrates AI across hundreds of enterprise systems). Flag
  Sana Enterprise on the Evergreen risk column when solutioning a broad multi-system agent (solution-options.md)
  - it may absorb the use case natively. Re-verify per release (release-impact.md has the GA tracker row).
  **Sana is ALSO the third-party-connector surface that is live today (2026-09-11):** calling third-party
  tools THROUGH Workday is a **Sana Enterprise** feature - admin-managed third-party connectors (~18 shipped
  at GA: Slack, Jira, Salesforce, ServiceNow, SharePoint, Google Workspace, Zoom, etc. - REPORTED) plus
  custom MCP connectors - NOT an ASOR/MCP-Explorer concept and distinct from the Pipedream Copilot knowledge
  connectors below. When a client asks "can a Workday agent reach system X today," the honest answer is:
  via Sana Enterprise connectors (GA) or your own Extend orchestration egress; the Pipedream agent-action
  library is still pre-documentation.

**How this relates to the rest of this file:** Developer Agent + Agent-Ready Tools are the BUILD + governed
data-access surface (Extend Pro); **ASOR** (Agent System of Record - now GA) is where the built agent is
registered and governed alongside employees; the **Agent Gateway** is the secure runtime entry point agents use
to reach Workday data; the `.agent`/`.agentskill` artifacts below are the on-disk shape. AI Gateway models
(external-apis-and-genai.md "Style 0") remain the in-platform ML surface. Sources: Workday newsroom 2026-06-02;
Workday/asor docs - **dated; re-verify names/timing/GA against the current release** (this is exactly what the
GA-status tracker in release-impact.md is for).

**GA status as officially stated (official-docs - Workday blog/newsroom + github.com/Workday/asor, 2026-08-25):** **ASOR is GA** ("the Workday Agent System of Record (ASOR) is now generally available" - announced Feb 2026) and the **Agent Gateway is GA as an ASOR component**, with **MCP + Agent-to-Agent (A2A) support and OpenTelemetry alignment officially stated**. **Agent-Ready Tools (MCP) and Developer Agent: early access via Extend Professional, GA projected H2 2026. Agent Passport: GA projected by end of 2026.** The **Agent Definition API v1.2 spec is PUBLIC** at github.com/Workday/asor (Markdown + JSON, no login) - corroborates the Workday/asor citations throughout this file. **UPDATE (portal-verified 2026-09-11):** the earlier "no developer.workday.com reference pages" caveat is now partially superseded - the portal ships a live **MCP Explorer (Beta)** with a Quick Start, endpoints, and a 426-tool catalog; see "Core MCP Tools + the MCP Explorer" below.

## Core MCP Tools + the MCP Explorer (portal-verified 2026-09-11, logged-in developer.workday.com)

Strongest-provenance snapshot in this file: read live from the portal, not press material.

**The catalog.** The MCP Explorer (Beta) lists **426 "Agent-Ready Core MCP Tools"** and its backing
catalog file is a literal MCP `tools/list` JSON-RPC response - each tool is a standard MCP definition
with a full JSON-Schema `inputSchema`, MCP `annotations` (readOnlyHint/destructiveHint/idempotentHint),
and a Workday `_meta` block (`wid`, `developerInfo`: productArea/resource/serviceName/httpMethod/
toolType/apiType, `segments`). Composition:
- 179 "service protocol operation" tools (real API-backed) + 247 "prompt resource" tools (value-lookup
  prompts pointing the agent at the right `GET /values/...` endpoint for valid IDs).
- apiType: 222 "Agent" (purpose-built agent APIs: staffingAgent, payrollAgent, recruitingAgent,
  learningAgent, organizationAgent, personalData...) vs 204 "Application (Legacy)" (existing public
  REST wrapped as tools).
- Safety: 386 read-only / 40 writes / 5 destructive (the DELETEs are staged home-contact-change
  records, not master data). Product areas: Workforce 205, Talent 96, Financials 42, Spend 34,
  Payroll 17, Core Platform 14, Student 11, Tools 4 (Financials/Spend are ~all read-only).
- **Writes are BP-mediated**: the pattern is initialize staged event -> CRUD children -> submit (home
  contact change), or a POST that STARTS a business process (create_worker_time_off_request,
  request_payroll_input, create_worker_reference_letter, initiate_performance_review_*). The MCP layer
  inherits BP approvals - an agent write does not bypass the BP framework. `validate_worktags` is a
  POST-but-read-only pre-submission check.
- Some tools REQUIRE their associated prompt tools in the agent definition (flagged per tool in the
  explorer details). ASOR itself is MCP-exposed (asor service: search_agent_resources,
  find_agent_registration, find_asor_agent_definition).

**Quick Start endpoints (portal-verified).**
- ASOR registration: `https://{workday-host}/api/asor/v1/{tenantname}/agentDefinition`
- **Agent Gateway MCP endpoint: `https://{region}.agent.workday.com/{tenant_alias}/mcp`** - POST
  JSON-RPC (`tools/list` etc.) with `Authorization: Bearer <ASU token>`. This is the TENANT gateway
  MCP; distinct from the per-app Orchestrate MCP endpoint under "Agent Actions and MCP" below.
- 8 gateway regions documented (US/EU/UK/CAN/AU/SIN/IND/JPN - full URLs in github.com/Workday/asor).
  Rate limits and a formal error model are NOT published (only "built-in rate limiting").

**Discovery / Finder API (Extend Model Components ARE agent-toolable in EA).** The explorer is STATIC
and shows Core MCP Tools only - it excludes Extend Model Components, Agents Configured as Tools, and
Agent Orchestrations. The portal's EA workaround: call ASOR's external **Finder API** - with
`toolType=AGENT_READY` it returns only the Agent-Ready Core tools + WIDs; with NO params it returns
**Extend Model Components dynamically, mapped alongside Public REST, Public SOAP, and 1P agent
definitions**. (!) reconcile: the public asor GitHub documents this surface as `agentResourceSearch`
(params searchString / operationType Create|Patch|View / toolType **SOAP|REST|MCP**; response
{type,name,description,wid,mcpEnabled,httpEnabled}) and the `AGENT_READY` param value does not appear
publicly - portal Quick Start vs public docs disagree on the param surface; verify the exact call
shape in-tenant before scripting against it. **Design implication: name and describe every Extend
model component as if an agent will call it - it is discoverable and callable via ASOR today (EA).**

**Pipedream status check (2026-09-11).** The FIRST live Pipedream surface is NOT agent actions and NOT
orchestration flow steps: it is **"Connectors in Developer Copilot for Orchestrate"** - 8 read-only
KNOWLEDGE connectors (Google Drive, Gmail, Jira, GitHub, Outlook, SharePoint, Confluence, Linear) that
feed the build-time Copilot's context. **Extend Pro customers, North America regions only.** Security
model (client-conversation-ready, from the official doc): auth is Pipedream-managed via the **official
shared Pipedream OAuth client per provider** (shared across the whole Pipedream platform, NOT unique to
the customer's org - an IdP admin consent approves the shared client, and cannot be scoped
per-Workday-app); most common failure is blocked IdP OAuth consent (Entra user-consent policy / Okta
app consent); tokens encrypted at rest; data processed in the US; Pipedream hosted AWS us-east-1;
SOC 2 Type 2 + DPA w/ EU SCCs on request via the account team. Clients with strict OAuth-app
allowlisting (healthcare/higher-ed) hit the shared-client problem immediately - treat as a security-
review conversation. Two operational rules from the official doc: (a) connections are at USER +
ORGANIZATION level (once per source, live across all threads/apps) and Copilot reads WHATEVER the
connected account can access - connect a least-privilege account, never a personal one; (b) retrieved
content and your input may be sent to the third-party service AND to LLM providers, processed in the
US - no sensitive/PII/confidential data in Copilot threads that use connectors. The DevCon "build custom agent actions from a library of 1,000+ Pipedream
connectors" story remains ANNOUNCED but NOT in developer documentation (portal search confirms no
agent-actions doc) - watch Rising 2026 (Oct 12-15). O4I runtime egress stays SendHttpRequest +
Integration CredStore (orchestration.md).

**Metering (confirmed shape, no published rate).** "Agents" and "API Requests" are explicit metered
usage components in the **Platform Consumption Console** (Credit Balance / Entitlement / Rate Card
pages), drawing on Flex Credits; the BP Optimize Agent docs carry a worked Flex-Credit estimator. No
flat per-call credit figure is published for MCP tool calls - verify in the tenant's console before
quoting a client (wd-estimate references/flex-credits.md owns the commercial model).

## The artifact model

Three new artifact types join the app source tree:

| Artifact | Shape | Holds |
|---|---|---|
| `.agent` | YAML front matter + markdown | `name`, `description`, `skills[]`, then a markdown **system prompt** (persona + top-level behavior) |
| `.agentskill` | YAML + markdown | `allowed-tools[]`, `tool-wids[]`, then markdown **Steps / tone** for that skill |
| `.agentflow` | flow | the agent's own flow layer (orchestrates skills; verify shape in-repo before authoring) |

An orchestration exposed to an agent is referenced in `tool-wids[]` as `{name, wid: "<appRef>/<OrchestrationName>", type: "AGENT_ACTION"}` (DevCon sample shape). **Caveat:** the asor docs address a skill's resources by the **WID of the securable item** (from API Explorer), not an endpoint/path string - see "Resource != endpoint" under Agent Actions below; populate `wid` accordingly.

> **A 4th sense of "skill" - don't conflate (checked 2026-08-07).** Workday's public DevRel catalog now lists **"Agent Skill"** as a first-class content TYPE, and its example (`examples/expense-policy-agent-skill/SKILL.md`) is a **plain markdown `SKILL.md` with `name` + `description` frontmatter and a system-prompt body** - the SAME portable format as a Claude Code skill / these wd-* skills, NOT the ASOR `.agentskill` artifact in the table above. So "Agent Skill" (a shareable prompt-skill in the catalog) != `.agentskill` (an ASOR-executed agent's skill). When someone says "a Workday agent skill," clarify which they mean before wiring anything.

## Agent Actions and MCP

An **Agent Action** is an orchestration made callable by the LLM: a `.maya.FlowSync` flow exposed as an **MCP tool** via an `mcpToolConfig` block (MCPToolInputConfig on the start node, MCPToolOutputConfig on the end node; flat JSON in / flat JSON out). This is the same construct orchestration.md documents under "Newer capabilities" - **the tool/param descriptions ARE the LLM tool schema, so write them as carefully as the code.** MCP endpoint (verify): `POST https://api.<region>.wcp.workday.com/orchestrate/v1/apps/<appId>/mcp`. Note there are TWO MCP endpoints - this per-APP Orchestrate endpoint (your app's Agent Actions) vs the TENANT **Agent Gateway** endpoint `https://{region}.agent.workday.com/{tenant_alias}/mcp` (Core MCP Tools + registered agents; portal-verified 2026-09-11, see "Core MCP Tools + the MCP Explorer" above).

Because it is a FlowSync orchestration, the 25-second page-sync cap does **not** apply, but the sync-flow ceilings in orchestration.md ("Runtime limits") still do - keep an Agent Action fast and push heavy work to an async/Integration-System flow it triggers.

**Status (per Workday/asor, official API docs):** the Agent Action construct is **confirmed**, not speculative - an agent references it as an `agent_resource` with `type: "AGENT_ACTION"`. What is **still Preview** in-spec is the Orchestrate-Action path specifically: the `descriptor`/`type` fields for Orchestrate Actions are preview-only. So treat "an orchestration can be an agent tool" as confirmed, but keep the preview caution on the exact Orchestrate-Action wiring until GA.

**Resource != endpoint (per Workday/asor).** A skill does not reference a tool by URL. Each API a skill calls is a **`workdayResource`** nested under that same `skillId`, and its `agent_resource.id` must be the **WID of the securable item** (the value you copy from **API Explorer**), not an endpoint string like `<appRef>/<OrchestrationName>`. Related securables - e.g. the WQL Data Sources a skill reads - nest in that resource's `tools[]`. The `.agentskill` `tool-wids[]` shape shown in the artifact table is the DevCon-sample surface for this; the asor docs describe the same idea as WID-addressed securables, so populate `wid` from API Explorer WIDs, not paths.

## A2UI - agent-rendered pages

**A2UI** lets an agent render a PMD-style page inside the chat surface: `"a2ui": true` plus `chat*`-tagged widgets; entered fields POST back via `valuePath`. It reuses PMD concepts (pmd.md, pmd-gotchas.md still apply to the widgets), so the page-authoring discipline carries over - this is how an agent collects structured input instead of free text.

## Auth - ASU + API Client at the Agent Gateway

Agent credentials live in the **Agent System of Record (ASOR)** and are **not** the App-Hub OAuth client used for external BO-REST/WQL access. security-setup.md already flags this in its owner table ("Agent credentials (custom agents) -> live in ASOR, not the App-Hub OAuth client -> client admin, if/when agents ship").

**Corrected mechanism (per Workday/asor, official API docs):** an agent authenticates as an **Agent System User (ASU)** backed by an **API Client + Secret per tenant**, and the credential is **validated at the Agent Gateway**. Model the domains an ASU needs the same way you scope an ISU in security-setup.md - least privilege, enumerated, granted by the client admin per tenant.

**Auth specifics (portal + Admin-Guide-Workday-AI PDF, 2026-09-11):**
- Token endpoint: `https://{region}.agent.workday.com/auth/oauth2/{tenant}/token`; authorize endpoint
  `.../auth/authorize/{tenant}`.
- Flow (portal Quick Start): agent activation in ASOR generates **Agent OAuth Client Credentials**; the
  user-authorization step then provisions the **ASU token**, which the portal describes as binding "the
  user's access permissions with a unique agent fingerprint" - (!) the term "agent fingerprint" appears
  ONLY on the portal, not in public docs; Workday's own OAuth diagram calls the ASU token a combo of
  user + ASU + tenant. Activating an agent **auto-creates its ASU**.
- Token lifetimes: 1P agents 60 min (customizable); 3P/external agents 4 hrs (NOT customizable);
  refresh token 24 hrs.
- **Ambient-mode agents authenticate via JWT assertion signed with an x509 keypair** (instead of the
  auth-code flow) - this CONFIRMS the x509 mechanism the note below had flagged unverified, scoped to
  Ambient mode specifically; Delegate mode uses the user-context auth-code flow.

> (!) **"Agent Passport" and "x509 key-pair" are unverified naming.** Earlier DevCon notes described agent credentials as an "Agent Passport" authenticated by an x509 key-pair. **Neither term appears in the asor v1.2 docs** - the confirmed mechanism is ASU + API Client/Secret at the Agent Gateway (above). Keep the "Agent Passport"/x509 wording only as a possible marketing/alias until confirmed against a GA tenant; do not build a security request around it.
> **FLAG UPDATE (official-docs - Workday newsroom/blog, 2026-08-25):** "Agent Passport" IS an official Workday product name - but it is the **pre-deployment compliance-validation product** (OWASP LLM Top 10 / NIST AI RMF / MITRE ATLAS stamps; Cisco first attestation partner; early access, GA projected by end of 2026), **NOT a credential mechanism**. So: naming confirmed, semantics corrected - the earlier DevCon "Agent Passport = agent credential" reading was wrong; the x509 key-pair claim remains unverified; ASU + API Client/Secret at the Agent Gateway stands as the confirmed auth mechanism.

### Skill execution modes - Delegate / Ambient (confirmed)

Per Workday/asor, execution mode is **confirmed** and set **per skill**, not per agent. Each skill in `workdayConfig[]` carries a required `executionMode.id` enum whose literal values are **`"Mode=Ambient"`** and **`"Mode=Delegate"`**:

- **Delegate** - runs *as the invoking user* (user-context; inherits that user's security; good for self-service where the user already has access). Drives a **user-context OAuth grant**.
- **Ambient** - runs standalone / unattended. Drives an **unattended OAuth grant**.

The key fact: **the mode drives the OAuth grant type** the Agent Gateway uses for that skill - so mode is a security decision, not just a UX one, and it is chosen skill-by-skill. Scope each skill's domains to the least privilege that mode requires.

## Registering an agent - the Agent Definition API (asor)

All facts here are **per Workday/asor (official API docs), v1.2 (2026.05)** - official-docs tier, not build-verified, and some pieces are Preview-flagged. Verify against a GA tenant before relying on them.

- **Base endpoint:** `.../api/asor/v1/{tenant}/agentDefinition`. **GET** is secured by the **Setup: Agents** domain; **POST** by the **Development** domain - two different domains for read vs. author, so scope the client admin's grant accordingly.
- **The POST body is an A2A (Agent-to-Agent) Agent Card**, with a Workday `workdayConfig[]` extension carrying the per-skill config (including the `executionMode.id` above). Required card fields: `name`, `description`, `url`, `provider.id` (formatted **`"Provider={name}"`**), `platform.id`, `version`, `capabilities`, and `skills[]`.
- **Upsert is by `name` + `provider` + `version`.** POSTing the same triple updates the existing definition; **bump `version`** to register a new/distinct definition rather than overwrite. There is no separate create-vs-update call for this.
- **Activation / deactivation are ASOR-Hub-UI-only.** There is **no GA programmatic activation** - `PUT` is **WIP** (work-in-progress) in v1.2, so you cannot flip an agent live via the API yet. Author via POST, then activate in the ASOR Hub UI.
- **Tagging discipline:** tag definitions by **domain / capability / risk**, lowercase - keep the taxonomy consistent so agents are discoverable and governable.
- **Observability is a hard contract, not optional logging.** Workday requires **OpenTelemetry (OTel) GenAI** spans across the agent lifecycle: Create Agent, Invoke Agent, Workflow, Inference, Embeddings, Retrievals, Execute-Tool. Required span attributes include `user.id` (resolved to a Workday worker). **Input/output and tool-definition capture is OPT-IN** - a deliberate privacy control: prompts and tool payloads are not captured unless explicitly enabled, so treat enabling it as a data-handling decision (note it in the design doc's security section).
- Note: `agentResourceSearch` / registration operations exist in the OpenAPI but are **not** in the published v1.2 doc set. **UPDATE (2026-09-11):** the portal Quick Start now officially directs EA developers at this surface ("Finder API") for Extend-Model-Component discovery, and github.com/Workday/asor documents `asor/agentResourceSearch` (searchString / operationType / toolType SOAP|REST|MCP) - it is now legitimate to build on, but see the "(!) reconcile" in "Core MCP Tools + the MCP Explorer" above: the portal's `toolType=AGENT_READY` param value is not in the public docs, so verify the exact call shape in-tenant first.
- **Registration lifecycle (github.com/Workday/asor v1.2 + sample, 2026-09-11):** POST `/agentDefinition` (register + define in one step) -> GET the Agent Card back -> Configure (skills, security groups, redirect URI / x509 key for Ambient) -> **Activate (auto-creates the ASU)** -> Deactivate when retiring. Re-POST with the same name+version+provider updates in place.

## Agent vs. PMD app vs. orchestration - which tool

- **PMD app / page** - the user knows the deterministic steps and wants a form-and-button workflow. Structured input, fixed flow, auditable BP. Default for line-of-business apps.
- **Orchestration (O4I)** - system-to-system automation, no conversational surface: scheduled loads, write-backs, integrations. See orchestration.md.
- **Custom agent** - the interaction is genuinely conversational / ambiguous (natural-language intent, variable path), and you want the LLM to *choose* among Agent Actions. The agent still calls the same orchestrations and BOs; it adds a reasoning + language layer, not new data-plane capability. If a fixed page would serve the user, prefer the page - it's cheaper to build, test, and hand off.

## Build / test / deploy via wdcli

Custom-agent artifacts ship inside an Extend app, so the wdcli-workflow.md loop is unchanged in principle: `wdcli app create` -> edit source -> `wdcli app upload`/`deploy` -> `wdcli app download` before edits (workflow.md pull-then-diff rule still governs). **Verify wdcli's agent-artifact support level against the current CLI before relying on it** - preview features sometimes lag in the CLI. Test the Agent Actions as ordinary FlowSync orchestrations first (run logs `wd_log_type = remote`, per orchestration.md "Debugging"), then exercise the agent end-to-end.

**Lifecycle note:** an agent build is still an Extend build - design doc (wd-design-doc), security request package (security-setup.md), per-tenant promotion (wd-deployment). The novelty is the artifacts and ASOR auth, not the delivery lifecycle.
