# Document Transformation (DT) - authoring guide + the O4I pre-formatter pattern

DT = the "Connector with Document Transformation" integration type: a tenant-configured
integration system that runs an XSLT you supply against a document, with no Studio project.
XSLT LANGUAGE mechanics (streaming, XTT/ETV annotations, merge idioms) live in
[xslt3.md](xslt3.md) - this file owns WHEN to use DT, how a DT integration is put together,
and the pre-formatter role DT plays in front of O4I template integrations.

Provenance: patterns below are verified against a delivered conversion program (2026-08)
and a firm training set with solution files unless marked otherwise.

## When DT is the right tool

- **Reshape a file, no orchestration logic needed.** Source system emits a layout Workday
  (or a downstream system) cannot consume directly: rename/reorder columns, fixed-width to
  delimited, value coercion, multi-record flattening.
- **Pre-formatter in front of a template integration** (the big modern use - see below).
- **Outbound formatting** after a Core Connector or EIB: XTT/ETV annotations produce the
  flat-file layout the receiver demands (see xslt3.md XTT/ETV section).
- NOT the right tool when you need per-row web-service calls, branching across documents,
  retries, or external HTTP - that is Studio or O4I territory.

Cost note: DT rides the integration that invokes it; the Flex-Credits metering question is
decided by that parent integration type (see SKILL.md).

## Anatomy of a DT integration

1. Tenant task: create the integration system from the Document Transformation template.
2. Attach the XSLT as the transformation attachment (versioned - keep the source in the
   repo, never only in-tenant).
3. Configure delivery/retrieval transport on the same integration system.
4. Standard integration hygiene applies: INT ID naming (integration-naming.md), ISU/ISSG,
   build gates (integration-build.md), IDD documents the mapping.

DT executes ONE stylesheet against ONE input document per run. Cross-file joins, lookups
against live tenant data, and stateful multi-run behavior do not belong here.

## The O4I pre-formatter pattern (verified, delivered 2026-08)

Template O4I integrations read a FIXED canonical column layout, because the O4I CSV surface
is positional:

- The only column accessor is `columnValueAtIndex(n)` - POSITIONAL. A header-driven
  read loop CAN make keys dynamic (`{{#each}}` over the header row), but FIELD MAPPING to
  web-service elements cannot be dynamic. So the template always reads a fixed, complete
  column order, and any client-specific condensing/reshaping happens UPSTREAM.
- What O4I structurally cannot parse (each one alone forces a pre-formatter):
  - Fixed-width files (no delimiter -> `columnValueAtIndex` has nothing to split on).
  - Multiple interleaved record types (header/detail/trailer) - no per-record-type branching.
  - Cross-record state (carry a header value down into its detail rows; check a trailer
    control total before loading).
- The pre-formatter is the CLIENT'S choice (DT is the firm default; a custom O4I or any
  other tool is acceptable) - the template must not assume DT. Ship example DT scripts
  with the template package so DT is the easy path.

Ship THREE example shapes with any canonical-layout template (mirror the delivered set):

1. **Column subset to canonical** - client sends fewer columns; expand to the full layout
   with blanks. The simplest case; proves the contract.
2. **Renamed/reordered to canonical** - rename + reorder + value coercion (TRUE/FALSE to
   Y/N, European decimal comma, case folding) + packed-column assembly (below).
3. **Fixed-width multi-record to canonical** - record-type dispatch on a type code,
   header values carried down into detail rows, trailer control total checked BEFORE load.
   This is the "why you still need DT" exemplar - its header comment should enumerate the
   O4I limitations above.

## Canonical-layout contract discipline (spec-as-code)

The failure mode this prevents: the design doc, the sample file, and the shipped DT scripts
silently drift apart. The fix, verified in a delivered template:

- **One machine-readable spec is the single source of truth** (e.g. `canonical_spec.py`):
  per-column `(name, required, format, sample, target-WS-element, notes)` plus any
  code-to-element maps (e.g. a worktag TYPE -> element -> ID-type map). Tag every fact with
  its provenance (`local` = verified in delivered source / `wdocs` = vendor API docs / `both`).
- **Generators emit everything else** - the layout README, the sample input file, and the
  example DT XSLTs are GENERATED from the spec and marked do-not-hand-edit. Generators
  self-validate (column counts, header equality, packed-pair parsing, XML well-formedness),
  so drift is structurally prevented. Change the spec, re-run, re-embed on the design doc's
  Examples tab.
- **Packed-column convention** for open-ended code sets: one column holding
  `TYPE=VALUE;TYPE=VALUE` pairs so a new type needs NO header change. Consequence: the
  file delimiter attribute must never be `;` or `=` - validate at run start.
- **Behavioral switches are integration ATTRIBUTES, not file columns** (e.g. an
  update-vs-add matching mode) - integration-wide choices do not belong per-row.
  Precedence rule stated in the contract: attribute over file where both could apply.
- **Control columns** (record type, source line number) that are never sent to Workday but
  are quoted in every error-log entry, so a rejected row is findable in the source file.
  Pair with the batch line-number reconciliation idiom: when loading in batches,
  `Row_Number mod batch-size` maps a Workday `Import_Process_Message` line number back to
  the true source row (see the error/audit framework files noted in xslt3.md).
- **Sample mode** (self-documenting integration): a launch parameter/attribute that skips
  the load and instead attaches the sample canonical file + the DT example scripts + the
  README to the run event, so a client admin can pull the contract from the tenant itself.

## Worked examples on hand (engagement inputs - never hardcode paths in deliverables)

- The generated 3-example DT set + spec + generators inside the conversion program's
  template folder (author's machine: `Studio to O4I Conversion\<template>\DT Example Scripts\`).
- Firm training set WITH solution files: ETV inbound/XML formatting, fixed-length
  transformation, XTT formatting, XSD + sample payloads (author's machine:
  a firm training-files folder, `...\Document Transformation\`).
- Client-derived starter templates for DT delimited/fixed-length output, Core Connector
  Worker, and PICOF (see the starter-template bullet in xslt3.md).

Genericize any client residue before reusing examples in deliverables.
