# Healthcare + Higher-Ed Adjacent Systems

Fluency-tier briefs on the vertical systems a Workday consultant meets
constantly in healthcare and higher-ed accounts, but does not own end to end:
UKG, GHX, Kyriba, TouchNet, symplr, and Ellucian Banner/Colleague. This is NOT
a deep-recipe reference like `salesforce.md` or `servicenow.md` - it is the
"walk into a design session and not sound lost" tier. Know where each system
sits relative to Workday, what the canonical integration shape looks like, and
the two or three gotchas that catch a first-timer.

**Version-sensitive:** vendor product names, certification status, and
partnership claims move fast here (UKG's Kronos/Dimensions rebrand, Workday
partner-of-the-year callouts, Marketplace app numbers). Anything time-bound
is flagged **verify-current** with the date checked. Facts are graded
CONFIRMED (vendor/primary source), REPORTED (secondary/press), or JUDGMENT
(synthesis), per the grounding research this file was built from (research
date 2026-09-10).

## How to use this reference

1. **Find the system in the landscape map** to see where it sits relative to
   Workday and its typical transport.
2. **Read that system's brief** for the canonical integration shape and the
   two or three gotchas that make a design session go sideways.
3. **Escalate when the work gets real.** This file gets you through
   discovery and design - it does not replace the vendor's current docs
   (some GATED), `healthcare-epic-fhir.md` for anything Epic/HL7/FHIR (a
   sibling reference in this skill), or `wd-integration-dev` /
   `wd-extend-dev` for the Workday-side build once the shape is agreed.
4. **Do not over-claim certification.** GHX and TouchNet ship certified
   Workday Marketplace products; symplr and Banner/Colleague are custom-
   integration territory. Know which is which before scoping.

## Landscape map

| System | Vertical | Sits between | Typical transport |
|---|---|---|---|
| UKG Pro / Pro WFM | Healthcare | Workday HCM/Payroll <-> hospital clinical timekeeping | API (UKG marketplace) + legacy flat-file |
| GHX | Healthcare | Workday SCM <-> supplier/GPO exchange network | EDI (ANSI X12) over the GHX exchange, certified connector |
| Kyriba | Both, strong higher-ed | Workday Financials <-> banks/payment rails | API (Kyriba Connect) + bank files (SWIFT, BAI2, positive pay) |
| TouchNet | Higher-ed | Workday Finance/Student <-> campus payments + SIS | API + certified Workday Marketplace app |
| symplr | Healthcare | Workday HCM <-> provider credentialing/privileging | Custom API/flat-file - no certified connector |
| Ellucian Banner/Colleague | Higher-ed | Workday HCM/Financials/(Student) <-> legacy SIS | Ethos Integration APIs, flat-file, EIB |

---

## 1. UKG (Pro / Pro WFM, formerly Dimensions/Kronos)

**Where it sits:** the default clinical timekeeping system in hospitals moving
HR/Payroll to Workday - the two coexist indefinitely; Workday rarely displaces
UKG for 24/7 shift scheduling. UKG's product line has churned names (Kronos ->
Workforce Dimensions -> UKG Pro Workforce Management / "Pro WFM") - **verify-
current** the customer's actual product name (checked 2026-09-10).

**Canonical flow:** worker demographics/org data DOWN, Workday -> UKG (hire,
transfer, term, job, cost center) so UKG can schedule a current worker; time
and attendance results UP, UKG -> Workday Payroll input (time blocks,
exceptions, accruals) each pay cycle.

**Transports:** UKG's own API surface (marketplace/REST) on newer builds;
legacy flat-file interfaces (fixed-width/comma extracts, often still called
WIM - Workforce Integration Manager - patterns from the Kronos era) for
either direction - many hospitals still run file-based batches even where
APIs exist, because that is what the original implementation left behind.

**Gotchas:** employee-ID matching - UKG often keys off a badge ID/legacy
employee number, not the Workday Worker ID; the crosswalk (and who creates it
on hire) is the first design decision. Pay-code mapping between UKG time
results and Workday earning codes is a manual table, not 1:1 - pull the full
list before scoping. Retro-pay reconciliation when a worker's org/position
changes mid-pay-period but UKG already recorded time against the old cost
center - decide whose timing wins. Real-time vs batch - scheduling wants
near-real-time worker updates; Payroll input tolerates batch; do not force
one cadence for both. Sources: healthcareitleaders.com "Bridging the Gap:
UKG & Workday Integration in Healthcare" (REPORTED); suretysystems.com
Kronos-Workday guides (REPORTED) - no certified-connector claim found in
primary Workday/UKG sources as of 2026-09-10, so treat "certified" language
from either vendor as verify-current.

---

## 2. GHX

**Where it sits:** the healthcare supply-chain exchange between Workday SCM
and suppliers/GPOs. "GHX for Workday Cloud ERP" is a named, certified product
(CONFIRMED, ghx.com/ghx-for-workday-cloud-erp, checked 2026-09-10) - the
default answer, not a custom build, for a hospital on Workday SCM needing
supplier connectivity.

**Canonical flow:** item-master sync (supplier catalog into Workday's item
master, near-real-time); POs OUT through GHX to the supplier; order
confirmations, ASNs, and invoices BACK through GHX into Workday; backorder
status tracked on the same exchange.

**Where bill-only sits:** bill-only is a product (commonly a physician-
preference implant) used directly from a supplier's trunk stock without first
being drawn from hospital inventory - billed to the patient and paid to the
supplier without a normal inventory depletion. It rides the same GHX PO/
invoice exchange as a variant transaction: the "order" is really a usage
confirmation after the fact, reconciled against the invoice rather than an
inventory-issue transaction in Workday SCM. Scope it explicitly in discovery
- it skips the standard receive-then-issue sequence and is a common gap.

**Gotchas:** GHX rides EDI (ANSI X12 850/855/856/810) over the exchange
network, not a direct point-to-point API - the network, not the hospital or
supplier, is the integration hub. Confirm which document set is actually in
scope; not every connected hospital runs all of them. Tecsys also has a
certified Workday integration for point-of-use supply capture (REPORTED, via
Seeking Alpha) - a related but distinct product. Source: ghx.com/ghx-for-
workday-cloud-erp (CONFIRMED, checked 2026-09-10).

---

## 3. Kyriba

**Where it sits:** treasury - between Workday Financials (system of record
for GL/AP/AR) and the banking world (connectivity, payment execution, cash
positioning, positive pay). Workday named Kyriba its 2025 Technology Partner
of the Year (CONFIRMED, kyriba.com/partner/workday, checked 2026-09-10) -
Workday's own preferred treasury partner, not a workaround.

**Boundary vs Workday Financials:** Workday stays system of record for the
accounting entries and the payment REQUEST (an approved AP run, a settlement
instruction); Kyriba owns everything past that - bank-format translation
(SWIFT, BAI2, positive-pay), multi-bank connectivity, cash visibility, and
payment execution - with reconciliation status flowing back to keep the GL
current. Do not let a design push payment-rail logic into Financials.

**Higher-ed angle:** Kyriba publishes a dedicated higher-ed solutions page
(CONFIRMED, kyriba.com/solutions/industries/higher-education, checked
2026-09-10) - endowment cash management, multi-entity/fund treasury, and
connectivity across a university's fragmented bank relationships (financial
aid disbursement, athletics, foundation entities).

**Gotchas:** prebuilt API connectivity exists (Kyriba Connect) but bank
onboarding timelines are bank-side - build that lead time into any project
plan touching treasury. Positive-pay formats stay bank-specific even where
Kyriba standardizes its own interface, so do not assume one file spec covers
every bank in a multi-bank client. Sources: kyriba.com/partner/workday and
kyriba.com/solutions/industries/higher-education (both CONFIRMED, checked
2026-09-10).

---

## 4. TouchNet

**Where it sits:** the campus commerce/payments layer for higher-ed - student
account payments, e-commerce, cashiering - alongside Workday Finance and,
where relevant, Workday Student. TouchNet ships a certified Workday
Marketplace app, "Secure & Integrated Payments for Higher Education"
(CONFIRMED, marketplace.workday.com app 452407, checked 2026-09-10).

**Two distinct patterns - do not conflate them:** GL-to-Workday-Finance -
payment/refund transactions processed in TouchNet are summarized and posted
into Workday Financials as GL entries; TouchNet is system of record for
transaction detail, Workday Finance for the ledger. SIS-to-Workday-Student -
for a campus running (or transitioning) a student information system
alongside Workday Student, TouchNet publishes an integration FAQ on the
SIS-side data needed for billing/payment (CONFIRMED, touchnet.com FAQ,
2024-06-25) - a separate integration, relevant only where Student (or a
legacy SIS beside it) is in play.

**Gotchas:** confirm which pattern (or both) a campus actually needs - a
Finance-only customer needs GL posting only. TouchNet's FAQ documents a
matrix of SIS pairings (Banner SaaS, Colleague SaaS, Workday Student,
Anthology) worth pulling directly when scoping a Student-adjacent engagement.
Sources: touchnet.com SIS-integration FAQ (CONFIRMED, 2024-06-25);
marketplace.workday.com app 452407 (CONFIRMED, checked 2026-09-10).

---

## 5. symplr

**Where it sits:** provider credentialing and privileging - verifying and
tracking a clinician's licenses, board certifications, and hospital
privileges. symplr claims 9 of 10 US hospitals (REPORTED, symplr.com product
pages and CIO Guide PDF, 2025) - assume any hospital client runs it or
evaluated it.

**Why this is a differentiator:** unlike GHX or TouchNet, no publicly
documented certified Workday connector for symplr surfaced in current
research (checked 2026-09-10) - the Workday HCM-to-symplr linkage is
**custom integration work** a generalist Workday shop will not have a
pattern for. Treat symplr's own developer/API docs as **GATED** (vendor-
portal access required) - confirm access during discovery, not build time.

**The provider-master boundary question:** a physician can be simultaneously
a Workday HCM worker, a symplr-tracked provider (credentialing record), and
an Epic provider (scheduling/ordering identity) - three systems, three IDs,
no single system of record. The decision that matters most: which system is
authoritative for which attribute (employment/Workday, credentialing/symplr,
clinical identity/Epic), and how the crosswalk survives any one changing.
Surface this in discovery - it is the most common scoping gap on a
healthcare HCM engagement with active medical staff.

**Gotchas:** credentialing events (a lapsed license, expired DEA
registration) can trigger HR consequences (suspension, leave) that need to
flow INTO Workday - confirm both directions are in scope, not just
provider-master sync outward. Sources: symplr.com product pages and CIO
Guide PDF (REPORTED, 2025); the Workday-linkage claim is JUDGMENT based on
absence of a public certified connector - verify-current before telling a
client "no integration exists."

---

## 6. Ellucian Banner / Colleague

**Where it sits:** the incumbent student information systems (SIS) in
higher-ed, coexisting with Workday HCM/Financials during a phased adoption,
or retained indefinitely where a campus never buys Workday Student. A typical
higher-ed client runs the common phasing: **HR/Financials first**, SIS retained
as-is, with crosswalk integrations so Workday and the SIS agree on who a
person is and where money posts.

**Canonical crosswalks:** person/position - a student worker or SIS-tracked
person (financial aid recipient, student employee) needs a Workday Worker ID
minted and kept in sync with the SIS person record; Workday HCM is typically
authoritative for employment, the SIS for academic/student status, keyed off
a shared identifier (a campus-wide person ID, not either system's internal
key). GL crosswalk - student billing, financial aid, and tuition revenue in
the SIS post into Workday Financials as summarized GL entries; the chart-of-
accounts mapping between SIS fund/org codes and Workday worktags is the
recurring design artifact.

**Transport:** Ellucian's modern layer is Ethos Integration (an API-based
data hub/iPaaS meant to replace older point-to-point interfaces) -
**verify-current** against the campus's actual version and Ethos adoption
before assuming API-first; many long-running SIS shops still lean on
flat-file extracts and Workday EIB inbound loads for the crosswalks above.
JUDGMENT/industry-pattern, not a sourced fact from the grounding research -
validate against the campus's current Ellucian contract during discovery.

**Gotchas:** phasing order matters - HCM/Financials-before-Student (the
common path) still needs the person/position crosswalk from day one even
with no Workday Student to reconcile against yet; do not defer it. TouchNet's
own SIS-pairing matrix (section 4) is a useful map of what a campus actually
runs when scoping this. Sources: touchnet.com FAQ, 2024-06-25 (CONFIRMED,
for the SIS-pairing matrix context only); Ellucian Ethos positioning is
JUDGMENT/general industry knowledge, not in the grounding research -
verify-current against Ellucian's own docs (ellucian.com /
developer.ellucian.com, may be partner-gated).

---

## Boundaries

**Workday-side build stays out of this file.** Once a shape above is agreed,
the EIB, Core Connector, Studio assembly, or O4I orchestration that
implements it is `wd-integration-dev` (traditional) or `wd-extend-dev` (O4I/
Extend) - this reference is decision and context only. **Epic and FHIR are a
sibling reference:** deep HL7v2/FHIR interface material, Epic's provider-
master and inventory-depletion patterns, and the Workday-Epic governance
boundary live in `healthcare-epic-fhir.md` (a companion reference in this
skill); this file only brushes Epic where symplr's provider-master question
touches it. **This is fluency, not mastery** - if a project scopes real
build hours against any system above, go to the vendor's current
documentation (noting GATED items) before committing to a design.

Grounded in web research conducted 2026-09-10; treat every vendor-partnership,
certification, and naming claim above as **verify-current** before repeating
it in a client-facing document - this space moves fast and this file is a
snapshot, not a living feed.
