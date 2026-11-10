# Solutioning - design the best fit, not the familiar one

Before building a new app or feature, spend real thought on **how** to solve it. The suite documents a deep toolbox precisely so you can reach past the first pattern that would work to the one that's most efficient, most maintainable, and - where it genuinely helps the client - most forward-thinking. The failure mode this guards against is reflexive pattern-matching: copying the last app's shape because it's familiar, when a newer or leaner capability fits the actual problem better.

**This is a design-phase mindset, gated at architecture review** (architecture-review.md asks "was this designed from the full current toolbox, or defaulted to a familiar pattern?"). It is NOT permission to build on unproven ground - pair every ambitious choice with the GA-fallback discipline (release-impact.md) and the provenance tiers (build-verified > sample-verified > doc-sourced).

## How to approach a new build

0. **Open the domain playbook FIRST.** If the build touches a functional area (HCM, time/absence, talent/learning, comp, benefits, payroll, financials, student), read that domain's playbook in the **wd-solution-playbooks** skill before designing. It hands you the configuration objects, the SOAP web services / RaaS / WQL sources that already read-write the domain, the delivered connectors and EIB shapes, named donor apps/integrations, and the design gotchas the domain will spring - so you canvass real building blocks instead of inventing an integration that already exists.
1. **Start from the problem and the user, not a template.** What outcome does the client actually need, who touches it, what's the data + volume + security shape? Let that drive the solution; don't retrofit the problem into a pattern you already know.
2. **Canvass the whole toolbox (below) - deliberately.** For each build, ask which capabilities *could* serve, including the modern/cutting-edge ones, before settling. A capability you don't know exists is one you can't choose.
3. **Prefer the efficient and native option.** A native widget over a hand-rolled workaround; a Graph combined mutation over N sequential calls; bulk/set-based over per-record loops; suborchestration decomposition over a monolith; externalized WQL/graphquery over inline. Efficiency is a design choice, not a cleanup step.
4. **Question the default.** Does this even need a custom UI, or would a home card / agent / A2UI chat surface serve? Does this need an orchestration, or is it plain BO REST / a Graph mutation from the page? Is Extend the right tool at all (that's wd-discovery `solution-options.md`)?
5. **Weigh the forward-thinking option honestly.** The newest surfaces (native agents, AI Gateway, Graph, Prism-in-Extend, MCP) can be genuinely better answers - or overkill that adds risk. Reach for them when they solve the problem *better*, not to be novel; always with a GA fallback for anything preview-tagged.
6. **Compose from primitives - do not shop for a precedent.** The strongest solutions come from RECOMBINING knowable platform primitives (BOs, PMD pages, orchestration nodes, WQL/RaaS, Graph mutations, Model BPs, cards, AI Gateway, agents), not from finding an app that already does the thing and cloning it. You should be able to author each artifact from a mental model of the platform - build-from-scratch.md holds the minimal-correct skeletons and the "given a need -> what to author" decision path. Reach for an example to SPARK an option or VERIFY an unfamiliar shape, never as a copy-source. Creative solutions live in the recombination; the more fluent you are in the primitives, the more of the solution space you can actually see.

## The toolbox - options to consider (each a pointer, not a prescription)

Treat this as the menu you canvass at design, not a checklist to include:

- **UI surface** - full PMD page shells and widgets (pmd.md), Chart 2.0 dashboards (charts.md), home/worklet cards, A2UI chat pages, or **no custom UI** (a card or an agent). Consider: does the interaction want a page, a card, a conversation, or an inbox step? Once the surface is chosen, design it to be ENGAGING, not just functional - the craft layer (5 anchors, dashboard question-first ordering, density budget, numeric alignment, state design, accessibility) is [ui-design-principles.md](ui-design-principles.md).
- **Data & logic** - Extend BOs + Model BPs (model.md, model-bp.md); tenant custom objects as a BO alternative; calc fields. **How the data gets loaded in and read back out at each scale (page create / grid / bulk / EIB seed of native data / REST vs delivered-WQL reads) is a design decision** - see data-loading-and-retrieval.md, especially "will the tenant even HAVE the native data this app reads" (a bare dev tenant will not). Confirm that assumption - and any other tenant fact your design leans on - with a programmatic read, not a browser eyeball: the "to confirm X, read Y" recipes are in [tenant-state-verification.md](tenant-state-verification.md).
- **Writes** - BO REST (bulk/PATCH), **Graph combined mutations** (rest-api-catalog.md - atomic multi-op, a real latency lever), SOAP for FDM master data, businessProcess launches. Pick by fit, not habit.
- **Orchestration** - the O4I node vocabulary + flow patterns (orchestration.md): paginated reads, folds, error-handler/rollback, TriggerIntegration, PDF/zip/Excel generation, retry config. Decompose per efficiency.md section 7.
- **Reads at scale** - WQL (incl. JSONPath-filter joins), RaaS, paginated REST; Prism when the volume/blend calls for it.
- **Analytics / data platform** - Prism-in-Extend read (cds_/WQL-addressable) and write (fileContainers->DCT); reporting via `.report` files (prism-and-reporting.md).
- **AI** - three distinct surfaces (external-apis-and-genai.md, custom-agents.md): **AI Gateway `/ml/`** (in-platform ML - sentiment/skills/docint/forecast, no egress, cheap to add value), external LLMs (page-direct or flow-proxy, gated), and **native agents** (.agent/.agentskill, Agent Actions, MCP). Ask: would a small AI Gateway call meaningfully improve this experience?
- **External / integration** - SendHttpRequest, typed AWS nodes, SaaS pulls; Studio/EIB/CC/DT when O4I isn't the fit (studio.md, integration-build.md in the wd-integration-dev skill); the reverse direction (external UI over Extend) and MCP bridge for external-LLM access.
- **Idea catalog** - [app-catalog-registry.md](app-catalog-registry.md) is 50 official apps indexed by *what they demonstrate* - browse it to see **what's possible** and spark a better solution. It is an inspiration source, NOT a copy-source: let it broaden the options you consider, then design in the suite's build-verified voice.
- **Build from primitives (author, don't clone)** - [build-from-scratch.md](build-from-scratch.md) is the minimal-correct skeleton for every artifact (BO, VIEW/EDIT page, AMD/SMD, .task, FlowSync, Model BP) plus the "given a need -> what to author" decision path. This is the resource that lets you compose a solution from nothing instead of hunting for a donor to copy.
- **Domain building blocks** - the **wd-solution-playbooks** skill (per functional area) maps the domain's config objects + web services + RaaS/WQL sources + delivered connectors + named donors. Where the app-catalog-registry shows *technique*, the playbooks show *what already touches this domain* - reach for both.

## API cost dimension (Flex Credits)

Every build choice now has a measurable API cost to the customer. Factor it in at design. The full commercial model AND the qualitative counting rule - what counts, what's free, entitlement tiers, credit pricing, the Extend multiplier, the agent Rate Card, and the non-production rule - lives in the canonical owner, **wd-estimate `references/flex-credits.md`**; read it there rather than re-deriving it here. The design levers that model creates (each a reason to open flex-credits.md, not a restatement of its numbers):

- **Prefer a Workday-built Core Connector when one serves** - it is free at the API layer where Extend apps and non-Workday integrations consume entitlement.
- **The Extend SKU's entitlement multiplier** is a real incentive for Extend over standalone integrations - weigh it when choosing the surface.
- **Wrapping logic in an agent may be commercially better** than raw API consumption, because Agent Actions meter differently - check the Rate Card.
- **Lean on non-production/sandbox for high-volume test runs**, which is cheaper or free for most agents - confirm per-agent in the Rate Card.

Include an API consumption estimate in every design doc and proposal. The question at architecture review is no longer just "does this work" but "what does this cost the customer to run."

## Creativity prompts (run these per build)

- Could a **native widget** replace a workaround I was about to hand-roll?
- Could a **Graph combined mutation** collapse several calls into one atomic request?
- Would the **AI Gateway** add real value here for near-zero cost and no data egress?
- Would **Prism** handle this volume/blend better than in-app BOs + WQL?
- Does this need custom UI at all, or would a **card / agent / A2UI** serve the moment better?
- Is there a **more efficient** shape - bulk instead of per-row, set-based instead of nested loops, one decomposed flow set instead of a monolith?
- Am I choosing this because it *fits* - or because it's what the last app did?

The answer is often the familiar pattern - that's fine when it's genuinely the best fit. The discipline is having *asked*, and being able to say at architecture review why the chosen shape beats the alternatives (the ADR-lite "alternatives rejected" line is where that lands).
