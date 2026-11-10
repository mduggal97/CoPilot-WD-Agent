# Dual-Audience Document Pattern (Part 1 Business / Part 2 Technical)

One document, two audiences, hard split: **Part 1** for business readers (directors,
process owners, sponsors), **Part 2** for technical readers (developers, admins,
integration owners). Each part is complete for its reader - nobody has to read the
other half.

## Real examples

Prior design/technical specs follow this pattern exactly - e.g. a
`<your workspace>\<Use-Case>_Design_Technical_Specification.docx` with sibling docs
for each related use case in neighboring folders.

Open one of these before authoring a new dual-audience doc - match the section
architecture rather than reinventing it.

## When to use it

- **Design/technical specifications** - the sponsor signs off on Part 1; the build
  team works from Part 2.
- **Post-production guides** - what the app does and who owns it (Part 1); how it's
  wired and how to change it (Part 2).
- Any deliverable where splitting into two separate documents would guarantee the
  business half goes stale - one file keeps them versioned together.

When NOT to use it: pure end-user guides (no technical audience) and pure runbooks
(no business audience). Those stay single-audience.

## Part 1 - Business

Written for a director who will **never open Part 2**:

- Purpose and business outcome: what problem this solves, in the client's own words.
- Who uses it (roles), the before/after of the process, and the process flow at
  swimlane level (business lanes, no API boxes).
- Scope and boundaries: what's in, what's explicitly out, what's deferred.
- Decisions and their business rationale ("approvals route to the primary grant
  manager because...") - decisions live here even when the *implementation* of the
  decision lives in Part 2.
- Zero acronyms without expansion, zero endpoint names, zero field-level detail.

**Readability test for Part 1:** a director reads it in one sitting, could explain the
app to their VP afterward, and never hit a sentence they had to skip. If a paragraph
needs Workday-internals knowledge to parse, it belongs in Part 2.

## Part 2 - Technical

Written for the person maintaining the thing:

- Architecture: components, orchestrations, business objects, integrations, security
  (ISSGs/ISUs), with the technical process flow.
- Data contracts: RaaS reports and prompt structures, API/SOAP operations and
  versions, field mappings.
- Configuration inventory: config attributes, reference attributes, schedules,
  environment differences.
- Error handling and logging conventions; known limitations and open items.

Part 2 may reference Part 1 sections ("implements decision D3") but Part 1 never
references Part 2.

## Keeping the parts honest

- **Every fact appears once.** Business rationale in Part 1, implementation in
  Part 2; if you're pasting the same paragraph into both, it's in the wrong place.
- Shared artifacts (the swimlane process flow) can appear in both - business-lane
  rendering in Part 1, full technical rendering in Part 2.
- On revision, update both parts in the same edit session - the pattern's biggest
  failure mode is a current Part 2 under a stale Part 1.
- Author in Word via the `docx` skill; use heading styles so the TOC visibly shows
  the two-part split.
