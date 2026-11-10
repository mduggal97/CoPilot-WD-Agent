# Moves 2-4 - Whitespace, sizing & validation, then score and rank

Once a signal clears the strength bar (opportunity-signals.md), work it into a decision-grade assessment:
what already exists, how big it is, whether it is real, and how it ranks against the other ideas.

## Move 2 - Whitespace & competition

Map what a buyer could use INSTEAD of your app - then find the gap:
- **Direct competitors** - existing marketplace apps / SaaS in the category. For each: what it does, pricing,
  reviews (the complaints ARE your differentiation), and momentum (updated recently? growing installs?).
- **The platform itself (native).** Does the platform vendor already do this, partially or on its roadmap?
  This is the make-or-break risk for a marketplace app - the **Evergreen risk** (a platform-native feature can
  strand a paid app overnight). Check the vendor's roadmap/release notes; weight this heavily. (For Workday,
  the GA/roadmap signal lives in wd-extend-dev `release-impact.md`; the same build-vs-native logic is
  wd-discovery `solution-options.md`.)
- **Substitutes** - the spreadsheet, the manual process, the consultant, the point tool. "Do nothing / do it
  by hand" is the most common competitor; your app must beat it clearly.
- **The gap** - state the specific under-served need and your wedge (better UX, a niche the incumbents ignore,
  a price point, an integration, a compliance angle). No credible gap -> no opportunity, stop here.
- **Moat** - once you win, what keeps you winning? (data, integrations, switching cost, brand, distribution).
  A gap with no moat gets copied.

## Move 3 - Size & validate

**Size it (order-of-magnitude, sourced - not false precision):**
- **TAM** (total addressable) - everyone who has the problem. **SAM** (serviceable available) - those you can
  actually reach on the target platform / segment. **SOM** (serviceable obtainable) - a realistic 1-3 year
  share. Build TAM bottom-up where you can (# of target accounts x plausible price) - it is more defensible
  than a top-down "1% of a huge number."
- **Monetization** - pricing model (per-seat / per-tenant / usage / flat), a plausible price anchored to the
  value or the workaround cost it replaces, and the platform's revenue share / fees (platform-fit).

**Validate it (cheap evidence before expensive build):**
- **Buyer & JTBD** - name the ICP, the buyer vs the user, and the job-to-be-done ("when [situation], I want
  to [motivation], so I can [outcome]"). Vague buyer = weak opportunity.
- **Evidence ladder (cheapest first):** existing workaround spend -> problem interviews (5-10 target buyers) ->
  a landing-page smoke test (does the pitch get sign-ups?) -> a design partner / LOI / pre-order. A **go**
  decision should rest on at least a rung or two, not conviction alone. State what evidence you have and its strength.
- **Painkiller test** - re-confirm severity x frequency from real buyers, not your own enthusiasm.

## Move 4 - Score & rank (one scorecard for all ideas)

Compare ideas on ONE scorecard so the decision is transparent, not loudest-voice. Score each factor 1-5:

| Factor | 1 (weak) ... 5 (strong) |
|---|---|
| **Demand / pain** | vitamin, rare -> painkiller, frequent, budgeted |
| **Whitespace / differentiation** | crowded, no wedge -> clear under-served gap + a wedge |
| **Market size (SOM)** | tiny -> large obtainable share |
| **Willingness to pay** | none / free-expectation -> proven spend, healthy price |
| **Reuse leverage** | net-new build -> large head start from the reuse catalog |
| **Feasibility** | hard/uncertain to build & maintain -> straightforward, in our wheelhouse |
| **Platform fit / distribution** | poor fit or heavy fees -> strong marketplace fit + reach (platform-fit) |
| **Strategic fit** | off-strategy -> reinforces the practice's focus & references |
| **Evergreen risk (REVERSE-scored)** | platform likely to ship it natively soon -> unlikely, durable |

Rank by weighted total (weight Demand, Whitespace, and Evergreen risk highest - they most often decide
success). Effort/feasibility is a tiebreaker, not the sort key - reuse recurrence decides, ease does not.
The output is a ranked shortlist; the top one(s) go to platform-fit + the opportunity brief for a go/no-go.
