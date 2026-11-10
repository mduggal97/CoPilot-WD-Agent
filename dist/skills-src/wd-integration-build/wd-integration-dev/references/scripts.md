# Scripts this skill references - regenerate-on-demand build-specs

All four scripts SHIP inside this skill at `wd-integration-dev/scripts/`. The build-specs below are
the regeneration source if a copy goes missing (a partial install, or a fresh machine). All are
cross-platform Python (stdlib + `openpyxl`/`python-docx` for the template builders); setup in
`wd-extend-lifecycle/references/prerequisites.md`.

- **`scripts/build_naming_standards_doc.py`** - vendor-neutral Workday Implementation Naming
  Standards `.docx` (spec below).
- **`scripts/build_integration_checklist.py`** - vendor-neutral integration design/build
  checklist workbook (spec below).
- **`scripts/build_security_segment_worksheet.py`** - vendor-neutral integration security
  segment worksheet (spec below).
- **`scripts/wws_inventory.py`** - inventory a tenant's SOAP Web Services (WWS) catalog: parse the
  in-tenant reports (authoritative) or crawl WSDLs live (spec below). BUNDLED and ready to run; the
  method + retrieval gotchas are in [wws-catalog.md](wws-catalog.md).

The three template builders regenerate clean **vendor-neutral blanks**; use them as they are,
or obtain the firm's branded master per engagement.

The orchestration/O4I engine's own scripts (`validate.py`, `workday_rest.py`, `generate_flow.py`,
`tenant_toolkit.py`) live in the wd-extend-dev skill (`references/scripts.md` there) - O4I built
as an integration still uses that engine.

---

### build_naming_standards_doc.py - vendor-neutral Workday Implementation Naming Standards (.docx)
- **Language / runtime:** Python 3 (`#!/usr/bin/env python3`).
- **Third-party deps:** `python-docx` (`pip install python-docx`). Stdlib: `sys`.
- **OS constraints:** Cross-platform.
- **Inputs:** CLI `argv[1]` = optional output path. Default `Workday_Naming_Standards.docx`. All content (section outline + tables) is embedded.
- **Outputs:** one `.docx` reproducing the source template's section hierarchy and **all 14 reference tables verbatim**: Introduction; General Guidelines (Reference IDs + examples table, Code Values); FDM / Cross-Functional (Locations table, Org/Worktag ID Format table); Sequence Generators (Financials master + transactional, HCM master + transactional); Condition Rules; Calculated Fields (guidance + naming + the 32-row function-abbreviation table); Integration Types; Encryption Keys; Integration Systems (+ the INT type-abbreviation table + guidelines); Workday Studio (+ Studio object-naming table); Integration System Components (XSLT/ISU/ISSG/segment/file-utility formats + the services table); XSLT & MVEL guidelines (+ common XSL-element table); and the Naming Standards Quick Reference (+ prompt-guidelines table). Stdout confirmation.
- **Method:**
  1. `TABLES` - a list of the 14 tables as lists-of-rows, reproduced from the source (cleaned of stray control chars; `/` inside a source cell = an in-cell line break, flattened to `; ` or a space).
  2. `CONTENT` - an ordered list of block tuples `('title'|'h1'|'h2'|'h3'|'p'|'b'|'bullet', text)` or `('table', <index into TABLES>)`. This is the section skeleton with the standard-defining prose (format strings, examples, do/don't lists).
  3. `add_table` builds a `Table Grid` table, bolds the header row, adds a spacer paragraph. `build` walks `CONTENT`: headings via `add_heading` (levels 0-3 = built-in Word styles), body via `add_paragraph`, bold lead-ins as a bold run, bullets via the `List Bullet` style.
- **Key constants:** uses **built-in Word heading styles** (Title + Heading 1/2/3) so a brand template can restyle them; client name rendered as the literal placeholder `<Client>`; example integration/vendor names genericized to "Sample ..." (no real vendor names); table style `Table Grid`.
- **Gotchas:** the tables ARE the load-bearing IP - keep them verbatim; the prose is the essential standard-defining guidance, condensed from the source's longer generic Workday commentary (it is a usable master, not a byte-for-byte copy). No firm branding is baked in (the source filename carried the firm name; the body did not) - it stays neutral. The source carried a stray client name and a "Word Template" core-title/author - both dropped here. Reference-ID digit patterns (`CC1nnn`, `GRyyyynnnn`, etc.) are examples; confirm the client's actual FDM digit conventions during discovery before adopting.
- **Regeneration confidence:** High for structure + tables (fully embedded); the prose is a faithful condensation, so exact sentence wording will vary on rebuild.

---

### build_integration_checklist.py - vendor-neutral integration design/build checklist workbook
- **Language / runtime:** Python 3.
- **Third-party deps:** `openpyxl`. Stdlib: `sys`.
- **OS constraints:** Cross-platform.
- **Inputs:** CLI `argv[1]` = optional output path. Default `Integration_Build_Checklist.xlsx`. Content embedded.
- **Outputs:** one `.xlsx`, 12 sheets: **Design Checklist - All Types**, **Build Checklist - Generic**, one per integration type (**EIB Inbound/Outbound**, **Studio Inbound/Outbound**, **Core Connectors**, **Connector with DT XSLT**, **Orchestration for Integration**), and three reference sheets (**API Clients**, **SSH & PGP Keys**, **SFTP - MFT Endpoint Setup**). Every action row carries a Status dropdown (Not Applicable / Not Started / In Progress / Complete). Stdout lists the sheet names.
- **Method:**
  1. Checklist content is data: `DESIGN_ROWS`, `BUILD_GENERIC_ROWS`, and per-type row lists as `(Area, Action, WorkdayTask)` tuples. Shared blocks (`ISSG_CHAIN`, the `NOTIF` notification text, the Studio `STUDIO_SETUP` preamble) are composed into the type lists so the ISSG->ISU->notification tail repeats verbatim.
  2. `build_check_sheet`: intro rows 1-2 (merged), header row 3 (Status/Area/Action, plus `Workday Task` for type sheets, plus `Reviewer Comments`), grey fill, widths (A14/B28/C80/D42/E30), a `Status` list validation over the data range defaulting each row to "Not Started", freeze `A4`.
  3. `build_reference_sheet`: API Clients (OAuth grant-type/config reference with a genericized "not migratable -> master tenant -> dev tenant after refresh" migration note and public `doc.workday.com` links), SSH & PGP Keys (four key/cert types + migratability), and the SFTP/MFT sheet (five generic connection patterns + generic request steps).
- **Key constants:** `STATUS_VALUES = "Not Applicable,Not Started,In Progress,Complete"`; `DEFAULT_STATUS = "Not Started"`; neutral header fill `D9D9D9`.
- **Gotchas:** this regenerates a **generic** template. All client-specific content in the source was genericized: internal tenant names -> "master tenant"/"dev tenant"; the source's two client-division codes -> `[Division A / Division B / Both]`; "firm-provided shared Studio utilities" (was a named firm utility); the source's client-questions working-comment column -> a blank `Reviewer Comments` column; the two program-specific SFTP/MoveIT sheets (internal request URLs, a "Do not Use" tab) -> one reusable **SFTP - MFT Endpoint Setup** sheet of connection patterns. Do NOT re-introduce client tokens. Public `doc.workday.com` OAuth/security links are retained (Workday-public).
- **Regeneration confidence:** High - every sheet's rows, headers, status picklist, and genericization are embedded and specified.

---

### build_security_segment_worksheet.py - vendor-neutral integration security segment worksheet
- **Language / runtime:** Python 3.
- **Third-party deps:** `openpyxl`. Stdlib: `sys`.
- **OS constraints:** Cross-platform.
- **Inputs:** CLI `argv[1]` = optional output path. Default `Integration_Security_Segment_Worksheet.xlsx`. Segment list embedded (`SEGMENTS`).
- **Outputs:** one `.xlsx`, single **Setup Details** sheet: a `Segment-Based Security Group` banner, a row-4 header (`Users | User-Based Security Group | (>>>>) | Access To Segments | Security Group | (<<<<) | Integration System Security Segment | Integration Systems`), then one editable block per functional-area segment, a red **View Only Below** banner, and the same segments repeated as VIEW-only variants. Stdout confirmation.
- **Method:** `_block(area, persons, int_count, int_start, view_only)` writes one segment: a yellow merged `D:E` header (`ISSG <Area> Segment Security Group[ VIEW Only]`), the group mapping on the first row (`ISUG <Area> INT Operator` >>>> `ISS <Area> Integrations` <<<< the segment), `Person 1..N` placeholders down column A, and `Integration 1..N` placeholders down column H (globally numbered per section). `build` writes the title/headers, three editable segments, the View-Only banner, then three VIEW-only segments.
- **Key constants:** `SEGMENTS` = three GENERIC example functional areas (Benefits / HRIS / Payroll) with `persons`/`int_count` counts - rename per engagement; column widths from the source; yellow `FFFF00` segment headers, red 18pt `View Only Below` banner. Group-name conventions match `integration-naming.md` (ISS/ISUG/segment).
- **Gotchas:** segment names are illustrative examples, not client data. The source's delivered-tenant screenshot tabs are intentionally omitted (they carried tenant data) - capture your own tenant views when instantiating. This worksheet plans the HUMAN side of integration security (who sees which integration systems); the machine side (the ISU running the integration) is `security-setup.md` in the wd-extend-dev skill. No firm branding; title uses the `[Customer]` placeholder.
- **Regeneration confidence:** High - the repeating block layout, segment triad, and View-Only mirror are fully specified; only the segment list and person/integration counts vary per engagement.

---

### wws_inventory.py - Workday SOAP Web Services (WWS) catalog inventory
- **Language / runtime:** Python 3.
- **Third-party deps:** live mode - `requests` + `truststore` (`pip install requests truststore`);
  reports mode - `openpyxl`. Stdlib: `os, re, sys, csv, time, xml.etree.ElementTree`.
- **OS constraints:** Cross-platform. `truststore` matters on corporate networks with TLS interception.
- **Inputs / modes:**
  - Reports mode (authoritative, no creds): `--reports <Public_Web_Services.xlsx> <Public_Web_Services_and_Related_Operations.xlsx>` (exports of the two delivered tenant reports).
  - Live mode (anonymous by default): env vars `WD_HOST` (tenant base URL), `WD_TENANT`. WSDL retrieval is anonymous, so NO credentials are needed; HTTP Basic auth for web services was retired ~R2 2026 and is removed. For the rare tenant that gates WSDL retrieval behind auth, an OPTIONAL API-client refresh-token bearer is minted from the OS keychain (service `wd-wws-inventory`, keys `client_id`/`client_secret`/`refresh_token`) and attached automatically - see `wd-auth/references/oauth-setup-guide.md`. Optional `WD_CA_BUNDLE` (corporate root CA .pem), `WD_INSECURE=1` (skip TLS verify - last resort).
- **Outputs:** reports mode -> `wws_inventory_master.csv` (Service, Operation, Kind[web-service|background], Status[DEPRECATED], NameProbeDiscoverable) + `wws_inventory_master.md` (counts + the not-name-probe-discoverable "private" list + all-services table). Live mode -> `wws_inventory.csv` (Service, Version, Operation) + `wws_inventory.md`.
- **Method:**
  1. Reports mode: openpyxl-parse the service report (service + documentation) and the operations report (a grouped report where each service header is followed by a single cell of `\n`-joined operations, in col0 OR col1 - scan both); flag DEPRECATED/Do-Not-Use and background-process ops; if `wws_inventory.csv` from a prior live run is present, mark each service discoverable-by-name-probe yes/no.
  2. Live mode: `truststore.inject_into_ssl()`; try `WD_HOST` and its `-services1` sibling until a known service WSDL (`Human_Resources?wsdl`) returns 200; resolve the current WWS version by probing `vNN.M` descending; then fetch each service in a seed list at that version (fall back to default `?wsdl`) and parse `wsdl:portType/operation` names.
- **Key constants:** `CAND_V` = `v48.2..v40.0` version probe order; `SEED` = the ~40 well-known public services (over-inclusive is safe - misses 404 and drop). Auth: anonymous WSDL crawl by default; `_mint_bearer()` attaches an OPTIONAL API-client refresh-token bearer (keychain `wd-wws-inventory`) for tenants that gate WSDL (Basic retired ~R2 2026; refresh-token grant per `wd-auth/references/oauth-setup-guide.md`).
- **Gotchas:** SOAP is often on the `-services1` gateway host, not the base URL; the browsable directory is frequently 404 (hence name-probe or the report export); default `?wsdl` returns an OLD version (undercount) so a version MUST be resolved; some tenants gate WSDL and return 401/403 (configure the optional bearer). Full narrative + "what private WWS actually are" in [wws-catalog.md](wws-catalog.md). No client data embedded (creds via OS keychain; env carries only host/tenant; docstring examples use `<pod>/<tenant>` placeholders).
- **Regeneration confidence:** High for both modes - parsing, host/version resolution, and the seed list are fully specified; the seed list only affects live-mode discovery breadth (reports mode is authoritative regardless).
