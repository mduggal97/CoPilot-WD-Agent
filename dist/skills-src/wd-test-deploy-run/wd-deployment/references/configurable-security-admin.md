# Workday configurable security - the concept and rules layer

doc-sourced - Workday Education course manuals (public), crawled 2026-08-25; cite: "Security for Administrators" + "Creating and Securing Integrations".
These are doc-tier facts: verify in-tenant before load-bearing use (labels and options can shift by release).

**Where this file sits:** this is the CONCEPT + RULES layer under the two files that already exist:
`security-role-design.md` (DESIGNING the client's end-user model) and `tenant-task-recipes.md`
(the click-level R1-R12 procedures). When a step is procedural, this file cites the recipe number
instead of restating clicks. App-runtime security (ISU for an Extend app, App Attributes) stays in
wd-extend-dev `security-setup.md`; the embeddable guide section stays in `security-setup-section.md`.

## The framework - five layers, two of them fixed

Chain: **System Users -> Security Groups -> Security Policies -> Domains (grouped into Functional Areas)**.

- A **domain** is a vendor-predefined set of related securable items: tasks, reports, report fields,
  data sources, data source filters, web services.
- **Fixed by Workday (not configurable):** domain contents, the set of domains, functional-area
  composition, the set of business process types.
- **Configurable by admins:** security group creation and membership, which groups sit on each
  domain/BP security policy, BP definition steps.
- Key admin reports: **Maintain Functional Areas**, **Domain Security Policies for Functional Area**,
  **Business Process Security Policies for Functional Area**.

### Permission levels

| Where | Levels | Rule |
|---|---|---|
| Domain policy - Report/Task section | View / Modify | Modify implies View |
| Domain policy - Integration section | Get / Put | Put implies Get |
| BP security policy | initiate, participate in action steps, approve, deny, delegate, view all, cancel, rescind, manually advance | granted per group per policy |

## THE ACTIVATION ASYMMETRY (the single most-missed rule)

Two different change classes with opposite behavior:

| Change | When it takes effect |
|---|---|
| Domain security policy edit / BP security policy edit | **Pending** until someone runs **Activate Pending Security Policy Changes** |
| Security group membership or definition change (add a user, edit a rule, add the ISU to an ISSG) | **Immediately** - no activation step |

- Every activation creates a **security timestamp**; Workday evaluates policies as of the active timestamp.
- Revert with **Activate Previous Security Timestamp** (pick from **View All Security Timestamps**).
  Later changes become inactive, not deleted - this is a rewind, not a single-change undo.
- Timestamps do NOT affect group definitions/assignments (they were never staged in the first place).
- Preview before activating: policy Related Actions > View Pending Changes; Domain/Business Process
  Security Policy History; Audit Trail - Security.
- Procedure: recipe **R2** in tenant-task-recipes.md. Put who/what/why/approver/change-ref in the
  activation comment.

## THE UNION RULE (why "least privilege" breaks silently)

- A user's access = the **UNION across all their security groups**.
- **One unconstrained membership bypasses every constrained/segment restriction** on the same domain -
  the constrained group still "works", it just no longer limits anything.
- Segmentation corollary: when you add a segment-based group to a policy, you must **remove the
  included base groups from that policy**, or members reach the domain through the base group and the
  segmentation is bypassed.
- Same warning applies to Integration System Security Segments: any unconstrained route to the domain
  defeats the segment.

## Security group types - when to use each

Membership arrives three ways: Workday-assigned (non-configurable), manually assigned, derived.
Context types: **Unconstrained** (all instances), **Constrained** (a subset), **Mixed** (combinations).
Groups can never be deleted once used - **inactivate** instead.

| Type | Membership | Constraint | Use when |
|---|---|---|---|
| Workday-assigned (All Users, All Employees, Employee As Self, Implementers, Initiator, Manager's Manager, Role Maintainer...) | automatic | varies | public/self-service baselines |
| User-Based | manual; survives job changes until removed | always UNCONSTRAINED | small admin populations (HR/Payroll/Finance/Security Administrator, Report Writer, Auditor) |
| Role-Based | derived from assignable-role assignments on a position ("the chair", not the person) | constrained or unconstrained | the default for scalable end-user access |
| Job-Based | derived from job profile, exempt status, management level... | constrained or unconstrained | access follows job characteristics |
| Organization / Location Membership | derived from org or location | location-membership groups are unconstrained | org-population targeting |
| Segment-Based | maps groups to SEGMENTS of values (~38 segmentable item types: pay components, document categories, integration systems, BP types...) | value-level | slice access to specific VALUES of an item |
| Aggregation | union of included groups minus excluded; members KEEP their own constraints | mixed | one policy grant for several groups; cannot include rule-based, integration system, or other aggregation groups; cannot partially remove access - add extras on the subordinate groups |
| Intersection | users in ALL included groups (AND), minus exclusions | tighter targeting | supervisory-org x location; sensitive-worker hiding. Exclude a group OR orgs, not both; org exclusions are View-only intent (not BP routing); cannot include intersection, rule-based, or integration system groups |
| Rule-Based | baseline group + include/exclude membership rule (max **5 conditions**; rule objects Worker, Student, Extended Enterprise Learner) | per baseline | dynamic membership; baseline cannot be aggregation, intersection, rule-based, or segment-based; enable fields first via **Maintain Fields for Security Rules**, test via **Test Security Rule** |
| Integration System | ISUs only | constrained or unconstrained | integration runtime identity (below) |
| Service Center-Based / Compensation or Manager Level-Based | derived | manager-level constrains target access to LOWER levels regardless of org | niche targeting |

Choosing: ask (1) how do users become members (assigned vs derived, from what), and (2) does the type
enforce the TARGET constraint you need? Unconstrained simple groups are common building blocks inside
aggregation/intersection groups. Design guidance (which type for which client role) lives in
security-role-design.md.

### Role-based specifics worth knowing cold

- **Maintain Assignable Roles** defines roles (secured by **Set Up: Assignable Roles** domain); one
  assignable role can back MULTIPLE role-based groups with different access rights.
- Access-rights options on the group: Current Organization Only / Current Organization and Unassigned
  Subordinates / Current Organization and All Subordinates / Current Org and Subordinates to Level.
- Subordinate orgs inherit role assignments from parents when unassigned. Audits: **Unassigned Roles
  Audit**, **Unfilled Assigned Roles Audit**, **Unassigned Tasks** (BP steps stuck on empty groups).
- Assign at the org (Related Actions > Roles > Assign Roles - Role Maintainer only, no approval BP
  possible) or at the worker (**Assign Roles - Add/Remove** / **Assign Roles - Change Assignments**).

### User-based specifics

- Who can assign: Modify on **User-Based Security Group Administration** domain OR being listed in the
  group's "Administered by Security Groups" field.
- Termination hygiene: add Service steps "Remove User-Based Security Groups" then "Terminate User
  Account" to the Termination BP - user-based membership does NOT expire on its own.
- **Maintain Permissions for Security Group** copies policy permissions group-to-group (BP permissions
  copy automatically only between same-type groups; domain permissions need manual selection; MUST
  activate afterward).

## Report security (the three-part access test)

To run a report a user needs ALL of: data source domain access AND data source filter access AND each
report field's domain access. A missing FIELD grant does not error - the field comes back **silently
blank** or as a constrained subset. Authoring-side rules (sharing, ownership transfer, calc-field
domains) live in wd-extend-dev `report-writer-admin.md`; this file owns the access-rule itself.

Troubleshooting order (concept - the tools):
1. **View Security for Securable Item** - which domains secure the thing, which groups hold them.
2. **View Security Groups for User** - what the user actually has.
3. **Security Analysis for Securable Item and Account** - the intersection, per user per item.
4. Fix by group membership (immediate) or policy edit (+ **Activate**), then test with **Start Proxy**
   (non-production only).

## Integration security - ISU / ISSG exact mechanics

The standard pattern is one ISU + one ISSG per integration system; the click-level builds are recipes
**R3** (ISU), **R4** (ISSG + domain grants), **R2** (activate), **R5** (integration system + credential)
in tenant-task-recipes.md. The rules layer:

- **Create Integration System User**: not a person; no UI access; ONLY ISUs can be ISSG members; the
  ISU is assigned to the integration system via Related Actions > Workday Account > Edit.
- ISSGs are constrained or unconstrained (constrained = contextual by organization).
- Integration permissions on a domain: **Get** (~View, extract) / **Put** (~Modify, load) - **Put
  implies Get**. Manual's rule of thumb: "most outbound integrations only need Get."
- Grant BP policy access too when the integration initiates or participates in a BP (web services
  calling Hire, Assign Roles; or the integration is triggered by a BP step).
- **Find the right domain, never guess:** **View Security for Securable Item**, enter the web-service
  operation name (3+ chars, e.g. GetPositions) -> it returns the securing domain(s). Field overrides:
  Related Actions > Integration Field Override > **Test Security** shows whether the ISU can read them.
- **Avoid over-privilege:** do not blanket-grant **Integration Build** or **Integration Debug** to an
  ISSG - per the manual, Delivery Assurance raises issues with integrations that hold more access than
  necessary. Grant the narrow functional-area domains the calls actually need.

### The integration functional-area domains (what each governs)

| Domain | Governs |
|---|---|
| Integration Build | create/edit integration systems (Modify) |
| Integration Configure | EIB services |
| Integration Event | launch/schedule + view events/output - business users LAUNCHING an integration need MODIFY here |
| Integration Reports | view integration reports |
| Integration Security | maintain segments / ISUs |
| Integrations: EIBs | users CONFIGURING EIBs need Modify |

### User access to integrations (humans, not ISUs)

- An inbound EIB run by a HUMAN uses the business user's own security, not an ISU: the user needs Put
  on the relevant domain and possibly "Initiating Action (Web Service)" on the BP policy.
- **Schedule ownership:** schedules belong to a USER; when that person leaves, scheduled runs break.
  Transfer via **Scheduled Future Processes** report -> Related Actions > Scheduled Future Process >
  **Transfer Ownership** -> assign to the ISU (which needs Modify on Integration Event).
- Segmenting which humans see which integration systems: **Create Integration System Security
  Segment** + segment-based groups; the 5-step build and the segment triad naming live in
  security-setup-section.md Part 2 / wd-integration-dev.

### DIS report-field exception

DIS-based connectors read REPORT FIELDS, not web services. For DIS field overrides grant
**Report/Task View** permissions (not Integration Get) - Get/Put still works at runtime, but the
**Test Security for Document Field Overrides** UI check only reads Report/Task grants, so a
Get-only ISU looks broken in the test while working live. Grant View so tests tell the truth.

## Quick self-test before calling security "done"

1. Did every policy edit get followed by **Activate Pending Security Policy Changes** (R2)?
2. Is any member of the target audience ALSO in an unconstrained group on the same domain (union rule)?
3. If segmentation is in play - were the base groups removed from the policy?
4. Ran **Start Proxy** as a real member and tested positive AND negative (security-role-design.md)?
