# Discovery & Design Brief - the front-end before you scaffold

Modeled on the reference architecture. Patterns only - every example below is
invented and generic. No client names, no real systems.

This is the DESIGN FRONT-END for a hosted tool. It sits BEFORE the module
contract: the small set of questions you answer, and the one-page brief that
answer set becomes, so that scaffolding starts from a decision instead of a
guess.

It is the Track-2 counterpart to Track-1's `wd-discovery` + `wd-design-doc` - but
right-sized for a hosted, non-Workday tool. No 16-tab workbook, no Workday FDM /
security / BP framing. A builder fills this in before writing code, and the output
feeds straight into module design (`module-contract.md`).

## Table of contents

- [Why a front-end at all](#why)
- [When to run this - and how heavy](#when)
- [The questions to answer](#questions)
- [The one-page design brief - the output shape](#brief)
- [How the brief feeds the build](#feeds)
- [Anti-patterns](#anti-patterns)
- [What to remember](#remember)

---

<a name="why"></a>
## Why a front-end at all

**Scaffolding is cheap; the wrong boundaries are expensive.** The module contract
makes a tool liftable and scalable, but it cannot tell you WHICH modules exist,
who they serve, or what data they own. Those are discovery answers. Skip them and
you scaffold a module shape you rip up a week later.

**The trap this closes:** on a hosted tool with no Workday template forcing the
questions, it is easy to jump straight to code. The Workday track has
`wd-discovery` and a design-doc workbook standing in the way on purpose. Track 2
had nothing between "good idea" and "scaffold a module." This file is that
something - deliberately light, so it gets used.

**The bar is right-sizing, not thoroughness for its own sake.** A one-module
internal tool might fill this in twenty minutes. A multi-module, agentic,
customer-sold product deserves a real session. Match the effort to the stakes -
the same instinct `wd-discovery` uses when it picks a playbook.

---

<a name="when"></a>
## When to run this - and how heavy

**Run it before the first scaffold** on any new hosted tool, and again before
adding a materially new capability to an existing one (a new module is a small
re-run of the data-model and integration questions, not the whole brief).

Right-size by reading the stakes first:

- **Internal accelerator, one module, no agent** - answer the questions inline in
  a few paragraphs; the brief is a half page. Do not ceremony it.
- **Customer-sold or multi-module or agentic** - hold a real working session, get
  the answers written and reviewed, and treat the brief as a signed-off input.
  This is also where `product-strategy` (internal-vs-external disposition) and
  `market-research` (is there demand) belong - upstream of, or alongside, this
  brief. Do not design a customer product without that disposition call made.

KT note: the internal-vs-external call is NOT this file's to make - it sets a very
different bar (support, SLA, security, TCO) and `product-strategy` owns it. This
brief ASSUMES that call is made and records it as a given at the top.

---

<a name="questions"></a>
## The questions to answer

Nine areas. Each is a short prompt, not a form to pad. Answer only as deeply as
the stakes justify.

### 1. Problem / opportunity

**State the problem in one or two sentences** - the pain or the opening, not the
solution.

- What is wrong, slow, manual, risky, or missing today?
- What happens if nobody builds this - who keeps living with it?
- Why now?

Guard: if you cannot state the problem without naming your solution, you have not
found it yet. "People re-key invoices by hand for hours" is a problem. "We need an
OCR module" is a solution wearing a problem's clothes.

### 2. Users and their jobs-to-be-done

**Name the user types and the job each is trying to get done.** Keep it to the
handful that matter.

- Who uses this - by role, not by name (e.g. "an intake reviewer", "an approver",
  "an admin who configures it")?
- For each, what job are they hiring the tool to do? Phrase it as their outcome:
  "see the exceptions that need me and clear them", not "use the exceptions page".
- Which user type is primary - whose job, if unmet, means the tool failed?

Why jobs-to-be-done and not "features": features fall out of the job. Anchor on
the outcome and the module boundaries almost draw themselves - one job often maps
to one module.

### 3. Scope - in and out

**Write two short lists: in scope, and explicitly out of scope.** The out-of-scope
list is the more valuable one.

- In scope: the capabilities this build WILL deliver.
- Out of scope: the tempting-adjacent things it will NOT - stated, so they are a
  decision, not a silence.
- Note anything deferred to "later, maybe" separately from "no, never" - they are
  different promises.

Guard: an unstated exclusion is a future argument. The out-of-scope list is what
protects the estimate (see `estimating.md`) and, for a sold product, the SOW.

### 4. Data model at a high level

**List the few core entities the tool is about and how they relate.** This is not
a schema - it is the nouns and their shape.

- What are the main things the tool stores or reasons over (e.g. "a request", "a
  reviewer", "an audit event")?
- How do they relate (one request has many events; a reviewer owns many requests)?
- Which entity is the center of gravity - the one most screens revolve around?
- Roughly how much data, and how fast does it grow? (Hundreds of rows or millions
  changes nothing about the contract, but it changes indexing, paging, and
  whether you need retrieval - see NFRs.)

Why now and not at code time: the entities map onto **schema-per-module ownership**
(`module-contract.md` s4). Deciding which module OWNS which entity here prevents
the cross-module row-read that the contract forbids. If two candidate modules both
want to own "a request", you have found a boundary question worth settling before
scaffolding, not after.

### 5. External systems to integrate

**List every system the tool must read from or write to, and which direction.**

- For each: the system, the direction (read / write / both), and what data
  crosses.
- Is it synchronous (the user waits) or a background sync?
- Who owns the credential and the rate limits - and what is the vendor lead time
  to get access? (Access lead time is a classic critical-path surprise; surface
  it on day one, exactly as `wd-discovery` insists for integrations.)

Cross-link: the mechanics of a hosted-tool integration - auth, sync style,
idempotency, retry, rate limits, mapping - are owned by the **saas-integration**
skill (Salesforce / ServiceNow / data platforms and the platform-neutral craft).
This brief only ENUMERATES the integrations and their lead times; saas-integration
is where you design each one.

### 6. Non-functional requirements

**Answer the NFR bar explicitly - these set the whole build's cost and shape.**

- **Auth** - who signs in, via which identity provider, and is there more than one
  audience (internal staff, external customers, service-to-service)?
- **Security / data sensitivity** - what class of data (public, internal, PII,
  regulated)? This drives the whole compliance and hosting bar.
- **Scale** - expected users, requests, and data volume at launch and at a
  believable ceiling. Size to real concurrency, not a round number.
- **Availability** - is this a "business hours, brief outages fine" internal tool
  or a "customers notice a five-minute outage" product? This decides Multi-AZ,
  min-size, and on-call - all real money (see `estimating.md` run-cost).
- **Compliance** - any standard it must meet (SOC 2, HIPAA-adjacent, data
  residency)? For a customer-sold product this is a `product-strategy` bar, not a
  detail.

Guard: NFRs are where "just a small tool" quietly becomes expensive. A tool that
holds PII and must be 99.9% available for external customers is a different build
- and a different price - from the same features behind the VPN for staff. Decide
the bar here, on purpose.

### 7. Does it need to be agentic?

**Decide, deliberately, whether this tool calls a model at all.**

- Is there a step that genuinely needs an LLM (summarize, extract, classify,
  converse, reason over unstructured text)? Or is it deterministic app logic
  dressed up as "AI"?
- If yes: is it a short in-request call, or long-running background work? (The
  second is materially more to build and to run - durable runs, spend caps,
  App Runner throttle - see `app-agentic` and `estimating.md`.)
- If yes: does it need retrieval / RAG over your own data (pgvector), or just the
  model?

Why this is its own question: "agentic" roughly doubles the build and adds an
open-ended run cost. Many "AI tools" have exactly one model call and a lot of
ordinary CRUD. Be honest here - it is the single biggest driver in the estimate.
If the answer is yes, `app-agentic` is the next skill; if no, skip it entirely.

### 8. Success metrics

**Name how you will know it worked - before you build it.**

- One or two outcome metrics tied to the problem (time saved, error rate down,
  volume handled, adoption).
- What is the baseline today, and what is "good enough to be worth it"?
- Who cares about the number - whose decision does it inform?

Guard: a tool with no success metric cannot be evaluated, only maintained. For a
sold product these become value-calculator inputs downstream (`product-gtm`).

### 9. Constraints and givens (the short tail)

**Capture the fixed facts that bound the design.**

- Disposition (internal accelerator vs customer product) - from `product-strategy`,
  recorded as a given.
- Hard deadline or event the tool must be ready for.
- Platform / hosting constraints already fixed (must run on the reference
  App Runner + RDS stack, must be off the corporate proxy, must reuse an existing
  identity provider).
- Team and skills available to build and to run it (you build it, you run it).

---

<a name="brief"></a>
## The one-page design brief - the output shape

The answers above collapse into ONE page. That page is the input to module design.
Keep it to a single screen - if it sprawls, the tool is probably more than one
brief.

```
DESIGN BRIEF - <tool name>
Date: YYYY-MM-DD   Author: <you>   Disposition: internal accelerator | customer product

PROBLEM
  <1-2 sentences: the pain or opening, no solution language>

USERS & JOBS
  <role>  -> <the outcome they hire the tool for>
  <role>  -> <...>            (primary: <which role>)

SCOPE
  In:   <capability>, <capability>, ...
  Out:  <tempting-adjacent thing deliberately excluded>, ...
  Later (maybe): <deferred>, ...

DATA MODEL (high level)
  <entity> --< <entity> (one-to-many), ...     center of gravity: <entity>
  Volume: <rows now / growth>                  -> owning module per entity: <entity>=<module>

INTEGRATIONS
  <system>  read|write|both  <data>  sync|background  lead-time: <known? risk?>
  (design each with the saas-integration skill)

NON-FUNCTIONAL
  Auth: <IdP / audiences>       Data class: <public|internal|PII|regulated>
  Scale: <users / rps / data at launch -> ceiling>
  Availability: <business-hours | customer-grade>    Compliance: <none|SOC2|...>

AGENTIC?  yes|no
  <if yes: in-request | long-running; RAG? yes|no>   -> next skill: app-agentic

SUCCESS METRICS
  <metric>  baseline <x>  target <y>  owner <who>

CONSTRAINTS / GIVENS
  Deadline: <...>   Hosting: <...>   Team: <build / run owners>

-> MODULES (first cut): <module>, <module>, ...   (one per job / owned-entity cluster)
```

The last line is the handoff: a first-cut list of modules. That is exactly what
`module-contract.md` needs as its input - each named module becomes a liftable
unit to scaffold.

---

<a name="feeds"></a>
## How the brief feeds the build

The brief is not a document you file and forget - each section wires into a later
skill:

- **Modules first-cut** -> `module-contract.md`: scaffold one liftable unit per
  named module (one job / owned-entity cluster = one module).
- **Data model + owning module** -> schema-per-module boundaries; settle any
  "two modules want this entity" fight before scaffolding.
- **Integrations** -> the **saas-integration** skill designs each seam; the
  lead-time notes go straight into the plan as critical-path risks.
- **Agentic? + RAG?** -> `app-agentic` (or skip it entirely if no).
- **NFRs (auth, scale, availability, compliance)** -> `app-hosting` sizing and the
  run-cost worksheet; the availability bar sets Multi-AZ / min-size.
- **Scope + drivers** -> `estimating.md`: the module count, integration count,
  static-vs-agentic, and security bar ARE the estimate's drivers.
- **Success metrics + disposition** -> `product-strategy` / `product-gtm`
  downstream for a sold product.

KT note: this is why the brief is worth the twenty minutes even for a small tool -
every answer is an input something else needs. Answer them here once, or answer
them ad hoc five times later, worse each time.

---

<a name="anti-patterns"></a>
## Anti-patterns

- **Solutioning in the problem statement.** "We need a dashboard" is not a problem.
  Push back to the pain until a non-builder would agree it is worth solving.
- **No out-of-scope list.** An empty out-of-scope section means scope is undefined,
  not unlimited. Force at least the obvious exclusions.
- **Skipping the agentic question.** Defaulting to "yes, it's an AI tool" doubles
  the build and adds open-ended run cost for maybe one model call. Decide it.
- **NFRs left as "standard".** There is no standard - PII-vs-public and
  internal-vs-customer-grade are the two biggest cost forks in the whole build.
- **A brief that runs three pages.** That is a sign the tool is several tools.
  Split it, one brief each, rather than one sprawling brief.
- **Treating this as a Workday design doc.** No FDM, no BP, no 16 tabs. This is a
  hosted tool. Right-sized on purpose.

---

<a name="remember"></a>
## What to remember

- **This is the Track-2 front-end** - the light, non-Workday counterpart to
  `wd-discovery` + `wd-design-doc`, run BEFORE the module contract.
- **Nine question areas, one-page brief out** - problem, users/JTBD, scope,
  data model, integrations, NFRs, agentic-or-not, success metrics, constraints.
- **The brief's last line is a first-cut module list** - that is the direct input
  to `module-contract.md`.
- **Right-size the effort to the stakes** - a paragraph for an internal one-module
  tool, a real session for a multi-module or customer-sold product.
- **The out-of-scope list and the agentic question earn their keep** - they are the
  two answers that most protect the estimate and most change the build.
- **Disposition (internal vs product) is a given here, owned by `product-strategy`**
  - record it, do not decide it in this brief.
