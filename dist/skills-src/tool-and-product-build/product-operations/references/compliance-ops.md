# Compliance operations - running the posture, not writing the paper or the audit

Reference for `product-operations`. Self-contained: read it without having read anything
else in the suite.

## GUARDRAIL - read this before anything else in this file

**This file is operational guidance for running a compliance posture day to day. It is NOT
legal advice, and it does NOT make a product SOC 2 compliant by itself.**

- **The DPA and any contractual compliance commitment is contract paper.** That belongs to
  `wd-contracts`, drafted as a DRAFT for the firm's legal/contracts team to review - never
  final, never executable, never a source of invented legal terms. This file describes what
  a DPA typically needs to cover OPERATIONALLY (section 3) so the operations team knows what
  the paper will ask of them; it does not draft the clause.
- **A real SOC 2 report requires an independent, licensed CPA firm auditor.** Nothing in this
  file, and no internal self-assessment, constitutes a SOC 2 attestation. "SOC 2 readiness"
  (section 1) means preparing the control environment so an actual audit can succeed - it is
  not a substitute for hiring an auditor.
- **When a question requires a legal or compliance professional's judgment** (whether a data
  flow needs a specific transfer mechanism, whether a breach triggers a specific
  jurisdiction's notification duty, whether a contract clause is enforceable), say so
  plainly and route it to counsel or the firm's compliance function rather than answering
  as if this file settled it.

## Table of contents

- [SOC 2 readiness](#soc2)
- [GDPR/CCPA operational duties](#gdpr-ccpa)
- [Security-questionnaire answer bank](#questionnaire)
- [What to remember](#remember)

---

<a name="soc2"></a>
## 1. SOC 2 readiness

**SOC 2 is an AICPA attestation framework (the Trust Services Criteria) evaluated by a
licensed CPA firm - it is not a certification a company can self-declare**
(https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2).
The five Trust Services Criteria categories are Security (the only mandatory one),
Availability, Processing Integrity, Confidentiality, and Privacy - a product typically scopes
to Security plus whichever others its customers' contracts or industry expect
(https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022).

**Type I vs. Type II - know which one is being asked for:**

| | Type I | Type II |
|---|---|---|
| What it attests | Controls are suitably DESIGNED as of a point in time | Controls are suitably designed AND operated EFFECTIVELY over a period (typically 3-12 months) |
| Effort | Lower - a design review | Higher - the auditor samples evidence across the whole period |
| What a customer trusts it for | A reasonable early signal | The credible, renewal-grade attestation most enterprise buyers actually want |

Most enterprise security questionnaires (section 3) ask specifically for a Type II report,
and many will not accept a Type I as sufficient for a production vendor relationship - if
the practice is quoting a timeline to a customer, be explicit about which type is in
progress and that a Type II cannot exist until the observation period has actually elapsed.

**Common control domains an operations team actually runs day to day** (illustrative, not
exhaustive - the auditor's scoped control list governs):

- **Access control** - least-privilege IAM (per `app-architecture`/`app-hosting`'s IAM-role
  and secrets-management posture), access reviews on a cadence, offboarding that actually
  revokes access same-day.
- **Change management** - the deploy pipeline itself is evidence here: `app-hosting`'s
  two-account, reviewed, pipeline-driven deploy (`references/cloudformation-pipeline.md`) is
  exactly the kind of controlled-change evidence an auditor samples.
- **Monitoring and incident response** - the alarms and incident/postmortem discipline in
  `sla-and-support.md` and `app-hosting/references/observability.md` are direct control
  evidence, not separate compliance busywork - run one process, not two.
- **Vendor/subprocessor management** - see section 2.
- **Vulnerability management** - a stated patching/dependency-update cadence and evidence it
  is followed.

**Readiness work, concretely:** map the practice's existing operational controls (many of
which this skill and `app-hosting` already describe) to the auditor's control list, close
genuine gaps, and start collecting evidence continuously BEFORE the audit period begins for
a Type II - evidence collected retroactively is far weaker than evidence generated as a
byproduct of already-running processes.

---

<a name="gdpr-ccpa"></a>
## 2. GDPR/CCPA operational duties

**GDPR (EU) and CCPA/CPRA (California) are statutes, not vendor certifications** - full text
at https://eur-lex.europa.eu/eli/reg/2016/679/oj (GDPR) and
https://oag.ca.gov/privacy/ccpa (CCPA, as amended by CPRA). This section covers the
OPERATIONAL duties a running product needs to actually execute, not the legal analysis of
whether/how each statute applies - that determination is counsel's call, made once and
recorded in the contract paper (wd-contracts), with this section describing what the
operations team then has to DO to honor it.

**DPA in practice.** A Data Processing Agreement (or Addendum) is the contract that
establishes the product operator as a processor acting on the customer's (the controller's)
instructions (GDPR Article 28 sets what such an agreement must contain -
https://gdpr-info.eu/art-28-gdpr/). Operationally, once that agreement exists, running
against it means:

- Processing customer data only per the customer's documented instructions and the agreed
  purpose - not repurposing it for an unrelated internal use (e.g., using customer data to
  train a general-purpose model, absent explicit agreement).
- Maintaining the technical and organizational security measures the DPA commits to - this
  is where the SOC 2 control evidence (section 1) and the sla-and-support/observability
  posture do double duty as the DPA's technical-measures evidence.
- Notifying the customer of a subprocessor CHANGE per the DPA's notice mechanism (see
  subprocessors below) and of a personal-data breach without undue delay (breach
  notification, below).

**Subprocessors.** Any third party that processes customer personal data on the product's
behalf (a cloud host, an email/notification service, an analytics tool) is a subprocessor.
Operational duties: maintain a current, PUBLISHED subprocessor list the customer can review,
and honor the DPA's notice period before ADDING a new subprocessor (a common pattern is a
right to object during a stated notice window) - this list needs an owner who updates it the
moment a new third-party dependency is introduced, not only when a customer asks.

**Data residency.** If a customer's DPA or contract commits to processing/storing personal
data within a specific region (e.g., EU-only), that is an infrastructure commitment, not
just a paper one - it constrains where `app-hosting`'s RDS instance and any downstream
service (including a model provider, for an agentic product) can physically run. Confirm
region commitments against the ACTUAL deployed region before making the commitment, not
after a customer asks and it turns out to be wrong.

**DSAR handling (Data Subject Access Request).** An individual has rights (access,
correction, deletion/erasure, portability, objection) over their personal data under GDPR,
and analogous rights (know, delete, correct, opt out of sale/sharing) under CCPA/CPRA.
Operationally:

1. **Intake** - a defined channel (a stated email address or form) for a request to reach
   the right team, and a stated internal response-time target that meets the statute's
   deadline (GDPR: respond within one month, extendable - Article 12(3); CCPA response
   timelines are statute-specific - verify current requirements before committing to a
   number, since these can be amended).
2. **Locate** - find the individual's data across the product's own stores AND any
   subprocessor holding it - a multi-tenant schema-per-module design (`app-architecture`)
   helps here if the schema was designed with a findable subject identifier; a data model
   with no consistent subject key makes this materially harder after the fact.
3. **Act** - fulfill access/export/deletion per the specific right requested, honoring any
   legal-hold or retention override (the same tension `wd-post-go-live`'s DSAR runbook names
   for a Workday app - a deletion request does not override a legal retention obligation;
   that conflict is a legal call, not an operational one).
4. **Log** - record the request and its fulfillment for audit purposes; a DSAR log is itself
   compliance evidence.

**Breach notification.** If a personal-data breach occurs, GDPR requires notifying the
relevant supervisory authority within 72 hours of becoming aware, where feasible (Article
33 - https://gdpr-info.eu/art-33-gdpr/), and notifying affected individuals without undue
delay where the breach is likely to result in high risk to them (Article 34). State-level
US breach-notification laws (relevant to CCPA-covered data) vary by jurisdiction. **The
notification TIMELINE and WHO sends it (the practice, or the customer as controller, per the
DPA's allocation) is set by the executed contract and applicable law, not by this file** -
treat the 72-hour figure above as the GDPR benchmark to know, not a number to commit to
without checking the executed DPA's actual allocation of that duty. Operationally: the
incident runbook in `sla-and-support.md` section 6 already pulls a suspected data-exposure
incident out of the normal severity scale for exactly this reason - a security incident
starts the breach-assessment clock the moment it is suspected, not once it is confirmed.

---

<a name="questionnaire"></a>
## 3. Security-questionnaire answer bank

**Enterprise buyers routinely gate a purchase behind a security questionnaire** (a
standardized or customer-authored form covering infrastructure, access control, data
handling, incident response, and compliance attestations). Two disciplines make answering
one tractable instead of a fire drill every time:

**Maintain a living answer bank, not a from-scratch response each time.** Most
questionnaires ask overlapping questions in different words - keep a canonical set of
answers, each traceable to a real, current fact (a control, a policy, an architecture
decision), and adapt the WORDING per questionnaire rather than re-deriving the FACTS. This
mirrors the suite's provenance-ladder discipline
(`wd-extend-lifecycle/references/quality-gates.md`): a factual claim entering a
security questionnaire needs a source and, where doc-sourced rather than build-verified, a
verify-current caveat - never assert a control exists from memory.

**Answer honestly, including "not yet."** A common categories map, with the operating rule
for each:

| Category | Typical question shape | How to answer honestly |
|---|---|---|
| Hosting/infra | Where is data hosted, what cloud, what region | Cite the actual `app-hosting` posture (App Runner behind VPN, RDS region) - do not describe an aspirational architecture |
| Access control | MFA, least-privilege, offboarding | Describe what is actually enforced today; if a control is planned but not live, say "planned for <date/quarter>," not "yes" |
| Encryption | At-rest and in-transit encryption | State what is actually configured (RDS encryption at rest, TLS in transit) - verify the current configuration rather than assuming a platform default that may not be enabled |
| Compliance attestations | SOC 2, ISO 27001, HIPAA, etc. | State the TRUE current status per section 1 - "SOC 2 Type II in progress, observation period ends <date>" is honest; claiming a report that does not exist yet is not just risky, it is the kind of claim that ends a deal on discovery, not before |
| Data handling | Retention, deletion, subprocessors, data residency | Cite the DPA's actual commitments (section 2) - never answer more expansively than the executed DPA supports |
| Incident response | Do you have an IR plan, notification SLA | Cite the actual incident runbook and severity/notification posture (`sla-and-support.md`) - do not invent a faster notification commitment than the DPA actually allocates |
| Business continuity/DR | Backup, RPO/RTO | Cite the actual RDS backup/PITR posture (`app-hosting/references/operations.md` section 2) and state real RPO/RTO figures derived from it, not aspirational ones |

**A "no" or "not yet" with a credible roadmap is a better answer than an inflated "yes."** A
buyer's security team will often accept a gap with a committed remediation date; they will
not forgive a "yes" that turns out to be false during a later audit or incident - and an
inflated answer becomes a contractual misrepresentation risk once it is submitted as part of
a deal, which is a legal exposure, not just a reputational one.

**Route anything requiring a legal determination (a liability question, an indemnification
question dressed as a security question, a data-processing-basis question) to counsel via
wd-contracts rather than answering it as an operational fact.**

---

<a name="remember"></a>
## What to remember

- This file is operational guidance, not legal advice, and not an audit. The DPA is
  wd-contracts' DRAFT-only paper; a real SOC 2 needs an independent licensed auditor.
- SOC 2 Type I attests design at a point in time; Type II attests operating effectiveness
  over a period and is what most enterprise buyers actually require - never conflate the
  two when stating status.
- GDPR/CCPA operational duties (subprocessor list + notice, data residency, DSAR handling,
  breach notification) are executed against whatever the signed DPA and applicable law
  actually commit to - this file describes the operational shape, not the legal
  determination of what applies.
- Maintain a living, sourced security-questionnaire answer bank; answer every question
  honestly including "not yet, planned for <date>" - an inflated "yes" is a bigger risk than
  an honest gap.
- When a question crosses into a legal judgment call, say so and route it to counsel rather
  than answering as though this file settled it.
