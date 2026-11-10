# Input schema - Integration Tracker

The engine ingests **one** Integration Tracker (Excel/CSV, or a live Smartsheet). No separate
systems file is needed - systems are **derived** from the integration rows (categories decided by a
majority vote across rows). Column headers are matched **case-insensitively** via an alias map, so
real-world trackers usually work without renaming anything.

A ready-to-run example lives at `references/sample-integration-tracker.csv` (~8 integrations, 3
workstreams, one Boomerang, one out-of-scope row).

## Fields

### Required
| Field | Meaning | Common header aliases |
|---|---|---|
| **Scope** | Inclusion filter; only in-scope rows are drawn | `Scope`, `Scope Status`, `Integration Scope`, `In Scope`, `Include` |
| **Workday ID #** | Unique integration ID (INT####) | `Workday ID #`, `Workday ID`, `WD ID`, `Integration ID`, `Int #`, `ID` |
| **Integration Name** | Human name | `Integration Name`, `Name`, `Description`, `Legacy Integration Description` |
| **Direction** | Inbound / Outbound / Bidirectional / Boomerang | `Direction`, `Inbound/Outbound`, `Flow`, `Flow Direction` |
| **Vendor/External Systems** | The non-hub system on the other end | `Vendor/External Systems`, `External System`, `3rd Party System`, `Vendor`, `Vendor System` |
| **Workstream** | Functional area -> one deep-dive page each | `Workstream`, `Work Stream`, `Module`, `Workday Module`, `Domain` |

**Endpoint inference:** if there are no explicit source/target columns (the usual case), the engine
runs in *direction-inference mode* - it treats **Vendor/External Systems** as the far endpoint and
uses **Direction** to decide which side is the hub. (The `source_system_id`/`target_system_id`
"columns not matched" log line is expected and harmless in this mode.)

### Optional (enrich the diagram if present)
| Field | Effect | Aliases |
|---|---|---|
| **Integration Type** | Connector line dash style (EIB, Core Connector, Studio, API, Orchestrate, RaaS, BIRT, SFTP, Real-time, ...; spelling variants normalized) | `Integration Type`, `Integration Method`, `Connector Type`, `Template` |
| **Vendor Type** | Node sub-label / category (Internal / External / Third-Party) | `Vendor Type`, `System Type`, `System Category`, `Internal/External` |
| **From System** / **To System** | Explicit endpoints (overrides direction inference) | `From System`/`Source`, `To System`/`Target` |
| **priority** | `P1` adds a gold ring to the node | `Priority`, `Integration Priority`, `P1/P2/P3` |
| **Workday Domain Area** | Grouping / go-live wave label | `Workday Domain Area`, `Domain Area`, `Wave`, `Go-Live Wave` |
| **Has PII Data?** | Data-sensitivity tag | `Has PII`, `PII`, `Data Classification`, `Sensitivity` |
| **frequency** | Run cadence | `Frequency`, `Schedule`, `Run Frequency` |
| **notes** | Free text | `Notes`, `Comment`, `Comments` |

## Multi-ERP hub
The hub ERP is **auto-detected** (the system that appears most often as an endpoint) and can be
overridden with `--hub "Oracle Fusion"` / `--hub "SAP S/4HANA"`. The hub name is display-only; it
drives the hub node label and description text, not the layout.

## Boomerang (hub-to-hub) rows
Set **Direction = Boomerang** and **Vendor/External Systems = the hub name** (e.g. `Workday`) for a
Workday-to-Workday integration. These render as a distinct boomerang connector and legend entry.

## Live Smartsheet mapping (`scripts/smartsheet_adapter.py`)
The adapter reads a sheet via the **wd-smartsheet** helper (`get_sheet`), maps its real column
titles onto the fields above using `SFD_COLUMN_ALIASES` (case/punctuation-insensitive), filters to
in-scope rows, and emits SFD-schema CSV that the engine ingests. Pure mapping functions
(`build_header_map`, `map_rows_to_sfd`, `rows_to_csv`) are offline-testable; only `fetch_tracker_csv`
touches the network.

**Reference sheet (example - not a hardcoded default):** an *Integration Tracker* sheet (registry
id like `<sheet-id>`, on the order of hundreds-to-thousands of rows), columns like `Workday ID #`,
`Integration Name`, `Workstream`, `Scope`, `Assigned To - Design`. (Use the integration-tracker
sheet id from your engagement's wd-smartsheet registry - not the RAID or other sheets.) Any client's
tracker works as long as its columns map through the alias table - add program-specific aliases there
if a column isn't picked up.
