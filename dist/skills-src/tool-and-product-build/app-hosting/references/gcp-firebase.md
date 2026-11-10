# GCP + Firebase Lane

This file covers two DISTINCT situations that both land on Google Cloud, and
they are not the same lane:

1. **Customer-mandated GCP production hosting** - a client's own cloud
   standard is GCP, so the hosted tool must run there instead of AWS.
2. **Firebase as a rapid-prototype/MVP lane** - a fast internal spike or a
   client demo, built to prove an idea, not to carry production load.

Read `../SKILL.md`, `aws-architecture.md`, `customer-hosting.md`, and
`operations.md` first - this file mirrors their shape and cross-links rather
than repeating them. The Azure customer-mandated variant is a sibling file:
app-hosting/references/azure-hosting.md. Placeholders used throughout:
`<APP_NAME>`, `<GCP_PROJECT_ID>`, `<REGION>` (e.g. `us-central1`),
`<SERVICE_ACCOUNT>`, `<WIF_POOL>`, `<WIF_PROVIDER>`.

---

## Contents

1. Decision gate - which of the two lanes is this
2. GCP production mapping table
3. Cloud Run recipe
4. Firebase prototype lane
5. CI/CD - GitHub Actions with Workload Identity Federation
6. BigQuery adjacency
7. What to remember

---

## 1. Decision gate - which of the two lanes is this

**State this plainly up front, because the two paths in this file get
confused with each other constantly.**

| | Customer-mandated GCP | Firebase prototype/MVP |
|---|---|---|
| **Why you are here** | The client's own cloud standard is GCP - not a firm choice, a contract/IT constraint | You need something running THIS WEEK to prove an idea, demo a concept, or validate a UX before committing build hours |
| **Durability** | Production-grade, same rigor as the blessed AWS stack, just on different services | Deliberately throwaway-or-graduate. Not hardened. Not the production answer. |
| **What it maps to in this file** | Section 2 (mapping table) + Section 3 (Cloud Run recipe) | Section 4 (Firebase prototype lane) |
| **Data isolation, schema, spend governance** | Full parity with the blessed stack (schema-per-module, SpendGuard) - see app-architecture, app-agentic | Explicitly NOT held to those contracts while it stays a prototype - see s4 |

**The blessed AWS stack (App Runner + RDS Postgres + ECR + Secrets Manager +
Bedrock + Entra + CloudFormation) remains the production default for every
hosted tool.** Reach for GCP production hosting only when a customer's
own mandate requires it - the same disposition gate `product-strategy` and
`practice-lifecycle` already apply to the AWS customer-hosting variant: this
is a variant, not a competing default.

**Firebase prototypes that graduate get REBUILT, not hardened in place.** If a
Firebase MVP proves out, the move is to rebuild it on the blessed AWS stack
(or, if the customer mandate applies, the GCP production lane in s2-s3) - not
to bolt multi-tenant isolation, relational integrity, and the suite's module
contract onto the Firestore/Functions prototype after the fact (s4 explains
why that retrofit does not work cleanly). Treat "we outgrew the prototype" as
a build decision, not a migration task.

---

## 2. GCP production mapping table

Read this the same way you would read a translation table between two
languages - most concepts carry over directly, a few do not map cleanly, and
one (App Runner -> Cloud Run) is close enough that it is worth saying so
explicitly.

| AWS (blessed stack) | GCP equivalent | Notes |
|---|---|---|
| App Runner | **Cloud Run** | The closest analog of anything in this file - both are a managed, scale-to-zero-capable container runtime that takes an image and runs it with minimal orchestration to own. Differences worth knowing before assuming 1:1 parity are in s3. |
| RDS Postgres | **Cloud SQL for Postgres** | Same relational-instance-plus-storage shape; schema-per-module carries over unchanged (verify-current, 2026-09-11: https://cloud.google.com/sql/docs/postgres) |
| ECR | **Artifact Registry** | Google's current container registry; ECR's "immutable tag" discipline (`cloudformation-pipeline.md` s5) has a direct Artifact Registry equivalent (tag immutability policy) - verify-current before relying on default behavior (2026-09-11: https://cloud.google.com/artifact-registry/docs) |
| Secrets Manager | **Secret Manager** | Same shape (named secret, versions, IAM-gated access); note the GCP product name is singular ("Secret Manager"), not "Secrets Manager" |
| CloudWatch (logs/alarms) | **Cloud Logging + Cloud Monitoring** | Split into two products where AWS has one; Cloud Run's structured JSON logs to stdout/stderr are auto-ingested by Cloud Logging without an agent (verify-current, 2026-09-11: https://cloud.google.com/logging/docs) |
| Amazon Bedrock | **Vertex AI** | Claude IS available on Vertex AI as a first-party partner model, not a Google-trained one (verify-current, checked 2026-09-11: Claude Sonnet 4.5 and Opus 4.1 GA; Opus 4.6, Sonnet 4.6, Sonnet 5, Opus 5, and Fable 5 have also shipped on Vertex AI over 2026 - https://docs.cloud.google.com/vertex-ai/generative-ai/docs/partner-models/claude). The current-vs-retiring list moves fast - re-pull it before pinning a model id, the same discipline `app-agentic`'s model registry applies to Bedrock. |
| IAM roles + instance role | **IAM + service accounts** | The concept carries over (a workload's identity grants scoped access, no embedded long-lived key) but the unit differs: AWS attaches a role to the compute resource; GCP attaches a **service account** to the Cloud Run service, and that account is what Secret Manager / Cloud SQL / Vertex AI grants are made against (s3). Do not port an AWS IAM policy JSON directly - re-derive the equivalent `roles/*` grants. |

**Do not assume every AWS primitive has a GCP twin.** This table covers only
what the blessed stack actually uses - for anything else (a queue, a CDN, a
warehouse), look it up fresh rather than guessing from the AWS name.

---

## 3. Cloud Run recipe

This section is the GCP-side equivalent of `aws-architecture.md` s3.1-3.3 -
the runtime, how it is reached, and how it gets to its secrets. It assumes
the same one-image, schema-per-module shape as the blessed stack; only the
hosting primitives differ.

**Service.** A Cloud Run **service** runs the same container image the
blessed stack would build (SPA + API in one image, or split if the design
calls for it) - point it at the image in Artifact Registry, set the port your
app listens on (Cloud Run reads `$PORT` the same way App Runner does; do not
hardcode it), and configure CPU/memory per workload, same sizing exercise as
`operations.md` s4 does for App Runner.

**Ingress - internal + IAP, or an internal load balancer, for VPN parity.** The blessed stack's
load-bearing decision is `IsPubliclyAccessible: false` behind the corporate VPN
(`aws-architecture.md` s3.2). Cloud Run's equivalent posture is **ingress = internal**, which
restricts the service to traffic from within the VPC (including on-prem traffic arriving over
Cloud VPN or Cloud Interconnect), not the public internet (verify-current, 2026-09-11:
https://docs.cloud.google.com/run/docs/securing/ingress). Two ways to get VPN-equivalent access on
top of that: **internal ingress + Identity-Aware Proxy (IAP)**, where IAP handles sign-in and only
forwards authenticated traffic - the closer analog of "network boundary + identity boundary, both
always on" from `aws-architecture.md` s2, since IAP contributes the identity check the way Entra
does on AWS; or **internal ingress + an internal Application Load Balancer**, a pure
network-boundary model if identity is instead enforced entirely in the app's own auth layer (e.g.
validating Entra JWTs application-side, federated the way s4 describes for Firebase). Pick per the
customer's actual network topology - flag it for the customer's own IT/security review, the same
way `customer-hosting.md` s7 flags the AWS public-ingress variant.

**Revisions and traffic-split - the deploy/rollback analog.** Every Cloud Run
deploy creates a new immutable **revision**; you control what percentage of
traffic each revision receives, giving gradual rollout (shift 10-50-100
percent to the new revision) and instant rollback (shift traffic back to the
previous revision - no rebuild, no redeploy) (verify-current, 2026-09-11:
https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration).
This is a materially SIMPLER rollback story than the blessed stack's prod
path - no dev-immutable-vs-prod-mutable SCP split to work around
(`operations.md` s3), because the revision model is natively
immutable-and-instantly-reversible in both environments, with no analog of
the App Runner `UpdateService`-is-denied trap. In-flight requests during a
traffic shift complete against whichever revision they started on.

**Workload identity to Secret Manager.** Create a dedicated service account
per Cloud Run service (not the default Compute Engine service account -
least-privilege, one identity per service, same principle as scoping an App
Runner instance role narrowly) and grant it `roles/secretmanager.secretAccessor`
only on the specific secrets it needs. Cloud Run injects the secret as an
environment variable or mounted volume at runtime, resolved through that
identity - no exported key, no plaintext secret baked into the image, the
same "credentials are secrets, fetched via identity, never baked in" rule as
`aws-architecture.md` s5 (verify-current, 2026-09-11:
https://docs.cloud.google.com/run/docs/configuring/services/secrets,
https://docs.cloud.google.com/iam/docs/best-practices-service-accounts).

---

## 4. Firebase prototype lane

Firebase is Google's rapid-app-development platform - genuinely fast for
standing up a working prototype, and genuinely NOT the suite's production
answer. This section names what it is good for and where it stops mapping to
the suite's production contracts, so the decision to use it is informed
rather than accidental.

**Firebase Auth, including Entra/OIDC federation.** Firebase Authentication
can federate sign-in to an external OIDC provider, so a prototype CAN
authenticate against a customer's (or the firm's) Microsoft Entra tenant rather
than inventing its own user store - configure Entra as a generic OIDC/OAuth
provider in the Firebase Auth console (verify-current, 2026-09-11:
https://firebase.google.com/docs/auth/web/microsoft-oauth). Convenient for a
demo that needs "log in with your work account" without standing up the
blessed stack's Entra app-registration ceremony, but it is a SEPARATE
identity integration from the one `aws-architecture.md` s3.6 owns - the
prototype's Firebase Auth config does not carry forward on graduation; it
gets rebuilt against the blessed stack's own Entra pattern.

**Firestore - the document model, and when it is fine vs when Postgres discipline matters.**
Firestore is a schemaless document database: flexible, fast to iterate against, no migration
ceremony to stand up a new collection. It is fine for a prototype when the data shape is still
changing weekly, access patterns are simple (fetch by key, a few flat queries), and there is no
cross-entity relational integrity to enforce. Postgres discipline starts to matter the moment the
tool needs real relational integrity (an order must reference a valid customer that cannot be
deleted out from under it), multi-row transactional consistency, or the ad hoc relational
querying/reporting a schema-per-module Postgres design gives for free. Firestore can do
transactions and security-rule-based access control, but it gives you no foreign-key constraint
and no join - modeling relational integrity in Firestore means re-implementing by hand what
Postgres enforces natively.

**Firebase Hosting + Cloud Functions/Cloud Run backend.** Firebase Hosting
serves the static SPA bundle; backend logic runs as Cloud Functions (simple,
per-function, event- or HTTP-triggered) or a Cloud Run service (a real API
server, not a handful of small functions) - both are legitimate prototype
backends, and Cloud Run here is literally the same primitive as s3, just
wired into the Firebase ecosystem instead of the blessed stack's module
contract.

**Emulator suite for local dev.** The Firebase Local Emulator Suite runs
Auth, Firestore, Functions, Hosting, and Storage locally with no cloud
project required - genuinely useful for the fast-iteration goal a prototype
lane exists for (verify-current, 2026-09-11:
https://firebase.google.com/docs/emulator-suite; needs Node.js + a Java JDK).

**Honest limits - why this stays prototype-lane only.** State these plainly
so a prototype's convenience does not quietly become a production decision.
**Multi-tenant / RLS-grade isolation does not map** - Firestore security
rules scope access per-document, but that is not the same enforcement model
as Postgres row-level security (app-architecture references/multi-tenancy.md);
there is no direct equivalent of a DB-enforced RLS policy that holds
regardless of application-code bugs. **Relational integrity does not map** -
no foreign keys, no cross-collection transactional constraints enforced by
the database itself, only what application code and security rules choose to
enforce by hand. **The suite's schema-per-module contract does not map** -
Firestore has no concept of a Postgres schema boundary or an isolated Alembic
migration tree per module (`aws-architecture.md` s3.4). This is exactly WHY
Firebase is scoped to prototype/MVP use only: those gaps are acceptable for
something meant to validate an idea fast and get rebuilt, not for something
meant to carry real production data under the suite's usual data-isolation
and integrity expectations.

---

## 5. CI/CD - GitHub Actions with Workload Identity Federation

The keyless pattern mirrors the AWS OIDC pattern already documented in the
app-harness skill's GitHub Actions evaluation (app-harness/references/
github-actions.md s2b): GitHub issues a short-lived OIDC token per job; the
cloud provider trusts GitHub's OIDC issuer and hands out temporary
credentials scoped by a trust condition - no long-lived key stored as a
GitHub secret.

On GCP the mechanism is **Workload Identity Federation (WIF)**: create a
Workload Identity Pool and an OIDC provider inside it that trusts
`https://token.actions.githubusercontent.com`, map the token's claims (repo,
ref, environment) to an attribute condition, and let that federated identity
impersonate a Google Cloud **service account** holding the actual IAM grants
(Artifact Registry push, Cloud Run deploy, Secret Manager access) - scoped
the same way the AWS trust policy's `sub` condition is scoped in the
app-harness recipe. Credentials expire automatically (about an hour) and
there is nothing to rotate beyond the initial pool/provider setup
(verify-current, 2026-09-11:
https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines;
action: https://github.com/google-github-actions/auth).

Workflow side needs `permissions: { id-token: write, contents: read }` plus
the `google-github-actions/auth` action configured with
`workload_identity_provider: <WIF_PROVIDER>` and
`service_account: <SERVICE_ACCOUNT>` - the direct GCP counterpart of
`aws-actions/configure-aws-credentials`. Same gotcha both directions: an
unscoped attribute condition (the GCP analog of an unscoped `sub: repo:*`)
trusts every branch/PR in the repo, not just the one deploying to prod -
scope it the same way.

---

## 6. BigQuery adjacency

Two separate reasons a GCP-hosted (or GCP-adjacent) engagement touches BigQuery, kept short here
because both are owned elsewhere. **As a Workday Data Connect zero-copy partner** - Google
BigQuery was announced as a Data Connect zero-copy sharing partner on 2025-11-19; the full
mechanism, EA/GA status, and the consulting decision rule for when to recommend zero-copy over
building an extract pipeline live in saas-integration/references/data-platforms.md (the "Workday
Data Connect - zero-copy via Iceberg" section). Read that file before proposing a BigQuery extract
pipeline for Workday-sourced data - Data Connect may make the pipeline unnecessary. **As an
analytics target when the client is a GCP shop** - for a client whose broader data estate already
lives in BigQuery independent of Workday, the same materialize-vs-query-live decision and generic
warehouse/lakehouse principles in that same file's s1 and s8 apply; BigQuery is explicitly named
there as one of the platforms those generic principles carry to (auth = service identity in
Secret Manager, bulk-load over row-by-row, incremental by watermark or native change feed, cache
and auto-suspend compute on live queries).

---

## 7. What to remember

- **The blessed AWS stack stays the production default** - this file is a
  variant for a customer GCP mandate or a throwaway prototype, never a
  general alternative to reach for by default.
- **Firebase prototypes get rebuilt, not hardened, on graduation** - multi-
  tenant isolation, relational integrity, and the schema-per-module contract
  do not retrofit cleanly onto Firestore.
- **Cloud Run is the closest AWS-to-GCP analog anywhere in this mapping**,
  but its revision-based traffic-split rollback is genuinely simpler than the
  blessed stack's dev-immutable/prod-mutable split - do not assume every AWS
  constraint (like the App Runner `UpdateService` SCP trap) has a GCP
  equivalent, because this one does not.
- **Claude runs on Vertex AI as a first-party partner model** - confirm the
  current model list before pinning an id; it has moved multiple times
  across 2026.
- **GitHub Actions to GCP uses Workload Identity Federation**, the direct
  keyless-OIDC analog of the AWS pattern in app-harness/references/
  github-actions.md - scope the trust condition the same way, for the same
  reason.
- **BigQuery shows up two ways** - as a Workday Data Connect zero-copy
  partner and as a generic analytics target - both owned in
  saas-integration/references/data-platforms.md, not duplicated here.
