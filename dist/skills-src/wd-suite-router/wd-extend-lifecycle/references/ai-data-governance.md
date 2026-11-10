# AI & client-data governance - the gate before anything client goes into an AI tool

This suite assumes AI-assisted delivery (Claude Code co-building, transcript syncs,
doc generation). That assistance runs on client material, which makes data handling,
review, disclosure, and IP provenance house rules - not optional etiquette. Read this
before ingesting client material into any AI workflow; the rules below are the
conservative floor, applied unless a confirmed client/firm policy is MORE permissive.

## 1. The data gate (what may and may not go in)

**Never paste into AI tools, in any form:**

- Credentials, tokens, API keys, client secrets, PGP private keys (the suite-wide
  rule - same posture as wd-extend-dev's security references).
- Production data extracts (transaction dumps, report output, tenant exports).
- PHI / PII / FERPA person records - any row that identifies a real person.

**Permitted for the engagement's own delivery work:** client app source code, tenant
configuration, design documents, and similar work-product artifacts - (!) subject to
the firm's AI policy AND the client MSA's confidentiality/AI terms. Neither is assumed
here: **confirm both at kickoff and record the answer in the engagement file** (this
confirmation belongs on the kickoff checklist - see SKILL.md, "Kickoff checklist").
If either forbids or restricts AI use, the restriction wins over everything in this
suite.

**Regulated-data access gate (before ANY tenant access or ingestion, not just AI).** For a healthcare
client / PHI-containing tenant, the firm-client **BAA must be confirmed executed before any consultant
accesses that tenant or ingests its data** - the firm becomes a HIPAA Business Associate the moment it can
see PHI, which is at discovery/mock-conversion/UAT, well before design sign-off. Same posture for a
higher-ed client where the engagement requires access to FERPA education records (the data-handling terms /
the firm's "school official" basis must be in the paper first). This is a **kickoff prerequisite** (see the
kickoff checklist in SKILL.md); it is separate from, and earlier than, the app-level BAA gate at design
sign-off (wd-design-doc nfr-accessibility.md).

**Minimize even when permitted:** strip person-identifying detail that isn't needed
for the task before ingestion. wd-discovery already asks for *anonymized* sample
transactions as a habit - treat that as a rule for every input, not a discovery nicety.

> **Firm-wide classification policy sits ABOVE this gate.** The firm's 3-tier data
> classification (Public / Confidential / Highly Confidential) and its safeguard rules are
> the parent policy that this Workday-specific data-handling gate operates under - classify
> the data BEFORE recommending a tool / storage / egress, and flag a mismatch rather than
> answering the literal question. Where the firm policy is stricter than this floor, the
> firm policy wins. (adapted from an internal data-classification skill, 2026-08-28 -
> a pointer to the firm policy, not a restatement of it.)

**De-identifying a real extract into safe demo/test data - the interval-preserving
date-shift method.** When you genuinely need *realistic* data (volume, shape, edge
cases) but must not carry real people, one technique does most of the work: replace
direct identifiers (names, IDs, addresses) with synthetic values, then **shift every
date by a random offset that is CONSISTENT per record** - the same person/record moves
all its dates by the same number of days. Because the offset is per-record, the
*intervals and sequences* survive (hire->transfer->termination spacing, days-between-approvals,
age bands, effective-dating order) while absolute dates no longer match reality - the
data still exercises the same logic but no longer points at a real person or event. This
is the general shape of a HIPAA Safe Harbor-style de-identification pass (dates are one of
Safe Harbor's identifier categories, so shifting them is central). It is also the
practical way to honor the standing **"no customer data in dev tenants" rule** (memory:
`feedback_no_customer_data_in_dev_tenants`) when a purely-invented dataset won't reproduce
the behavior you need to build or test against.

(!) Method is externally sourced, not a verified Workday/firm procedure - validate the
offset range, the full direct-identifier list, and whether interval-preservation is
sufficient de-identification for the specific data class (a small population or a rare
combination can still re-identify) with QRM/privacy before treating any output as
"de-identified." Confirm it also satisfies the client MSA before the extract is created.
(Folded in from external skillsmp `shifting-clinical-dates` and `synthetic-data-workflow`.)
For staging the *demo* cast and story-shaped transactions once you have safe data, see
wd-demo's seed-data policy (`references/demo-playbook.md`) - this note is the
de-identification method, not the seeding recipe.

## 2. Human-review obligation

Every AI-drafted client deliverable gets a **named-human review before it leaves** -
design doc, proposal, email, guide, contract draft, all of it. The consultant is the
author of record and owns every statement in the artifact; "the tool wrote it" is
never an account of an error. Review means reading it as the client will, not
skimming the diff.

## 3. Disclosure rule

Time-to-value framing of AI-assisted delivery is legitimate positioning (wd-estimate
references/proposal-content.md owns the framing). But **framing is not concealment**:
if a client asks directly whether AI was used, or the contract/RFP requires AI
disclosure, answer accurately - never deny or obscure AI assistance. (!) The firm's
formal disclosure stance (standard language, when proactive disclosure is required)
needs QRM/legal confirmation - until confirmed, the floor is: never misrepresent,
and honor any contractual disclosure term to the letter.

## 4. IP-provenance rule (what may cross clients)

- **Reusable:** patterns, methodology, checklists, platform facts, and lessons
  harvested from engagements - the generic layer this suite is made of.
- **Never cross-client:** client work product, negotiated commercial terms, pricing,
  client-confidential facts, named-client data or metrics (external use of those is
  gated by bow-sales-enablement references/claims-register.md).
- The suite's **"Program defaults (swap per client)" blocks are per-client private
  overlays** - they carry client names, IDs, paths, and executed-contract facts.
  Before ANY team packaging or distribution of these skills, scrub or split those
  blocks out. The wd-smartsheet pattern is the template: client-specific IDs isolated
  in a swap-per-client defaults block plus a per-client registry reference, kept
  separate from the reusable method.
- **Ownership of AI-assisted output:** confirm who owns AI-generated deliverables against the client MSA and
  the AI tool's terms; and note that purely machine-generated material may have thin/no copyright protection,
  so anything the firm intends to protect or sell (productized templates, BoW/Marketplace collateral) should
  carry meaningful human authorship. (QRM/legal awareness item.)
- **External fold-in provenance:** methods folded in from outside sources (e.g. community "skillsmp" skills)
  are safe at the **idea/fact level** (uncopyrightable). Confirm each fold-in is idea-level, not copied
  prose/code, and note the source's license where it is anything more than an idea - keep the existing
  "Folded in ... vendor-neutral" annotations and extend them with the license when relevant.

## 5. Transcript ingestion note

Meeting transcripts are the **highest-sensitivity routine input** this suite handles -
they carry names, verbatim quotes, and often HR/finance detail nobody scrubbed. The
section 1 data gate applies BEFORE wd-pm meeting-intake Step 1 ingests anything (that skill
cross-references this gate); if a transcript contains person records or production
data beyond what the sync needs, minimize first.

## 6. Sensitive data in OUTPUT artifacts (what may go INTO trackers, docs, reports, comms)

Section 1 keeps sensitive data OUT of the AI; this section keeps it OUT of the artifacts the AI helps
produce. The things this suite writes - Smartsheet trackers / RAID / status reports, design docs, KT and
user/admin guides, client emails and Teams posts, diagrams, screenshots - are typically **broadly shared,
cloud-synced, long-lived, and access-scoped more loosely than the source data**. A real person's PHI/PII in a
RAID row or a status report is exposed to everyone with sheet or distribution access, not just those entitled
to it. The conservative floor (unless a confirmed client/firm policy is more permissive):

- **Default: none.** No PHI / PII / FERPA person records - and **never** credentials, tokens, keys, or secrets
  - in any tracker, report, design doc, guide, comm, or diagram. These artifacts describe the *work*, not a
  real person's identifying or sensitive data.
- **Match exposure to sensitivity.** Before writing sensitive detail anywhere, ask *who can see this artifact*
  (the Smartsheet workspace's members, the email's recipients, the doc's distribution) versus *who is entitled
  to the data*. If the artifact is more widely visible than the data warrants, do not put it there - reference
  it where it already lives (the tenant, a secured system) instead of copying it out.
- **Minimize / least-identifying form.** When a reference to a real person or record is genuinely necessary
  (e.g. a RAID item about one worker's data issue), use the least-identifying form that still does the job - a
  worker ID or role/position, not name+SSN+DOB; "a worker in Cost Center X", not the full record. Aggregate or
  count rather than enumerate where possible.
- **Examples and sample data are SYNTHETIC.** Design-doc field examples, how-to snippets, test/demo rows, and
  screenshots use invented data (the de-identification method in section 1; wd-demo seeding) - never a copy of
  a live record. A screenshot carrying real PHI is a leak even in an "internal" document; scrub or synthesize
  person data and secrets before embedding anything in a guide/deck/doc (delivered-tenant screenshots are the
  classic offender - the suite already strips them from bundled templates).
- **Point of enforcement.** Check at the moment of writing/sending, not after: wd-smartsheet's mandatory
  pre-write column review, wd-comms' before-send pass, wd-pm's RAID/status entry, wd-design-doc's
  sample-data/examples convention, and wd-kt's guide/screenshot authoring all apply this rule (they point
  here; this section owns it). The quality-gate registry carries it as a named check.
