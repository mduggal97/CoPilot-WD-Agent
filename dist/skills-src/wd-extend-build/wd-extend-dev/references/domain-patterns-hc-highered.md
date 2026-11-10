# Domain patterns - Healthcare & Higher-Ed (discovery/design cheat-sheet)

> (!) **Externally-sourced domain reference - verify before you rely on it.** Every fact below is a *discovery/design CUE*, mined/inspired from public skillsmp.com skills (cited inline). It is **not** an authoritative spec for any client's actual systems, contracts, or regulations. Standards drift (EDI companion guides, FHIR profiles, F&A rate agreements, IPEDS survey years all vary by org and year). Treat each item as "ask the client about this," then confirm against their real interfaces, rate agreements, and compliance posture - same verify-before-promote discipline as the other wd-extend-dev references (see `pmd.md`, `custom-agents.md` (!) flags).

**What this file is / isn't.** It is a vocabulary + landscape crib so you can hold an intelligent first conversation with a Healthcare or Higher-Ed client and spot the Workday-adjacent hooks. Discovery *methodology* (how to run the sessions, what to ask, vendor-lead-time discipline) is owned by **wd-discovery** - this file only supplies the domain nouns that skill's `integration-discovery.md` points at. Don't re-own discovery here.

> **Workday FUNCTIONAL-SKU literacy** (what each Workday module does - HCM, Financials, Payroll, Student, Analytics - its process areas, config objects, and terminology) lives in **wd-discovery** `references/workday-functional-skus.md` + its domain files (doc-sourced from official Workday course manuals). This HC/Higher-Ed file is the *industry* crib; that set is the *product-functional* crib. Use both in discovery.

---

## Healthcare / Revenue Cycle

The revenue cycle = patient encounter -> charge -> claim -> payment/denial. Workday sits on the **finance** end (GL, cost centers, analytics), not the clinical end - so the cues are about *where clinical/claims data crosses into Workday-finance*.

### EDI transaction map (X12 - the claims/payment rails)
Inspired by skillsmp `medical-billing`. These are the standard X12 transaction sets a payer/clearinghouse exchange uses:

| X12 set | Name | Carries (cue) |
|---|---|---|
| **837P** | Professional claim | Physician/clinician charges (CMS-1500 world) - service lines, CPT/HCPCS, diagnosis, rendering provider |
| **837I** | Institutional claim | Facility charges (UB-04 world) - revenue codes, room/board, DRG |
| **835** | Remittance advice | What the payer actually PAID: paid amount, adjustments (CARC/RARC reason codes), patient responsibility -> the money that lands in GL |
| **270 / 271** | Eligibility inquiry / response | Is the patient covered? Benefits, copay, deductible - front-of-cycle |
| **276 / 277** | Claim status inquiry / response | "Where is my claim?" - pending/paid/denied status |

**Workday-adjacent angle (the actual integration surface):**
- **Charges -> GL:** posted charges/payments summarized into Workday journal lines (often via a Prism staging layer, not row-level).
- **Denials analytics:** 835 adjustment/reason codes feed denial dashboards - a common Prism + Extend reporting ask.
- **Provider / credentialing data:** provider master (NPI, taxonomy, credentialing status) reconciled against Workday worker/supplier records.
- **Cost-center <-> department mapping:** clinical department -> Workday cost center/worktag is the mapping that makes charge data postable. Pin this crosswalk early; it's the usual design landmine.

### Clinical data formats at a glance (when clinical detail is in scope)
- **HL7 v2** (legacy, still dominant in-hospital; skillsmp `parsing-hl7v2-messages`, `ehr-data-parsing`): pipe-delimited segments. Cues you'll hear -
  - `MSH` = message header (routing, message type e.g. ADT^A01)
  - `PID` = patient identification (demographics, MRN)
  - `OBX` = observation/result (a lab value, a vital)
  - **ADT** = admit/discharge/transfer feed; **ORU** = observation/result feed.
- **FHIR R4** (modern REST/JSON API; skillsmp `fhir-bulk-data`, `ehr-data-parsing`): resources instead of segments -
  - `Patient`, `Coverage`, `Claim`, `Observation` (rough FHIR equivalents of PID / eligibility / 837 / OBX).
- **FHIR bulk `$export` -> Prism ingestion pattern** (skillsmp `fhir-bulk-data`): the EHR's Bulk Data `$export` emits NDJSON files per resource type; land those files and ingest to **Prism** as the analytics base, rather than calling FHIR row-by-row. This is the cleanest Workday-side pattern when a client wants EHR data blended with financials.

**Design cue:** most Workday work needs *aggregated/financial* slices, not raw clinical records. Push clinical parsing (HL7/FHIR) to the EHR/clearinghouse/middleware side and receive a summarized feed - smaller egress surface, fewer PHI headaches.

---

## Higher-Ed / Research & Student

Two distinct worlds: **sponsored research** (grants/awards -> Workday Grants & Financials) and **student** (SIS, IPEDS/CDS reporting). Workday Grants is the anchor for the research side.

### Sponsored-research budgeting terms -> Workday Grants (cues)
Inspired by skillsmp `su-osp-budget` (Office of Sponsored Programs budgeting):

| Term | Plain English | Workday-adjacent cue |
|---|---|---|
| **F&A / indirect rate** | "Facilities & Administrative" overhead recovered on top of direct costs; negotiated **rate tiers** (on-campus vs off-campus, research vs instruction) | Grant's F&A rate + base drives auto-calculated indirect; confirm which negotiated tier and effective dates |
| **MTDC** | Modified Total Direct Cost - the *base* F&A is applied to (excludes equipment, tuition, the part of each subaward over $50,000 - over $25,000 on federal awards made before 2024-10-01 - etc.; 2 CFR 200.1, 2024 revision) | The exclusion rules are the tricky part of grant budget config |
| **Fringe** | Benefits loaded onto salary by a negotiated fringe rate | Fringe rate by employee class -> payroll costing on the grant |
| **Subaward caps** | Pass-through funding to another institution; F&A charged only on the first $50,000 of each subaward for federal awards made on or after 2024-10-01, and on the first $25,000 for earlier awards unless the awarding agency applied the 2024 rule to them (2 CFR 200.1 "Modified Total Direct Cost", 2024 revision) | Drives a worktag/spend-category split so F&A base is computed right; record which threshold each award uses |
| **Cost-share** | Portion of project cost the institution commits (not billed to sponsor) | Tracked as a separate grant/worktag; reportable to sponsor |
| **Tuition remission** | Grad-student tuition charged to a grant | Special spend category, often F&A-exempt |

**Workday angle:** these map to Grant / Award / Grant Hierarchy config, F&A rate setup, and grant worktags on spend. Extend apps here tend to be *pre-award budget builders* or *post-award variance/attestation* tools feeding Workday Financials/Prism.

### IPEDS / CDS reporting structures at a glance
- **IPEDS** (skillsmp `education-data-source-ipeds`): federal Integrated Postsecondary Education Data System - mandatory surveys (Enrollment, Finance, Human Resources, Graduation Rates, etc.). The **Finance** and **HR** surveys pull from Workday Financials/HCM - cue: a reporting/Prism extract mapped to IPEDS survey categories, run on the federal survey calendar.
- **CDS** (skillsmp `cds-extractor`): Common Data Set - a standardized institutional dataset (enrollment, admissions, financial aid, faculty) shared with publishers/rankings. Overlaps IPEDS categories; cue: another standardized extract, often student-system-sourced.

**Design cue:** both are *periodic standardized extracts*, not real-time integrations - batch/scheduled, calendar-driven, with category crosswalks as the real work.

### FERPA vs HIPAA data-handling split (universities with a health center)
Inspired by skillsmp `us-privacy-federal`. When a university also runs a hospital/clinic, two regimes collide - and the same person can be a *student* and a *patient*:
- **FERPA** governs **education records** (student data) - the student-system / registrar side.
- **HIPAA** governs **PHI** (patient/clinical data) - the health-center side.
- **Cue:** a student treated at the university health center generates BOTH; which record is which determines who may see it and how it's stored. Never blend student and patient data in one Extend BO or Prism dataset without confirming the governance line. Ask *early* which regime each data element falls under - it constrains security domains, data residency, and who can be granted access.

---

## Cross-refs
- Discovery methodology, intake questions, vendor lead-time discipline -> **wd-discovery** (`references/integration-discovery.md` - its "Vertical domain cues" subsection points here).
- FHIR-bulk -> Prism ingestion mechanics, RaaS/WQL/LDQ, Prism-in-Extend -> `prism-and-reporting.md`, `external-apis-and-genai.md`.
- Grants/worktag/cost-center config verification against a live tenant -> `tenant-ops.md` (THE WRITE GATE).
- Security-domain / data-egress governance (the how, once you know the FERPA/HIPAA/PHI split) -> `security-setup.md`, `external-apis-and-genai.md`.
