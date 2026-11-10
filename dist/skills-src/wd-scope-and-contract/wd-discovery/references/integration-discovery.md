# Integration Discovery Questionnaire

Use this for any build that moves data between Workday and another system - a dedicated integration (e.g., an O4I orchestration with no UI) or the integration surface of an Extend app. Work through every section; a skipped section is a category of go-live surprise. The single most important output is the **vendor contact + lead time** answer, because third parties are the usual critical path: your build can be done in weeks while a vendor's test-endpoint request sits in their queue for months.

## 1. Endpoint inventory

For each system in scope, one row each:

- System name, owner (business) and technical contact.
- Direction: Workday -> system, system -> Workday, or bidirectional.
- Exact endpoint(s): URL/host per environment (test AND prod - if the vendor has no test endpoint, that is a finding, not a footnote).
- Protocol: REST, SOAP, SFTP file drop, database, message queue.
- On the Workday side: which surface - RaaS report, WQL, public web service (name the service and version, e.g., Staffing v43.0), Extend API, orchestration? Note that FDM/master-data creation is SOAP-only; pin the web-service version early because payload shapes differ across versions. The Workday-side surface is verifiable live via tenant-ops (anonymous WSDL fetch pins service + version; WQL dataSources confirms queryability - wd-extend-dev references/tenant-ops.md).

## 2. Authentication

- Method per endpoint: OAuth 2.0 (which grant type?), client certificate, basic auth, API key, or Workday ISU (Integration System User).
- Who issues credentials, and what is the request lead time? Credential provisioning is a classic hidden dependency.
- For ISUs: which security groups/domains does the ISU need (Get and Put separately)? Who at the client grants them?
- Certificate expiry and rotation ownership - decide now who gets the page when it expires in prod.
- Any IP allowlisting? Whose firewall team, and their lead time?

## 3. Payloads

- Request a **real sample payload per message type** (anonymized), not just a schema. Schemas describe intent; samples reveal truth (optional fields that are always empty, "string" fields carrying dates, inconsistent casing).
- Field-level mapping: source field -> target field -> transformation. Unmapped required fields on the target side are design decisions, not defects.
- Character encoding, date/timezone conventions, decimal/currency formats.
- Maximum payload size and whether the API paginates - matters at volume.

## 4. Error and retry semantics

- What does a failure look like per endpoint - HTTP codes, SOAP faults, an "OK" response with an error body? (Some vendors return 200 with errors inside; you must ask.)
- Is each operation **idempotent**? If the same request is sent twice, is data duplicated? This dictates the retry design.
- Retry policy: automatic retries safe? Backoff? Poison-message handling after N failures?
- Who is notified on failure, via what channel, and what is the manual remediation path? An integration with no remediation runbook is not done. (e.g., in a staffing automation, "what happens to a worker whose transaction returned non-200" was a top open item.)
- Partial-failure behavior for batch payloads: all-or-nothing, or per-record?

## 5. Frequency and volumes

- Trigger: schedule (what cadence, what timezone, what conflicts - nightly maintenance, close week?), event-driven, or manual launch?
- Records per run: typical, peak, and the theoretical max (first run / backfill is often 100x steady state).
- Vendor-side rate limits or throttling?
- SLA: how stale may the data be before the business notices? This drives cadence honestly, instead of defaulting to "real-time" nobody needs.

## 6. Middleware

- Is there middleware in play (Boomi, MuleSoft, Workday Studio, an ESB), or is this point-to-point?
- If middleware exists: who owns it, what is their change/release process, and what is THEIR lead time? Middleware teams have their own backlog - a two-week build can hide behind a six-week middleware release cycle.
- Does the client have a standard ("all integrations go through X")? Discovering that standard late means rework.

## 7. Third-party vendor contacts and lead times - the critical path

- Named technical contact at each vendor, with an escalation path. "Support ticket queue" is not a contact.
- Lead times, asked explicitly and separately: test credentials; test-endpoint access; a joint test session; prod credentials; any vendor-side configuration or professional-services work (some vendors charge and schedule for enabling an API).
- Does the vendor require a signed agreement, security review, or data-processing addendum before granting access? Legal review can be the longest pole of all.
- Put every vendor dependency on the project plan with a date the moment you learn it - vendor lead time consumed early is free; discovered late it slips go-live.

## 8. Test-environment availability (vendor side)

- Does the vendor have a sandbox/test environment at all? With realistic data, or empty?
- Can it receive writes without real-world side effects (no real emails, payments, shipments)?
- Refresh cadence - will your test data survive to E2E testing?
- Can the vendor participate in scheduled end-to-end test windows? Book their calendar as early as tenant test windows.
- Match environments explicitly: which Workday tenant pairs with which vendor environment, and confirm nothing in the test path can touch prod.

## Vertical domain cues - Healthcare & Higher-Ed

When the client is a Healthcare or Higher-Ed org, a little domain vocabulary makes discovery faster and sharper - you spot the Workday-adjacent hooks (and the compliance landmines) before the client has to explain them. A domain cheat-sheet lives in **wd-extend-dev** `references/domain-patterns-hc-highered.md` (externally-sourced; verify against the client's real systems). Use these cues to steer the sections above:

- **Healthcare:** ask which EDI sets are in play (837P/837I claims, 835 remittance/denials, 270/271 eligibility, 276/277 status) and whether clinical detail arrives as HL7 v2 (ADT/ORU) or FHIR R4. Pin the charges->GL summarization, the denials-analytics ask, provider/credentialing reconciliation, and - the usual landmine - the clinical department <-> Workday cost-center/worktag crosswalk.
- **Higher-Ed:** for sponsored research, get the F&A/indirect rate tiers + MTDC base, fringe rate, subaward caps, cost-share, and tuition remission - they drive Workday Grants config. For reporting, expect periodic IPEDS/CDS extracts (calendar-driven, category crosswalks). If the university runs a health center, establish the FERPA (student) vs HIPAA (patient) split up front - it constrains security domains and who may see what.

## Output

Feed answers into the design document's integration tabs per the **wd-design-doc** skill. Anything unanswered - especially vendor lead times - becomes an open item with an owner and a chase date, per that skill's open-items conventions.
