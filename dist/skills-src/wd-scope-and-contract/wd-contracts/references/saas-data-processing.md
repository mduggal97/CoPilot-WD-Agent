# SaaS Data Processing, Residency & Subscription Security - contract paper for a hosted product

For the **customer-sold hosted-product path** (Marketplace/BoW app, or any firm-built tool sold as a subscription). Covers the data-protection contract paper an enterprise buyer of a hosted product will demand before signing: a Data Processing Agreement (DPA), data-residency commitments, and a subscription security exhibit. This file is new - it fills a gap the existing SaaS/SOW pair does not cover.

## Contents

1. NON-NEGOTIABLE GUARDRAIL - this is a DRAFT, not legal advice
2. Scope boundary - paper vs. operations
3. When a DPA is required
4. Controller/processor roles
5. Standard DPA sections (checklist for counsel)
6. Data residency and data location
7. Subscription security exhibit
8. International transfer mechanism (checklist level)
9. Pre-close checklist
10. Cross-links
11. Sources (general background, not advice)

## 1. NON-NEGOTIABLE GUARDRAIL - this is a DRAFT, not legal advice

Everything in this file is **drafting structure and a checklist for counsel** - not legal advice, and not a substitute for a qualified attorney. This is not a formality:

- **Never** present any output built from this file as an executed, final, or authoritative legal document. Every draft gets marked "DRAFT - pending firm legal/contracts review" in the header or title, same as every other wd-contracts deliverable.
- **Never invent legal terms.** A DPA, residency clause, or security exhibit built here must come from the firm's confirmed template or an executed precedent. If the deal needs a term the template doesn't have, insert a highlighted placeholder describing the need - do not write the clause yourself.
- **Never treat a statute citation as advice.** Where this file names a specific law (GDPR, CCPA/CPRA) or mechanism (SCCs, UK IDTA), that is general legal background to help you recognize what a document needs to cover - not a determination that it applies to a given deal, or that a given clause satisfies it. Confirm applicability and sufficiency with the firm's legal/contracts team every time.
- **Flag every deviation** from a confirmed template inline (`[DEVIATION FROM TEMPLATE: ...]`) and in the closing Open Placeholders & Deviations list, per the SKILL.md markup rules.
- **This is not the practice of law.** Drafting novel data-protection terms without qualified review is unauthorized practice of law and a firm-level liability - a DPA or security exhibit is a binding promise about how customer data is handled, so an unreviewed clause here is a bigger exposure than an unreviewed liability cap.

## 2. Scope boundary - paper vs. operations

This file owns the **contract paper**: the DPA, the residency clause, and the subscription security exhibit as documents that get signed. It does not own whether the underlying practice is actually true.

- **product-operations/references/compliance-ops.md** (authored in parallel) owns the **operational compliance posture** - how encryption, access control, the SOC 2 program, vendor/sub-processor risk review, and incident response actually work day to day. Read it before drafting any clause below; every contractual commitment here must be a faithful restatement of what that operational program actually does, not an aspirational upgrade.
- **This file** owns turning that operational reality into binding contract language: the DPA structure, the residency commitment wording, and the security exhibit that gets attached to or incorporated into the SaaS Agreement.
- If the operational answer isn't confirmed yet (e.g., SOC 2 Type II not yet issued, sub-processor list not finalized), placeholder the clause - don't draft a security exhibit ahead of the operational fact it describes.

## 3. When a DPA is required

Default to **yes** for a hosted product unless confirmed otherwise - most enterprise buyers will not sign without one, and a Workday-adjacent hosted tool is likely to touch HR/employee data even indirectly. Concrete triggers:

- The product processes **personal data of individuals in the EU/UK/Switzerland** - GDPR's territorial scope reaches this regardless of where the firm is based (General Data Protection Regulation (EU) 2016/679, Art. 3).
- The relationship fits **CCPA/CPRA's "business" and "service provider"/"contractor"** structure - California Civil Code section 1798.140 - which applies whenever California-resident personal data is in scope, not just for California-headquartered clients.
- The data includes **employee or HR-related personal data** - treat as a near-certain yes for anything adjacent to Workday data.
- The **client simply asks for one** - many enterprise procurement/security-review processes require a DPA as a checklist item regardless of the legal analysis above.

If none of these clearly apply, still placeholder the question for legal rather than omitting the DPA - `[DPA APPLICABILITY - needs: legal confirmation of whether a DPA is required for this deal]`.

## 4. Controller/processor roles

Get this right first - it determines which party's obligations attach where in the DPA.

- **Controller** (client): determines the purposes and means of processing the personal data that flows through the hosted product. GDPR Art. 4(7).
- **Processor** (the firm, as the hosted-product vendor): processes personal data only on the controller's documented instructions. GDPR Art. 4(8); the processor's specific obligations are enumerated in Art. 28(3).
- **CCPA/CPRA equivalent**: the client is the "business," the firm is the "service provider" or "contractor" (Cal. Civ. Code section 1798.140) - similar restriction to processing only for the disclosed business purpose, no sale/share of the data, no combining it with other clients' data.
- Most hosted-product deals are this straightforward controller(client)/processor(firm) shape. Flag for legal if a deal looks like **joint controllership** (both parties determine purposes/means) or if the firm's own use of aggregated/de-identified data (see saas-agreement.md section 3.4, Service Provider Data) needs to be reconciled against the DPA's restriction to processing only on instruction.

## 5. Standard DPA sections (checklist for counsel)

Use this as the section list to verify against the firm's confirmed DPA template - or, if none exists yet, as the skeleton to hand to legal for template development. Do not draft clause language from scratch; this is the checklist, not the clause.

1. **Subject matter and duration** - what processing this DPA covers and for how long (tied to the SaaS Agreement/SOW term).
2. **Nature and purpose of processing** - what the hosted product does with the data (e.g., storing and displaying HR records, running the subscribed workflow) - pull from the product's actual function, not generic boilerplate.
3. **Categories of personal data and categories of data subjects** - e.g., employee name/ID/compensation data; data subjects = client's employees/contractors. Source this from the design doc's data model, not from memory.
4. **Processor obligations** - the GDPR Art. 28(3) list: process only on documented instructions, ensure personnel confidentiality, implement security measures, respect sub-processor conditions, assist with data-subject rights, assist with breach notification and DPIAs, delete/return data at term end, make available information to demonstrate compliance.
5. **Security measures exhibit** - referenced, not restated - see section 7 below. The DPA should point to the exhibit as an attachment/schedule, avoiding two documents drifting out of sync.
6. **Sub-processors and notification** - a current list of sub-processors (cloud hosting, any AI/ML inference provider, support tooling), a mechanism for updating the list, and a notice-and-objection right before adding a new one. Keep this list synced with product-operations' vendor inventory - it is the same list, viewed from the contract side.
7. **Data-subject-rights assistance** - the processor's obligation to help the controller respond to access/deletion/portability requests within the controller's own regulatory deadlines.
8. **Breach notification timing** - jurisdiction-sensitive and easy to get wrong: GDPR requires the controller to notify the supervisory authority within 72 hours of the controller becoming aware (Art. 33), which means the processor-to-controller notice window in the DPA must be short enough to leave the controller room to act - commonly drafted as prompt/"without undue delay" or a fixed short window (e.g., 24-72 hours) depending on the template. Confirm the exact figure against the firm's confirmed template or precedent; do not pick a number from this file.
9. **Audit rights** - the controller's right to audit or receive an audit report (commonly satisfied by furnishing the SOC 2 report in lieu of a full audit - see section 7).
10. **Deletion/return of data on termination** - what happens to client data when the subscription ends, and the timeframe.
11. **International transfer mechanism** - see section 8; the DPA must name the specific mechanism (SCCs, adequacy, etc.) if data crosses a restricted border.

## 6. Data residency and data location

Data residency is a **hosting/architecture fact restated as a contract promise** - it must match how the app is actually deployed, not how the buyer hopes it's deployed.

- **What it commits to**: the specific region(s) where Client Content is stored at rest, and the region(s) where it is processed (which can differ from storage).
- **Ties directly to the app's hosting region choice** - the region(s) named in the residency clause must be the actual AWS region(s) the app is deployed in (see the app-hosting skill for the firm's reference architecture and its region conventions). Do not let sales or contracts pick a residency commitment the deployed architecture can't honor.
- **Cross-region-inference caveat** - if the hosted product calls an LLM (e.g., Amazon Bedrock via the app-agentic skill's provider seam) for an AI feature, inference may run in a different AWS region than the one storing the client's data (the firm's reference architecture defaults Bedrock inference to us-east-2 regardless of the app's primary hosting region). A residency clause that promises "all data stays in [REGION]" without carving out AI/ML inference is a promise the architecture may not keep - flag this every time an AI feature is in scope.
- **Sample residency commitment structure** (a pattern to adapt, not language to sign as-is):
  > "[Client Content will be stored and processed in the [PRIMARY REGION] AWS region, except that: (a) [named sub-processors] may process data in [SUB-PROCESSOR REGION] for [purpose]; and (b) AI/ML-assisted features described in the Documentation may process data in [INFERENCE REGION] for the purpose of generating [feature output].]"
- If the client demands a single-region-only commitment and the product's AI features can't honor it, that's a `[DEVIATION FROM TEMPLATE: data residency - AI inference region conflict]` for legal and the deal team, not something to paper over by omitting the caveat.

## 7. Subscription security exhibit

The **contract counterpart** of the security-questionnaire answers product-operations maintains operationally - this exhibit takes those operational facts and turns them into a document the buyer can attach to the SaaS Agreement and rely on contractually.

Standard contents an enterprise buyer expects to see in or attached to the agreement:

- **Encryption** - at rest and in transit (e.g., AES-256 at rest, TLS 1.2+ in transit) - state the actual standard in use, not a generic aspiration.
- **Access control** - authentication method (e.g., Entra/SSO per the app-hosting skill's reference architecture), least-privilege/role-based access, MFA expectations.
- **Logging and monitoring** - what's logged, retention, and whether the client can request access to relevant logs.
- **SOC 2 attestation reference** - name the report type held (Type I vs. Type II), the audit period covered, and how it's shared (typically the report itself or a bridge letter under NDA - not reproduced in the contract body). If no SOC 2 report exists yet, say so plainly rather than implying one; a false attestation reference is a contract misrepresentation, not just an inaccurate marketing claim.
- **Incident notification** - the timeframe the firm commits to notifying the client of a security incident affecting their data, and the notification channel. Should be consistent with (or feed into) the DPA's breach-notification clause in section 5.8 above - don't let the two documents state different windows.
- **Penetration-test cadence** - how often third-party pen testing occurs and what's shared with the client (commonly a summary/attestation letter, not the raw findings report).

**Do not let this exhibit outrun the operational facts.** Pull every item above from product-operations/references/compliance-ops.md's current operational posture. An inflated security exhibit is a bigger liability than a slower "we'll confirm and get back to you" - it is a written representation the client can hold the firm to.

## 8. International transfer mechanism (checklist level)

Only relevant when personal data crosses a border with transfer restrictions (most commonly EU/UK/Switzerland to the US). Checklist, not analysis - confirm current status with legal every time, since adequacy decisions and approved mechanisms change:

- **EU Standard Contractual Clauses (SCCs)** - the European Commission's 2021 modular SCCs (controller-to-processor, processor-to-processor, etc.) are the default mechanism for EU-origin transfers absent an adequacy decision.
- **UK International Data Transfer Agreement (IDTA)** or the UK Addendum to the EU SCCs - the UK's post-Brexit equivalent, administered by the ICO.
- **Switzerland** - typically the EU SCCs with a Swiss-specific adaptation; confirm current guidance rather than assuming EU treatment applies unmodified.
- **Adequacy decisions** - the list of countries the EU/UK have deemed to provide adequate protection changes over time (e.g., the EU-US Data Privacy Framework covers many US transfers as an alternative to SCCs for participating organizations) - do not hardcode a list in contract paper as if it were evergreen; confirm current status.
- **Schrems II supplementary measures** - even with SCCs in place, EU guidance expects a transfer-impact assessment and supplementary technical/organizational measures for transfers to jurisdictions with government-access risk (including the US) - flag for legal rather than assuming SCCs alone are sufficient.

## 9. Pre-close checklist

What to have ready before a hosted-product deal can close, so the deal doesn't stall on paper that should have existed already:

- **DPA template** - confirmed by legal, ready to attach or reference (not drafted ad hoc per deal).
- **Sub-processor list** - current, matches product-operations' actual vendor inventory, with a process for the notice-and-objection updates the DPA promises.
- **Security exhibit** - current, matches actual SOC 2 status and architecture (not aspirational).
- **Residency statement** - matches actual hosting region(s) and inference region(s); AI-feature carve-out included if applicable.
- **SOC 2 status** - accurately described (Type I vs. Type II, audit period, bridge letter if the report has gone stale between annual audits).
- **BAA note** - if the product touches PHI, the Business Associate Agreement is a **separate document** from the DPA (see saas-agreement.md section 3.2) - confirm one exists or is in progress; don't let the DPA imply it covers HIPAA obligations it doesn't.

## 10. Cross-links

- **saas-agreement.md** - the master SaaS Agreement this DPA and security exhibit attach to or are incorporated into; see its section 3 (Data) for the existing PHI/PII/offshore-support clauses this file's DPA must reconcile with, not duplicate.
- **sow.md** - the Provisioning SOW; usage/fees terms live there, not in the DPA.
- **product-operations/references/compliance-ops.md** - the operational compliance posture (how encryption, access control, SOC 2, and vendor risk actually work). This file's job is to restate that posture as contract paper - read it first, every time.
- **app-hosting skill** - the AWS region and deployment facts that must match the residency clause.
- **app-agentic skill** - the Bedrock/inference-provider facts (including default region) behind the cross-region-inference caveat.

## 11. Sources (general background, not advice)

Cited to identify the concept and the authoritative text - not a legal opinion on applicability. Confirm current text and applicability with the firm's legal/contracts team before drafting.

- General Data Protection Regulation (EU) 2016/679 - Art. 3 (territorial scope), Art. 4(7)-(8) (controller/processor), Art. 28 (processor obligations), Art. 33 (breach notification), Chapter V (Art. 44-49, international transfers) - eur-lex.europa.eu.
- European Commission Standard Contractual Clauses (2021 modular SCCs) - ec.europa.eu.
- UK Information Commissioner's Office - International Data Transfer Agreement (IDTA) and UK Addendum - ico.org.uk.
- California Consumer Privacy Act / California Privacy Rights Act, Cal. Civ. Code section 1798.100 et seq. (definitions at section 1798.140) - oag.ca.gov.
- AICPA SOC 2 (System and Organization Controls) framework - aicpa-cima.com.
