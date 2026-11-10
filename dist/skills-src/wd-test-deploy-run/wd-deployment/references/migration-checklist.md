# Integration Migration Checklist - per-integration tenant-migration tracker

The deliverable for migrating **traditional integrations** (EIB, Studio, Core Connector, DT, BIRT, APIs, O4I) tenant-to-tenant: one tracker row per integration per migration, a fixed set of verification checks filtered by integration type, and a migrator -> reviewer workflow. Distinct from Extend app promotion (`promotion-and-environments.md` owns that) - this is the tenant-side config verification that Extend promotion never touches. To get a blank tracker, **regenerate via `scripts/build_migration_checklist.py`** (spec in `scripts.md`) - it emits the adopted column set, the type-applicability matrix, and the workflow notes; or obtain the firm's branded master per engagement (environment memory). Per house convention it is designed as a Smartsheet with Dynamic Views (transport: wd-smartsheet), but the column set works in Excel too.

## Column layout (the 2024-08-20 proposed revision - the newer design; the workbook also keeps the prior layout)

**Tracking columns:** Is Current? (checkbox marking the active migration row) / Integration ID / Name / Type / Owner / Developer (auto-populate from the program's Integration Tracker) / Migration Assigned To / Migration Status / Migration Notes / Planned/Actual Migration Date / Review Assigned To / INT Lead Review Status / Review Notes / Planned/Actual Review Date / Source Tenant / Target Tenant / Modified By/Date.

**Check columns** (each an `x`-if-applicable per the type matrix below):

- *Security:* ISU exists in target tenant; ISSG exists and contains the ISU; ISU Workday Account attached to the Integration System; ISSG contains ALL Domain and BP permissions (the revision splits Domain and BP into two questions).
- *Transport:* Retrieval / Delivery Environment Restrictions; PGP key installed; SSH key installed (revision proposes merging into one "Encryption Key Installed"); SFTP connection tested; master SFTP tracker updated. (**Master SFTP Tracker** = the tech lead's tracker confirming the CUSTOMER has set up every integration's SFTP connection in each environment - dev/implementation, QA/sandbox, and production. Stand one up per program if the tech lead doesn't already run one.)
- *RaaS:* uses RaaS report(s)?; ISU owns the report; shared with Implementers (revision: share with all authorized users?); cleared of errors; report actually run.
- *Config:* INT Attributes/Maps configured; Attributes Environment Restrictions; document retention set (workbook default 180 days; revision: set to the integration's required length); BP Definition configured; review calc fields; review sequence generators; review transaction logs; scheduled future processes configured + ISU owns the scheduled process.
- *Deploy:* deploy Orchestration to tenant (O4I - new in the revision); deploy CLAR to tenant (Studio/BIRT); Studio connected to RaaS report(s); Custom Report Transformations configured (**EIB-specific**: tenant configuration that formats columns on OUTBOUND EIBs - not XSLT, not DT); Custom Objects tied to the INT set up.
- *Wrap-up:* integration system reviewed for warnings/errors; miscellaneous functional config steps (notes); run DART. Several checks are API-verifiable instead of eyeball-verifiable - run the same read-set against source and target tenants and diff (RefID liveness, RaaS report reachable under the ISU, row counts): wd-extend-dev `references/tenant-ops.md`.

## Type-applicability matrix

An `x` per Integration Type marks which checks apply; Dynamic Views filter each migrator's list to only those. Rough tiers from the workbook: **SOAP/REST/RaaS API** = security checks (+ RaaS block for RaaS API) only; **Inbound EIB** = transport + config, no ISU/ISSG block; **Outbound EIB / Packaged / Core Connector / DT** = the full security + transport + config set (+ RaaS block where reports feed them); **Studio / BIRT** add CLAR deploy + Studio-RaaS connection + custom objects; **O4I** = full set + orchestration deploy. The builder (`scripts/build_migration_checklist.py`) embeds the exact matrix on its Type Applicability sheet - regenerate rather than reconstructing by hand.

## Workflow (statuses drive the hand-offs)

1. INT Lead populates rows ahead of tenant builds (or per change control); tracker feeds ID/Name/Type/Owner/Developer; lead assigns Migration/Review Assigned To, planned dates, source/target tenants.
2. Migrator works their Dynamic View, checks off applicable items, then sets Migration Status: **Migration Issue** (+ notes for reviewer/lead) or **Ready for Review**.
3. Reviewer works their view; sets INT Lead Review Status: **Migration Issue** (adds Review Notes; flips Migration Status back to Migration Issue - migrator fixes and resets to Ready for Review) or **Complete** (also flips Migration Status to Complete). Status value set: Not Started / In Progress / Migration Issue / Ready for Review / Complete.

## Design-change-note convention (reusable pattern)

The workbook revises itself in place: current layout kept at top, `*`-prefixed change notes in a row ABOVE the proposed new header row (each note in the column it concerns), `**` marking conventions, and open questions left as `*` notes rather than resolved. When proposing tracker/checklist revisions, follow this shape - old layout, annotated notes row, new layout, applicability matrix, process flow - so reviewers see the delta without a separate doc.

Admin-guide provenance (Jul 2026 review): the Jul 2026 Integrations admin guide contains **no tenant-to-tenant migration chapter** for traditional integrations and no "master tenant" / "not migratable" language - the PGP-private-key and API-client migratability rows remain house-checklist-sourced (neither confirmed nor contradicted by the docs). **Exception - x509:** official guidance says create x509 private key pairs **in Production** (a non-Prod-created pair cannot migrate to Prod; Sandbox inherits Prod's keys via the weekly refresh) - align any x509 check with the corrected R9 row in `tenant-task-recipes.md`. Two doc-confirmed underpinnings worth citing in migration reviews: give objects **reference IDs unique across all tenants before the first Object Transporter migration**, and WIDs differ per tenant - WID-dependent integrations are riskier to migrate/test. (Per Workday Admin Guide (Integrations), Jul 2026.)

Provenance note (owner-confirmed 2026-08-05): the source workbook may no longer be in active program use - it was provided as learning material. **This reference IS the adopted house pattern going forward** (the workbook's "proposed revision" column set, adopted here); instantiate from this reference and regenerate the workbook via `scripts/build_migration_checklist.py`. Master SFTP Tracker and Custom Report Transformations definitions above are owner-confirmed.

## Cross-references

Naming/ISU/ISSG standards behind the checks: wd-integration-dev `references/integration-naming.md`. Per-type build gates and key/API-client migratability (PGP private keys and API Clients do NOT migrate): wd-integration-dev `references/integration-build.md`. Extend app promotion + per-tenant re-setup matrix: `promotion-and-environments.md`.
