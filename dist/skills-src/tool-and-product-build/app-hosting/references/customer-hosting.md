# Customer Hosting Variant - public ingress, external identity, multi-tenant

This file is a VARIANT, not a replacement. `aws-architecture.md` describes the
correct, permanent shape for an INTERNAL tool - private VPN ingress, a
single internal Microsoft Entra tenant, schema-per-MODULE isolation. Keep using
that shape for internal tools. Reach for THIS file only when the product's
disposition is CUSTOMER-SOLD (see `product-strategy` for how that call gets
made) - a paying customer who is not on the firm's VPN and not in the firm's Entra
tenant, and therefore cannot reach the internal architecture at all.

`aws-architecture.md` s3.2 flagged this gap on 2026-09-10: a customer product
needs public ingress, an external identity provider, and per-customer tenancy,
"none of which is designed in this suite yet." This file is that design. It
EXTENDS the internal architecture (App Runner container, RDS Postgres, Bedrock
in `<REGION>` all carry over unchanged) and REPLACES only the ingress and
identity layers.

**Ownership split - read this before the rest of the file.** This file owns
**ingress, identity, and network/tenant-boundary provisioning** (who can reach
the service, who they are, which customer they belong to). It does NOT own the
**data-isolation model** (how one customer's rows are kept out of another
customer's queries) - that is `app-architecture/references/multi-tenancy.md`
(authored in parallel). The two meet at one interface: this file's identity
layer resolves a `tenant_id` from the authenticated request; that `tenant_id`
is the input the data-layer isolation model consumes. Do not duplicate the
data-isolation content here, and do not duplicate the ingress/identity content
there - cross-link instead.

Placeholders used throughout: `<APP_NAME>`, `<REGION>` (default `us-east-2`),
`<CUSTOMER_DOMAIN>`, `<COGNITO_USER_POOL_ID>`, `<COGNITO_APP_CLIENT_ID>`,
`<ACM_CERT_ARN>`, `<WAF_WEB_ACL_ARN>`, `<TENANT_ID>`.

---

## Contents

1. Why the internal shape does not serve external customers
2. Public, hardened ingress - ALB/CloudFront + WAF + ACM + Shield
3. External identity - Cognito, SSO federation, or Auth0
4. Multi-tenant provisioning - onboarding a new customer
5. Isolation + security posture at the network/identity layer
6. Cost + ops delta vs the internal shape
7. DECISION note - this needs IT/security sign-off, not a suite default
8. What to remember

---

## 1. Why the internal shape does not serve external customers

**The one-line reason.** `aws-architecture.md` s3.2 makes `IsPubliclyAccessible:
false` the PERMANENT end state for internal tools, on purpose - the corporate
VPN is the network boundary and Entra is the identity boundary, and there is
deliberately no "flip to public later" path. A customer-sold product breaks
both assumptions at once:

| Internal assumption | Why it fails for a customer |
|---|---|
| Reachable only via a private VPC Ingress Endpoint, over the VPN | A customer's browser is never on the firm's VPN. The service is unreachable, full stop - not a permissions problem, a network-path problem. |
| Identity = one Microsoft Entra app registration in the firm's tenant | A customer's users are not employees of the firm; they do not exist in the firm's Entra tenant and cannot be added to it per-customer at scale. |
| Schema-per-MODULE data isolation | Isolates FEATURES from each other, not CUSTOMERS from each other. Two customers' rows can sit in the same module schema with nothing stopping a query from crossing between them. |

**Why not just flip `IsPubliclyAccessible: true` on the same App Runner
service and call it done.** App Runner's private-ingress model has no WAF, no
managed DDoS mitigation, and no per-customer identity concept attached to it -
flipping the flag removes the network boundary without installing anything to
replace it. A publicly reachable App Runner service with no WAF in front of it
is an unshielded origin: it is defenseless against the L7 abuse patterns (SQLi,
XSS, credential stuffing, bot floods) that the VPN previously made moot by
simply being unreachable. Public ingress is a new boundary that has to be
built, not a checkbox.

This file's job is to design the replacement for each broken assumption in
turn: ingress (s2), identity (s3), and the tenant-provisioning + isolation
posture that ties them together (s4-s5).

---

## 2. Public, hardened ingress - ALB/CloudFront + WAF + ACM + Shield

**The shape.** Public traffic terminates at an Application Load Balancer or
CloudFront distribution - never directly at the App Runner service - with AWS
WAF attached, TLS via ACM, and AWS Shield Standard automatically in place (with
Shield Advanced as an option for a product with real DDoS exposure). App Runner
itself CAN be made public
(`IsPubliclyAccessible: true`,
https://docs.aws.amazon.com/apprunner/latest/dg/network-vpc.html), but a raw
public App Runner URL with no front door is the "unshielded origin" problem
from s1. The front door is what turns "publicly reachable" into "publicly
defensible."

```
                    Public internet (customers, anywhere)
                              |
                    DNS: <CUSTOMER_DOMAIN>  (Route 53 or customer's own DNS)
                              |
                              v
              +----------------------------------------+
              |  CloudFront distribution (or ALB)        |
              |  - TLS via ACM cert <ACM_CERT_ARN>        |
              |  - AWS Shield Standard (automatic)        |
              +--------------------+---------------------+
                                   |
                                   v
              +----------------------------------------+
              |  AWS WAF Web ACL  <WAF_WEB_ACL_ARN>       |
              |  - AWS Managed Rule Groups                |
              |    (Core rule set, Known bad inputs,      |
              |     SQLi, Bot Control)                    |
              |  - Rate-based rule (per-IP request cap)   |
              +--------------------+---------------------+
                                   |
                                   v
              +----------------------------------------+
              |  AWS App Runner service <APP_NAME>-cust  |
              |  IsPubliclyAccessible: true               |
              |  (reachable ONLY as WAF/CDN origin -      |
              |   restrict further with a shared secret   |
              |   custom header the CDN injects, checked   |
              |   by the app, so direct-to-origin calls    |
              |   that skip the CDN are rejected)          |
              +----------------------------------------+
```

**Choosing ALB vs CloudFront.** Both attach WAF the same way
(https://docs.aws.amazon.com/waf/latest/developerguide/how-aws-waf-works.html).
CloudFront additionally gives you edge caching and a broader DDoS absorption
surface (Shield Standard is strongest at the CloudFront/Route 53 edge); ALB is
the simpler choice if the app is pure dynamic API traffic with nothing worth
caching. For a customer-facing product with a marketing/app SPA plus an API,
CloudFront in front of the SPA + API is the common default - confirm against
the actual traffic shape before deciding, and flag the choice for IT/security
review either way (s7).

**AWS WAF - managed rule groups + rate-based rules.** Do not hand-author rules
from scratch as the first line of defense; start from AWS Managed Rule Groups
(Core rule set, Known Bad Inputs, SQL Database, and optionally Bot Control /
Account Takeover Prevention for a login-heavy product)
(https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-list.html),
then layer a rate-based rule that blocks an IP exceeding a request-count
threshold in a rolling window
(https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html).
**(!) Version-sensitive: AWS revises managed rule group contents and rate-based
rule evaluation windows over time - re-pull the current rule-group list and
defaults before configuring, do not hardcode a rule-group version.**

**TLS via ACM + custom domains.** Request or import the customer-facing
certificate in AWS Certificate Manager, attach it to the CloudFront
distribution or ALB listener, and point `<CUSTOMER_DOMAIN>` at it via Route 53
(or the customer's own DNS if the domain is customer-owned)
(https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html). This
replaces `aws-architecture.md` s3.2's DNS caveat (App Runner's own
custom-domain feature is public-only and was irrelevant for the internal
path); here it is exactly the mechanism you want, just fronted by CloudFront/
ALB rather than attached to App Runner directly.

**DDoS posture - Shield Standard is automatic; Shield Advanced is a decision,
not a default.** Shield Standard protects every CloudFront distribution and
Route 53 hosted zone at no extra charge
(https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html).
Shield Advanced adds cost, a 1-year commitment, and dedicated DRT (DDoS
Response Team) support - justify it against the product's actual exposure
(is it a high-profile or high-value target?), do not default to it for every
customer-facing app.

**Why not just skip the front door and put WAF rules on the app itself.**
WAF's managed rule groups run at the edge, before a request ever reaches your
compute - malformed and malicious requests never spend App Runner CPU/memory
or reach application code at all. Reimplementing that filtering in the FastAPI
app would mean writing and maintaining your own SQLi/XSS/bot-detection logic,
which is both more work and a worse security posture than a managed,
continuously-updated rule set.

---

## 3. External identity - Cognito, SSO federation, or Auth0

**The internal assumption that breaks.** `aws-architecture.md` s3.6: "a single
Entra app registration per environment." That works because every internal
user already has a firm Entra account. A customer's employees do not, and
adding every customer's every user into the firm's own Entra tenant does not
scale and is not the firm's identity to own.

**Three viable replacement patterns - pick per product, not per customer
within a product:**

| Option | Shape | Best fit |
|---|---|---|
| **Amazon Cognito user pools** | Cognito hosts sign-up/sign-in directly; issues its own JWTs; can itself federate to a customer's IdP per pool or per app client | A product selling direct to individual users or SMB customers who will not bring their own IdP |
| **Customer-SSO federation (SAML/OIDC per enterprise customer)** | Each enterprise customer connects their own IdP (Entra ID, Okta, Ping, etc.) via SAML 2.0 or OIDC; Cognito (or the IdP broker of choice) federates to N different customer IdPs | An enterprise-sold product where each customer mandates "log in with our IdP" - the common enterprise SaaS requirement |
| **Auth0** | A dedicated identity-as-a-service platform; strong out-of-box support for per-tenant SSO connections, custom domains per tenant, and enterprise federation | When the number and variety of customer IdPs is large enough that hand-rolling federation config in Cognito becomes its own product to maintain |

**Cognito as the default starting point.** For most customer products,
start with a Cognito user pool: it is AWS-native (no new vendor relationship),
integrates directly with the ALB/CloudFront + App Runner shape above via an
ALB authenticate-cognito listener rule or a backend JWT check, and supports
adding SAML/OIDC identity providers to the SAME pool later without a
re-architecture
(https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html,
https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html).
Escalate to per-customer SAML/OIDC federation (still inside Cognito, as
additional identity providers on the pool, or via a broker) once an actual
enterprise customer requires "log in with our own IdP." Reach for Auth0 only
if the number of distinct customer IdPs and the per-tenant SSO config burden
outgrows what Cognito's IdP-per-pool model comfortably manages - that is a
real vendor decision, flag it for review (s7) rather than defaulting to it.

**Tenant-aware auth - "which customer is this user."** This is the piece the
internal single-Entra-tenant model never had to solve, because there was only
ever one tenant (the firm). A customer product needs to resolve `tenant_id` from
every authenticated request, by one of:

- **Pool-per-tenant** - a separate Cognito user pool per customer; the pool
  itself IS the tenant boundary (which pool issued the token tells you the
  tenant). Cleanest isolation, more pools to manage at scale.
- **Shared pool, tenant claim** - one Cognito user pool for all customers, with
  a custom attribute or a post-confirmation/pre-token-generation Lambda that
  stamps a `tenant_id` custom claim into every issued JWT
  (https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html).
  Simpler to operate at scale (one pool), but the tenant_id claim becomes a
  security-critical value - it MUST be set server-side (by the Lambda, from a
  trusted tenant-record lookup), never accepted as a client-supplied field at
  sign-up, or a malicious user could self-assign another tenant's id.
- **Federation-per-tenant** - one pool, but each enterprise customer maps to
  its own SAML/OIDC identity provider entry on that pool; the IdP that
  authenticated the user identifies the tenant.

Whichever pattern is chosen, the backend's JWT validation step must extract
`tenant_id` and treat it as the ONLY source of truth for which customer's data
this request may touch - this is the handoff point to the data-isolation model
in `app-architecture/references/multi-tenancy.md`. This file's job ends at
"here is a validated `tenant_id`"; what happens to a query using it is that
file's contract.

**Per-customer sign-up/onboarding replaces the single app registration.**
Where the internal model has one static Entra app registration per
environment (dev, prod - done once, forever), the customer model has a
REPEATABLE onboarding flow that runs once per NEW CUSTOMER (s4) - because
"add a customer" is now a runtime business event, not a one-time environment
setup step.

---

## 4. Multi-tenant provisioning - onboarding a new customer

Onboarding a new paying customer must be a repeatable, scriptable/console
procedure, not an ad hoc one-off - because unlike standing up dev/prod once,
this runs every time a new customer signs a contract.

**What gets created per new tenant:**

1. **Tenant record** - a row in a control-plane table (`tenants`: `tenant_id`,
   `customer_name`, `status`, `plan`, `created_at`) that is the source of truth
   for "this tenant exists and is active." This table itself lives in a
   platform/control-plane schema, distinct from any per-tenant data schema
   (cross-link `multi-tenancy.md` for how per-tenant data is actually
   partitioned once the tenant exists).
2. **Identity wiring** - per the pattern chosen in s3: either a new Cognito
   user pool (pool-per-tenant), a new SAML/OIDC IdP connection on the shared
   pool (federation-per-tenant), or simply a new set of users tagged with the
   tenant's `tenant_id` claim (shared-pool pattern) - whichever was chosen as
   the product's identity model.
3. **Per-tenant config** - anything that varies by customer and is not a
   secret: branding (logo, display name), feature flags/plan entitlements,
   custom domain if offered (`<TENANT_ID>.<APP_NAME>.example.com` or a fully
   customer-owned domain), notification email addresses. Store this in the
   tenant record or a keyed config table, served to the frontend the same
   runtime-config way `aws-architecture.md` s4 serves Entra config - never
   baked into the image per tenant, because that would mean a per-customer
   build, defeating the "one image, many tenants" model this whole variant is
   built to preserve.
4. **Per-tenant secrets in Secrets Manager** - anything a specific customer's
   integration needs that IS sensitive (a customer's own API key for an
   outbound integration, a per-tenant signing secret) gets its own Secrets
   Manager secret, named/tagged with `tenant_id`, fetched by the app at
   request time keyed off the resolved tenant - never one shared secret
   reused across tenants, and never a tenant's secret held in the tenant
   config table in plaintext.
5. **DNS/subdomain, if the product offers one** - a `<TENANT_ID>.` CNAME onto
   the shared CloudFront distribution (path- or host-based routing to the same
   backend, tenant resolved from the Host header) or a fully customer-owned
   domain pointed at the same distribution with its own ACM cert (CloudFront
   supports multiple alternate domain names / SNI certs on one distribution).

**The isolation boundary THIS layer enforces.** Onboarding, done correctly,
guarantees two things at the network/identity level before any application
code runs a query: (a) a request can only ever resolve to ONE tenant_id, set
by identity infrastructure the tenant's own users cannot influence, and (b) a
tenant's secrets are stored and fetched in a way that no other tenant's
request path can reach. That is the full extent of what this file's boundary
covers - it does not by itself stop a buggy query from joining across two
tenants' rows once tenant_id reaches application code. That enforcement is the
data-isolation model: see `app-architecture/references/multi-tenancy.md` for
row-level security / schema-per-tenant / database-per-tenant and which one a
given product's compliance posture requires. **Do not treat this file's
network/identity boundary as sufficient on its own** - it is necessary, not
sufficient; the data layer must also enforce the boundary independently
(defense in depth, s5).

---

## 5. Isolation + security posture

**Per-tenant data-plane isolation is a DATA-layer decision, cross-linked, not
owned here.** `app-architecture/references/multi-tenancy.md` owns the choice
between row-level security (shared tables + `tenant_id` column + a DB-enforced
policy), schema-per-tenant, or database-per-tenant, and the tradeoffs between
them. What THIS file guarantees going into that decision is a trustworthy
`tenant_id` on every request (s3-s4) - garbage in that value means every
downstream isolation control is moot, however well built.

**Encryption.** At rest: RDS encryption-at-rest (KMS-backed) for all
tenant data, and Secrets Manager's own encryption for the per-tenant secrets
in s4 - both are the same primitives the internal architecture already uses,
just now holding customer rather than internal data, which typically
raises the bar on key management (customer-managed KMS keys, stricter
rotation) - confirm against the specific customer contract's data-handling
terms. In transit: TLS terminates at the ACM cert on CloudFront/ALB (s2) and
should also run un-terminated (re-encrypted) from the load balancer to App
Runner where the compliance posture requires it end-to-end, not just
edge-to-LB.

**The "no cross-tenant access" invariant - state it, then verify it.** The
invariant a customer product must be able to assert, in writing, to a
prospective enterprise customer's security review is: *no code path, given a
valid session for tenant A, can read or write tenant B's data.* This file's
layer contributes the network/identity half of that proof (a request cannot
carry an attacker-chosen `tenant_id`); the data layer contributes the other
half (a query cannot cross the boundary even if application code has a bug).
Treat it as two independent controls, not one - the OWASP-aligned habit is
defense in depth: an identity-layer guarantee alone, or a data-layer guarantee
alone, is a single point of failure; both together tolerate a bug in either.

**Mapping to OWASP / AWS security expectations for a customer product.**

| Control area | This file's contribution | Reference |
|---|---|---|
| Injection / bad input at the edge | WAF managed rule groups (s2) block before compute | OWASP Top 10 - Injection; https://owasp.org/www-project-top-ten/ |
| Broken authentication | Cognito/SSO federation replaces ad hoc auth (s3); MFA and password policy configured at the pool/IdP, not hand-rolled | OWASP Top 10 - Identification and Authentication Failures |
| Broken access control / tenant isolation | Tenant_id resolved server-side only, never client-supplied (s3-s4); paired with data-layer enforcement | OWASP Top 10 - Broken Access Control; AWS SaaS Lens tenant isolation pillar |
| Security logging/monitoring | Extends `observability.md`'s structured logging with `tenant_id` as a first-class field on every line, so a security incident can be scoped to "which tenant" as fast as "which run" | OWASP Top 10 - Security Logging and Monitoring Failures |
| Multi-tenant architecture posture overall | The AWS SaaS Lens is the dedicated reference for tenant isolation tiers (silo/pool/bridge), noisy-neighbor mitigation, and tenant-aware operations - read it before finalizing the isolation tier for a specific product, do not treat this file as a substitute for it | https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html |

**(!) Version-sensitive.** AWS SaaS Lens guidance, Cognito federation
capabilities, and WAF managed rule groups are all actively evolving areas -
re-check current AWS docs before finalizing a design; do not treat the summary
above as frozen.

---

## 6. Cost + ops delta vs the internal shape

Public + multi-tenant costs more than the internal shape on every axis
`operations.md` s6 sizes, and adds line items that internal hosting does not
have at all:

| Cost center | Internal shape | Customer shape - what's new/bigger |
|---|---|---|
| Ingress | $0 extra (shared VPCE, IT-owned) | CloudFront/ALB data transfer + request pricing; WAF Web ACL + rule evaluations, billed per request (https://aws.amazon.com/waf/pricing/) |
| Identity | $0 extra (Entra already licensed org-wide) | Cognito monthly active user (MAU) pricing beyond the free tier, or Auth0 subscription tiers - both scale with customer count, not flat |
| DDoS | Implicit (unreachable = safe) | Shield Standard is free; Shield Advanced is a real recurring cost + 1-year commitment if elected (s2) |
| Data plane | Shared RDS instance, schema-per-module | Same instance can still work for early customers, but per-tenant isolation tier (s5) may force schema- or database-per-tenant, multiplying RDS instance/storage cost as tenant count grows - size this against `multi-tenancy.md`'s isolation-tier choice, not against s4 of `operations.md`'s single-app worksheet |
| On-call | Business-hours, internal-tool tolerance | A paying customer expects an SLA. This is a REAL on-call commitment, not the internal "escalate on health + spend only" note in `observability.md` s6 - cross-link `wd-practice-ops` / product-operations for what an actual customer-facing SLA and incident-response commitment requires before selling one |

**The rule of thumb.** Do not extrapolate the internal-tool cost worksheet
(`operations.md` s6) onto a customer product by just adding a WAF line -
identity cost scales with customer/user count, potential per-tenant data-plane
isolation scales with tenant count, and the on-call model changes in kind, not
just in degree, once there is a contractual SLA on the line. Re-run the
worksheet with these new, usage-scaling cost centers before quoting a
customer-hosting cost internally.

---

## 7. DECISION note - this needs IT/security sign-off

**State this plainly, because it is easy to skim past: everything in this
file is real AWS security-architecture work, not a configuration a solo
builder should finalize alone.** Public ingress, external identity, and
multi-tenant data isolation are exactly the surface area that a security
review exists to catch mistakes in - a misconfigured WAF rule, a tenant_id
claim that can be spoofed, an isolation tier that does not match what was
promised in a customer contract, or a Shield/on-call commitment the practice
cannot actually staff.

**What this file is, and is not:**

- **IS:** the pattern - the shape of ingress, identity, and provisioning a
  customer-sold product should start from, informed by the reference
  architecture's internal shape and AWS's own documented practices.
- **IS NOT:** an approved architecture for any specific product, and IS NOT a
  substitute for your IT/security review of the actual design (network
  diagram, IAM boundaries, data-classification-driven isolation tier, and the
  identity provider chosen) before a real customer's data goes anywhere near
  it.

Treat every design produced from this file as a DRAFT for that review, not as
a decision the suite - or a single builder following this reference - can make
unilaterally. Route it through the same product-strategy disposition gate that
flagged this gap in the first place (`practice-lifecycle` + `product-strategy`
own that gate) before committing engineering time to build it.

---

## 8. What to remember

- **This is a variant, not a replacement.** Internal tools keep
  `aws-architecture.md` unchanged; reach for this file only when the
  product's disposition is customer-sold.
- **Public ingress needs a real front door.** ALB/CloudFront + WAF + ACM +
  Shield in front of App Runner, not a bare `IsPubliclyAccessible: true` flag -
  the flag alone leaves an unshielded origin.
- **Identity moves from one Entra app registration to an external, tenant-aware
  provider.** Cognito is the default starting point; escalate to per-customer
  SAML/OIDC federation or Auth0 only when an actual customer requires it.
  `tenant_id` must always be set server-side, never client-supplied.
- **This file owns ingress + identity + tenant provisioning; it does NOT own
  data isolation.** That is `app-architecture/references/multi-tenancy.md` -
  cross-link, don't duplicate. Both layers must independently enforce
  "no cross-tenant access" - defense in depth, not one control doing double
  duty.
- **Cost and on-call both go up in kind, not just in degree** - re-run the
  cost worksheet with customer/tenant-count-scaling line items, and treat a
  customer SLA as a real staffing commitment.
- **This needs IT/security sign-off before it is a product,** not just a
  reference file to build from unilaterally.
