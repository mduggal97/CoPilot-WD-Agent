# Provisioning SOW - section-by-section drafting guide

Template: the confirmed SOW template (location in Engagement inputs, SKILL.md), authored around the "Bill Only Supply Chain Solution" example - its app-specific language is baked into several sections; artifact sweep at the end of this file. This is a **Provisioning SOW** under an executed SaaS Agreement - a subscription deployment of a pre-built Extend app, not a services engagement. The SOW prevails over the SaaS Agreement on conflict, so precision here matters most.

DRAFT guardrail applies throughout: fill blanks, adapt enumerated lists to the app, placeholder unknowns, flag every other change as `[DEVIATION FROM TEMPLATE: ...]`.

## Title block + preamble

- Two Heading-3 lines: `Statement of Work` / `Workday Extend: <App Name> Application SAAS Agreement`.
- Preamble para 1: identifies this as a Provisioning SOW to the SaaS Agreement **dated ___** between the firm's contracting legal entity (legal name, entity type, and registered office - the "Service Provider"; pull from your contracts team, see Engagement inputs) and the Client identified below. Fill the SaaS date from the *executed* master agreement - verify against the signed copy, not another SOW's reference (SOW drafts have been seen carrying a date matching no executed agreement).
- Preamble para 2: Effective Date. Template default = last date of signature below; some executed SOWs instead specified a fixed date (e.g. "entered into as of <fixed start date>") to align the subscription start with go-live/fiscal timing. Either is fine; a fixed future date is a deliberate choice - confirm with the MD, placeholder until confirmed.
- **Client Information table** (1 row x 2 cells): left = Name of Client / Address / State of Incorporation; right = Contact Name / Phone / E-Mail (all from Engagement inputs). The contact is the client's contract contact, not the project SME.

## 1. Objectives and Scope

The section reviewers and clients actually read. Four parts:

1. **Objective paragraph**: names the app (quoted, becomes the defined "Application"), states it is a Workday Extend application deployed into the Client's existing Workday environment, then 1-2 sentences of what it does end-to-end (source: design doc overview / product description). Rewrite fully per app - the template's text is Bill Only-specific (Supplier Portal, requisition, purchase order).
2. **Scope components** ("the Services") - the enumerated pre-built components, adapt headings to what the app actually has: Application Pages, Business Objects, Security Domains, Orchestrations, Integrations (some executed SOWs merged these into "Integration and Orchestrations"), and ongoing Technical Support via the firm's managed-services process for designated client support contacts.
3. **Included enhancements** (optional pattern seen on enhancement-bearing subscriptions): "The application will include, at no additional charge to the Client, the following enhancements as new features:" + a short name-dash-description list (each enhancement named and one-line described, e.g. a section-control feature, a dynamic-visibility feature, a role-pairing feature). This is how client-specific enhancement commitments ride on a Marketplace subscription. Source: the enhancement scope from the design doc. If enhancements are included, the Exclusions wording must change in step (see next).
4. **Exclusions - Customizations**: template excludes ALL customizations/modifications to the delivered codebase. When enhancements are included, use the enhancements-included variant: "...outside of the enhancements listed in the scope section above". Mismatch between (3) and (4) is a real contradiction - check it every draft.
- Closing paragraph: template artifact alert - it promises "a streamlined requisition-to-payable process" (Bill Only leftover that shipped verbatim in more than one executed SOW to date). Replace with the app's actual process or cut the sentence.

## 2. Term

Initial Term (per the accepted standard terms in Engagement inputs - e.g. a multi-year initial term from Effective Date) + Renewal Term (a renewal term of the same length, auto-commences unless either party gives written notice >= thirty (30) days before expiration). Note the master SaaS Agreement section 7.1 says sixty (60) days - the SOW's 30 prevails for this SOW; don't "fix" it silently, but a `[DEVIATION?]` note asking legal to confirm intent is appropriate on new paper.

## 3. Application Usage

Institution-limited use (does NOT extend to affiliated institutions - significant for a multi-entity client structure; if affiliated client entities will use the app, that's a scope/legal question to flag, not a wording tweak). Unlimited number of Users; "Users" defined as employees/contractors of Client. Artifact alert: the template's Users definition adds "external users with existing system access to the Client's Workday Supplier Portal" - Bill Only leftover; keep only if the app genuinely has external users.

## 4. Updates and Upgrades

Periodic evaluations aligned to Workday releases/product updates; changes pushed to all Service Provider clients after testing; optional product enhancements may incur additional fees. Executed SOWs on some programs softened the template's promissory tone ("our commitment to ensuring the reliability" -> "As part of sustaining the reliability"; "ensures that Client's software remains up-to-date" -> "is to work toward having Client's software remain up-to-date") - where a program has such negotiated precedent, prefer the softened executed language on new drafts.

## 5. Configuration Changes

Client agrees to make no direct changes to Application configuration or supporting objects that would impact functioning; >= thirty (30) days written notice for changes. Fill-in-free; leave as-is.

## 6. Invoices and Fees

Fees table, one row per subscription year: `Subscription Name | Period | Start Date | End Date | Fees | Invoice Schedule`. Pattern: Start/End expressed relative to Effective Date ("Effective Date + 1 year"); Year 1 invoiced "As of the Effective Date", later years "Upon the start of Year N". Flat annual fee (per the approved subscription fee - from the estimate; placeholder if unapproved). Source: approved subscription price (wd-estimate/UET or product pricing decision) - never infer from precedent apps; placeholder if unapproved. Trailing sentence: Service Provider may increase fees each renewal term - keep.

## 7. Additional Services

Included services list (template + executed): Kickoff session and Application overview presentation; Demonstrate Application; Knowledge Transfer and Support. Add rows only if the deal genuinely includes more (each addition = deviation flag; consider whether it belongs in a services SOW instead).

## 8. Client's Responsibilities (i)-(x)

Items (ii)-(x) are stable boilerplate (acceptable-use policies, fit-for-purpose validation before production, data/config accuracy, cooperation/access, notify of Workday changes impacting the app, authorized-user conformance, terminating non-authorized access, legal compliance, Primary + Alternate Support Coordinator designation). **Item (i) is a fork - the deployment model:**

- Variant A (template): "Providing [Service Provider] resources with implementer access to appropriate Workday tenants" -> **the firm deploys**.
- Variant B (executed precedent): "Application deployment and configuration using the provided deployment and user guides" -> **client self-deploys** (per the accepted deployment model in Engagement inputs).

Pick deliberately per the delivery model; this single line decides who owns deployment labor. Placeholder if undecided.

## 9. Other Services (exclusions)

"Service Provider is not required to provide..." list - the silence-reads-as-inclusion protection (same logic as wd-estimate's exclusions guidance). Template/executed items: Client's Workday tenant functional configuration (per the solution's Deployment Guide - template enumerates Bill Only examples like Supplier Portal enablement/Procurement config; replace with THIS app's dependency list or trim), client data/tenant-config correction, custom report development, third-party integrations (a common executed-precedent addition - keep), user training, user support (how-to/system-access inquiries). Closing sentence: these are available for additional fee under a separately-executed Professional Services Agreement + SOW - keep verbatim; it is the bridge to services work.

## Signature block

Template: plain two-column In-Witness-Whereof block. Use the program's executed pattern (specific signers/entities in Engagement inputs, SKILL.md): a 2x2 table - the firm's contracting legal entity signed by the firm's authorized signatory | the client's legal-entity block(s). Where the client spans multiple entities that both sign, include every entity block plus any required legal-department review/stamp line. Never drop a required entity block or the legal-review stamp on that client's paper.

## Template-artifact sweep (run on every draft)

Search the draft for these Bill Only leftovers before handoff:
- "requisition-to-payable" (closing para of section 1) - has shipped verbatim in more than one executed SOW; replace.
- "Supplier Portal" / "suppliers" (section 1 objective + components, section 3 Users definition, section 9 dependency list).
- "sourcing process" / "purchase order" (section 1 objective).
- section 1 component descriptions ("user-friendly interface for suppliers and internal users") - reword to the app's users.
Then confirm section 1 enhancements list <-> section 1 Exclusions wording agree, and section 8(i) matches the actual deployment model.
