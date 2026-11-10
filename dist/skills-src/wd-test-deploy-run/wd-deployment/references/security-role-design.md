# Client production security-role design (the end-user security model)

Designing **who can see and do what in the client's production Workday tenant** - the end-user security model:
security groups, the roles that map to them, domain and business-process access, and segregation of duties.
This is a functional DESIGN activity (done during design, implemented at deployment); it is distinct from the
*machine* security that lets a built app/integration run.

## Security ownership map (which reference owns which security question)

Security is the most-scattered topic in the suite; use this map so "help with security" lands in the right place:

| Security question | Owner |
|---|---|
| **The client's END-USER production security model** (who gets which security groups; role design; SoD) | **this file** |
| An Extend APP's runtime security (its ISU, security domains, App-Attribute WIDs, BP security) | wd-extend-dev `references/security-setup.md` |
| A traditional INTEGRATION's security (ISU/ISSG, integration security segments - who sees which integration systems) | wd-integration-dev (`integration-naming.md` + the security-segment worksheet) |
| The reusable **Security Setup Section** every deployment/tenant guide embeds (exact tasks + the enumerated domains-and-permissions table for the built solution) | wd-deployment `references/security-setup-section.md` |
| Answering a client **InfoSec/security questionnaire** about an Extend app | wd-deployment `references/security-questionnaire.md` |
| The client's **technical team's** access (who on the client owns integrations/Extend/Prism/reporting/security, staged least-privilege provisioning) | wd-extend-lifecycle `references/customer-technical-roles.md` |
| Sensitive-data handling classification (PII/PHI/FERPA) and the AI/data governance gate | wd-extend-lifecycle `references/ai-data-governance.md` |
| Programmatically **discover** the domains/BP permissions a built app or integration needs, and (dev/sandbox) **apply** the grants via guarded SOAP - the non-browser bulk path, an alternative to the browser recipe in wd-tenant-config | wd-extend-dev `scripts/security_domain_discovery.py` + `security_domain_apply.py` (spec: `references/scripts.md`; safety model: `references/domain-apply-safety.md`) |

This file owns the first row; it hands the built model to the rows below for implementation.

## Workday security building blocks (plain language)

- **Security groups** are how access is granted. The common types:
  - **Role-based (position-based)** - access follows a POSITION's assigned role (e.g. "Cost Center Manager").
    People inherit access when they move into the position. **Preferred for scale** - it self-maintains as people move.
  - **User-based** - access is assigned to named users. Simple, but high-maintenance and audit-heavy; reserve for
    small admin/config populations, not broad end-user access.
  - **Aggregation** - combines several groups into one (a convenience wrapper); grants nothing new by itself.
  - **Segment-based** - grants access to a narrow SLICE of data (e.g. specific document categories, pay components).
  - **Intersection** - access only where membership in two groups overlaps (tighter targeting).
- **Constrained vs unconstrained** - a *constrained* (contextual) group sees only its own organization's data
  (a manager sees their own team); an *unconstrained* group sees ALL instances. **Default to constrained**
  (least privilege); every unconstrained group is an audit question you must be able to answer.
- **Domains** control access to DATA and TASKS by functional area (View/Modify, or Get/Put for integrations).
- **Business-process security policies** control who can INITIATE, APPROVE, or view each step of a process.
  Role design must cover both domain access (the data) and BP policy access (the actions) - people miss the BP side.

## The design method

1. **Start from role mapping** (wd-change-adoption `impact-and-readiness.md`) and the security requirements from
   discovery (wd-discovery dimension 5): the list of job roles and what each must do.
2. **Define each security role** - name it for the job, list the tasks/data it needs, and pick the group TYPE
   (default role/position-based; user-based only for small admin sets).
3. **Choose the constraint** - constrained by which organization dimension (cost center, supervisory org,
   company, region)? Least privilege: grant the narrowest context that lets the role do its job.
4. **Map to domains + BP policies** - for each role, which domains (View vs Modify) and which BP steps
   (initiate/approve/view). Keep a role-to-domain-to-BP grid so coverage and gaps are visible at a glance.
5. **Run the SoD check** (below) before finalizing.
6. **Document in the design-doc Security tab** (wd-design-doc), then hand to implementation
   (security-setup-section.md + tenant-task-recipes for the click-level setup, per tenant).

## Segregation of Duties (SoD) matrix

SoD prevents one person from controlling both sides of a risky transaction. Build a matrix of conflicting
duty PAIRS and check no single role (or realistic combination of a person's roles) holds both:
- Classic conflicts: create/edit a supplier **and** approve its payment; hire/appoint **and** set that person's
  pay; create a customer **and** write off its receivable; configure security **and** approve one's own access;
  enter a journal **and** approve it.
- For each conflict: list the two duties, the domains/BPs that grant each, which roles hold them, the risk if
  combined, and the **mitigation** (split the roles, or a compensating control - e.g. a mandatory second
  approver, or an after-the-fact audit report - when the org is too small to split).
- SoD is the most common thing skipped and the most common audit finding - make it an explicit design gate, not
  an afterthought. Where a small team cannot fully separate duties, DOCUMENT the compensating control.

## Security design workbook (the deliverable)

One row per security role, columns: Role name | Group type (role/user/aggregation/segment) | Constrained by |
Domains (View) | Domains (Modify) | BP policies (Initiate/Approve/View) | SoD conflicts + mitigation | Business
owner | Notes. Plus an SoD-matrix tab (conflict pairs x roles) and a role-to-person assignment tab. This is the
functional design; the domains-and-permissions IMPLEMENTATION table for the built solution lives in
security-setup-section.md.

## Security testing (positive AND negative)

Test each role two ways: it **can** do everything its job needs, and it **cannot** do anything it should not
(negative testing is where over-provisioning hides). Use proxy / "view as" to experience the tenant as a role.
Remember **Activate Pending Security Policy Changes** must run for grants to take effect, and re-test after it.
Fold role-based test cases into the wd-testing scenario set.

## Audit & attestation (ongoing)

- **Least privilege, reviewed:** periodic access reviews (who has unconstrained/admin groups and why), removal
  of access on role change or termination, and manager/owner attestation of their team's access.
- **Sensitive domains** (PII/PHI/FERPA/comp data) get tighter constraint and an explicit owner; classify per
  ai-data-governance.md.
- **FERPA (student education records):** any role granting access to education records records its
  **legitimate-educational-interest** justification (FERPA's "school official with legitimate educational
  interest" access basis); access reviews attest to it - the FERPA analogue of the least-privilege/SoD
  discipline above. **HIPAA (PHI):** scope roles to the **minimum necessary** for the job, not the whole record.
- Keep the security workbook current as config evolves - a stale security model is both an adoption problem
  (people cannot do their jobs) and an audit problem (people can do too much).

## Where this goes / handoffs

Model designed here -> **wd-design-doc** Security tab (documented) -> **wd-deployment**
security-setup-section.md + tenant-task-recipes (implemented per tenant, with **Activate Pending Security Policy
Changes**) -> **wd-testing** (role-based positive/negative test cases). Role source = **wd-change-adoption**
role mapping; requirements = **wd-discovery** dimension 5; app/integration machine security stays with
**wd-extend-dev** / **wd-integration-dev** per the ownership map above.
