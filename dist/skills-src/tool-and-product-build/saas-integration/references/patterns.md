# SaaS Integration Patterns (platform-neutral)

The craft that every non-Workday integration reuses, regardless of which SaaS is
on the other end. The platform files (salesforce.md, servicenow.md,
data-platforms.md) are specializations of THESE patterns - read this first so
you recognize the shape when a specific platform names it differently.

This is a practitioner overview plus the load-bearing gotchas, not an API dump.
Anything version-sensitive is flagged; verify against the platform's own docs.

## Contents

- [1. Auth - which flow, and where the secret lives](#1-auth)
- [2. Sync style - webhook vs polling vs batch](#2-sync-style)
- [3. Idempotency - the one you skip and regret](#3-idempotency)
- [4. Retry, backoff, and rate limits](#4-retry-backoff-rate-limits)
- [5. Pagination](#5-pagination)
- [6. Error handling and the dead-letter queue](#6-error-handling-dead-letter)
- [7. Data mapping](#7-data-mapping)
- [8. iPaaS vs code - when to write neither](#8-ipaas-vs-code)

---

## 1. Auth

Almost every SaaS uses **OAuth 2.0**. The only real question is WHICH grant, and
that is decided by one thing: **is there a human in the loop, or is this
server-to-server?**

**Server-to-server (the common case for a hosted tool).** No human present at
call time - your backend acts as itself.

- **Client Credentials grant** - the tool has a client id + secret, exchanges
  them for a short-lived access token, calls the API as a service identity. This
  is the default for a backend integration. (RFC 6749 section 4.4.)
- **JWT bearer grant** - instead of a stored client secret, you sign a JWT with
  a private key; the SaaS verifies it against a public key/cert you registered.
  Preferred when the platform supports it because there is no shared secret to
  leak - only a private key you hold. Salesforce and Snowflake both lean on this
  (Salesforce JWT bearer, Snowflake key-pair JWT).

**Human-in-the-loop (a user connecting THEIR account).** A person authorizes the
tool to act on their behalf.

- **Authorization Code grant (+ PKCE)** - the browser redirects to the SaaS,
  the user consents, you get a code, you exchange it for access + refresh
  tokens. Use PKCE always for public/SPA clients. (RFC 6749 section 4.1; PKCE
  RFC 7636.)
- Store the **refresh token** as the durable credential; access tokens are
  short-lived and re-minted from it.

**API keys** - some platforms (and many smaller SaaS) issue a long-lived API
key instead of OAuth. Simpler, but it is a bearer secret with no expiry and
often no scoping - treat it as the weakest option, rotate it, and never put it
in a URL query string (it lands in logs and proxy history).

**Avoid the Resource Owner Password grant.** Sending a username+password to get
a token is deprecated across the industry (Salesforce has disabled it by default
for new orgs; OAuth 2.1 drops it entirely). If a platform still offers it, do
not build on it.

### Where the secret actually lives (cross-link, do not re-invent)

**A hosted tool stores every integration credential in AWS Secrets
Manager, injected as a RuntimeEnvironmentSecret - never a plaintext env var,
never in the image, never in the repo.** That is owned by **app-hosting**
(`references/aws-architecture.md` section 3.4 and the config-injection table);
this skill does not re-teach it. The rule of thumb from that skill applies
unchanged: **credentials are secrets (Secrets Manager); everything else
per-environment is a plain runtime env var.**

- Client secrets, refresh tokens, API keys, private keys for JWT signing =
  Secrets Manager.
- The token endpoint URL, client id, instance/host URL = plain runtime env vars.
- Cache the minted access token in memory with its expiry; refresh a skew window
  (e.g. 60s) BEFORE it expires, not after a 401. Reactive-only refresh causes a
  thundering-herd of retries under load.

KT note: a token that works in dev and 401s in prod is almost always a
wrong-environment secret, not a code bug - same failure mode wd-auth warns about
for Workday. Check WHICH secret the environment resolved before you debug code.

---

## 2. Sync style

Three ways to move data between systems. Pick by latency need and who owns the
trigger - do not default to polling just because it is the easiest to write.

**Webhook / event-driven (push).** The source SaaS calls YOUR endpoint when
something changes. Lowest latency, lowest waste (no calls when nothing changed).

- You must expose an inbound HTTPS endpoint - for a hosted tool that means
  a route on the App Runner service (still behind the VPN; a public SaaS webhook
  cannot reach a private-ingress service without an IT-provisioned public relay -
  flag this early, it is an architecture constraint, not a code detail).
- **Verify the signature.** Every reputable webhook signs its payload (HMAC with
  a shared secret, or a platform signature header). Reject unsigned/unverified
  calls - an unauthenticated webhook endpoint is an open write to your system.
- **Webhooks are at-least-once.** The sender retries on non-2xx, so you WILL get
  duplicates - see idempotency (section 3). Return 2xx fast; do the real work
  async, or the sender times out and re-sends.

**Polling (pull).** You call the source on a schedule and ask "what changed
since last time?" Use when the source has no webhook, or when you want to own the
cadence and smooth load.

- **Always poll incrementally** by a high-water mark (a `lastModified`/`sysparm`
  cursor or an updated-since timestamp), never a full scan. Persist the mark;
  resume from it. A full re-pull every cycle is the most common polling defect.
- Watch clock skew and the boundary: query `>= lastMark` and dedupe, or you drop
  records that share the boundary timestamp.

**Batch ETL / ELT (bulk).** Move a large set on a schedule - the right tool when
volume is high and latency of minutes-to-hours is fine.

- **ETL** transforms before load (classic, when the target is rigid).
- **ELT** loads raw, transforms in the target (modern default when the target is
  a warehouse that can transform cheaply - see data-platforms.md). For a tool
  landing data in its own Postgres, you are usually doing ELT: land raw, shape
  in SQL.
- Use the platform's BULK API, not the record-at-a-time API, above a few
  thousand rows (Salesforce Bulk API 2.0, Snowflake COPY, Databricks COPY INTO).
  Row-by-row over the transactional API will exhaust rate limits and take hours.

Rule of thumb: **event-driven for "react now," incremental polling for "the
source has no push," batch for "a lot, periodically."** Many real integrations
combine them - webhook for live deltas plus a nightly batch reconcile to catch
anything the webhooks dropped.

---

## 3. Idempotency

The pattern people skip and then chase phantom duplicates in production.

**Every retry-capable, at-least-once channel WILL deliver the same message more
than once** - webhooks retry, queues redeliver, a client retries a request whose
response was lost in flight. If applying the same event twice corrupts state
(double-charge, duplicate record, doubled quantity), you have a bug that only
shows under load.

Make writes idempotent:

- **Idempotency key.** Derive a stable key from the event (the source record id +
  a version/updated timestamp, or a provider-supplied event id). Record processed
  keys; on a repeat, no-op and return the prior result. Many APIs accept an
  `Idempotency-Key` header on writes - use it.
- **Upsert, not insert.** Key the target row on the source's natural id and
  upsert. A re-delivered "create" becomes a harmless overwrite instead of a
  duplicate.
- **Design for reprocessing.** You will replay a dead-letter batch someday.
  Idempotent handlers make replay safe; non-idempotent ones make replay a second
  incident.

KT note: idempotency and retry are a pair. Retries (section 4) are only safe
BECAUSE the handler is idempotent. Build them together.

---

## 4. Retry, backoff, rate limits

**Retry only what is retryable.** Transient failures (network blip, 429, 5xx,
timeout) - retry. Deterministic failures (400 bad request, 401 auth, 403
forbidden, 422 validation) - do NOT retry; the same call fails the same way and
you burn rate limit. Retrying a 400 in a loop is a self-inflicted outage.

**Exponential backoff with jitter.** Wait 1s, 2s, 4s, 8s... but add random
jitter so many failing clients do not retry in lockstep and hammer the recovering
service. Cap the total attempts and the total wait; after the cap, dead-letter
(section 6). Never retry forever.

**Rate limits are a contract, not an error.** Every SaaS caps requests (per
second, per user, per 24h). Respect them proactively:

- **Honor `Retry-After`.** A 429 (or 503) usually carries a `Retry-After` header
  telling you exactly how long to wait - wait that long, do not guess.
- **Read the limit headers.** Many APIs return remaining-quota headers
  (`X-RateLimit-Remaining`, Salesforce `Sforce-Limit-Info`); throttle yourself
  as you approach zero instead of sprinting into a wall.
- **Concurrency cap.** Bound in-flight requests (a semaphore / small worker
  pool). Unbounded fan-out is the fastest way to trip a limit.
- **Prefer bulk endpoints.** One bulk call of 5,000 records costs one request
  against the limit; 5,000 single calls cost 5,000. This is often the difference
  between fitting in the daily allocation and blowing it - and on metered
  platforms, the difference in cost.

---

## 5. Pagination

Any list endpoint caps the page size, so you iterate. Three common shapes:

- **Cursor / opaque token** (best) - the response hands you a `nextRecordsUrl`
  or `next_cursor`; you follow it until it is absent. Stable under concurrent
  writes. Salesforce REST (`nextRecordsUrl`) and most modern APIs use this.
- **Offset / limit** (`?offset=200&limit=100`) - simple but fragile: rows
  inserted or deleted mid-scan shift the window and you skip or double-read.
  Acceptable for a stable snapshot, risky over live data.
- **Keyset / seek** (`WHERE id > :lastId ORDER BY id`) - stable and fast at
  scale; the incremental-poll high-water mark (section 2) is keyset pagination.

Rules: **follow the cursor the API gives you rather than hand-rolling offsets;
set an explicit page size; and put a hard cap on total pages** so a pathological
response cannot loop forever. Stream/process each page - do not accumulate every
page in memory before writing, or a large pull OOMs the container.

---

## 6. Error handling and the dead-letter

A record that cannot be processed must not (a) crash the batch or (b) vanish
silently. Both happen constantly in naive integrations.

- **Isolate the failing record.** In a batch, one bad row should not fail the
  other 4,999. Catch per-record, collect failures, continue.
- **Dead-letter queue (DLQ).** After retries are exhausted, write the failed
  message + the error + enough context to reprocess to a durable store (an SQS
  DLQ, or a `failed_events` table in the tool's Postgres). It is parked, not
  lost. Because handlers are idempotent (section 3), replaying the DLQ later is
  safe.
- **Alert on DLQ growth, not on every error.** A steady trickle of expected
  validation rejects is noise; a spike in the DLQ is a real signal. Wire the DLQ
  depth to an alarm (app-hosting `references/observability.md` owns the CloudWatch
  alarm patterns for a hosted tool).
- **Structured, correlated logs.** Log the source id, the idempotency key, and a
  run/correlation id on every integration event so you can trace one record end
  to end. Never log the token, the secret, or full PII payloads.
- **Poison-message guard.** Cap redelivery attempts; a message that fails N times
  goes straight to the DLQ instead of cycling forever and starving the queue.

---

## 7. Data mapping

The unglamorous middle where most defects actually live.

- **Map to a canonical internal shape, not point-to-point.** Translate the
  source's fields into the tool's own model at the adapter boundary, then work in
  your model. If you later add a second source, it maps to the same canonical
  shape - you do not rewrite everything downstream. (Same instinct as the
  provider seam in app-agentic: normalize at the edge, depend on the neutral
  shape.)
- **Pin the field contract.** Externalize the field map (source field -> target
  field, type, transform) as data/config, not buried in code branches. It is the
  first thing that changes and the first thing a reviewer needs to see.
- **Type and null discipline.** Dates/timezones (store UTC, know the source's
  zone), numbers vs strings, empty-vs-absent, enum/picklist value translation,
  and truncation limits are the perennial offenders. An empty field omitted by
  the source is not the same as a field set to empty - decide which you mean.
- **Validate on the way in.** Reject or dead-letter a record that violates the
  contract at the boundary; do not let a malformed payload propagate and corrupt
  clean data three layers deep.

---

## 8. iPaaS vs code - when to write neither

Not every integration should be hand-coded. An **iPaaS** (integration
platform-as-a-service - MuleSoft, Workato, Boomi, Zapier/Make for lighter needs,
or the platform's own tooling like ServiceNow IntegrationHub) is a hosted
low-code integration layer with pre-built connectors, retries, and monitoring
already solved.

**Lean iPaaS when:**

- The connectors already exist and the logic is mostly mapping + routing (the
  80% case of "move records from A to B on a schedule").
- Non-engineers need to own or change the flow.
- You want managed retry/monitoring/alerting without building it.
- Speed-to-integrate matters more than fine control.

**Write code when:**

- The logic is complex, custom, or performance-sensitive (heavy transforms,
  bespoke business rules, tight latency).
- It must live INSIDE the hosted tool's runtime and data model (an integration
  that is really a feature module of the app - app-architecture territory).
- iPaaS licensing/per-task cost does not pencil at your volume.
- You need full control of error handling, idempotency, and testing in your own
  CI.

**A hosted tool usually writes code** - the integration is a module of the
app, runs in its App Runner runtime, shares its Secrets Manager and Postgres, and
is tested in its harness. iPaaS is the right call for a standalone
system-to-system sync that does not belong inside a specific tool. It is a real
decision - make it deliberately, do not default to code because "we're
engineers" or to iPaaS because "there's a connector."

---

Sources (verify version-sensitive details against the current page):
- OAuth 2.0 - RFC 6749 (https://datatracker.ietf.org/doc/html/rfc6749); PKCE -
  RFC 7636 (https://datatracker.ietf.org/doc/html/rfc7636).
- Secrets storage for a hosted tool - app-hosting `references/aws-architecture.md`
  (Secrets Manager as RuntimeEnvironmentSecret) and `references/observability.md`
  (DLQ/alarm patterns).
- Platform-specific realizations of these patterns - salesforce.md, servicenow.md,
  data-platforms.md in this skill.
