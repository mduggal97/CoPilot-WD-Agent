# DSAR / Erasure Runbook - Servicing a Data-Subject Request Against a Live Extend App

When a data subject (worker, applicant, student, vendor contact) exercises an
access, portability, or erasure right (GDPR DSAR / right-to-erasure, CCPA/CPRA
delete request, FERPA record request, etc.), and the app holds their personal data
in custom Extend BOs, someone has to service that request against production. This
runbook is the operational procedure for the implementer/admin. It sits on top of
the retention/purge mechanics in [data-retention-export.md](data-retention-export.md)
- read that first for the export options and the hard purge constraints; this file
is the request-servicing workflow around them.

**Legal-determination boundary - hold it throughout.** WHAT must be disclosed or
erased, WHICH records are in scope, and WHETHER a legal-hold or regulatory minimum
blocks erasure are the **client's / their counsel's / records-management's**
determinations - never the implementer's. The implementer LOCATES the data, presents
the options and their consequences, EXECUTES the client's written instruction, and
LOGS it. Do not decide scope, and do not action an erasure without a written
client decision naming the subject, the records, and the disposition.

## Step 1 - Intake and scope (client-owned decision, implementer-supported)

1. **Log the request** in the support/ticketing channel with: request type
   (access vs erasure vs portability), subject identity + identifiers, the client
   decision-maker who owns it, and the legal basis/deadline (GDPR = 1 month;
   confirm the client's clock).
2. **Get the scope in writing from the client.** Which record types, which app(s),
   which date range. Access and erasure have different scopes - an access request
   returns data; an erasure request destroys it. Do not proceed on a verbal ask.
3. **Confirm subject identity** is verified by the client before any data moves -
   servicing a DSAR for an unverified requester is itself a data breach.

## Step 2 - Locate the subject's instances across the app's BOs

Never assume where the subject appears - FIND every instance programmatically. Build
a BO-by-BO inventory from the app's design doc (which BOs hold personal data was
inventoried at design time - see data-retention-export.md, retention-question #2),
then read each one under a known identity.

- **Primary path - WQL** over each app data source:
  `SELECT ... FROM <dataSource> WHERE <subjectKey> = <worker/email/externalId>`.
  A returned row proves an instance; zero rows = truly absent; an S22 = you cannot
  see it (a scope gap, not absence). Page at 10k rows.
- **Reference fields matter.** The subject may appear as a *referenced* value on
  another BO (approver, requester, contact, "entered by"), not only as the row
  subject. Search reference fields too, or those copies survive an erasure.
- **Attachments** hold personal data the row-level reads do NOT return (binaries
  come out only via the attachment-out pattern). Inventory attachment-bearing BOs
  separately - see data-retention-export.md, retention-question #4.
- **Prism / data-lake copies.** If the app exports to Prism or a rolling data lake
  (the delivered pattern in data-retention-export.md), the subject's data also lives
  there and in any downstream system - carry those into Step 5.

**Verify every read** against the cookbook: to confirm an instance exists (or is
truly gone), read the authoritative source, do not eyeball a browser grid - see
`wd-extend-dev/references/tenant-state-verification.md` (the HOW) and its front-door
gate `wd-extend-lifecycle/references/verify-in-tenant.md`. Transport/auth for the
reads is `wd-extend-dev/references/tenant-ops.md`. Produce a located-instances
inventory (BO, instance key, field vs. reference vs. attachment) and confirm it back
to the client before actioning anything.

## Step 3 - Choose the disposition (soft-delete vs field-scrub vs full-delete)

For an **access/portability** request, stop at export: run the appropriate export
option from data-retention-export.md (BO REST / RaaS / WQL) scoped to the subject,
deliver via secure transport, log, done. No mutation.

For an **erasure** request, pick per instance - the choice is constrained by whether
the BO is deletable at all (see the purge constraints below):

| Disposition | What it does | Use when |
|---|---|---|
| **Field-scrub / anonymize** | Overwrite the PII fields (name, email, ID, free-text) with a tombstone value; keep the row + keys | The row must survive for referential/BP/audit reasons but the person must no longer be identifiable. The default for BP-tied BOs. |
| **Soft-delete** | Set the app's `isDeleted`/status flag | The app already uses soft-delete AND the client accepts the row persists - NOTE: soft-deleted data still exists in the tenant, still in scope for future requests. Rarely sufficient for a true erasure alone; usually pair with field-scrub. |
| **Full (physical) delete** | REST DELETE the instance | The BO is deletable (not BP-tied, no blocking references) and the client wants the row gone. Delete children before parents; expect 500s on referential constraints. |

**Purge constraints carry straight over from data-retention-export.md:**
- **BP-tied BOs cannot be physically deleted** (the BP event trail references them).
  For those, **field-scrub/anonymize is the erasure mechanism** - you cannot delete
  the row, so you destroy identifiability within it. Say this plainly to the client:
  a BP-bound record is anonymized, not removed.
- **There is no bulk DELETE**; referential integrity throws 500s (skip-and-log,
  clear dependents first).
- **Soft-deleted rows persist** - "we soft-deleted it" does NOT satisfy an erasure
  obligation on its own.

## Step 4 - Honor legal-hold and retention overrides FIRST

Before executing any erasure, check the overrides - **a hold beats an erasure
request**:

- **Legal hold / litigation hold** on the record type blocks erasure outright.
  If any in-scope record is on hold, do NOT erase it; return that to the client
  decision-maker and record the hold as the reason the request was partially
  refused. This is the client's call to assert - you enforce it, you don't judge it.
- **Regulatory retention minimum** (grants/federal awards, financial approvals, HR
  actions, FERPA education records) can legally REQUIRE keeping the record for a set
  period - which can lawfully override an erasure request. The client/counsel decides
  whether a minimum applies; you flag the record type and wait for the ruling.
- The retention values and who-set-them live in the design doc (data-retention-export.md,
  retention-question #1). Cross-check the located inventory against them before
  actioning.

Document, per in-scope record, whether it was erased or retained-under-override and
why. A DSAR response almost always includes "these records were retained because...".

## Step 5 - Handle downstream propagation

Data the app already SENT does not get erased by touching the source BO. Trace every
outbound path the subject's data took and coordinate erasure/anonymization there too:

- **Outbound integrations** - any O4I/EIB/Studio/Core Connector that pushed the
  subject's data to an external system (ECM/OnBase, data lake, vendor API, SFTP
  drop). List them from the app's IDD/integration inventory. Each downstream system
  needs its own erasure - either an automated delete call if the target supports it,
  or a documented manual request to that system's owner. The source erasure is not
  complete until downstream is addressed.
- **Prism tables / data lake** - if the app feeds Prism or a rolling lake, the copy
  there must be erased too. Prism has real deletion mechanics (row-level delete by
  load ID / DCT delete keyed on external ID - see data-retention-export.md, Prism
  purge paths); the lake is the client data team's action.
- **Attachments** archived externally (OnBase/ECM/SFTP) - erase the archived binary,
  not just the in-tenant copy.
- **Exports already delivered** (audit spreadsheets, prior DSAR responses) - flag to
  the client; those live outside Workday and are the client's to manage.

Record which downstream systems were in scope and the disposition of each. If a
downstream system cannot honor erasure (immutable archive, backup), that limitation
is a client risk decision - surface it, don't bury it.

## Step 6 - Log the action for audit

Every DSAR is itself an auditable event. Capture a durable record (support ticket +
the app's design/closeout artifacts):

- Request id, type, subject identifiers, client decision-maker, received + completed
  dates (and the legal deadline).
- The located-instances inventory (Step 2) and the disposition per instance
  (erased / anonymized / soft-deleted / retained-under-override + reason).
- Downstream systems actioned and their dispositions (Step 5).
- Who executed each action and when; the identity/ISU used for the reads and writes.
- For access/portability: what was exported, the transport, and the recipient.

Note the WRITE GATE: all mutations go through the confirmed-write path in
`wd-extend-dev/references/tenant-ops.md` (plan-first, confirm each write, verify the
result). Tenant-side native audit trails (WQL/RaaS Usage Metrics, Report Run
History) have limited windows (90 days / 6 months - see data-retention-export.md,
monitoring hooks); if the DSAR audit trail must outlive those, snapshot it into the
durable ticket/closeout record above, not only the tenant logs.

## Where this shows up in deliverables

- **Post-production guide, Part 2 (technical)** - reference this runbook as the
  DSAR/erasure servicing procedure; name the app's PII-bearing BOs and their
  deletable-vs-BP-tied status so the disposition choice is pre-answered.
- **Support-ownership matrix** - who receives a DSAR, who verifies identity (client),
  who locates + executes (implementer/admin), who owns downstream systems.
- **Design doc** - the PII/BO inventory, the client-set retention values +
  decision-makers, and which BOs are BP-tied (erasure = anonymize) feed Steps 2-4.
