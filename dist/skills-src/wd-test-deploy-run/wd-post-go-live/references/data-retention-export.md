# Data Retention & Export for Live Extend Apps

Extend business-object data and Prism tables live **inside the Workday tenant**. Once an app is in production, the client owns data that Workday hosts but that no standard Workday retention policy covers. Two clocks start at go-live: the audit clock (auditors will ask for extracts) and the growth clock (BOs accumulate rows forever unless someone designs otherwise). Settle retention/archival/export **before audit season**, ideally as a go-live exit item.

**Servicing an actual data-subject access / erasure request** (GDPR DSAR, CCPA/CPRA delete, FERPA record request) against the live app is a distinct operational procedure that sits on top of the export/purge mechanics here - see [dsar-runbook.md](dsar-runbook.md).

**Advice boundary - hold it throughout this reference:** retention periods, legal holds, and regulatory minimums are the **client's** legal / records-management determinations, not the firm's. The firm presents the options and tradeoffs (this reference) and implements the mechanics; the client's counsel or records-management function sets the values. The design doc records **WHO on the client side set each retention value** (name + role + date), so the answer reads as the client's decision, not our recommendation. (!) Standard disclaimer language for client-facing retention deliverables needs QRM confirmation - until then, attribute every retention value to its client decision-maker and avoid language that reads as legal advice.

## The five export options

### (a) Extend BO REST API export

The generated REST endpoints on every custom BO. Paged at <=100 rows per page (the BO REST collection limit, owned by wd-extend-dev pmd-gotchas.md).

- **Good for:** small objects (config BOs, low-volume request BOs), scripted incremental pulls, ad-hoc extracts during hypercare.
- **Tradeoffs:** at 100 rows/page, a 500k-row BO is 5,000 sequential calls - impractical for bulk. Returns the full JSON shape including references, so downstream parsing is on you. Requires an API client / ISU with the app's data scope.
- **Pattern:** script it (Python + requests, or an orchestration writing to an attachment) and page on the `total`/`offset` envelope.

### (b) RaaS custom report over app BOs

Build an advanced custom report on the app's BO data sources, expose as RaaS.

- **Good for:** **large structured extracts - 500k+ rows** are routine. Output as XML, JSON, CSV, or Excel. The workhorse for recurring bulk export.
- **Tradeoffs:** requires report-writer effort per BO (a client reporting resource can own it); report definitions must be maintained when the BO changes; prompts needed for incremental windows (e.g., last-modified date range). Large runs should be scheduled, not interactive.
- **Hard bounds (per Workday Admin Guide (Reporting & Analytics), Jul 2026):** RaaS request timeout is **6 h via the tenanted host** but only **5 min via the WCP API Gateway** (api.workday.com) - bulk pulls must use the tenanted host URL. RaaS extracts cap at **~1M rows per request**; beyond that the sanctioned path is **scheduled report output**, whose formats degrade by size: <10k rows any format; 10k-500k Excel/CSV; 500k-1M CSV only; **>1M rows CSV only, up to 15 GB**. Browser-run output caps at 50 MB; interactive report processing at 30 min; background/scheduled at 6 h.
- **Official-example confirmation (per Workday/raas-python, official client, Apache-2.0):** RaaS runs on the tenanted `customreport2` host (`/ccx/service/customreport2/{tenant}`, reached via the tenant's `tenantGwUrl`, NOT the WCP API Gateway) and returns the **whole report in one un-paged, in-memory response** - no streaming, no offset paging. This reinforces the "schedule large runs, not interactive" guidance and the "bulk pulls must use the tenanted host URL" rule above: a big run materializes entirely in memory on both ends. The hard bounds above (6 h / 5 min timeouts, ~1M-row cap, format degradation) are **not** contradicted - they are **server-side** limits; the client library enforces no timeout or row cap of its own, so the server bounds remain authoritative.
- **Pattern:** one report per BO with a `Last Updated >= prompt` filter -> scheduled RaaS pull into the client's landing zone.

### (c) WQL

Workday Query Language over the app BOs (and Prism datasets published to WQL).

- **Good for:** targeted, filtered extracts in JSON; joins/selects you'd otherwise build a report for; automation from orchestrations or external scripts.
- **Limits:** in-query `LIMIT` max **1M rows**; REST paging at **10k rows/page** - much better bulk throughput than BO REST, still not a data-lake pipe. Doc-confirmed refinements (per Workday Admin Guide (Reporting & Analytics), Jul 2026): query timeout **30 min via the tenanted host / 5 min via the WCP API Gateway**; a query whose result exceeds 1M rows **without a LIMIT fails outright** - with `LIMIT` <=1M it succeeds truncated, so always set one on unbounded extracts.
- **Pattern:** parameterized WQL with a date filter, paged at 10k, run from a scheduled job.

### (d) Live Data Query (LDQ) / Data Cloud SQL

Zero-copy **SQL** reads (joins, GROUP BY, window functions) over Workday objects via Python (`workday_dataservice`) or JDBC drivers. Auth = **JWT Bearer + x509 key-pair** (register an API Client for the ISU, grant type "Jwt Bearer Grant", upload the x509 cert).

- **Good for:** **bulk and aggregate reads** - the best-performing option for large analytical extracts; plugs straight into Tableau/DBeaver/Snowflake via JDBC.
- **Tradeoffs:** read-only; current effective time only (no point-in-time - use REST/WQL for effective-dated history); guardrails ~30-min query timeout, ~90 concurrent queries/tenant. **Check GA status before proposing to a client** - this was a DevCon 2026 preview; verify it is released and the tenant is enabled.

### (e) Rolling data-lake export (one delivered program's answer)

The program-level pattern: **all custom Extend BOs AND Prism tables exported to the client data lake on a rolling 18-24 month schedule**, with the lake becoming the long-term system of record for aged records. Workday holds the active window; everything older lives (only) in the lake.

- **Good for:** programs with many apps - one answer covers every app's retention cells on the Volumes Questionnaire (C21/C22/C24), one pipeline pattern, one audit story.
- **Tradeoffs:** needs a client data-lake team and a transport (RaaS or LDQ feeding the lake); the export interval must be settled (18 vs 24 months was still being settled); once records are purged from Workday, in-tenant reporting loses them - dashboards must not assume full history.
- Prism side: **Prism Tables Materialize API** (`POST /api/prismAnalytics/v3/tables/materialize`, keyed by apiName, tenant-portable) or dataset exports feed the lake for Prism-resident data.

## Decision guide

| Situation | Use |
|---|---|
| Small config/reference BO, occasional pull | BO REST (scripted) |
| Recurring bulk extract, 100k-500k+ rows, needs CSV/Excel | RaaS |
| Targeted filtered slice, automation-friendly JSON | WQL |
| Very large / analytical / SQL-shaped reads, BI-tool destination | LDQ (verify GA) |
| Program-wide long-term retention, data-lake destination | Rolling lake export (RaaS or LDQ transport) |
| Effective-dated / point-in-time history | REST or WQL (LDQ can't) |

Pick by three axes: **data size** (100 rows/page vs 10k/page vs 500k+/report vs SQL bulk), **cadence** (one-off vs scheduled vs rolling), **destination** (auditor spreadsheet vs ticketing system vs data lake vs BI tool).

## Monitoring & audit hooks (per Workday Admin Guide (Reporting & Analytics), Jul 2026)

Who-ran-what evidence for the export pipeline - natural rows for the support-ownership matrix:

- **WQL/RaaS Usage Metrics** report - a rolling **90 days** of WQL + RaaS executions (needs the Manage: All Custom Reports domain; **production tenant only**). Assign an owner to snapshot it if the audit trail must outlive 90 days.
- **Report Run History** - holds a maximum of **6 months** and must be **enabled** (Edit Tenant Setup - Reporting and Analytics); it is not on by default. Longer audit trails need a monthly extract integration of the history itself.

## Retention policy questions to settle with the client

Walk these in a working session - get written answers into the design doc / closeout note:

1. **Legal hold** - do any record types carry litigation-hold or regulatory retention minimums (grants/federal awards, HR actions, financial approvals)? Holds override any purge schedule.
2. **PII / PHI / FERPA in Extend BOs** - inventory which BOs hold personal data, health data (PHI), or education records (FERPA - ask explicitly at education clients; student-touching apps are routinely FERPA-covered). Any of these changes the retention answer (minimize), the export answer (secure transport/landing), and the purge answer (right-to-erasure requests); PHI additionally implicates the BAA (wd-contracts references/saas-agreement.md section 3.2).
3. **Soft-deleted rows** - if the app uses the soft-delete pattern (an `isDeleted`/status flag instead of physical delete), **"deleted" data persists in the tenant**. It's in scope for audits, exports, and legal hold whether or not the UI shows it. Flag this explicitly - clients assume deleted means gone.
4. **Attachments - treat as their own archive stream.** Apps that store attachments (uploaded docs, supporting files on a request/task BO) have a retention problem distinct from the row data: the **binaries don't come out through the row-level RaaS/WQL/LDQ paths** - those return the row and a reference, not the file. Settle separately:
   - **Where do the files go?** Common asks: archive to the **client data lake**, or to an **external ECM/content vendor (e.g., OnBase)**, or retain in-tenant. If the destination is OnBase or similar, that's effectively another **outbound integration** (an O4I/SFTP/API push of the binaries + metadata) - scope and estimate it as one, not as a checkbox.
   - **How to get binaries out - the proven pattern:** an O4I that GETs the attachment (base64) and delivers it via `StoreDocument` (Delivery Service -> SFTP/data lake) or `SendHttpRequest` (-> an ECM like OnBase), looped for many files. This is the **attachment-out pattern** documented in wd-extend-dev's orchestration reference, build-verified against the Worker Photo Outbound O4I - mirror that flow. Preserve the row<->file linkage (keys/metadata in filename/tags) so the archive is reconstructable.
   - **Purge of attachments** follows the same BP-tied rule above: if the attachment hangs off a BP-bound BO, it can't be purged either - archive-then-retain. If it's on a deletable BO, attachments often get a **shorter** purge horizon than the row (files are the storage hog).
   - Flag attachment-archival as an explicit design decision and, if external (OnBase/vendor), its own IDD/integration line item.
5. **Active window** - how much history must stay queryable **inside** Workday for the app's own screens and reports? That sets the purge horizon; everything older can live only in the archive.
6. **Who owns the pipeline** - client data team, a firm-provided managed service, or nobody (retention-by-design only)?

## Purge design

**Export and purge are separate capabilities - you can almost always EXPORT, but you cannot always PURGE.** Design the two independently; never assume "we exported it, so we can delete it."

**(X) BOs tied to a Business Process cannot be deleted.** If a BO is the target of a custom (Model) BP - or otherwise has BP events/audit history against it - Workday **blocks deletion** of those instances (the BP event trail references them). So for any app with BP-driven objects (approvals, request/approve/write-back flows), the records you'd most want to age out are exactly the ones you **can't purge**. Consequences:
- **Export still works** on those BOs (REST/RaaS/WQL/LDQ all read them fine) - so the archive/audit story is intact.
- **Purge is off the table for BP-tied BOs** - plan **retention-by-design** for them (data stays in-tenant; show growth projections stay manageable), or archive-then-leave. Do NOT promise a client a purge schedule for BP-bound records.
- Decide this at DESIGN time (wd-design-doc): which BOs are BP targets -> those are export-only. An app that's *all* BP-driven has no meaningful purge - say so in the retention answer rather than designing a purge orchestration that can't run.

**Extend has no bulk DELETE** even for non-BP BOs. Physical deletion is one REST DELETE per instance, and referential integrity bites: deleting a parent still referenced by children (or referenced from another BO) returns **500s**. For the BOs that *can* be deleted, your two realistic designs:

1. **Purge orchestration** - a scheduled orchestration that queries rows past the retention horizon (WQL with a date filter), deletes **children first, then parents**, in batches, with logging. Confirm the target rows are already in the archive before deleting. Expect and handle 500s (skip-and-log, retry after dependents clear). Budget real dev time - this is a feature, not a config toggle.
2. **Retention-by-design** - documented decision that data is never purged in-tenant (or only soft-deleted), with growth projections showing volumes stay manageable for the tenant's life. Acceptable for low-volume apps; write it down so it reads as a decision, not an omission.

Either way, the answer goes into the app's Volumes Questionnaire retention cells and the post-production guide's technical part.

### Prism purge paths - a contrast to BP-tied Extend BOs

Unlike BP-bound Extend BOs, **Prism data has real deletion mechanics** (per Workday Admin Guide (Reporting & Analytics), Jul 2026) - use them in retention answers covering Prism-resident data:

- **Truncate** a table/dataset - schema kept, rows gone; note the published dataset (PDS) keeps serving **stale data until republish**.
- **Row-level delete** - by **load ID**, or a DCT delete-operation keyed on external ID / `WPA_LoadID` / `WPA_RowID`.
- **Delete Published Rows** - the PDS goes empty **and inactive**; dependent reports break until it's reactivated.
- **Unpublish dataset** - removes the PDS entirely; only allowed when no reports use it.
- **Delete table** - only when no reports/vizzes use its PDS and no DCT is configured against it.

Decommissioning checklist item: run **View Calculated Field Usage in Prism** before deleting a custom report or report calc field - Prism pipelines referencing it break silently otherwise.

## Where this shows up in deliverables

- **Extend Volumes Questionnaire** - retention/archive cells (Extend tab C21/C22/C24) must state the policy; "TBD" cells get yellow-highlighted until resolved.
- **Post-production guide, Part 2 (technical)** - export mechanics, purge orchestration runbook (or the retention-by-design statement), archive location and interval.
- **Support-ownership matrix** - who runs the export, who monitors the purge orchestration, who fields audit requests.
