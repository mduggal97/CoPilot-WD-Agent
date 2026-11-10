# Client Security / InfoSec Questionnaire - Answer Bank for an Extend App

This reference answers the **client's** security questionnaire - the InfoSec /
vendor-risk / third-party-assessment form a client security office sends before
(or during) an Extend engagement. It is **NOT the Workday-issued Extend Volumes
Questionnaire** (that platform gating doc is the SKILL.md main body +
`volumes-questionnaire.md`). If someone says "the security questionnaire,"
establish which one first - they arrive from opposite directions.

## The key teaching: most answers are INHERITED

An Extend app runs **inside Workday's platform** - same data centers, same
encryption, same tenant isolation, same access infrastructure as the client's
core Workday tenant they already security-reviewed. So for most questionnaire
domains the honest, strongest answer is: **"inherited from Workday's platform
controls"** plus the small **app-specific delta**. Answering as if the firm
operates independent infrastructure both understates the security posture and
invites follow-up questions that don't apply.

Tag every answer with its source so the client can route follow-ups:

- **[inherited-Workday]** - a Workday platform control (SOC 2 Type II reporting,
  encryption at rest/in transit, data-center/physical certifications, tenant
  isolation, platform vulnerability management). (!) Cite Workday's
  certifications **generically** - pull the current certification names, report
  vintages, and attestation letters from Workday's trust/compliance page (or via
  the client's own Workday account team) **per engagement**. Never hardcode a
  cert vintage into a reusable answer; a stale "SOC 2 (2024)" in a 2027 response
  is a credibility hit.
- **[app-specific]** - what THIS app adds on top of the platform (the delta
  checklist below).
- **[firm-process]** - the delivering firm's delivery practices (access control
  during the engagement, code review, credential handling, offboarding at closeout -
  wd-post-go-live `handoff-and-closeout.md`).

## The app-specific delta checklist

Populate from the design doc's **Security tab** (wd-design-doc) and the
data-classification pass (wd-design-doc `references/nfr-accessibility.md` section 5).
These are the only things the platform answer does NOT cover:

- [ ] **External endpoints the app calls out to** - every non-Workday URL,
      including GenAI/LLM egress. Each one already passed the data-egress gate
      in wd-extend-dev `references/external-apis-and-genai.md` (field-level
      enumeration + classification); the gate's design-doc record IS this
      answer. No external calls = say so explicitly ("all processing stays
      inside the Workday tenant") - it is the strongest single sentence in the
      response.
- [ ] **Secrets inventory** - App Attributes holding API keys/endpoints
      (per-tenant, admin-set, out of source - wd-extend-dev
      `external-apis-and-genai.md`), any CredStore entries.
- [ ] **ISU inventory** - every Integration System User, what it can reach
      (domains), and any ISU-authenticated PAGE endpoints (a deliberate
      user-context bypass - disclose where used, per wd-extend-dev
      `references/security-setup.md` section ISU-authenticated page endpoints).
- [ ] **Data classes the app stores/processes** - from the nfr section 5 per-BO/field
      classification (PII / PHI / FERPA / none), including attachments and
      free-text fields.
- [ ] **Retention/purge posture** - what is kept, how long, how purged, who
      decided (wd-post-go-live `references/data-retention-export.md`).

## Common questionnaire domains - default answers

| Domain | Default answer shape | Tag |
|---|---|---|
| Data centers / physical security | Workday's platform certifications; app deploys into the client's own Workday tenants | [inherited-Workday] |
| Encryption at rest / in transit | Workday platform encryption; app adds no independent storage or transport outside the tenant (unless the delta checklist says otherwise - then describe that endpoint's transport) | [inherited-Workday] (+ delta) |
| Tenant/data isolation | Workday tenant model; app data lives in Extend business objects inside the client's tenant | [inherited-Workday] |
| Authentication | **SSO via the client's Workday session** - the app has no separate login, no password store; users reach it only through authenticated Workday sessions | [inherited-Workday] |
| Authorization | Workday **security domains** (`securityDomains` on every BO/page), granted to the client's own security groups by the client's security admin; disclose any ISU-authed page endpoints (delta checklist) | [app-specific] |
| Subprocessors / offshore support | Route to the contract paper: SaaS agreement **section 3.6 Offshore Support** (wd-contracts `references/saas-agreement.md`) - client must notify the firm of data-residency restrictions; don't freelance an answer the contract already governs | [firm-process] |
| Penetration testing | "The app runs inside Workday's tested platform (Workday's own program covers the infrastructure); app-level testing scope for this engagement = X" - state X honestly from the test evidence (wd-testing). (!) Confirm the firm's standard pen-test posture language with the practice/QRM lead before first use; do not improvise a claim that the firm pen-tests Extend apps | [inherited-Workday] + [firm-process] |
| Vulnerability management / patching | Platform-side: Workday. App-side: the support agreement's fix path (wd-post-go-live `references/managed-services.md`) | [inherited-Workday] + [firm-process] |
| Incident response | Platform incidents: Workday's process. App-level: the security-incident classification and notification chain in wd-post-go-live `references/managed-services.md` | split |
| Data retention / disposal | The app's documented retention/purge posture (delta checklist); the client's own records-management determinations govern the periods | [app-specific] |
| Consultant access controls | Engagement-scoped accounts, removed/DNU'd at closeout with client countersign (wd-post-go-live `handoff-and-closeout.md` closeout checklist) | [firm-process] |

## Platform authentication facts - answer bank

Doc-sourced specifics for the authentication/session/monitoring rows above, so answers
carry exact mechanisms instead of hand-waves. All **[inherited-Workday]**; all per Workday
Admin Guide (Authentication & Security), Jul 2026.

> **Verify current before sending (standard of care).** The numeric/config specifics below (timeouts,
> TLS version, URL paths, factor list) are point-in-time facts from the dated Admin Guide - Workday changes
> them between releases. Before these go into a client-facing security response, re-check each against the
> CURRENT Admin Guide (same discipline this file already requires for certification vintages), or date-stamp
> the value so the reviewer knows to confirm. A stale definitive fact in a signed InfoSec response is a
> standard-of-care exposure.

- **Authentication policy:** one active policy per environment, applying to all clients
  including mobile. Rules evaluate **first-match by security-group order** - best practice
  is decreasing restriction plus a default rule. Workday **refuses to activate changes that
  would lock out the activating admin**. Activation is its own task - **Activate All
  Pending Authentication Policy Changes** (distinct from security-policy activation) - with
  an audit timestamp.
- **MFA:** available on username-password, SAML, and OIDC types (**OAuth is not an
  authentication-policy type**). Delivered factors: Authenticator App, Duo, Email OTP,
  SMS OTP; enabled on Edit Tenant Setup - Security. Best practice: more than one factor,
  and stricter rules for admins.
- **Sessions:** Default Idle Session Timeout must be under 720 min (PCI-scoped users:
  15 min); Absolute Session Timeout defaults to 24 h (8/12 h options, new sessions only);
  per-account Session Timeout Minutes overrides the default.
- **Sign-on monitoring:** **Signons and Attempted Signons** report (includes OAuth
  failures and proxy session start/stop); **Workday Accounts Currently Locked Out by
  Excessive Failed Signon Attempts** for lockout review.
- **TLS:** inbound AND outbound integrations require **TLS 1.2+**.
- **Sign-in URL paths** per auth type: `login.htmld` (username-password) /
  `login-saml.htmld` / `login-oidc-auth.htmld`.
- **Proxy access:** **non-production only**; one proxy policy per environment;
  unconstrained groups only; delegated tasks excluded. Accounts past Maximum Inactive Days
  Before Disabling Account are **silently blocked from being proxied** - also the first
  thing to check when a demo-tenant proxy (e.g. a client demo cast) mysteriously stops
  working.

## Working the questionnaire

1. Identify which questionnaire this is (client InfoSec form vs Workday Volumes
   doc) and who consumes the answers.
2. Fill the inherited rows first - they're the bulk and they're reusable.
3. Build the delta from the design doc's Security tab + nfr section 5; a Security tab
   that can't answer the delta checklist is a design-doc gap (route to
   wd-design-doc, yellow-highlight it).
4. Anything asserting a Workday certification: verify current names/reports per
   engagement ((!) above).
5. Anything contractual (subprocessors, breach notification, liability):
   answer from the executed paper via wd-contracts - never draft new terms in a
   questionnaire response.
