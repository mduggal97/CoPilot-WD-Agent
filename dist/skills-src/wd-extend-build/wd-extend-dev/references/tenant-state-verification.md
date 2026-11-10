# Tenant-state verification cookbook - to confirm X, read Y

**Principle:** never assume a tenant fact you can programmatically read. Before you build on,
test against, or claim a piece of tenant state (an instance exists, a grant is live, an
integration ran, the native data the app needs is even present), CONFIRM it with an
authoritative programmatic read - not a browser eyeball, not memory, not the design doc.

**The rule and the gate that enforces it are owned by the FRONT DOOR:**
`wd-extend-lifecycle/references/verify-in-tenant.md`. That file owns *when* verification is
mandatory and the quality-gate wording. **This file owns the HOW** - the concrete "to confirm
X, read Y" recipes, each citing the suite reference that documents the read.

The transport for every read below (auth profile, WQL/REST invocation, the WRITE GATE) is
`references/tenant-ops.md`; auth itself is owned by the wd-auth skill.

---

## Why programmatic, not a browser eyeball

A browser view showing **"No Items" / "None" / an empty grid is not proof of absence.** It is
just as often an async artifact (the data has not materialized yet), a security-gated view
(your user lacks the domain, so the row is hidden - not missing), or a filter/soft-delete
default hiding rows that exist. A programmatic read against the authoritative source removes
all three ambiguities: WQL/REST run under a known identity, return the actual row, and
distinguish "zero rows" from "you cannot see these rows" (an S22 / permission error is a
different result than an empty set). So: **prefer the programmatic read; treat a browser empty
state as a prompt to verify programmatically, never as the answer.**

---

## The cookbook

Each row: what you want to confirm -> the authoritative read -> where the suite documents it.
Provenance tags: **[BV]** build-verified, **[DS]** doc-sourced (verify at use).

### An instance or field value exists
- **Read:** WQL `SELECT ... FROM <dataSource> WHERE <key> = ...`. A returned row proves the
  instance; a returned column proves the field is populated (null vs. absent is visible in the
  result shape). Zero rows = truly absent (distinct from an S22, which = you cannot see it).
- **Cite:** [references/wql.md](wql.md) (grammar, data-source discovery, result shapes). **[BV]**

### A worker / org / cost-center (native master data) exists
- **Read:** WQL against the delivered data source (e.g. workers, organizations, costCenters),
  or a RaaS call to a custom report exposing the same. WQL is the lighter check; RaaS when you
  need report-shaped output or a calc field the raw source lacks.
- **Cite:** [references/wql.md](wql.md); RaaS gating + report types in
  [references/report-writer-admin.md](report-writer-admin.md). **[BV]** (WQL) / **[DS]** (RaaS shape)
- **Companion check:** if the answer is "the tenant has none," that is the native-data gap -
  see "will the tenant even HAVE the data" below.

### A security domain / role grant is actually live
- **Read:** the security-audit WQL sources. `roleBasedSecurityAuditLogLite` returns role
  assignment delta events (grants + revokes) - query with a timestamp window to see only
  changes since a baseline; yields workerId, roleId, orgId, effectiveDate, action.
- **Cite:** [references/wql.md](wql.md) (the `roleBasedSecurityAuditLogLite` data-source row).
  **[BV]** (documented from a delivered role-reconciliation build).
- **Corroborating live check:** the grant's real effect is "does the BO data call still S22?"
  - run the tenant-readiness read-set and capture the before/after as grant evidence
  ([references/security-setup.md](security-setup.md) "Verification per tenant" +
  [references/tenant-ops.md](tenant-ops.md)). A domain shown as granted in the UI but not yet
  activated still S22s - the programmatic BO call is the truth. **[BV]**

### A business-process EVENT's status (approval chain / step routing)
- **Read:** `businessProcess v1` `/events` + `/eventSteps` inspect a BP event's in-flight
  status programmatically - not Process Monitor by eye. This is for a BUSINESS-PROCESS event
  (approval chain, step routing, awaiting-action). It is NOT the read for an integration
  background run - that is a Process Monitor process, see the next row; do NOT reach for
  `businessProcess v1` there.
- **Cite:** [references/rest-api-catalog.md](rest-api-catalog.md) (`businessProcess v1`
  endpoints); `wd-test-execution/references/scenario-flows.md` SF-10 (launch + validate the
  event). **[BV]**
- **Note:** a status-code / HTTP 200 alone is not success for Graph or SOAP/REST - errors can
  ride a 200 body (`errors[]`), so read the body, not the status (rest-api-catalog.md,
  orchestration.md). **[BV]**

### An integration RUN's status + its attachments (a Process Monitor background process)
- **Read:** an integration run is a background process in Process Monitor, NOT a BP event - so
  `businessProcess v1` does not apply. Read its status via the **Integrations WWS**
  `Get_Integration_Events` / `Get_Integration_Event` SOAP operations, or drive browser step
  SF-10 to launch and confirm the run. For the run's output file(s) and log(s), pull the
  attachment and validate it with the output-file validator rather than opening it in the
  browser. Read the run's own status + messages (completed-with-errors is distinct from a hard
  failure) - not just an HTTP code.
- **Cite:** Integrations WWS `Get_Integration_Events`/`Get_Integration_Event` live in the
  wd-integration-dev skill; `wd-test-execution/references/scenario-flows.md` SF-10 (launch +
  validate the run) and SF-11 (verify attachments) with its `scripts/validate_output_file.py`.
  **[DS]** (WWS read, verify at use) / **[BV]** (SF-11 attachment validation)

### A BO instance exists / is populated (this app's own data)
- **Read:** BO REST `GET https://api.us.wcp.workday.com/apps/<refId>/v1/<collection>` for the
  app's own instances, or WQL against the app's BO data source for a filtered/aggregate check.
  BO REST is the direct "does this instance exist" read; WQL is better for "how many / which
  match."
- **Cite:** [references/model.md](model.md) (BO REST API, security domains); WQL in
  [references/wql.md](wql.md). **[BV]**
- **Landmine:** a soft-delete boolean left unset hides rows from filtered lists - an "empty"
  BO collection may be populated-but-filtered (pmd-gotchas #45 / model.md). Query without the
  filter to disambiguate. **[BV]**

### "Will the tenant even HAVE the native data this app reads?"
- **The check that precedes all the others.** A bare/new dev tenant will not have workers,
  orgs, financial master data, or historical events for the app to read - so a "nothing shows
  up" symptom is often *no seed*, not a bug. Decide the load channel + scale and confirm the
  native data is seeded before testing reads.
- **Cite:** [references/data-loading-and-retrieval.md](data-loading-and-retrieval.md)
  ("which load channel at which scale, and will the tenant even HAVE the native data"). **[BV]**

---

## Discipline

- Run the read under a KNOWN identity and tenant (the tenant-ops WRITE GATE's identity check
  applies to reads too - prove which tenant the token actually hits before trusting the
  result).
- Record the read + its result as the evidence for the fact you are asserting (grant evidence,
  test evidence, design-fact confirmation) - a verified fact with no captured read is not
  verified for the next person.
- Provenance-tag what you learn: a read you ran and saw is build-verified; a read you expect to
  work from docs is doc-sourced until you run it.
