# Build report

**Result: PASS** - 23 of 23 checks passed.

Source suite: `v2.3 (2026-09-11)`. Limits checked against Microsoft Learn, 2026-11-10.

## Checks

- **PASS** - Name fingerprint file present
  - 5 fingerprints in build/name-hashes.json
- **PASS** - Name fingerprints match the private name list
  - in sync
- **PASS** - Every listed member skill found in the suite
  - 35 skills
- **PASS** - Every member has a description
  - all present
- **PASS** - No excluded skill packaged
  - none
- **PASS** - No skill packaged twice
  - none
- **PASS** - Every in-scope suite skill is packaged
  - 35 of 35
- **PASS** - Each SKILL.md under 20,000 characters
  - wd-suite-router=12,612; wd-scope-and-contract=8,920; wd-design=11,315; wd-extend-build=10,049; wd-integration-build=5,491; wd-test-deploy-run=13,020; wd-project-delivery=11,056; tool-and-product-build=15,708
- **PASS** - At most 8 skills
  - 8 skills
- **PASS** - At most 350 files across all skills
  - 307 files
- **PASS** - Folder depth at most 3
  - deepest file sits 2 folders below the skill root
- **PASS** - Each zip under 50 MB
  - largest 336 KB
- **PASS** - No file over 25 MB
  - none
- **PASS** - SKILL.md at the root of every zip
  - all 8
- **PASS** - No script files shipped (v1 decision)
  - 68 scripts held back
- **PASS** - Every file path listed in a SKILL.md exists
  - all resolve
- **PASS** - Agent instructions at most 8,000 characters
  - 5,464 characters
- **PASS** - Instructions name all 8 skills
  - all named
- **PASS** - Agent name at most 100 characters
  - 24
- **PASS** - Agent description at most 1,000 characters
  - 383
- **PASS** - At most 12 conversation starters
  - 12
- **PASS** - Sanitize sweep: no blocking hits (author paths; names by private list and by fingerprint)
  - 0 hits
- **PASS** - No scrubbed term in the package (2 listed in groups.json)
  - 0 hits

## The 8 skill packages

- **wd-suite-router.zip** - 6 member skills, 32 files, 129 KB, SKILL.md 12,612 characters
- **wd-scope-and-contract.zip** - 4 member skills, 29 files, 117 KB, SKILL.md 8,920 characters
- **wd-design.zip** - 4 member skills, 46 files, 234 KB, SKILL.md 11,315 characters
- **wd-extend-build.zip** - 2 member skills, 46 files, 336 KB, SKILL.md 10,049 characters
- **wd-integration-build.zip** - 1 member skill, 13 files, 87 KB, SKILL.md 5,491 characters
- **wd-test-deploy-run.zip** - 5 member skills, 49 files, 236 KB, SKILL.md 13,020 characters
- **wd-project-delivery.zip** - 6 member skills, 38 files, 119 KB, SKILL.md 11,056 characters
- **tool-and-product-build.zip** - 7 member skills, 54 files, 334 KB, SKILL.md 15,708 characters

## Sanitize sweep - blocking hits

- None.

## Sanitize sweep - hits to review by eye (7)

A hit here is a pattern match, not a confirmed leak. Each one needs a human look before sharing outside the team.

- non-ASCII character: `wd-design/wd-design-doc/assets/brands--neutral.json` line 68: `—`
- non-ASCII character: `wd-design/wd-design-doc/assets/brands--neutral.json` line 71: `—`
- non-ASCII character: `wd-design/wd-design-doc/assets/brands--neutral.json` line 85: `—`
- long numeric ID (sheet/workspace?): `wd-project-delivery/wd-smartsheet/references/api-details.md` line 30: `1234567890123456`
- long numeric ID (sheet/workspace?): `wd-project-delivery/wd-smartsheet/references/api-details.md` line 72: `4567890123456789`
- long numeric ID (sheet/workspace?): `wd-project-delivery/wd-smartsheet/references/api-details.md` line 86: `7654321098765432`
- long numeric ID (sheet/workspace?): `wd-project-delivery/wd-smartsheet/references/smartsheet-registry-template.md` line 23: `0000000000000000`

## Held back: scripts (68)

Not shipped in v1. See the README backlog, item 3.

- wd-extend-lifecycle/scripts/setup_doctor.py
- wd-folder-hygiene/scripts/archive_old_versions.py
- wd-design-doc/scripts/build_extend_design_doc.py
- wd-design-doc/scripts/build_idd_structure.py
- wd-design-doc/scripts/check_profiles.py
- wd-design-doc/scripts/idd_audit.py
- wd-design-doc/scripts/rebrand_template.py
- wd-design-doc/scripts/reset_views.py
- wd-design-doc/scripts/selftest_checks.py
- wd-design-doc/scripts/write_idd_readme.py
- wd-design-doc/scripts/xlsx_apply_layout.py
- wd-design-doc/scripts/xlsx_apply_structure.py
- wd-design-doc/scripts/xlsx_balance_columns.py
- wd-design-doc/scripts/xlsx_brand_style.py
- wd-design-doc/scripts/xlsx_calibrate.py
- wd-design-doc/scripts/xlsx_col_roles.py
- wd-design-doc/scripts/xlsx_com.py
- wd-design-doc/scripts/xlsx_coverage_guard.py
- wd-design-doc/scripts/xlsx_extract_layout.py
- wd-design-doc/scripts/xlsx_format_audit.py
- wd-design-doc/scripts/xlsx_layout_match.py
- wd-design-doc/scripts/xlsx_layout_rules.py
- wd-design-doc/scripts/xlsx_merge_narrow_notes.py
- wd-design-doc/scripts/xlsx_normalize_borders.py
- wd-design-doc/scripts/xlsx_normalize_layout.py
- wd-design-doc/scripts/xlsx_place_wordmark.py
- wd-design-doc/scripts/xlsx_repair_wrap.py
- wd-design-doc/scripts/xlsx_sheet_visibility.py
- wd-design-doc/scripts/xlsx_transplant_sheet.py
- wd-systems-diagrams/scripts/generate_diagrams.py
- wd-systems-diagrams/scripts/sfd_engine/__init__.py
- wd-systems-diagrams/scripts/sfd_engine/config/__init__.py
- wd-systems-diagrams/scripts/sfd_engine/config/brand.py
- wd-systems-diagrams/scripts/sfd_engine/config/color_suggestions.py
- wd-systems-diagrams/scripts/sfd_engine/config/diagram_config.yaml
- wd-systems-diagrams/scripts/sfd_engine/core/__init__.py
- wd-systems-diagrams/scripts/sfd_engine/core/graph.py
- wd-systems-diagrams/scripts/sfd_engine/core/ingest.py
- wd-systems-diagrams/scripts/sfd_engine/core/layout.py
- wd-systems-diagrams/scripts/sfd_engine/core/logo_lookup.py
- wd-systems-diagrams/scripts/sfd_engine/core/models.py
- wd-systems-diagrams/scripts/sfd_engine/core/scope_discovery.py
- wd-systems-diagrams/scripts/sfd_engine/core/validation.py
- wd-systems-diagrams/scripts/sfd_engine/output/__init__.py
- wd-systems-diagrams/scripts/sfd_engine/output/drawio_generator.py
- wd-systems-diagrams/scripts/sfd_engine/output/lucidchart_generator.py
- wd-systems-diagrams/scripts/sfd_engine/output/packager.py
- wd-systems-diagrams/scripts/sfd_engine/output/pptx_generator.py
- wd-systems-diagrams/scripts/sfd_engine/output/svg_generator.py
- wd-systems-diagrams/scripts/sfd_engine/output/svg_raster.py
- wd-systems-diagrams/scripts/smartsheet_adapter.py
- wd-extend-dev/scripts/pmd_preflight.py
- wd-extend-dev/scripts/requirements_preflight.py
- wd-extend-dev/scripts/security_domain_apply.py
- wd-extend-dev/scripts/security_domain_discovery.py
- wd-extend-dev/scripts/tenant_toolkit.py
- wd-integration-dev/scripts/build_integration_checklist.py
- wd-integration-dev/scripts/build_naming_standards_doc.py
- wd-integration-dev/scripts/build_security_segment_worksheet.py
- wd-integration-dev/scripts/wws_inventory.py
- wd-test-execution/scripts/extract_frames.py
- wd-test-execution/scripts/validate_output_file.py
- wd-deployment/scripts/build_cutover_spreadsheet.py
- wd-deployment/scripts/build_migration_checklist.py
- wd-smartsheet/scripts/smartsheet_api.py
- wd-kt/scripts/build_int_kt_template.py
- wd-kt/scripts/build_kt_plan.py
- app-architecture/scripts/scaffold_module.py

## Skipped files

- wd-design-doc/.claude/settings.local.json (housekeeping file)
- wd-design-doc/assets/logos/png/_ASSETS_REMOVED.md (housekeeping file)
- wd-extend-dev/scripts/__pycache__/pmd_preflight.cpython-312.pyc (housekeeping file)

## Wording replaced in the package (9 files)

Each file listed here differs from the installed suite. Only the packaged copy was changed.
The replacements cover scrubbed terms, dev tenant aliases and, on the maintainer's machine, engagement names.

- wd-extend-lifecycle/references/platform-compatibility.md: 1 replacement
- wd-extend-lifecycle/SKILL.md: 4 replacements
- wd-solution-playbooks/references/adaptive-planning.md: 1 replacement
- wd-extend-dev/references/custom-agents.md: 2 replacements
- wd-integration-dev/references/integration-review.md: 4 replacements
- wd-integration-dev/references/xslt3.md: 1 replacement
- wd-post-go-live/references/adoption-and-feedback.md: 1 replacement
- wd-comms/SKILL.md: 1 replacement
- app-harness/references/conformance-checklist.md: 1 replacement

## Renamed or flattened

- Every member's `SKILL.md` is packaged as `GUIDE.md`.
- wd-design-doc/brands/_example-customer.json -> wd-design-doc/assets/brands--_example-customer.json
- wd-design-doc/brands/neutral.json -> wd-design-doc/assets/brands--neutral.json
- wd-design-doc/templates/idd.json -> wd-design-doc/assets/templates--idd.json
- wd-design-doc/templates/layouts/payroll-input-inbound-o4i.json -> wd-design-doc/assets/templates--layouts--payroll-input-inbound-o4i.json
- wd-comms/references/clients/_template.md -> wd-comms/references/clients--_template.md
