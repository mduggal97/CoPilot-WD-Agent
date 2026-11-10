# Functional testing of traditional integrations (EIB / Studio / CC / DT / O4I-as-INT)

The scenario methodology in this skill is Extend-app-centric (pages, BPs, orchestrations). Traditional
integrations are batch/file/API with no UI, so they are tested differently: you verify the OUTPUT against the
spec, the transport, the security, the schedule, and the error/audit behavior. Same core principle as app
testing - **derive scenarios at design time from the signed design** - but the design here is the Integration
Design Document (IDD) and the checklist below is integration-specific.

## Core principle: derive from the IDD, field by field

Walk the IDD at design time and produce scenarios from it - do not reverse-engineer them from the built
integration. The load-bearing source is the **File / Field-mapping tab** (every output field: source, mapping,
format, length, default, calc field, XSLT transform) plus the transport, security, and schedule design. Every
mapped field yields at least one "value is correct per the mapping" check; every input record type yields a
happy + a malformed/rejected scenario. A mapping row that cannot produce a testable expectation is a design
gap - push it back (same rule as vague requirements).

## Integration derivation checklist (apply every line)

| Element | Mandatory scenarios |
|---|---|
| **Every output field** | Value correct per the mapping - format, length, padding, decimal/date format, defaulting, calc-field/XSLT transform result. This is field-level reconciliation against the IDD File tab, not "a file appeared." |
| **File structure** | Delimiter/encoding, header/trailer, record counts in the trailer, line endings; fixed-width column positions; filename convention + timestamp; empty-file / zero-record behavior. |
| **Every input record type** (inbound) | Happy payload loads; malformed/invalid payload is rejected with the expected, readable error; the tenant-side error surface is captured. |
| **Transport / connectivity** | SFTP/endpoint reachable with the real credentials, correct directory, retrieve vs deliver, retries; PGP encryption/decryption round-trips; advance-ship-notice / acknowledgement if used. |
| **Security** | Runs under the intended ISU with least-privilege ISSG/domains (positive); and a **negative** test - a missing domain fails as expected, no over-broad access, no data the integration should not see. |
| **Scheduling** | The schedule actually fires at the right frequency; blackout/holiday handling; a missed/failed run catches up or alerts (a silently-unscheduled integration is a classic miss). |
| **Volume** | Run at FULL expected volume, not a 5-record sample; confirm streaming/large-file handling and that it completes within its window (functional volume - Workday's mandated Performance Testing is a separate wd-deployment gate). |
| **Error handling / audit** | The error framework produces the expected audit/log output (global catch, per-step catches, severity rollup); partial-failure behavior is correct; retry/replay works and is idempotent (Put vs Submit matters). |
| **Boundary data** | Nulls, special/multi-byte characters, max-length values, effective-dating, and delta vs full-extract behavior (a delta run picks up only changed records). |

## Parallel run (the gold standard for outbound)

Run the new integration alongside the legacy one for one or more cycles and **reconcile the output
field-by-field and by record count**. Sign-off = N consecutive cycles of matching output (agree N with the
client). This is the strongest validation that the new integration reproduces the trusted behavior; schedule
it into the plan - it needs real cycles, not a one-shot.

## Reconciliation chain

Prove the data survives every hop: source count -> extracted -> transformed -> delivered -> loaded in the
downstream system. Record counts at each stage plus spot field-value checks; every variance explained. (Same
discipline as a data-conversion load - wd-extend-dev `data-conversion.md`.)

## Integration UAT (validate in the DOWNSTREAM system)

Integration UAT is not "the file generated" - it is the client/vendor confirming the output is correct **in
the consuming system** (the downstream app loaded it, the vendor accepted it, the numbers are right there).
Entry criteria: unit/reconciliation passed, connectivity established, a real test file delivered end to end.
Exit criteria: downstream sign-off, no open Sev1/Sev2, and (for outbound) an agreed parallel-run result.

## Recording & boundaries

- **Record** results in the design doc's integration test section / test log (format owned by wd-design-doc);
  a fixed defect flips to Pass only after a re-run reproduces correct output.
- **Build gates + DART** (per-type build verification, migration) are owned by **wd-integration-dev**
  `integration-build.md` - that is build/migration verification; THIS is functional testing of the result.
- **Code/XSLT fixes** -> wd-integration-dev. **Scenario tab/format** -> wd-design-doc. **Workday-mandated
  Performance Testing / Volumes Questionnaire** -> wd-deployment (a deployment gate, not functional testing).
- **O4I orchestrations** tested as flows use this skill's orchestration row (success / API-error / empty /
  timeout) + wd-extend-dev orchestration.md; an O4I tracked as an INT also gets the transport/schedule/security
  rows above.
