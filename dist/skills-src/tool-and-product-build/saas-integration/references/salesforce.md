# Salesforce Integration

How a hosted tool integrates WITH Salesforce - the API surfaces, the auth flows,
the governor limits that shape every design, and the ISV/AppExchange context.
Practitioner overview + the load-bearing gotchas, not a full API reference. Read
patterns.md first; this file specializes those patterns to Salesforce.

**Version-sensitive:** Salesforce ships THREE releases a year (Spring / Summer /
Winter) and bumps the REST API version each time - v60.0 was Spring '24, and the
current version is higher. Always pin an explicit API version in your endpoint
path (`/services/data/vXX.0/`) and confirm the current number against the release
notes rather than trusting any number written here.

## Contents

- [1. Which API - the decision](#1-which-api)
- [2. SOQL - querying](#2-soql)
- [3. Bulk API 2.0 - high volume](#3-bulk-api-2)
- [4. Composite - fewer round trips](#4-composite)
- [5. Events - Platform Events and Change Data Capture](#5-events)
- [6. Auth - connected app, JWT bearer](#6-auth)
- [7. Governor limits and API allocation](#7-governor-limits)
- [8. AppExchange / ISV context](#8-appexchange-isv)

---

## 1. Which API - the decision

Salesforce has many APIs; for an external tool integrating in, four matter:

- **REST API** - the default. CRUD on records, SOQL queries, describe metadata,
  over JSON. Reach for this first for interactive, low-to-moderate volume work.
- **Bulk API 2.0** - asynchronous, for large data sets. Salesforce's own
  guidance: operations over ~2,000 records are good candidates for Bulk. Do NOT
  loop the REST API 50,000 times; that exhausts the daily allocation (section 7).
- **Composite API** - bundle multiple REST operations into one round trip (and
  reference the output of one subrequest in the next). Cuts request count and
  latency.
- **Pub/Sub API** - the gRPC event bus for subscribing to Platform Events and
  Change Data Capture (section 5).

Rule of thumb: **interactive + small -> REST; large batch -> Bulk 2.0; several
related writes at once -> Composite; react to changes -> Pub/Sub.**

Sources: REST API Developer Guide
(https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm);
Bulk API 2.0 Developer Guide
(https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/bulk_api_2_0.htm).

---

## 2. SOQL

Salesforce Object Query Language - SQL-like, but with hard differences that bite:

- **No `SELECT *`.** You must name every field. There is no wildcard - query the
  describe metadata if you need the field list dynamically.
- **Relationship traversal, not JOIN.** Traverse parent with dot notation
  (`Contact.Account.Name`), children with a subquery
  (`SELECT Id, (SELECT Id FROM Contacts) FROM Account`). No arbitrary JOIN.
- **Query rows are governed.** A single SOQL call returns up to 2,000 rows by
  default and you page the rest via `nextRecordsUrl` (cursor pagination -
  patterns.md section 5). Total rows retrievable and query CPU are governed.
- **Use SOQL for large result sets, not the Bulk query, when interactive**; use
  Bulk API 2.0 **query** jobs when the result set is huge and async is fine.

Gotcha: SOQL injection is real. Parameterize / escape user input in dynamic SOQL
exactly as you would SQL. Source: SOQL and SOSL Reference
(https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/sforce_api_calls_soql.htm).

---

## 3. Bulk API 2.0

The high-volume path. You do NOT manage batches yourself (that was the older Bulk
API 1.0) - in 2.0 you create a job, upload CSV data, and Salesforce chunks and
processes it asynchronously.

Flow (insert/update/upsert/delete):

1. `POST .../jobs/ingest` with object + operation -> get a job id.
2. `PUT .../jobs/ingest/{id}/batches` with the CSV payload.
3. `PATCH` the job state to `UploadComplete`.
4. Poll the job until `JobComplete`, then GET successful/failed results.

Load-bearing gotchas:

- **It is asynchronous.** You get a job id, not the result - poll (with backoff,
  patterns.md section 4), do not block. Results come back as success and FAILURE
  result sets; process both.
- **Upsert on an external id** to stay idempotent (patterns.md section 3) - a
  replayed load updates instead of duplicating. Define an External Id field on
  the object for this.
- **Bulk consumes a SEPARATE allocation** (batches/records per 24h) from the
  regular API request limit - verify the current numbers in the limits doc, they
  change by edition and over time.
- Enabled by default on Performance, Unlimited, Enterprise, and Developer
  editions.

Source: Bulk API 2.0 Developer Guide + Limits
(https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/asynch_api_concepts_limits.htm).

---

## 4. Composite

Cut round trips (and API-request count against the allocation):

- **Composite** - up to 25 subrequests in one call; a later subrequest can
  reference an earlier one's output (`@{ref.id}`) - e.g. create an Account then a
  Contact linked to it, in one call. Counts as a small number of requests, not
  25.
- **Composite Batch** - run up to 25 independent subrequests together (no
  cross-referencing), each succeeding/failing on its own.
- **sObject Collections** - create/update/delete up to 200 records of the same
  type in one call - lighter than Bulk for mid-size writes that still want to be
  synchronous.
- **Composite Graph** - larger, dependency-ordered graphs of records (up to 500)
  with all-or-nothing semantics per graph.

Gotcha: the whole composite request shares ONE timeout - a slow subrequest can
time out the batch. Keep composites focused. Source: Composite resources
(https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_composite.htm).

---

## 5. Events

For "react when something changes in Salesforce" - event-driven (patterns.md
section 2), far better than polling SOQL on a timer.

- **Platform Events** - a custom, publish-subscribe event (a defined event
  object). Salesforce or your app publishes; subscribers receive. Use for
  intentional business events you model yourself.
- **Change Data Capture (CDC)** - Salesforce automatically emits create / update /
  delete / undelete events for records of enabled objects, with the changed
  fields. Use to keep an external store in sync without polling.
- **Pub/Sub API** is the modern transport for both - a **gRPC** service using
  Avro-encoded payloads (replacing the older CometD/streaming approach). Confirm
  the current subscribe mechanism in the docs; the transport has evolved.

Gotchas: events are delivered on a **best-effort, at-least-once** basis with a
retention window (about 72 hours) and a replay id - persist the replay id so you
can resume after a disconnect, and handle duplicates idempotently. High-volume
Platform Event publishing has its own daily allocation.

Sources: Platform Events Developer Guide
(https://developer.salesforce.com/docs/atlas.en-us.platform_events.meta/platform_events/);
Change Data Capture Developer Guide
(https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/);
Pub/Sub API (https://developer.salesforce.com/docs/platform/pub-sub-api/overview).

---

## 6. Auth

Everything goes through a **Connected App** (Salesforce is transitioning these to
**External Client Apps** - check which your org uses; the OAuth concepts carry
over). The connected app defines the OAuth client, its scopes, and which flows
are allowed.

For a server-to-server hosted tool, the right flow is the **JWT Bearer flow**:

- You register a certificate (public key) on the connected app and hold the
  private key (in Secrets Manager - patterns.md section 1).
- Your backend signs a JWT and POSTs it to the token endpoint; Salesforce
  returns an access token. **No stored client secret, no interactive login,
  no refresh token to manage** - ideal for an unattended integration.
- Requires the target user to have pre-authorized the connected app (admin
  approval / "Admin approved users are pre-authorized").

For a user connecting their own Salesforce org, use the **Authorization Code +
PKCE** flow and store the refresh token.

**Do not use the Username-Password flow.** Salesforce disables it by default for
new connected apps and orgs; it is deprecated. Build on JWT bearer or auth-code.

Gotcha: the token response includes an **`instance_url`** - use it as the base
for subsequent API calls. Hardcoding `login.salesforce.com` or one pod host
breaks against sandboxes and My Domain. Source: OAuth flows / JWT Bearer
(https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm).

---

## 7. Governor limits and API allocation

Salesforce is a multi-tenant platform, so it governs API usage hard - this is the
single biggest design constraint, and unlike an on-prem system you cannot tune it
away.

- **Total API requests per rolling 24 hours** is capped per org (a base
  allocation plus a per-user increment, varying by edition). Both REST and SOAP
  requests count. Bulk API has its OWN separate allocation.
- **Watch your remaining quota via the `Sforce-Limit-Info` response header** (or
  the Limits REST resource) and throttle before you hit zero - a hard stop at the
  cap halts ALL integrations to that org, not just yours.
- **Concurrent long-running requests** (>20s, up to a small concurrent cap) are
  separately limited - a burst of slow queries can lock out others.
- **Design to minimize request count:** bulk over row-by-row, Composite to fold
  many operations into one call, events over polling. Every avoided call is quota
  (and, if the org is metered by its own contract, money) saved.

**All numeric limits are version- and edition-sensitive** - read them from the
current cheat sheet, do not trust a number memorized here. Source: API Request
Limits and Allocations
(https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm).

---

## 8. AppExchange / ISV context

If the tool is not just calling one org's API but is a **packaged product**
distributed to many Salesforce customers, that is the **ISV / AppExchange** path -
relevant here only as integration context (the GTM/listing motion is product-gtm,
not this skill):

- You build in a **managed package** (namespaced), distributed and installed into
  subscriber orgs from AppExchange.
- **AppExchange security review** is mandatory before you can list - it scrutinizes
  how the app authenticates, stores secrets, and calls out. Design the integration
  to pass it from day one (no hardcoded secrets, least-privilege scopes, encrypted
  storage).
- An installed managed package's API calls generally run against the SUBSCRIBER
  org's limits - be a good tenant; the customer feels your request volume.
- A **Connected App can be distributed with the package** so subscribers get the
  OAuth client without hand-configuring it.

For most hosted-tool integrations you are the FIRST case (call one or a few
orgs' APIs), not an ISV package. Only go down the AppExchange path when the
product is genuinely being distributed to many Salesforce customers. Source:
ISVforce Guide
(https://developer.salesforce.com/docs/atlas.en-us.packagingGuide.meta/packagingGuide/).

---

Sources are linked inline above; all are official `developer.salesforce.com` /
`help.salesforce.com` docs. Every version number and numeric limit in this file
is version-sensitive - confirm against the current page before relying on it.
