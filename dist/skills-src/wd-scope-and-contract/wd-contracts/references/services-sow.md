# Professional-Services SOW - content skeleton (bespoke Extend build)

For a **bespoke professional-services engagement** - a custom Extend/integration build delivered as a project (T&M or fixed-fee), NOT a subscription to a pre-built Marketplace/BoW app. This is the practice's core delivery work. Use this when the ask is "draft the services SOW" / "the SOW for this build" and the deal is a scoped project, not an app subscription. (Subscription paper = the SaaS Agreement + Provisioning SOW pair, `sow.md` / `saas-agreement.md`.)

## NON-NEGOTIABLE GUARDRAIL - this is a DRAFT for legal, and the legal SHELL is not yours to write

This file is a **content** skeleton - it specifies the *business substance* a services SOW must carry (scope, assumptions, responsibilities, fees mechanics, deliverables). It is deliberately NOT a legal template:

- **The legal shell/terms must be confirmed by firm legal.** The governing terms (which master agreement this SOW executes under - a Professional Services Agreement / MSA, plus its liability, warranty, IP-ownership, indemnity, confidentiality, and termination clauses) come from the firm's confirmed PSA/services template, NOT from this file. If no confirmed PSA/services-SOW template exists in your client-docs tree, say so, request the current template from the firm's contracts team, and draft only the content inputs below in the meantime.
- **Never invent legal terms.** Every risk-allocation clause must come from the confirmed firm template or an executed precedent. Where the deal needs a term the template lacks, insert a highlighted placeholder describing the need - do not write the clause.
- **Mark every output** "DRAFT - pending firm legal/contracts review" in the header/title.
- **Flag every deviation** from the template inline (`[DEVIATION FROM TEMPLATE: ...]`) and in the closing Open Placeholders & Deviations list.

Why: drafting novel legal terms is unauthorized practice of law and firm/personal liability; the reviewers can only catch what is visibly flagged. This file gets the *substance* right so legal can focus on the shell.

## Where the content comes from

Never compose scope/assumptions/pricing from memory - pull them from the upstream estimate. The primary source is **wd-estimate `references/sow-handoff.md`** (the estimate's assumptions ARE the SOW's protective wall) plus the design doc and the proposed timeline:

| SOW section | Source |
|---|---|
| Scope of services, deliverables | Design doc scope (wd-design-doc) + the enumerated apps/integrations from wd-estimate `sow-handoff.md` |
| Assumptions, exclusions, client responsibilities | wd-estimate `sow-handoff.md` - lift the assumption/exclusion/responsibility lists directly |
| Timeline / milestones | Proposed timeline (wd-estimate step, or the wd-pm plan skeleton) |
| Fee structure, hours by role, rates | UET pricing output (wd-estimate) - T&M rate table or fixed-fee total; rates are engagement inputs, never hardcoded |
| Client info, signers, entity structure | Client program facts (see Engagement inputs, SKILL.md) |

If a source artifact doesn't exist yet, placeholder it (highlighted `[BRACKETED - needs: ...]`) and name which artifact resolves it.

## Section-by-section content skeleton

### Title block + preamble
- Heading: `Statement of Work` / `Workday Extend Professional Services: <Engagement / App Name>`.
- Preamble: identifies this as an SOW executed under the governing **Professional Services Agreement / MSA dated ___** between the firm's contracting legal entity (the "Service Provider" - pull from your contracts team) and the Client. `[legal shell - confirm the governing-agreement name and date against the executed copy]`.
- Effective Date convention (last signature date vs. a fixed start date) - confirm with the MD, placeholder until confirmed.
- Client Information table (as in `sow.md`): Client legal name / address / state of incorporation | contract contact name / phone / e-mail (the contract contact, not the SME).

### 1. Scope of Services
The section reviewers and clients actually read. Draft it fully from the design doc + estimate - no template boilerplate:
- **Objective paragraph**: what the engagement delivers end-to-end (1-3 sentences from the design-doc overview / opportunity summary).
- **In-scope services**, enumerated so "add another X" is visibly out of scope: the apps/integrations to be built, and per item the archetype-level description (business objects, page groups/variants, business processes + approval complexity, orchestrations + triggers, external integrations, Prism/reporting, data conversion, security design). Mirror the estimate's decomposition - the enumeration IS the scope boundary.
- **Phases of work**: Discovery -> Design -> PoC/Build -> Unit Test -> UAT/E2E support -> Deploy/Cutover -> Hypercare (match the estimate's phase structure; name the Workday production-approval gating docs - Volumes Questionnaire, Performance Testing - as in-scope deliverables where applicable, wd-deployment).

### 2. Assumptions
Lift directly from the estimate's assumption list (wd-estimate `sow-handoff.md`) - these are the protective wall:
- Volumes assumed; number of design cycles included; number of UAT defect-fix rounds included.
- **Tenant/environment assumptions**: client provides a dedicated dev/impl tenant (and which), Extend/Innovation Services SKU is owned and within capacity, access + security grants provided within X business days (see section 4). Name the tenants assumed available and when.
- Client staffing: SME availability for scheduled sessions; security-admin turnaround.
- Data-conversion scope (or its explicit exclusion); historical-data cutoff.
- Standard-hours / working-calendar assumptions for T&M; any assumed dependency on third parties.
- Each unstated assumption that later slips becomes an unpriced change - if in doubt, state it.

### 3. Exclusions / Out of Scope
State them explicitly - silence reads as inclusion (same logic as the estimate's exclusions guidance):
- Legacy-system changes; historical data conversion beyond the stated cutoff; integrations not enumerated in section 1; report development beyond the listed set.
- Post-hypercare / ongoing support (unless a separate managed-services line is added); Workday-side subscription/SKU/Flex-Credit run costs (the client's responsibility - see the Flex Credit terms in SKILL.md); training beyond the stated KT scope; tenant remediation / tenant-readiness work.
- Any second-app or module scope not enumerated in section 1.

### 4. Roles & Responsibilities (RACI-lite)
A two-column split plus a light RACI. Do not deep-model roles here - point to the delivery role model:
- **Service Provider (firm) responsibilities**: deliver the in-scope services and deliverables; staff the agreed pod (Developer Lead, Developer(s), Functional Consultant, PM, SME/MD oversight - the estimate's staffing model); run design/build/test; produce the design doc, build, test evidence, and KT materials; manage the change-control log (section 7).
- **Client responsibilities** (lift from the estimate's client-responsibilities list): provide tenant access + security grants within X business days; make SMEs available for scheduled sessions; execute UAT; provide/validate test data; return sign-offs within Y business days (schedule protection); notify of Workday changes impacting the build; validate fitness-for-purpose before production.
- **RACI-lite table** (optional but recommended for multi-party deals): rows = key deliverables/decisions, columns = Firm / Client / (third party), cells = R/A/C/I with a named Accountable owner. For a full stage x task RACI model, the delivery-side owner is the project's RACI (wd-pm); this SOW carries only the contract-level responsibility split.

### 5. Deliverables & Acceptance Criteria
- **Deliverables list**: name each deliverable (design document, configured app in the named tenant(s), unit-test evidence, UAT support, deployment/cutover run, KT materials/session, Workday gating docs) with a one-line description and the phase it lands in.
- **Acceptance criteria + process**: how each deliverable is accepted - client review window (e.g. N business days), what constitutes acceptance (written sign-off or deemed-accepted-if-no-response-in-N-days), and how rejections/rework are handled. Deemed-acceptance language is a **legal-shell item** - `[legal shell - confirm acceptance/deemed-acceptance mechanics with legal]`; this file only flags that the SOW must have one.

### 6. Project Timeline / Milestones
- Derive from the estimate's phase LOE and pod size; show it per workstream with gates marked (design sign-off, UAT complete, Workday production approval, go-live).
- **Milestone table**: milestone | target date/duration | dependency | (for fixed-fee) associated payment. Tie payment milestones to gates matching the estimate's phase structure.
- Note schedule assumptions (start date dependency on contract signature + tenant access; Workday production-approval review lead time - submit the gating docs EARLY, wd-deployment).

### 7. Fee Structure - describe BOTH models, pick per deal
Rates/amounts are **engagement inputs** - never hardcode a rate; pull from the UET and use placeholders/ranges in the skeleton.

- **Time & Materials (T&M)**:
  - Fees = hours actually worked x role bill rate, per a **rate table** (role | bill rate `[RATE - needs: approved bill rate per role from UET]`). Invoice monthly in arrears against actual hours.
  - Include a **not-to-exceed (NTE) cap** and the estimated hours-by-role/phase from the UET as the planning basis; state that hours beyond the NTE require an approved change order (section 8).
  - State the assumptions the estimate rests on (section 2) as the basis for the estimate-to-NTE.
- **Fixed-fee**:
  - Fees = a fixed total `[FEES - needs: approved fixed-fee total from UET]`, invoiced against the payment milestones in section 6 (e.g. % at kickoff / design sign-off / UAT / go-live).
  - The fixed fee is predicated on the section-2 assumptions and the section-1 scope; scope/assumption changes re-price via change order (section 8). Make the assumption-dependence explicit - it is what protects a fixed fee.
- **Which to use**: T&M where scope is uncertain or discovery-led; fixed-fee where scope is well-bounded and the assumptions hold. State the chosen model unambiguously; do not blend without saying how (e.g. fixed-fee for defined phases + T&M for support).

### 8. Change Control
- Changes to signed scope/assumptions go through a written change-order process: requested change -> impact assessment (scope, hours, fee, timeline, priced from the estimate model, wd-estimate) -> both-party written approval -> the SOW/fee updated.
- **Cross-reference the delivery-side mechanics**: the design-change-control convention is owned by **wd-design-doc** (change control + the yellow-highlight open-items convention); the running change-request log is owned by **wd-pm** (the CR log). This SOW's change-control clause is the contractual gate; those skills own how the change is assessed and tracked. State that material changes are re-priced from the estimate model and papered as a signed change order under this SOW.

### 9. Invoicing & Expenses
- Invoicing cadence (monthly in arrears for T&M; per milestone for fixed-fee); payment terms (net-N days) - `[legal shell - confirm payment terms with legal]`.
- **Expenses**: whether travel/expenses are billed separately at cost (with any client T&E policy applied) or included; approval threshold for pre-authorized expenses. Placeholder the client's T&E policy if provided.
- **Flex Credit / run-cost note**: ongoing Flex Credit consumption for the built app/agents post-go-live is the client's responsibility and is not part of these fees (see the Flex Credit commercial terms in SKILL.md; figures live in wd-estimate `references/flex-credits.md`). State the estimated annual consumption from the design doc for the client's budgeting.

### 10. Warranty & Limitations (LEGAL SHELL - do not draft)
- The warranty scope (e.g. a limited defect-correction warranty period on delivered code), warranty disclaimer, limitation of liability, and IP-ownership terms are **risk-allocation clauses owned by firm legal** - fill only defined blanks from the confirmed PSA/services template; flag any needed change with `[DEVIATION]` and route to legal. `[legal shell - warranty, liability cap, IP ownership, indemnity per the confirmed PSA/services template]`.
- This file only asserts the SOW MUST carry these - it does not supply the language.

### 11. Term & Termination (LEGAL SHELL - do not draft)
- Term of the engagement (from Effective Date through completion/acceptance of the final deliverable, or a stated end date), and termination provisions (for cause, for convenience with notice, effect on fees/work-in-progress) come from the confirmed PSA/services template. `[legal shell - term + termination per the confirmed PSA/services template]`.
- For T&M, note the effect of termination-for-convenience on hours already worked; for fixed-fee, on milestones reached. This is a legal-shell mechanic - flag it, do not write it.

### Signature block
Two-column In-Witness-Whereof block: the firm's contracting legal entity signed by the firm's authorized signatory | the client's legal-entity block(s). Include every required entity block plus any legal-department review/stamp line the client requires (see Engagement inputs). Never drop a required entity block.

## Closing (run on every draft)
- Append the **Open Placeholders & Deviations** list (every `[BRACKETED - needs: ...]`, every `[legal shell - ...]`, every `[DEVIATION FROM TEMPLATE: ...]`).
- Stamp **DRAFT - pending firm legal/contracts review**.
- Handoff note names the reviewers: engagement MD + firm contracts/legal. wd-comms drafts the cover email if client-facing.
