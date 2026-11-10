# Reusable-asset & IP catalog (build once, reuse many)

A governed register of the practice's reusable delivery assets, so a pattern solved on one engagement is
found and reused on the next instead of rebuilt. This is the operational home of the **"prioritize by reuse,
not effort"** principle: rank what to build/templatize/productize by how often the pattern recurs across
clients; effort is a tiebreaker, not the sort key.

## What qualifies as a reusable asset

- **Extend building blocks** - whole apps used as archetypes, and components (pods/cards, business objects,
  Model BP patterns, page layouts).
- **Orchestration (O4I) patterns** - proven flow shapes (two-pass dated import, boomerang+Prism, bulk-create
  join, etc. - the donor-flow library in wd-extend-dev).
- **Integration templates** - Studio/CLAR frameworks, EIB templates, Core Connector/DT setups, XSLT idioms.
- **Cross-cutting patterns** - calc-field selectors, custom-validation matrices, security-role models, naming
  standards.
- **Document/diagram templates & accelerators** - design-doc/wireframe/process-flow templates, scripts, the
  suite's own builders.

## Catalog schema (one row per asset)

| Field | Holds |
|---|---|
| Asset ID / name | stable id + human name |
| Type | app / component / orchestration pattern / integration template / cross-cutting pattern / template / script |
| What it does | one-line purpose + the problem it solves |
| Maturity | prototype -> proven (used on a real engagement) -> productized (Marketplace/BoW) |
| Reuse count | how many engagements have used it (drives the "prioritize by reuse" ranking) |
| Source | originating engagement, **genericized** (no client specifics) |
| Location / link | where the asset lives (repo / workspace / this skill's donor registry) |
| Dependencies | platform features, other assets, GA status (link to release-impact.md GA tracker) |
| Last verified | against which Workday release (assets rot at R1/R2) |
| Owner + known limits | who maintains it; caveats/anti-patterns |

Keep the register in the shared tracker (transport via **wd-smartsheet**); it is a living practice artifact,
not a one-time inventory.

## Reuse decisioning (check the catalog FIRST)

Before building anything net-new, search the catalog for a fit - the **donor-app / donor-flow pattern**
(wd-integration-dev `references/studio.md` example registry + wd-extend-dev's reference apps are the
technical indexes this governs). Then decide:
- **Reuse as-is** (config only) -> fastest; confirm it is verified against the current release.
- **Adapt** (fork + modify) -> most common; record the new variant back in the catalog if broadly useful.
- **Build fresh** -> only when no asset fits or the fit forces more rework than a clean build; note WHY, so the
  gap becomes a future asset candidate.

## Versioning shared components

When more than one live app depends on a shared component, treat it like released software:
- **Semantic versioning** + a change log; a breaking change bumps the major version.
- **Named owner** for the shared component; downstream consumers are listed so a change's blast radius is known.
- **Downstream-impact check** before changing a shared component - the same "what else calls this?" discipline
  as a live-BO field change (wd-extend-dev model.md). A shared asset changed without checking consumers is how
  one fix breaks three apps.

## Contribute-back (definition of done includes "catalogued")

After each build, **harvest** the reusable pieces into the catalog as a closeout step:
- **Genericize/scrub first** - strip client specifics per the share sanitize sweep (README) and
  ai-data-governance.md IP-provenance rule; an asset enters the catalog vendor-neutral.
- Record maturity honestly (prototype vs proven) and the source (genericized).
- A frequently-reused, well-proven asset is a **productization candidate** - route by TRACK: a **Workday
  Marketplace/BoW** product -> **bow-sales-enablement**; a **non-Workday hosted tool/product** (a Track-2
  accelerator - a hosted app/agent) -> **product-strategy** (the internal-tool-vs-customer-product
  disposition + productization lifecycle). Do not assume Marketplace/BoW is the only exit.
- **Track-2 asset fields:** the schema above is Workday-shaped. For a **hosted-tool asset** the Maturity
  ladder is `prototype -> proven (used internally) -> productized (hosted product)`, "Last verified against
  a Workday release" is N/A (record the app-* stack + last deploy instead), and the securing surface is
  IAM/secrets/auth, not Workday domains. Tag each catalog entry with its track so the fields read correctly.

## De-brand naming transform (client-coded name -> reusable functional name)

When a client-coded artifact enters the catalog, its NAME has to be genericized too, not
just its contents. A deterministic checklist (adapted from an internal firm skill,
2026-08-28) keeps this repeatable and prevents meaning loss:

1. **Strip the client/coded PREFIX and leading junk** - the client token, an org short-id,
   a leading numbering/date stub. What remains should read as a functional name.
2. **Light cosmetic canonicalization only** - normalize spacing/casing/separators to the
   catalog convention. Nothing more.
3. **NEVER rewrite the descriptive tail tokens.** The words inside the functional tail
   ("Supplier Invoice Import", "Cost Center Rollup") carry the meaning - a blind
   find/replace on the prefix must not touch them, or the asset becomes unfindable.
4. **Set a recyclability FLAG.** Mark non-recyclable variants - anything named as an
   archive / backup / test / dated one-off copy - so they do not get harvested as if they
   were the canonical asset. A flagged variant stays out of the reuse ranking.

This is the naming half of the genericize/scrub step below; the content-scrub rules
(README sanitize sweep + ai-data-governance IP-provenance) still apply in the same pass.

## Relationship to the rest of the suite

- **wd-extend-dev** holds the technical donor indexes (reference apps, studio example registry, donor flows) -
  this catalog is the governed practice layer ON TOP that adds maturity/reuse-count/ownership/versioning.
- **bow-sales-enablement** is the productization exit for the highest-reuse assets.
- **wd-smartsheet** transports the register; **program-mode** (wd-pm) consumes it for shared-component planning
  across a multi-app program.
- A firm's internal solved-solution library is a private instance of this idea; the neutral catalog method here
  stands alone and names nothing private.
