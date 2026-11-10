---
name: wd-contracts
description: Draft Workday Extend contract documents - statement of work (SOW), SaaS agreement, subscription agreement, provisioning SOW, engagement letter, scope language, contract terms. Use this skill whenever the task involves a contract, "draft the SOW", an SOW for a Marketplace/BoW app subscription, a SaaS/subscription agreement for a firm-built app, contract scope/assumptions/exclusions language, term/renewal/fees sections, or turning a won estimate into contract paper. The docx skill owns Word mechanics; wd-estimate owns the estimate/assumptions/pricing that feed the SOW; this skill owns contract structure and drafting.
---

# Drafting Extend Contract Documents (SOW + SaaS Agreement)

## NON-NEGOTIABLE GUARDRAIL - everything here is a DRAFT

Every document this skill produces is a **DRAFT for firm leadership and the firm's legal/contracts team to review** - nothing more. This is not a formality:

- **Never** present output as an executable or final legal document. Mark every output "DRAFT - pending firm legal/contracts review" in the header or title.
- **Never invent legal terms.** Every clause must come from the confirmed firm template (or an executed firm precedent). If the deal needs a term the template doesn't have, insert a highlighted placeholder describing the need - do not write the clause.
- **Never touch risk-allocation clauses** (limitation of liability, warranty disclaimer, IP/proprietary rights, indemnity, termination) except to fill in defined blanks. If asked to change one, make the edit only with an inline `[DEVIATION]` flag and say plainly it needs legal review.
- **Flag every deviation from the template** - inline where it occurs AND in a deviations list at the end of the draft (see markup rules below).

Why: drafting novel legal terms is unauthorized practice of law and personal/firm liability; a silently modified liability cap or IP clause that slips through review is a firm-level risk on every renewal of a multi-year subscription. The reviewers can only catch what is visibly flagged.

## The two documents (and which one the ask needs)

The firm's Extend contract paper for Marketplace/BoW products is a two-layer structure:

1. **SaaS Agreement** - the master. One per client legal entity. Legal terms only (rights, data, fees mechanics, liability, term/termination, general). No app-specific business terms. Structure: [references/saas-agreement.md](references/saas-agreement.md).
2. **Provisioning SOW** - one per application, executed under the SaaS Agreement. All the business terms live here: scope, term, usage, fees, responsibilities, exclusions. The SOW prevails over the SaaS Agreement on conflict, so this is where deal-specific drafting happens. Structure: [references/sow.md](references/sow.md).

Routing: client subscribing to a firm-built app (Marketplace/BoW) -> this pair. First app for a new client entity -> draft both; subsequent apps -> Provisioning SOW only, referencing the executed SaaS Agreement's date (verify that date against the actually executed copy - a draft SOW has been seen referencing a SaaS date matching no executed agreement).

**Selling a CUSTOMER-SOLD hosted product (Track 2)?** An enterprise buyer of a hosted SaaS product will demand a **Data Processing Agreement**, data-residency commitments, and a subscription-security exhibit on top of the pair above. The structure + checklist for that data-protection paper is [references/saas-data-processing.md](references/saas-data-processing.md) (its operational counterpart - SOC 2 posture, security-questionnaire answers - is product-operations `references/compliance-ops.md`). DRAFT for counsel, as always - not legal advice.

Enhancement routing: paper for enhancing an already-subscribed app = **change order under the existing Provisioning SOW by default**; a new/amended Provisioning SOW only when the scope is effectively a new module/app. (!) confirm the precedent against the executed document before citing it as the pattern - a prior enhancement may have been papered under a client SOW without its form (change order vs. standalone enhancement SOW) being verified; check the executed contract set in your workspace.

**Custom professional-services engagements** (a bespoke Extend build, T&M or fixed fee) are NOT this pair - and this bespoke SOW is the practice's core delivery work, so the skill drafts its *substance* rather than just deferring. The SOW template itself says other services require "a separately-executed Professional Services Agreement and corresponding statement of work"; the legal shell (the governing PSA/MSA and its risk-allocation terms) must come from the firm's confirmed services template. Draft the services-SOW **content** from [references/services-sow.md](references/services-sow.md) - a section-by-section skeleton (scope, assumptions, exclusions, roles & responsibilities/RACI-lite, deliverables & acceptance, timeline/milestones, T&M vs fixed-fee fees, invoicing/expenses, change control, warranty/term-termination-as-legal-shell). It sources scope/assumptions/pricing from wd-estimate's `sow-handoff.md`. If no confirmed PSA/services-SOW template exists in your client-docs tree, say so, request the current template from the firm's contracts team, and draft the content inputs from `references/services-sow.md` in the meantime - flagging every legal-shell item for legal. Any program-specific services SOWs you hold (see Engagement inputs) are precedent-shaped but not a reusable template. Do not synthesize a services SOW from the SaaS pair, and do not write the legal shell.

## Where the content comes from

Never compose contract substance from memory - pull it from the upstream artifacts:

| SOW section | Source |
|---|---|
| Scope components, included enhancements | Design doc scope (wd-design-doc) / product feature list; archetype-level description per wd-estimate `references/sow-handoff.md` |
| Assumptions, exclusions, client responsibilities | wd-estimate `references/sow-handoff.md` - the estimate's assumption list IS the SOW's protective wall |
| Milestones / effective date framing | Proposed timeline (wd-estimate step, or wd-pm plan) |
| Fees table | UET pricing output (wd-estimate) or the approved subscription price |
| Client info, signers, entity structure | Client program facts (see Engagement inputs) |

If a source artifact doesn't exist yet, don't guess - placeholder it (below) and name which artifact would resolve it.

## Draft markup rules (the yellow-highlight convention for Word)

The yellow-highlight open-items convention is **owned by wd-design-doc** (the what/why/when - consult it). This section is only the Word-specific delta for applying it via the docx skill:

- Word mechanics: mark every unresolved value as highlighted text (WD_COLOR_INDEX.YELLOW) in the form `[BRACKETED - needs: <what resolves it>]` (e.g. `[FEES - needs: approved Year 1-3 subscription price from UET]`), and collect an "Open Placeholders & Deviations" list at the end of every draft. Contract-local addition: flag template deviations inline the same way - `[DEVIATION FROM TEMPLATE: <clause> - <what changed and why>]`.
- Placeholders get unhighlighted only when the real value lands; deviation flags come out only by the legal/contracts reviewer, not by this skill.
- Beware inherited template artifacts: the SOW template was authored for "Bill Only Supply Chain Solution" and stock phrases ("requisition-to-payable process", Supplier Portal user language) leaked verbatim into the current program's executed SOWs. Sweep for them on every draft - checklist in [references/sow.md](references/sow.md).

## Workflow

1. Identify document(s) needed (routing above) and confirm the master-agreement status for this client entity.
2. Start from the confirmed template file - copy it, never edit the template in place (docx skill for mechanics).
3. Fill section by section per the reference file, pulling substance from the sources table; placeholder anything unresolved.
4. Sweep for template artifacts; flag deviations.
5. Append the Open Placeholders & Deviations list; stamp DRAFT.
6. Hand off: name the reviewers (engagement MD + the firm's contracts/legal) in the delivery note. wd-comms drafts the cover email if client-facing.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **SOW template file** - the confirmed Provisioning SOW template (location in your workspace). If a template isn't on your machine, author from `references/sow.md` (it fully specifies the content).
- **SaaS Agreement template file** - the confirmed master-agreement template (location in your workspace). If absent, author from `references/saas-agreement.md`.
- **Firm Service Provider legal entity** - the firm's contracting legal name, entity type, and registered office address used in the preamble/signature (from your contracts team; the template pre-fills it).
- **Services-SOW precedents** - any program-specific services SOWs you hold (precedent-shaped, NOT a reusable services-SOW template).
- **Executed subscription-SOW precedents** - prior executed app SOWs for this client and their annual fees, used only to confirm patterns - never to infer a new app's fee.
- **Execution-version identifiers** - the contract-number prefixes and made-dates on executed PDFs (these appear only on execution versions, not drafts).
- **Executed SaaS Agreement copies + made-dates** - the master-agreement filenames and the date each was made (every SOW must cite the correct executed made-date).
- **Client legal entity/entities** - the exact registered legal name(s) that sign, the office address, and the state of incorporation. (Some clients require dual/multiple entity signature blocks plus a legal-department review/stamp - capture which.)
- **Client contract contact** - name, phone, and e-mail of the client's contract contact (not the project SME).
- **Firm signer(s)** - the firm's current authorized signatory for this paper (per document type).
- **Accepted standard terms** - the initial term, renewal term, fee cadence, user scope (affiliate extension or not), and deployment model (firm-deploys vs. client self-deploys) this client has accepted (drives the term/usage/fees/responsibilities choices in `references/sow.md`).
- **Draft naming convention** - the filename pattern for drafts (the contract-number prefix appears only on execution versions).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

## Flex Credit commercial terms in contracts

The Flex-Credit + API-metering fact block - credit pricing, entitlement tiers, complimentary amounts, the Extend multiplier, the agent Rate Card, promotions, and the UMSA prerequisite - is owned by `wd-estimate/references/flex-credits.md`. Read it there; cite those figures in the paper rather than restating them here.

- **Contract-local:** Flex/API run-cost and overage terms belong in the SOW commercial section. Add a standard assumption to every SOW that includes agents or metered API work - ongoing Flex Credit consumption post-go-live is the Customer's responsibility and is not included in this SOW, with the estimated annual consumption from the design doc referenced for budgeting - and surface any UMSA-migration dependency, complimentary-tier limit, and time-sensitive promotion end date in the assumptions/exclusions section.

## Lifecycle neighbors

**Previous:** wd-estimate - the quote this contracts; its assumptions/exclusions/pricing are the SOW's raw material. **Next:** after signature, wd-discovery / project kickoff (wd-pm plan, wd-extend-lifecycle phase map). Post-signature scope changes = change orders priced from the estimate model (wd-estimate) under wd-design-doc change control.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
