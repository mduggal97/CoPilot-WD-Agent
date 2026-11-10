# Proposal & pitch content - selling the work, not just pricing it

A proposal's job is to SELL. The estimate makes it priceable; this reference makes it persuasive. Applies to customer RFP responses AND internal firm pitches (e.g., proposing a new Marketplace/BoW product to Workday Digital practice leadership).

## Structure - executive summary first, then the depth most writers omit

The high-level overview (problem, fit, approach, price) is the executive summary, not the proposal. Executives and buyers want to understand HOW we work before they buy. Include:

- **Methodology section**: our delivery arc (discovery -> design with wireframes/process flows reviewed live -> PoC in parallel with design -> build -> unit/UAT -> Workday production approval -> cutover -> hypercare), what the client sees at each gate, and the artifacts they sign. Show the working rhythm (weekly design sessions burning down open items, transcript-driven doc updates, RAID discipline) - process maturity is a differentiator.
- **Tools & accelerators**: name the toolkit categories - standardized design templates, wireframe/process-flow generators, estimation calibration from delivered apps, AI-assisted development workflow - without handing over the implementation details. The rule: describe what the machine does for the client, not the blueprints of the machine. "We generate complete, client-reviewable wireframes for every screen within days of discovery" sells; shipping our builder scripts does not.
- **Standard inclusions that differentiate - say them explicitly**: every firm-built application includes **KPI & executive reporting** designed in from day one (reports recommended for the specific process being administered, not bolted on later) and **data retention export/purge tooling** for the app's data. Competitors treat both as change orders; we treat them as table stakes - make the proposal say so.
- **Market evidence (ground the sell in reality, not adjectives) - include in EVERY proposal**: bring the relevant market context in from the **market-research** skill - the why-now trend, a demand/benchmark data point, the competitive/whitespace picture, and (for a product pitch) the sizing (TAM/SAM/SOM) plus the honest platform-native / build-vs-buy risk. Every market figure carries a **source + date** and follows the claims-register discipline below - a sourced market fact persuades a buyer or a funding committee; an unsourced one is a liability. If no market research exists yet for the opportunity, run market-research first (even a quick moves-1-2 triage) rather than asserting a market from memory. For a Marketplace/BoW product, the market-research **opportunity brief** IS the market section of the pitch (see the variant below).

## The AI-acceleration pitch (framing matters - two different versions)

- **Internal firm pitch** (product proposals, practice leadership): advocate explicitly for co-building with Claude Code - expedited design and development, the eval'd skill suite, faster PoC turnaround. Internal audiences want the how; being specific builds confidence in the LOE.
- **Customer proposal**: highlight the **expedited timeline to deploy** - never quote reduced hours. Frame: "our AI-assisted delivery methods compress design and build cycles, getting you live sooner." Reduced-hours framing invites rate-shopping and undercuts the value story; time-to-value framing sells outcomes. Keep the LOE/pricing model intact and let acceleration show up as a shorter calendar. **Pricing-model caveat (billing integrity):** this time-to-value framing is a **fixed-fee / outcome** positioning. On **T&M / hourly** engagements, invoices must reflect hours **actually worked** - do not bill the un-reduced estimated LOE for effort AI compressed away; there, acceleration shows up as fewer billed hours and a shorter calendar, and the value story leans on speed and quality, not on billing unworked time.
- **Framing != concealment**: if the client asks directly whether AI was used, or the RFP/contract requires AI disclosure, answer accurately - never deny or obscure the assistance (the disclosure rule lives in wd-extend-lifecycle references/ai-data-governance.md).

## Visuals - proposals without images don't sell

Every proposal includes sharp, professional visuals. Sloppy images read as sloppy delivery.

- **UI mockups**: 2-4 key screens of the proposed app (wd-design-visuals; a clean Balsamiq export or polished HTML/SVG mock - clearly labeled "illustrative concept").
- **Concept/process graphics**: the delivery-arc timeline as a graphic, the future-state flow as a simplified swimlane, an architecture-at-a-glance diagram (what lives in Workday vs outside). Simplify for the audience - the full design-doc swimlane is too dense for a proposal.
- **Illustrative/clipart-style accents**: icons and simple illustrations to emphasize concepts and break up text walls (canvas-design skill or clean SVG). Consistent style throughout - one visual language per document.
- Quality bar: high-resolution, consistent fonts/colors (client branding per wd-comms, or neutral formatting for internal/firm documents), no stretched or pixelated images, every visual captioned with the point it proves.

## Competitive positioning - the "why Extend + the firm" argument library

Use when the pursuit is contested (an ISV product, another SI, an internal build, or do-nothing is in the room). Three layers, in order of strength:

- **Why Extend (platform argument)**: the app is **tenant-native** - Workday security domains and BPs govern it, the data never leaves the tenant (no data egress, no separate vendor's cloud in the audit scope), one platform for IT to run (no new vendor contract, SSO integration, or separate DR story), and Workday's release cadence carries it forward. Against an ISV point solution these are structural, not feature, advantages - lead with them.
- **Why the firm (delivery argument)**: methodology proof over adjectives - show the delivery arc, the design artifacts the client signs, the calibration-backed estimate, and the **standard inclusions competitors charge for** (KPI/executive reporting designed in, data retention export/purge tooling - the Structure section above says these explicitly; in a contested deal, contrast them). Relevant-experience excerpts come from the closeout library (wd-post-go-live references/value-capture.md section 6).
- **Honest Extend-vs-ISV framing (the credibility play)**: name when an ISV genuinely wins - deep third-party content/data the ISV maintains (tax tables, benchmark libraries), very large packaged functionality where configure-not-build is truly cheaper, or needs outside Workday's user population. Conceding the cases we'd lose anyway makes the recommendation trusted in the cases we should win; a proposal that claims Extend always wins reads as a hammer looking for nails.

**Named-competitor discipline**: any claim about a specific competitor (their price, gaps, roadmap) follows **bow-sales-enablement**'s claims governance BY REFERENCE (references/claims-register.md - competitor-sourced facts require sourced, dated, human-supplied input and are never used externally as ours). Do not fork or soften that rule here; unsourced competitor claims stay out of proposals entirely. Competitor intelligence from pursuit debriefs arrives via [references/win-loss.md](win-loss.md) routing.

**Our-own-numbers discipline (same register, same rule)**: the claims-register-resolution rule applies to the firm's OWN quantified-benefit claims too, not just competitor facts. "Saves X hours," "cut cycle time Y%," "N clients live" in a proposal each require a claims-register row (bow-sales-enablement references/claims-register.md) or a delivered-app value snapshot (wd-post-go-live references/value-capture.md section 6) as the source - an unsourced benefit number is a Facts-to-confirm item, not proposal copy.

## Internal product pitch variant (Marketplace/BoW)

When the "customer" is the firm's leadership deciding whether to fund a product: lead with the **market opportunity - straight from the market-research `opportunity-brief`** (the need + demand signals, whitespace/wedge, TAM/SAM/SOM, the score, and the **honest platform-native / Evergreen risk** - a funding committee trusts a pitch that names the risk far more than one that hides it), then the product concept with mockups, two-phase plan (MVP -> integrations) with the LOE per phase and staffing, AI-accelerated build as the margin/speed story, distribution/pricing open questions stated honestly as decision asks. The estimate's role here is investment sizing, not a quote; the go/no-go rationale is the market-research brief's recommendation.

## Standard proposal outputs - three artifacts, not one

1. **The proposal document** (this reference's structure).
2. **The proposal deck** - a selling slide deck, NOT the document reformatted: each slide is a headline that asserts + one dominant visual (mockups, delivery arc, architecture), minimal visible text (<=~20 words beyond the headline), and a guiding **talk track in the speaker notes** (what to say, the point to land, the anticipated question). ~10-12 slides ending in the decision ask and next steps. More visuals than words - the deck is what actually gets presented.
   **The visual bar** (a content-correct deck full of white space does NOT sell - learned 2026-08-03): no slide where content fills less than ~60% of the canvas; scale visuals up to dominate; alternate light and dark full-bleed brand surfaces for rhythm (cover, concept, and the ask go dark and dramatic); use oversized stat numerals, filled icon cards, and color blocks instead of naked text columns; cover and closing feel like a product launch. Render every slide to an image and eyeball it before delivering - composition defects don't show in the XML.
   **Mockups are FRAMED, never bled off the edge** (corrected 2026-08-03 - full-bleed crops that ran off the slide read as broken, not bold): show each screen fully inside a clean bounded frame (subtle card/border in the palette) with margins to the slide edge; no image touches or crosses the slide boundary; never distort aspect. A product tour = **one screen per slide, framed, with 2-4 feature callout cards that SELL the capability** (what it does for the user, not a UI label) - split crowded tour slides into more slides rather than shrinking or bleeding screens.
3. **A UET draft populated from assumptions** - don't wait for certainty: fill the UET (per uet-guide.md) from the estimate's staffing model with every assumption documented in a companion notes file and every cell needing review flagged. An assumption-based UET that pricing can react to beats a TBD.

## Assembly

Draft content per this reference -> Word/PowerPoint via the docx/pptx skills (neutral formatting for firm deliverables). The SOW that follows a win is wd-contracts' territory; scope/assumptions flow from sow-handoff.md.
