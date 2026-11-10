# The Security Setup Section - the novice spec every guide embeds

When a guide (Deployment Guide, tenant-setup guide, or wd-kt admin/config guide) tells
someone to "set up security," a novice needs three things spelled out, not a vague pointer:

1. **The exact Workday tasks** to run, in order (the searchable strings).
2. **The naming conventions** to apply to every object they create.
3. **The domains and permissions** to grant - enumerated, with the exact access level,
   in a table, in plain English.

This reference is the reusable template for that section. **Every guide with a security
step embeds all three parts below**, filled with the app's real names. Parts 1 and 2 are
short blocks; Part 3 is a table you build from the app's design doc. Do not hand a reader
"configure the security groups" and stop - that is the #1 thing that reads as finished but
leaves the admin stuck.

> **Where the pieces already live:** the click-by-click task steps are the numbered recipes
> in `tenant-task-recipes.md` (R1-R12); the naming patterns are in wd-integration-dev's
> `integration-naming.md` (integration objects) and `standards.md` (Extend app objects); the
> who-owns-what and the request-package framing are in wd-extend-dev's `security-setup.md`.
> This file assembles them into the one section a guide ships. Restate nothing - embed and
> cross-reference.

---

## Part 1 - Tasks to use (name them, in order)

State the exact Workday task before each step (the string typed into the search bar), one
action per step, and define each term (ISU, ISSG, domain, WID) in one plain sentence the
first time it appears. Embed the matching numbered recipe from `tenant-task-recipes.md`
rather than re-writing the clicks. The order depends on the app type:

**Extend UI app**

| # | Do this | Task | Recipe |
|---|---|---|---|
| 1 | Confirm/create the security groups that get access | `Create Security Group` (client usually owns the role-based names) | - |
| 2 | Grant the app's security domains to those groups | `Maintain Permissions for Security Group` **or** `View Security for Securable Item` -> Edit Security Policy Permissions | **R1** |
| 3 | **Activate** the staged grant | `Activate Pending Security Policy Changes` | **R2** |
| 4 | (only if something outside Workday calls the app's REST/WQL) Register the API client | `Register API Client for Integrations` | **R6** |

**O4I / integration**

| # | Do this | Task | Recipe |
|---|---|---|---|
| 1 | (file integrations) Create the SSH/PGP keys | `Create x509 Private Key Pair` / `Create PGP Public Key` / `Create PGP Private Key Pair` | **R9** |
| 2 | Create the service account | `Create Integration System User` | **R3** |
| 3 | Create the security group, add the ISU, grant its domains | `Create Security Group` + `Maintain Permissions for Security Group` | **R4** |
| 4 | **Activate** the staged grants | `Activate Pending Security Policy Changes` | **R2** |
| 5 | Wrap the orchestration so it can run/be secured | `Create Integration System` (-> map the ISU) | **R5** |

(X) **The blocking step is the Activate (R2).** Every grant is *staged* until you run it;
until then a business-object data call returns **S22 "permission denied"** even though pages
load. Say this loudly in the guide so a mis-ordered run self-diagnoses.

---

## Part 2 - Naming conventions to apply

Give the reader the pattern **and** a filled example for every object they'll name, so they
never invent a name. Authoritative sources: `integration-naming.md` (integration objects) and
`standards.md` (Extend app objects); the client's own standard wins if one exists (capture it
in discovery). Fill this block once at the top of the guide's security section:

| Object | Pattern | Example (fill for this app) |
|---|---|---|
| Integration System User (ISU) | `ISU <INT ID> <Description> <Type> <Direction>` | `ISU INT005 TIBCO Studio Outbound` |
| Integration System Security Group (ISSG) | `ISSG <INT ID> <Description> <Type> <Direction>` (Community variant ends `Get`/`Put`) | `ISSG INT005 TIBCO Studio Outbound` |
| Integration System | `<INT ID> <Vendor/Target> <Description> <Type> <Direction>` | `INT050 ICIMS Employee Hire Studio Inbound` |
| Extend app security domain(s) | named by the app's `.securitydomain` files - typically one **Data** domain (BO data) + one **Pages** domain (PMD pages) | `<App> Data`, `<App> Pages` |
| Role-based security group (user access) | client's own role naming (finalized by the client) | `<Client role group>` |
| API client | `<descriptive Client Name>` (registered against the ISU) | `<App> BO REST Client` |
| Encryption key | `EK <INT ID> <Key Type> <Audience>` | `EK INT005 PGP Public` |
| Integration System Security Segment (ISS) + operator groups (human access to integration runs/files - the segment triad in wd-extend-dev `security-setup.md`) | `ISS <Area> Integrations` / `ISUG <Area> INT Operator` / `ISSG <Area> Segment Security Group` (+ `... VIEW Only` twins) | `ISS Payroll Integrations` |

Rules the reader must follow (from the naming standard): **Reference IDs** use letters,
numbers, and underscores only, **no leading zeros** (Workday compares them
case-insensitively); title case, descriptive not vague, no customer identifiers inside object
names; a temporary/retired object gets the **`DNU` prefix FIRST** (`DNU INT001 ...`) - never
delete an ISSG, deactivate-and-rename with DNU. One ISU per integration system.

---

## Part 3 - Domains and permissions to grant (the enumerated table)

This is the part guides most often skip and the part the client security admin most needs.
List **every** domain the app/integration touches, the exact access level, in a table with a
plain-English "what this lets the app do" column so a novice understands *why* each grant is
needed. Most readers get a little lost with Workday security, so be explicit: every security
instruction names the **functional area AND the exact domain** - never "grant the usual
domains" (user feedback, verified in a delivered build session, 2026-08-05). Two accesses exist and both may be needed on the same domain:

- **Report/Task Permissions** - the UI / report / task side. Access is **View** or
  **View & Modify** (Modify = can create/edit data through pages).
- **Integration Permissions** - the programmatic side (orchestrations, BO REST, WQL). Access
  is **Get** (read) and/or **Put** (write).

### How to derive the exact domain list (don't guess)

- **Extend app:** one row per `.securitydomain` file the app declares - usually a **Data**
  domain (its business-object data) and a **Pages** domain (its PMD pages). Read them from the
  app source or the design doc's Security tab.
- **Orchestration / SOAP calls:** the securing domain is whatever secures the web-service
  operation the orchestration calls. Find it exactly with `View Security for Securable Item`
  -> look up the operation (e.g. `Put_Supplier_Invoice (Web Service)`) -> grant the domain(s) it
  lists. **Trust that lookup over any static list** - domain names differ by tenant version.
- **Source of record:** the app's design doc already carries this - the **Extend Design Doc
  Security section** or the **IDD `WD Solution` tab** (ISSG/ISU/domains, View-Modify-Get-Put).
  The guide's table is *populated from the design*, not invented. If the design doesn't have
  it yet, that's a design gap - flag it TBD-with-owner (yellow-highlight spirit), don't leave
  the guide's table blank.

### Table template - Extend UI app

Columns: Domain | What it secures / what it lets the app do (plain English) | Report/Task access | Integration access | Grant to which group | Task.

| Security domain | What it lets the app do | Report/Task | Integration | Grant to | Task |
|---|---|---|---|---|---|
| `<App> Data` | Read & write the app's own business-object records (the request/config data behind every page) | **View & Modify** | **Get & Put** | `<role group>` (+ a test group early) | R1 -> R2 |
| `<App> Pages` | Open the app's PMD pages (the screens themselves) | **View** | - | `<role group>` | R1 -> R2 |
| `<any Workday domain the app's WQL/REST reads>` | e.g. read workers/orgs the app displays | **View** | **Get** | `<role group>` | R1 -> R2 |

### Table template - O4I / integration (ISSG gets Integration Permissions)

Columns: Domain (functional area) | Web service / operation it secures | What the integration does with it | Integration access | Grant to ISSG | Task.

| Security domain (functional area) | Secures | What the integration does | Integration access | Grant to | Task |
|---|---|---|---|---|---|
| `<Functional area, e.g. Process: Supplier Invoice>` | `<Web service op, e.g. Submit_Supplier_Invoice>` | Writes the record the integration creates | **Get & Put** | `ISSG <INT ID> ...` | R4 -> R2 |
| `Integration Event` | integration event framework | Lets the orchestration create/read its own run events | **Get & Put** | `ISSG <INT ID> ...` | R4 -> R2 |
| `Integration Process` | launch/monitor the integration | Lets the ISU launch and monitor the run | **Get** | `ISSG <INT ID> ...` | R4 -> R2 |
| `Integration Debug` | debug messages | Lets the run write debug detail (validation-mode testing) | **Get** | `ISSG <INT ID> ...` | R4 -> R2 |
| `<each additional functional area the orchestration calls>` | `<its web service op - confirm via View Security for Securable Item>` | `<what it reads/writes>` | **Get / Put** | `ISSG <INT ID> ...` | R4 -> R2 |

> The bottom four rows above are the recurring baseline a delivered O4I granted
> (Process: Supplier Invoice, Integration Event, Integration Process, Integration Debug) -
> use them as a starting checklist, then add the functional-area domains **this** orchestration
> actually calls. Always confirm each domain via `View Security for Securable Item` against the
> real web-service operation.

### The one-page request package

The filled Part 2 + Part 3 together **are** the written request you hand the client security
admin (per wd-extend-dev `security-setup.md`'s request-package pattern): app name + reference
ID, every domain with its exact access, the group names, the ISU + Integration System spec.
Batch it into **one** request per tenant - five separate tickets take five lead times, and
each client security-admin request often runs **1-2 weeks** (front-load per tenant).

---

## Checklist before the guide ships

- [ ] Part 1 present: every task named as a searchable string, in dependency order, with the
      matching recipe embedded and the Activate (R2) called out as the blocking step.
- [ ] Part 2 present: naming pattern **and** a filled example for every object the reader
      creates; reference-ID rules and DNU rule stated.
- [ ] Part 3 present: **no blank domain table** - every domain enumerated with plain-English
      purpose, exact Report/Task and Integration access, and the group it's granted to;
      derived from the design doc (or the gap flagged TBD-with-owner).
- [ ] "You're done when..." + the S22 failure symptom stated, so a mis-ordered run self-diagnoses.
