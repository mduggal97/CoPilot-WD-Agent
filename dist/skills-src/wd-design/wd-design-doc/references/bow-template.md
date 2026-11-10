# BoW / Marketplace design doc - the 10-tab template

For Marketplace ("Built on Workday" / BoW) apps, the Marketplace products team requires THEIR template - do not substitute the 16-tab format even though it's richer.

## Tab order

`Overview | Discovery | Specification | Process Flow | Object Model | UI Wireframes | Unit Testing | QA Review | Open Items | Migration Checklist`

- Canonical blank: the engagement's BoW design-doc template (see **Engagement inputs** below).
- Requirements live INSIDE the Discovery tab (no separate Requirements tab).
- Endpoint/API inventories go in the Specification tab.
- Extra tabs are allowed but must match the template's formatting exactly.
- The yellow-highlight convention and professional formatting rules apply unchanged.

## Fill method

This template's structure fills more reliably via Excel COM (pywin32) than openpyxl - precedent: a delivered BoW doc (`fill_bow.py` pattern). COM preserves the template's conditional formatting, formulas, and shapes that openpyxl can drop. Copy cloud-synced (e.g. OneDrive) files to the scratchpad before opening - sync locks can block even reads. **After any fill, diff the result against the blank template tab-by-tab: Unit Testing's status-summary formulas and each tab's formatting must survive intact** (a delivered draft once lost both - that class of regression is unacceptable in a delivered doc).

## Polish the template's weak spots (without breaking products-team compliance)

The raw BoW template's look is spartan and is not client-professional as-is (standing house judgment). The tab structure and existing formatting are the products team's and must stay - but everything you ADD must meet the full professional-formatting bar in SKILL.md: bordered tables for all populated regions (Discovery Q&A, Object Model as a real object/field/type/relationship grid, Process Flow as structured content - never prose clumped down column B), inserted rows carrying table formatting with content below shifted down, wrapped/sized text, yellow-with-question cells, and a blank spacer row between sections. Leave the document better-formatted than the template alone would produce.

**Phantom band-fill on appended sections (build-verified on a delivered app, v1.7).** When you ADD a section into a region that looks empty, those cells often already carry the template's blue band-fill (the used-range is oversized). Your new text lands white-on-blue and is illegible - and the G1-G17 property checks all pass; only the G18 verify-by-render gate catches it. So on every appended block: (1) explicitly clear the fill on the block before writing, then (2) apply the bordered-table treatment by **copying the live template's own style objects** - `copy.copy()` the fill/font/border from an existing band cell, header cell, and data cell - never reconstruct them. The band is a THEME color, so `fgColor.rgb` returns a theme index, not a hex, and reading/rebuilding it throws `Values must be of type str`. Copy the whole style object and you sidestep it.

## When BOTH formats exist

Some apps maintain a BoW doc as the document of record for the products team AND a 16-tab version for delivery depth. If so, declare ONE the document of record in its Overview tab and mirror decisions into the other at each version - divergent twins are worse than one doc.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Canonical blank BoW template** - the engagement's 10-tab BoW/Marketplace design-doc template workbook. Obtain the branded template master per engagement, or regenerate it and keep the neutral default.
- **Style donor (optional)** - a delivered BoW doc from the engagement to clone style objects from, when formatting parity is needed.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
