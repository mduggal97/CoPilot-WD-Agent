# Healthcare: Epic / FHIR Boundary

How a hosted tool (or a Workday-Extend/O4I flow acting on its behalf) integrates
WITH Epic - the API surfaces, the auth flow, and the recurring boundary
patterns where Epic and Workday both think they own a piece of data. Read
patterns.md first; this file specializes those patterns to Epic and adds the
Workday-Epic design questions a generic SaaS integration never raises.

**Why this file exists:** Epic holds 43.7 percent of US acute-care EHR
market share (KLAS 2025 data, reported via FierceHealthcare, 2025), so most
large Workday healthcare clients are Epic shops. Who masters what, which
direction data flows, and which transport carries it is a paid governance and
design problem on nearly every academic-medical-center engagement. This file
is Epic-side API and design literacy only - no EIB, Studio, or O4I flow is
authored here (that is wd-integration-dev / wd-extend-dev). Genericized from a
practice supply-chain product build - no client or internal product names
appear below.

**Version-sensitive:** Epic's developer program was renamed twice - App Orchard
(launched ~2017) became App Market (2021), then retired in December 2022. As of
this writing the program runs as **Epic Vendor Services** (the paid developer/
certification program) plus **Epic Showroom** (the public marketplace,
including a **Connection Hub** tier for pre-vetted connectivity and a
**Toolbox/Workshop** tier for build resources). Confirm current tier names and
fees against fhir.epic.com and open.epic.com before quoting anything to a
client - Epic has renamed this program before and will again.

## Contents

- [1. Epic integration landscape map](#1-landscape-map)
- [2. US Core / USCDI - what matters for non-clinical work](#2-us-core-uscdi)
- [3. The Workday-Epic boundary patterns](#3-boundary-patterns)
- [4. Auth - Backend Services JWT flow, end to end](#4-auth-backend-services)
- [5. Gotchas](#5-gotchas)

---

## 1. Landscape map

Epic exposes several integration surfaces; which one applies depends on what
you are moving and who initiates it.

- **FHIR R4 REST APIs** - the modern, standards-based surface. A public sandbox
  is available at fhir.epic.com with synthetic patients, free registration, and
  no health-system sponsor required to start building - where you prototype
  and where SMART on FHIR and Backend Services both live. Source:
  fhir.epic.com (accessed 2026-09).
- **SMART on FHIR app launch** - a user-facing app launched FROM inside Epic
  (or standalone), where a clinician or patient is present and authorizes the
  app via an OAuth authorization-code flow. Use when a human is in the loop -
  not the pattern for a backend batch job.
- **Backend Services (SMART Backend Services)** - unattended, server-to-server
  access using OAuth2 client-credentials with a signed JWT (section 4). The
  pattern most Workday-adjacent integrations actually need.
- **HL7v2 interfaces (Bridges)** - Epic's long-standing messaging engine for
  ADT, ORM, ORU, and similar message types over MLLP. Most EXISTING Epic
  interfaces at a hospital are still HL7v2, not FHIR - inventory depletion,
  ADT feeds, and charge messages frequently ride this rail today. Do not
  assume "Epic integration" means FHIR; ask what the existing interface
  engine already runs.
- **Interconnect web services** - Epic's older proprietary SOAP/API layer
  (pre-dating FHIR), still present for functionality FHIR does not yet cover.
  Treat as legacy - reach for it only when nothing else exposes the data.
- **File-based** - flat-file exchange (CSV, fixed-width, X12) is still common
  for high-volume batch feeds (charge extracts, item-master loads). Same
  file-transport discipline as any other flat-file interface (SFTP/PGP) - no
  Epic-specific mechanics beyond the file layout itself.

Rule of thumb: **human-present, app-launched -> SMART on FHIR; unattended
server-to-server -> Backend Services; high-volume real-time clinical messaging
-> HL7v2/Bridges; bulk periodic -> file-based.** Confirm which surfaces a given
Epic customer has actually enabled - not everything here is turned on at every
site, and enabling a new one is itself a change request with its own lead time.

Sources: fhir.epic.com (public sandbox, Vendor Services registration); Epic
Vendor Services / Showroom / Connection Hub program pages, open.epic.com
(HL7v2 interface catalog).

---

## 2. US Core / USCDI

For non-clinical, Workday-adjacent integrations you rarely need the full FHIR
resource catalog. **US Core** profiles the base FHIR resources against the
**USCDI** (US Core Data for Interoperability) data classes that ONC/CMS
mandate for certified EHR technology - this is why the same handful of
resources shows up in nearly every Epic integration regardless of vendor.

The resources that matter outside clinical documentation:

- **Patient** - demographics and identifiers. In a Workday-adjacent flow this
  is almost always about the IDENTIFIER, not the clinical record (section 3c
  MRN gotcha) - do not pull more of the resource than the integration needs.
- **Encounter** - a visit/admission/episode of care. Relevant when a boundary
  flow needs to know WHEN care happened (e.g., timing a bill-only charge to an
  encounter).
- **Practitioner** - the clinical-provider record, at the center of the
  provider-master boundary question (section 3b) - Epic's Practitioner and
  Workday's Worker/Position both claim to be authoritative about "who this
  person is."
- **Organization** - a legal entity, department, or service line. Maps Epic's
  org hierarchy to Workday's supervisory-org/cost-center hierarchy - a mapping
  exercise, not a 1:1 join, since the two systems model hierarchy differently.
- **Location** - a physical site (an OR, unit, or clinic room). Matters for
  supply-chain and case-costing work where usage must attribute to a place.
- **Device** - the UDI-bearing resource for a physical device or implant, the
  FHIR-side anchor for the supply-chain boundary (section 3a) - it can carry
  the Unique Device Identifier that also drives the openFDA GUDID lookup.

Do not over-scope: pulling PHI-adjacent resources (full Patient demographics,
clinical notes) into a non-clinical integration multiplies both compliance
surface (HIPAA minimum-necessary) and Epic's own scrutiny during
production-access review (section 5). Scope the resource list to exactly what
the boundary question in section 3 requires.

Sources: US Core Implementation Guide (hl7.org/fhir/us/core); USCDI
(healthit.gov/isa/united-states-core-data-interoperability-uscdi); ONC
Certification Program (healthit.gov).

---

## 3. The Workday-Epic boundary patterns

This is the consulting-value section. Every large Epic+Workday client hits
these four boundaries; the design question in each is what an engagement
is actually paid to resolve. (Genericized - no client or product names.)

### 3a. Supply chain - bill-only / implant case charges

An implant or bill-only device used in a case must become both a clinical
charge (Epic) and a procurement/AP event (Workday Financials/SCM), usually via
**GHX** sitting in the middle handling item-master and PO/order lifecycle
between hospital, GHX, and distributor.

- **Who owns which master:** the usage event originates in Epic (case
  documentation, charge capture); the item MASTER (vendor catalog, contract
  pricing, GL mapping) typically lives in Workday SCM or a GHX-brokered
  catalog. Item-master ALIGNMENT across all three (Epic charge description,
  GHX catalog, Workday item master) is the recurring design gap - the same
  physical item can carry three different identifiers if not deliberately
  mapped.
- **Direction:** predominantly Epic -> Workday (charge/usage flows outbound
  to become a financial transaction), with GHX returning order/backorder
  status toward the hospital.
- **Transport:** historically HL7v2 (charge messages) or file-based extracts;
  increasingly FHIR Device/ChargeItem-adjacent resources on modernized sites -
  do not assume FHIR is live; verify per site.
- **UDI/device enrichment:** the openFDA GUDID (Global Unique Device
  Identification Database) is a PUBLIC, free API (api.fda.gov/device/udi.json)
  that resolves a Unique Device Identifier's DI segment to manufacturer,
  brand, and device attributes - useful for enriching a bill-only charge
  record without any Epic or GHX credential. Source: open.fda.gov/apis/device/udi.
- **Governance question:** when the same device is represented three ways,
  which system is the source of truth for EACH attribute (price, GL account,
  clinical description) - and who owns reconciling drift when one side
  changes and the others do not.

### 3b. Provider master + credentialing boundary

A physician or advanced-practice provider exists as a Practitioner in Epic
(clinical privileging, order-entry identity) AND as a Worker/Position in
Workday (HR, payroll) - often ALSO in a dedicated credentialing system (e.g.,
symplr) that neither natively replaces.

- **Who owns which master:** Workday HCM is typically authoritative for
  employment status and compensation; Epic for clinical privileging and
  order-entry access; the credentialing system for license/board/privilege
  verification. No single system should be treated as master of the whole
  provider record - that is the mistake clients make before a consultant engages.
- **Direction:** typically Workday -> Epic for the active-employee signal
  (provisioning gate), with credentialing status flowing bidirectionally as a
  gate on both employment and clinical access.
- **Transport:** HL7v2 (SIU/ADT-adjacent provider messages) or a scheduled
  file/API sync is common; FHIR Practitioner is where newer builds lean, but
  legacy HL7v2 feeds are frequently still load-bearing.
- **Governance question:** when a provider is terminated or suspended in ONE
  system, what is the SLA for that status propagating to the other two - and
  what breaks (order-entry access, payroll, badge access) if it does not
  propagate in time. A design doc must answer this explicitly, not infer it.

### 3c. GL / finance boundary

Epic Resolute/Prelude generates charges and revenue transactions; Workday
Financials owns the General Ledger. The question is which SUMMARY-LEVEL
postings cross from Epic's revenue cycle into Workday's GL, and at what grain.

- **Who owns which master:** Epic owns charge/revenue detail (patient-level,
  HIPAA-covered); Workday owns the GL and chart of accounts. Detail almost
  never crosses in full - what crosses is a SUMMARIZED, de-identified posting
  (by department/cost center/revenue code).
- **Direction:** Epic -> Workday, typically a batch journal-entry feed on a
  daily or per-shift cadence.
- **Transport:** file-based (a defined extract landing via SFTP) dominates
  here - a batch-ETL boundary (patterns.md section 2), not API-driven, given
  volume and the PHI-minimization requirement (summarize before it leaves
  Epic's boundary).
- **Governance question:** what grain of summarization satisfies both Finance
  (enough detail to reconcile) and Compliance (no PHI leaves the clinical
  system unnecessarily) - negotiated per client, not a fixed answer.

### 3d. Timekeeping adjacency - UKG in the middle

Clinical staff often punch and get scheduled in **UKG (Dimensions/Pro)** for
24/7 unit-based scheduling neither Epic nor Workday models natively; UKG feeds
time to Workday Payroll, while Epic may separately reference staffing data for
unit coverage views.

- **Who owns which master:** UKG owns time/attendance and clinical
  scheduling; Workday owns payroll calculation and HR system of record; Epic
  is a CONSUMER of scheduling context, not a source, in most shops.
- **Direction:** UKG -> Workday (time import for payroll) is the primary
  flow; Epic involvement is usually read-only reference, not a direct feed.
- **Transport:** a scheduled file or API-based time-import job into Workday
  Payroll - Workday-side territory (a Core Connector or O4I import) once the
  data lands; this file stops at "UKG is the third party in the mix."
- **Governance question:** whether Epic's staffing view needs to STAY in sync
  with UKG's schedule of record, and if so how - a common source of "the
  schedule Epic shows doesn't match what payroll paid" defects left implicit.

---

## 4. Auth - Backend Services, end to end

The unattended, server-to-server pattern (patterns.md section 1's JWT-bearer
grant, specialized to Epic). Working detail level:

1. **Generate a key pair.** RSA (2048-bit minimum) or EC. Keep the private key
   in Secrets Manager (app-hosting owns this - patterns.md section 1
   cross-link); never let it leave secure storage.
2. **Register on fhir.epic.com.** Create an app registration under Vendor
   Services, select **Backend Services (client_credentials)** as the auth
   type, and upload the PUBLIC key (a JWK, or a URL to a hosted JWKS endpoint
   Epic can fetch from). Epic issues a **non-production (NONPROD) client ID**
   immediately for sandbox use; a separate production client ID is issued only
   once a real Epic customer sponsors and activates your app in their
   environment (section 5).
3. **Sign a JWT assertion per token request.** Construct a JWT with:
   - `iss` (issuer) and `sub` (subject) both set to your client ID.
   - `aud` (audience) set to Epic's token endpoint URL.
   - `jti` a unique value per request (replay protection).
   - `exp` a short expiry (Epic's guidance: a few minutes out, not hours).
   - Sign with your PRIVATE key, matching the algorithm (RS384/ES384 per
     Epic's current spec) declared in the JWT header.
4. **POST to the token endpoint** with:
   - `grant_type=client_credentials`
   - `client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
   - `client_assertion=<the signed JWT from step 3>`
5. **Receive a short-lived access token** (typically ~60 minutes) and use it
   as a Bearer token on subsequent FHIR REST calls. Cache and refresh before
   expiry (patterns.md section 1) - do not sign a fresh JWT per API call, only
   per token refresh.

Gotchas specific to this flow:

- **NONPROD vs production client IDs are DIFFERENT credentials against
  DIFFERENT base URLs** (sandbox host vs the customer's own Epic instance
  host). A NONPROD ID never works against a live customer instance and vice
  versa - a classic "works in sandbox, 401s at the client" defect that is a
  wrong-environment credential, not a code bug (same KT note as patterns.md
  section 1).
- **The public key registration step is per-app, and re-keying requires
  re-registration** - do not treat key rotation as a zero-touch operation the
  way you might for a platform with a client-secret rotation API.
- Each Epic CUSTOMER instance requires its own registration/activation even
  once your app is approved at the vendor level - "approved by Epic" is not
  "connected to every hospital automatically" (section 5).

Sources: Epic on FHIR OAuth2 documentation
(fhir.epic.com/Documentation?docId=oauth2); SMART Backend Services
specification (hl7.org/fhir/smart-app-launch/backend-services.html).

---

## 5. Gotchas

- **Rate limits are per-instance and NOT publicly documented.** Unlike
  Salesforce or ServiceNow, Epic publishes no universal numeric rate limit -
  throughput is negotiated per health-system instance and depends on that
  customer's Interconnect configuration and infrastructure; two hospitals on
  the same Epic version can throttle differently. Confirm the ceiling with the
  CUSTOMER's Epic technical team before go-live design. Always implement
  exponential backoff on 429 (patterns.md section 4) regardless.
- **Bulk Data Export for volume.** For large, periodic pulls (a population
  export rather than one-record-at-a-time), Epic supports the FHIR **Bulk Data
  Export** specification - an async, file-based export job, closer in shape to
  Salesforce Bulk API 2.0 than to REST-per-record.
- **Versioning: pin FHIR R4 explicitly**, and track Epic's own release cadence
  (roughly annual platform versions per customer, each upgrading on its own
  schedule) - a resource's supported fields can differ between a customer on
  an older version and one on the latest. Verify per instance via its
  CapabilityStatement endpoint rather than assuming parity across clients.
- **Sandbox access is instant; production access is not, and is NOT
  self-service.** The public sandbox requires no sponsor. PRODUCTION requires
  a real Epic customer to sponsor your app, activate it in their environment,
  and complete that customer's own security/validation review - there is no
  path to production without a live health-system customer flipping the
  switch. Timeline is use-case-dependent and NOT fixed; do not commit a client
  to a specific week-count without confirming against that customer's own
  Epic governance process (reported industry guides, 2026 - unverified until
  confirmed with the customer's Epic team).
- **MRN / identifier validation gates on inbound data (genericized).** Any
  flow that writes INTO a Workday-side process using an Epic-sourced patient
  or encounter identifier (e.g., a bill-only charge keyed to a medical record
  number) needs an explicit validation gate before that identifier is trusted
  downstream - a malformed or stale MRN propagating into a financial record is
  a data-integrity incident, not a cosmetic bug. Validate format and, where
  possible, existence at the boundary, and dead-letter (patterns.md section 6)
  records that fail rather than letting them flow through with a bad key.
- **Do not conflate "Epic integration" with "FHIR integration."** Most
  existing interfaces at an established hospital are still HL7v2/Bridges or
  file-based; FHIR is where NEW builds should land when the resource is
  available, but assuming it is already live everywhere will be wrong at
  plenty of client sites. Ask what is actually running before proposing a
  transport.

---

Sources are cited inline above; primary sources are fhir.epic.com,
open.epic.com, hl7.org (US Core, SMART Backend Services), healthit.gov
(USCDI), and open.fda.gov (GUDID). Secondary/REPORTED sources (integration-
consultancy blogs on timelines and program-rename history) are flagged as such
in context - verify anything client-facing against the primary source before
quoting it. Epic's program names, fees, and numeric limits are the most
version-sensitive facts in this file; do not rely on them without a
fresh check against fhir.epic.com.

For the Workday-side transport once data crosses the boundary (EIB, Studio,
Core Connector, O4I orchestration), see wd-integration-dev / wd-extend-dev -
this file stops at the Epic-side API and the design question, not the Workday
build.
