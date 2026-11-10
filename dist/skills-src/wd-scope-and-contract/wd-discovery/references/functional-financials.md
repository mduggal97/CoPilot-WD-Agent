# Functional literacy - Financials

Assumes shared primitives in [workday-functional-skus.md](workday-functional-skus.md) (FDM, worktags,
account posting rules, security, BP framework). Source: Financial Management, Financial Accounting,
Accounting Center, Financial Consolidation, Procure-to-Pay, Customer Accounts & Contracts (for Administrators).

**The FDM thread (trace this end-to-end in any Financials engagement):** Financial Management DEFINES the FDM
(company = balanced books; worktags = dimensions); Financial Accounting ENFORCES/EXTENDS it (worktag usage rules,
account sets, multi-book, sequencing); Accounting Center FEEDS it from external data (mapping tables -> ledger
accounts + worktags); Consolidation COMPUTES on it at report time. **Account set** and **worktags** are the two
constructs to follow through the whole build.

---

## Financial Management - the ERP foundation
Sets up the enterprise structure (companies, worktags), banking, security, and the transactional cycles (supplier/
customer invoices, payments, journals) that feed the GL.

**Constructs:** Company (balanced-books boundary); Organizations (Cost Center holds transactions/budgets/workers,
Location, Region + sector types Program/Fund/Project/Business Unit); Worktags (<=15 custom types; <=10 financial-
enabled org worktags; related-worktag defaulting); Organization Hierarchies (reporting rollups, no posting); security
groups/domains/policies. Financial event = automated accounting triggered by an operation.

**Gotchas:** (1) Company = the balanced-books boundary - almost every accounting decision is per-company. (2) worktag
caps are real design constraints - model the dimensional design early. (3) hierarchies are reporting-only; posting is
at org/company level. (4) related-worktag defaulting + "last one in wins" can silently overwrite dimensions -
validate defaulting order. (5) role-based groups scope to org targets; user-based groups are effectively tenant-wide.

**HC/Higher-Ed:** the sector org types **Fund, Grant, Program, Project** + custom worktags ARE the standard
higher-ed/nonprofit fund-accounting and grant-tracking structures.

---

## Financial Accounting - advanced core-financials + close
Data-integrity controls plus the advanced accounting engines: journal sequencing, intercompany, multi-book,
allocations, account certification, lease accounting, and period-end close.

**Constructs:** Custom Validations (critical/warning; reusable across transaction types); **Worktag Usage** (Primary
single-field vs. Additional multiselect, optionally required, per transaction type) + Related Worktag Usage;
**Sequence Generator Rules** (lifespan, accounting-vs-posting date, format placeholders, padding); **Company
Intercompany Profile** (companies must share the same **account set**); Allocation definition (Source/Basis/Target/
Offset) + Allocation Group Set; Account Certification Sets; lease accounting (ASC 842 / IFRS 16) + posting rules.

**Core terminology:** Custom Validation severity - Primary vs. Additional worktag - Sequence padding - Intercompany
Affiliate (worktag for due-to/due-from) - On Behalf Of vs. Direct intercompany - **Account Set** (shared chart/rules
grouping; prerequisite for intercompany + consolidation) - Allocation Basis (Fixed Percent / Pro-Rata / Spread Even)
- Pro Forma (draft allocation journal) - Account Certification Set / Auto-certification - ROU asset / lease liability
- ASC 842 vs. IFRS 16.

**Gotchas:** (1) journal sequencing is ONE-WAY - enable before posting, can't retro-apply, **can't be disabled once
on** (a compliance decision, not a toggle). (2) intercompany requires companies to SHARE an account set (also gates
consolidation eliminations). (3) recommend one Account Certification Set per company. (4) every allocation needs all
four parts; Pro Forma lets you verify before finalizing. (5) lease treatment forks on standard (ASC 842 vs. IFRS 16)
+ lease type. (6) EIB template model for bulk journal import.

**HC/Higher-Ed:** statutory journal sequencing + account certification support academic-medical-center/university
audit rigor; intercompany/multi-book support multi-entity health systems and university+health-system splits.

---

## Accounting Center - external data -> GL journals (Prism-based)
Ingests high-volume external/operational transaction data, enriches it with worktags + account posting rules, and
generates balanced journal entries into the ledger. Use when transaction data lives outside Workday or is too
high-volume for standard journal import.

**Four-phase flow:** Acquire -> Transform -> Publish -> Report (engine stages: Ingestion -> Enrichment ->
Transformation -> Detailed Accounting -> Summarization).

**Constructs:** Prism Table (schema-validated, rejects invalid rows on load) / Base Dataset (schema-on-read,
NULL-out at publish) / Derived Dataset; Pipeline of stages (Value Mapping, Joins, Validation, Manage Fields, Filter,
Group By, Union, Unpivot); Accounting Source (orchestrates enrichment/validation/detailed-accounting/posting);
Mapping Tables (input->output -> worktags/ledger accounts); Account Posting Rules; Accounting Groups; Data Change Task.

**Core terminology:** schema-on-read - Value Mapping stage - Left Outer Join (recommended, preserves transaction
count) - Detailed vs. Summarized accounting - Transaction Grouping ID (links rows into a balanced unit of work) -
Additional Attributes (detail-only) - WPA fields (audit) - Error Manager (edit / dismiss / reprocess).

**Gotchas:** (1) validation timing differs by object - Tables reject on load; Base Datasets NULL-out at publish. (2)
use Left Outer Join to avoid inflating/dropping counts. (3) Transaction Grouping ID enforces balanced units + drives
error handling - design it deliberately. (4) Detailed vs. Summarized is an audit-detail vs. ledger-performance
trade-off; some attributes survive only in detailed.

**HC/Higher-Ed:** classic use = high-volume operational feeds - patient billing/claims/charges (health), SIS/bursar/
research (higher-ed) - enriched into GL journals; Prism blending suits research-grant and clinical-ops reporting.

---

## Financial Consolidation - multi-entity roll-up
Combines multi-entity financials up to a parent, applying eliminations, noncontrolling interest (NCI), equity pickup,
and multicurrency translation/revaluation.

**Constructs:** intercompany profiles, company hierarchies, ownership details, elimination rules by account set (three
categories: Intercompany/Interworktag, NCI Activity, Equity Pickup); Variance Account (per-rule, best practice);
Equity Pickup Rules; currency rate types (Current/Historical/Average); Revaluation Rules; Close and Consolidation Hub.

**Core terminology:** consolidation methods by ownership (<20% cost / 20-50% equity / >50% full + NCI) - Elimination
entry (report-time, NOT stored in actual accounting) - Intercompany Affiliate - Roll-forward (retained earnings must
carry the Intercompany Affiliate worktag) - Noncontrolling Interest - Consolidation Journals (posted in the
Eliminations column) - Conversion vs. Translation vs. Revaluation.

**Gotchas:** (1) eliminations/NCI/equity-pickup are **report-runtime, not journal-persisted** - the ledger stays
clean while consolidated views are computed. (2) ownership % + effective dates drive the method - get them right or
the roll-up is wrong. (3) run revaluation BEFORE equity pickups/allocations. (4) depends on a shared account set
(ties to Financial Accounting intercompany). (5) retained earnings must carry the Intercompany Affiliate worktag or
year-end eliminations break on roll-forward. (6) currency-rate effective timestamp is PST regardless of tenant -
non-US clients frequently misload.

**HC/Higher-Ed:** multi-hospital legal entities/JVs (NCI, equity method); universities consolidating a health system +
academic entities + foundations; multicurrency for global research/international campuses.

---

## Procure to Pay (Procurement + Supplier Accounts) - spend management
Acquire goods/services/project-services/contingent labor and settle supplier payables, with real-time analytics.

**Process flow:** Requisition -> Sourcing -> Purchase Order (issue/acknowledge/change) -> Receiving & Returns ->
Supplier Invoice -> Matching (2/3/4-way, real-time) -> payables settlement -> month/year-end -> spend reporting.
Supplier lifecycle + supplier-contract governance + item management run alongside.

**Constructs:** Spend Categories (hierarchical commodity classification driving accounting/sourcing); Requisition &
Purchase Order Types (incl. **Bill Only** = no accounting, **Consignment** = at no cost); Supplier Category (exactly
one required), duplicate-detection + sanction-list screening; Purchase/Supplier/Catalog/Web items; **Match Rule Set**
(one per company); Requisition Sourcing Rules (ranked attribute precedence); Procurement Conditional Rules.

**Core terminology:** Requisition - Requisition Sourcing Rule - Purchase Order / POA (acknowledgement) / Change Order
- Receipt - Supplier Invoice - Match Exception / 2-3-4-way Match / Match Tolerance - Supplier / 1099 Supplier -
Supplier Contract (15 types incl. leases) - Catalog Item (can auto-route a PO, bypassing requisition) - Bill Only.

**Gotchas:** (1) this is the ADMIN/config course - it stops at payables/close + spend reporting; cash disbursement/
settlement runs live in Financial Accounting. (2) ONE Match Rule Set per company; matching is real-time and re-fires
on receipt/PO-change events - tolerance design controls auto-pay rate. (3) Bill Only (no accounting) / Consignment
(no cost) are accounting-special - misclassifying a requisition type breaks journals. (4) pricing hierarchy: Supplier
Contract line > Advance Pricing > Supplier Info > Purchase Item default. (5) can't receive/invoice a PO until Issued;
can't receive items not on the PO.

**Integration touchpoints (our work):** supplier inbound via Supplier Collaboration hosted sites / portals + EDI;
item feeds via punchout/UNSPSC + worksheet mass-maintain (<=5,000); invoice inbound via Supplier Invoice Requests /
EIB / ASN; Discovery Boards + role-based dashboards for spend. **Supplier-invoice inbound is a canonical O4I/Studio
integration** (see wd-extend-dev orchestration.md `supplierInvoicesInbound`).

**HC/Higher-Ed:** ships healthcare supply-chain reports; Item Tags (Refrigerated/Latex-Free), PAR Replenishment +
Inventory usages for hospital par-stocking; Supplier Diversity dashboard for diversity-spend mandates.

---

## Customer Accounts and Contracts (Revenue Management) - opportunity-to-cash
Customer setup, contracting, billing, revenue recognition (ASC 606 / IFRS 15), invoicing, cash application, collections.

**Process flow:** Customer -> Customer Contract -> Billing Schedule -> Customer Invoice -> Revenue Recognition ->
Customer Payment (record -> apply -> deposit) -> collections. Account Posting Rules journal every step.

**Constructs:** Customer Category (one; drives receivables ledger account); Revenue Categories (hierarchical,
worktag-capable, a posting-rule condition); Sales Items (exactly one revenue category); Account Posting Rules
(dimensions AND, values OR, most-to-least restrictive, default last); Contract Types + 11 Workday Contract Line Types;
fair-value price lists; Billing Schedules + Methods + Milestones; Revenue Recognition Methods (6); Payment Rule Sets +
Application Rules; Settlement Engine.

**Core terminology:** Customer Category / Hierarchy - Revenue Category - Sales Item - Customer Contract - **Contract
Line Type** (one of 11; fixes field behavior; CANNOT change after approval) - Billing Schedule / Installment - Out of
Balance (blocks processing when lines != installment amounts) - Deferred vs. Accrued Revenue - Revenue Recognition
Schedule - Alternate Contract (draft replica for ASC 606 modeling) - Auto-Apply - Write-off - Milestone (hard gate) -
Usage Billing Rate.

**Gotchas:** (1) Contract Line Type is destiny - dictates whether a line bills, recognizes revenue, or both, and
can't change after approval. (2) billing and revenue are decoupled (separate schedules/methods/installments) but must
reconcile at contract level ("Out of Balance" blocks). (3) ASC 606 via multiple-element fair-value allocation +
Alternate Contracts for what-if modeling. (4) milestones are hard gates - pending milestones stop billing/revenue. (5)
can't cancel invoices once a payment/write-off/credit exists - use credit-and-rebill. (6) payment application must net
to zero to submit.

**HC/Higher-Ed:** Subscription/Prepaid/Usage-Based/Recurring line types + Sponsor invoices apply to higher-ed
sponsored-billing/grants and healthcare recurring-service/membership billing (not called out in the manual, but
directly relevant).
