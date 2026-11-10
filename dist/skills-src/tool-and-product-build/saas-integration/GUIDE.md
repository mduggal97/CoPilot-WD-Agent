---
name: saas-integration
description: >-
  Integrate a hosted tool or product with NON-Workday SaaS: Salesforce, ServiceNow, data platforms
  (Snowflake, Databricks, Workday Data Connect) and healthcare or higher-ed adjacent systems
  (Epic/FHIR, UKG, GHX, Kyriba, TouchNet, symplr, Ellucian Banner/Colleague). Owns the decisions:
  auth, sync style (webhook, polling, batch), idempotency, retries, rate limits, pagination,
  dead-letter, mapping, iPaaS vs code. TRIGGERS: "integrate with Salesforce", "ServiceNow
  integration", "Snowflake / Databricks / data platform", "call the X API", "webhook", "OAuth to a
  SaaS", "iPaaS", "sync data between systems", "ETL / ELT", "reverse ETL", "Epic / FHIR", "UKG /
  Kronos", "GHX", "Kyriba", "TouchNet", "symplr", "Banner / Colleague", "healthcare or higher-ed
  adjacent system", "Workday Data Connect / zero-copy". NOT Workday integrations: EIB / Studio /
  Core Connector go to wd-integration-dev, O4I to wd-extend-dev, Workday auth to wd-auth. The
  app-* family hosts the runtime that makes these calls.
---

# SaaS Integration (non-Workday)

This skill is a thin index for integrating a hosted tool or product with
**non-Workday SaaS platforms**. It is a Track-2 skill - the integration craft a
tool built via the `app-*` family needs when it has to talk to Salesforce,
ServiceNow, a data warehouse, or any third-party API. Each reference is
self-contained; read the one for the platform you are touching, plus
`patterns.md` for the parts every integration shares.

## Scope boundary - read first

**This skill is everything NON-Workday.** Workday has its own deep integration
track and this skill deliberately does not touch it:

- **Workday traditional integrations** (EIB, Studio/CLAR, Core Connector,
  Document Transformation, XSLT) -> **wd-integration-dev**.
- **Workday O4I / Orchestrate flows and Extend apps** (`.orchestration`, PMD,
  wdcli, WQL/RaaS/SOAP against a tenant) -> **wd-extend-dev**.
- **Workday authentication** (wdcli, tenant OAuth, API Clients, ISU tokens) ->
  **wd-auth**. This skill owns non-Workday OAuth only.

If the other end is a Workday tenant, you are in the wrong skill. If the other
end is Salesforce, ServiceNow, Snowflake, Databricks, Stripe, a partner REST
API, or any other non-Workday SaaS, you are in the right one.

## What this skill owns

- **The integration decision per target** - which API surface, which auth flow,
  which sync style, for Salesforce / ServiceNow / a data platform.
- **The platform-neutral patterns** every integration reuses - auth, sync style,
  idempotency, retry, rate limits, pagination, error handling + dead-letter,
  data mapping, iPaaS-vs-code. These are the load-bearing craft; the
  platform files are the target-specific specializations of them.
- **Reputable-source discipline** - patterns here are distilled from the
  official developer docs (cited inline). API version names and numeric limits
  drift release-to-release, so anything version-sensitive is flagged; verify the
  current value against the linked doc before you rely on it.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| Platform-neutral craft: auth flows, sync styles (webhook/poll/batch), idempotency, retry + backoff, rate limits, pagination, error handling + dead-letter, data mapping, iPaaS-vs-code | [references/patterns.md](references/patterns.md) |
| Salesforce: REST / Bulk 2.0 / Composite APIs, SOQL, Platform Events + Change Data Capture, connected-app OAuth + JWT bearer, governor limits, ISV/AppExchange context | [references/salesforce.md](references/salesforce.md) |
| ServiceNow: Table API, Scripted REST APIs, IntegrationHub / Flow Designer, import sets + transform maps, OAuth, scoped apps, inbound rate limits | [references/servicenow.md](references/servicenow.md) |
| Data platforms: Snowflake + Databricks + generic warehouse/lakehouse - connection + auth (key-pair, OAuth M2M), bulk load (COPY / stages / Snowpipe / Auto Loader), query vs reverse-ETL, incremental patterns, materialize-in-Postgres vs query-live, Workday Data Connect zero-copy via Iceberg | [references/data-platforms.md](references/data-platforms.md) |
| Healthcare: Epic FHIR/HL7v2 surfaces, Backend Services JWT auth, and the Workday-Epic boundary (supply chain/bill-only, provider master, GL/finance, timekeeping adjacency) - who owns which master, direction, transport, the governance question | [references/healthcare-epic-fhir.md](references/healthcare-epic-fhir.md) |
| Healthcare + higher-ed vertical-adjacent systems (fluency tier): UKG, GHX, Kyriba, TouchNet, symplr, Ellucian Banner/Colleague - where each sits vs Workday, canonical integration shape, load-bearing gotchas | [references/healthcare-highered-adjacents.md](references/healthcare-highered-adjacents.md) |
| The ONE Workday exception: a hosted tool reading a Workday tenant UNATTENDED (API-client refresh grant, token in Secrets Manager, RaaS-classic-host vs WQL-gateway trap) - distinct from wd-auth's interactive path | [references/workday-from-a-hosted-tool.md](references/workday-from-a-hosted-tool.md) |

## Boundaries

- **wd-integration-dev / wd-extend-dev** = ALL Workday integration. This skill
  never authors an EIB, Studio assembly, Core Connector, or O4I flow.
- **Epic is a non-Workday SaaS integration target** (references/healthcare-epic-fhir.md) -
  the Epic-side FHIR/HL7v2 API and the Workday-Epic design boundary live here; once
  data crosses into Workday, the transport (EIB, Studio, Core Connector, O4I) stays
  wd-integration-dev / wd-extend-dev.
- **wd-auth** = Workday authentication only. Non-Workday OAuth (Salesforce
  connected app, ServiceNow OAuth, Snowflake/Databricks tokens) lives HERE.
- **app-* family = the hosting runtime that CONSUMES these integrations.** A
  hosted tool built via those skills is the caller; this skill is what it calls
  through. Specifically:
  - **app-hosting** owns where the integration code runs (App Runner behind the
    VPN) and where its credentials live (AWS Secrets Manager). `patterns.md`
    cross-links to it for secret storage - this skill does NOT re-teach Secrets
    Manager, it points at the owner.
  - **app-agentic** owns the model-call provider seam and any MCP server the
    tool hosts. When an "integration" is really an agent tool-call or an MCP
    connector, that shape is app-agentic; the underlying SaaS API call is here.
  - **app-architecture** owns the module contract - an integration to one SaaS
    is typically its own module/adapter behind a port.
- **market-research / product-gtm / bow-sales-enablement** = the marketplace
  channels (AppExchange, ServiceNow Store) as a GTM surface. This skill covers
  AppExchange/ISV only as INTEGRATION context (how an ISV app calls Salesforce),
  not as a sales motion.

## Lifecycle neighbors

- **Track/front door:** practice-lifecycle (Track 2) -> app-architecture shapes
  the tool; this skill fills in a specific external-system adapter.
- **Consumes from:** app-hosting (runtime + Secrets Manager), app-agentic (MCP /
  tool-call framing when the integration is agent-driven).
- **Sibling craft on the Workday side:** wd-integration-dev - same integration
  discipline (idempotency, security objects, streaming), different platform.
  Read it for the house style; do not cross the boundary.

**Sources are cited inline in each reference.** Reputable = the official
Salesforce / ServiceNow / Snowflake / Databricks developer documentation only.
Treat every version string and numeric limit as version-sensitive - the docs
are the source of truth, this skill is the map.

**Ship gate for this track (not the Workday `quality-gates.md` registry):** integration code built here ships through app-harness `references/conformance-checklist.md` (AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps) and app-harness `references/testing.md` (integration/contract tests), like the rest of the Track-2 build.
