# The configuration-guide pattern - format, reuse discipline, and building a library

> Vendor-neutral. This file defines what a good per-area configuration guide LOOKS like
> and how a practice accumulates its own library. It deliberately ships NO configuration
> content: per-area leading practices are exactly the kind of accumulated IP that lives
> in a firm's private layer (or in Workday's own documentation), never in a shareable
> skill.

## What a configuration guide is

A per-area (module, sub-module, or feature) document that lets a competent consultant
configure that area WELL on the first pass - the difference between "what the setup task
does" (Workday's documentation) and "what we recommend and why" (the guide).

**Guide vs. configuration workbook** (the names are close; the artifacts are not): the
GUIDE is reusable practice IP - the default positions and their rationale, carried
engagement to engagement. The WORKBOOK (delivery-norms.md) is THIS engagement's record of
what this client decided against those defaults. During Architect & Configure the guide's
recommended baseline pre-populates the workbook's decision entries; the workbook then
records where the client confirmed or diverged, and why.

## The format (use for every guide)

1. **Purpose and scope** - the area covered, the Workday products/SKUs it applies to,
   and what is explicitly out of scope.
2. **Prerequisites** - foundation data, tenant setup, security, and upstream decisions
   that must exist first (e.g. FDM structure before anything that routes or reports on
   it).
3. **Recommended baseline configuration** - the default-position setup, stated as
   decisions with RATIONALE ("start with X because Y"), not as click paths.
4. **Decision points and considerations** - where clients legitimately diverge: the
   options, the trade-offs, the questions to ask, and what each choice commits the client
   to downstream (reporting, security, integrations, maintenance).
5. **Common pitfalls** - the mistakes that cost rework, each with the symptom and the
   avoidance.
6. **Cross-area touchpoints** - what this area's choices force elsewhere (payroll <->
   time, FDM <-> security, student <-> finance), so single-area decisions stop being
   program surprises.
7. **Testing hooks** - the unit-test scenarios this area's configuration implies (feeds
   wd-testing scenario derivation).
8. **Currency block** - Workday release the guide was last verified against, author,
   date, and open items. Guides rot at every twice-yearly release; an unverified guide
   says so on page one.

## The reuse-before-build discipline

Before designing or configuring net-new in ANY area:

1. **Check the catalog first** - the practice's reusable-asset catalog
   (wd-practice-ops references/reuse-and-asset-catalog.md) and its configuration-guide
   library: reuse as-is, adapt, or build fresh - and when building fresh, record WHY the
   existing assets did not fit.
2. **Check Workday's own material** - the Administrator Guide, setup-task documentation,
   release notes, and Workday Community for the area (access-gated content is referenced
   by link, NEVER copied into shareable artifacts).
3. **Contribute back at closeout** - a solved problem that stays in one engagement's
   folder is a problem the practice will pay to solve again. Genericize per the
   IP-provenance rule (wd-extend-lifecycle references/ai-data-governance.md - patterns
   are reusable; client facts and work product never cross clients) and file it in the
   catalog with maturity recorded honestly.

## Building a firm library over time

- **Harvest at every closeout** - the reusable-asset gate in the suite's quality-gate
  registry already requires it; configuration guides are its highest-value output.
- **One guide, one owner, one currency date** - an ownerless guide decays fastest; track
  re-verification against each Workday release like a milestone (wd-extend-dev
  release-impact conventions).
- **Index the library** - a one-line-per-guide index (area, products, last-verified
  release, owner, maturity) so "do we have guidance for X?" is a lookup, not an
  archaeology dig.
- **Keep the library in the firm's private layer** - the library is competitive IP. This
  suite's shareable skills carry the FORMAT (this file); the CONTENT stays in the firm's
  own store or private skill.
