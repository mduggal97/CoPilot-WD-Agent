# ServiceNow Integration

How a hosted tool integrates WITH ServiceNow - the inbound API surfaces, the
in-platform integration tooling, auth, scoped-app packaging, and the rate limits
that shape inbound traffic. Practitioner overview + load-bearing gotchas. Read
patterns.md first; this specializes those patterns to ServiceNow.

**Version-sensitive:** ServiceNow ships two named releases a year (recent line:
Vancouver, Washington DC, Xanadu, Yokohama, Zurich...). API behavior and rate-limit
UI paths move between releases and the docs are versioned per release bundle -
read the bundle matching the customer's instance, not a random one. Endpoints
also live under the customer's own instance host (`https://<instance>.service-now.com`).

## Contents

- [1. Which surface - the decision](#1-which-surface)
- [2. Table API - CRUD on any table](#2-table-api)
- [3. Scripted REST APIs - custom endpoints](#3-scripted-rest-apis)
- [4. Import Sets and Transform Maps - the load pattern](#4-import-sets-transform-maps)
- [5. IntegrationHub and Flow Designer - low-code](#5-integrationhub-flow-designer)
- [6. Auth](#6-auth)
- [7. Scoped apps](#7-scoped-apps)
- [8. Inbound rate limits](#8-inbound-rate-limits)

---

## 1. Which surface - the decision

Integrating INTO ServiceNow, you choose among:

- **Table API** - generic REST CRUD over any table (`incident`, `sc_request`,
  a custom `u_*` table). The default for reading and writing records. No code on
  the ServiceNow side.
- **Scripted REST API** - you define a CUSTOM endpoint (your own path, verbs,
  and server-side logic) when the generic Table API is too raw - to enforce
  business rules, shape a response, or expose an operation that is not 1:1 with a
  table.
- **Import Set API + Transform Map** - the staging-and-transform load pattern for
  bringing external data IN as records, with mapping and coalesce logic on the
  ServiceNow side (section 4).
- **IntegrationHub / Flow Designer** - ServiceNow's own low-code integration
  layer for OUTBOUND and orchestrated flows (section 5) - the platform's built-in
  iPaaS.

Rule of thumb: **read/write a known table -> Table API; need custom logic or a
tailored contract -> Scripted REST; bulk-load-and-map external data -> Import
Set + Transform Map; orchestrate a flow from ServiceNow out -> IntegrationHub.**

Source: ServiceNow REST API reference (per-release bundle,
https://docs.servicenow.com/ under "Integrate > Web services > REST APIs").

---

## 2. Table API

`/api/now/table/{tableName}` - GET (query), POST (create), PATCH/PUT (update),
DELETE. Query with `sysparm_query` (encoded query syntax), pick fields with
`sysparm_fields`, page with `sysparm_limit` + `sysparm_offset`.

Load-bearing gotchas:

- **Reference and choice fields: display value vs value.** By default the API
  can return the raw sys_id for a reference field; set
  `sysparm_display_value=true` (or `all` to get BOTH) when you need the
  human-readable value. Mismatched expectations here are the classic ServiceNow
  integration bug.
- **Paginate by limit+offset** and follow the `Link` response header for
  next/prev (offset pagination - patterns.md section 5; watch the shifting-window
  caveat on live data). Always set an explicit `sysparm_limit`.
- **ACLs apply.** The Table API respects the integration user's ACLs and roles -
  a query that returns nothing may be an access problem, not an empty table. Give
  the integration user exactly the roles it needs, no more.
- **`sysparm_query` uses ServiceNow encoded-query syntax**, not SQL - build it
  from the platform's query grammar (e.g. `active=true^priority=1`).

Source: Table API
(https://docs.servicenow.com/ -> "Table API" in the current release bundle).

---

## 3. Scripted REST APIs

When the generic Table API is not the right contract, define a **Scripted REST
API**: a custom API with its own base path, one or more resources (each a verb +
relative path), and server-side scripts that run on request.

Use it to:

- Enforce business logic or validation the caller should not have to know.
- Return a shaped/aggregated response instead of raw table rows.
- Expose an operation that spans multiple tables or triggers a process.

Gotchas: it runs server-side script under a scope (section 7), so it is bound by
that scope's access and by the platform's transaction limits. Version the API
(the platform supports API versioning) so you can evolve the contract without
breaking existing callers. Secure it with the same auth as any inbound endpoint
(section 6) - a Scripted REST API is not automatically protected. Source:
Scripted REST APIs (ServiceNow docs / Developer site,
https://developer.servicenow.com/).

---

## 4. Import Sets and Transform Maps

The canonical pattern for LOADING external data as ServiceNow records - the
platform's equivalent of a staging table + mapping.

1. Push rows to an **Import Set table** (a staging table) via the Import Set API.
2. A **Transform Map** maps import columns -> target-table fields, with
   **coalesce** fields that decide insert-vs-update (the idempotency key -
   patterns.md section 3) and per-field transform scripts.
3. The transform runs, creating/updating the real records.

Why use it instead of hammering the Table API: it gives you mapping, coalescing
(natural-key upsert), and transform logic on the platform side, and it handles
bulk loads cleanly. Gotcha: **coalesce is your dedupe** - set it on the natural
key or you get duplicates on re-load. Source: Import Sets
(https://docs.servicenow.com/ -> "Import sets" in the current release bundle).

---

## 5. IntegrationHub and Flow Designer

ServiceNow's built-in low-code integration + automation layer - **Flow Designer**
authors the flow (triggers, actions, logic); **IntegrationHub** provides the
connectors/spokes that call external systems and execute REST/SOAP steps from
within a flow.

This is the **iPaaS-vs-code decision (patterns.md section 8) resolved inside
ServiceNow**: for orchestrating ServiceNow-initiated integrations (call an
external API when an incident is created, sync a record outbound), IntegrationHub
is often the right answer over hand-rolled Business Rule scripts - retries,
logging, and reusable spokes come built in.

Gotchas: IntegrationHub spokes/actions are frequently a **licensed/subscription**
capability (entitlement tiers) - confirm the customer has it before designing
around it. It is the tool for ServiceNow-INITIATED flows; for a hosted tool
calling INTO ServiceNow you are still on the Table / Scripted REST / Import Set
surfaces above. Source: Flow Designer + IntegrationHub
(https://docs.servicenow.com/ -> "Flow Designer" / "IntegrationHub").

---

## 6. Auth

ServiceNow inbound APIs support:

- **OAuth 2.0** - register an OAuth application registry entry (client id +
  secret). For server-to-server use the **Client Credentials** grant; for a user
  connecting their account use **Authorization Code**. This is the preferred
  mechanism for a hosted-tool integration - short-lived tokens, no stored
  password.
- **Basic auth** - username + password of an integration user. Simple, widely
  used for internal integrations, but it is a long-lived credential; if you must
  use it, it is a dedicated integration user with least-privilege roles, stored
  in Secrets Manager (patterns.md section 1), rotated.
- **Mutual TLS** - available for higher-assurance setups.

Gotchas: create a **dedicated integration user** with only the roles its ACLs
require - do not reuse a human admin. OAuth is strongly preferred over Basic;
some managed instances disable Basic for inbound. Source: OAuth 2.0 inbound
(https://docs.servicenow.com/ -> "OAuth 2.0"; ServiceNow Developer blog on
inbound OAuth auth-code grant, https://developer.servicenow.com/).

---

## 7. Scoped apps

ServiceNow code lives in either the **global scope** or a **scoped application**
(a namespaced boundary - its own tables `x_<vendor>_<app>_*`, script access
rules, and API surface). If you are building custom logic (Scripted REST APIs,
transform scripts) on the ServiceNow side, **build it in a scoped app**, not
global:

- Isolation - your tables and scripts do not collide with the customer's or
  another app's, and cross-scope access is explicit and controlled.
- Distribution - a scoped app is packaged and installed cleanly (and is the unit
  a ServiceNow Store listing ships as - the Store GTM motion is product-gtm, not
  this skill).

Gotcha: cross-scope access is DENIED by default - if your scoped script must
touch a table in another scope, you configure an explicit access record. Design
the scope boundary deliberately. Source: Application scope / scoped apps
(https://docs.servicenow.com/ -> "Application scope").

---

## 8. Inbound rate limits

ServiceNow lets an instance admin define **inbound REST API rate limits** (rules
capping requests per user/role over a time window). Your integration is subject
to whatever the target instance configures - so:

- **Expect and honor 429.** When a rate-limit rule trips, the API returns 429;
  back off and retry per patterns.md section 4 (respect any `Retry-After`).
- **Coordinate with the instance admin** on a sensible limit for the integration
  user before go-live, rather than discovering the ceiling in production.
- Instance capacity is finite and shared - a runaway integration degrades the
  whole instance for human users, so cap your concurrency (patterns.md section 4)
  and prefer Import Sets for bulk over a Table-API write storm.

Rate-limit rules and their admin UI path are **version-sensitive** (the doc pages
are per-release: Tokyo, Vancouver, ... newer). Read the bundle matching the
customer's instance. Source: Inbound REST API rate limiting
(https://docs.servicenow.com/ -> "Inbound REST API rate limiting", current
release bundle).

---

Sources are linked inline; all are official `docs.servicenow.com` /
`developer.servicenow.com`. ServiceNow docs are versioned per release bundle and
endpoints are instance-hosted - confirm behavior against the customer's release
before relying on anything here.
