# Conformance Checklist - grade a hosted agentic tool before it ships

Reference for `app-harness`. This is a **checklist you RUN**, not prose to
read. Before a hosted agentic tool built on the app-* family ships, walk it
against two reputable, independent frameworks and record a verdict per line. Two
frameworks on purpose: one is architecture-quality (AWS), one is threat-model
(OWASP); a tool that passes both is defensible in a way that passing either alone
is not.

The two sources (cite these, do not paraphrase a blog):

- **AWS Well-Architected Agentic AI Lens** - the six Well-Architected pillars
  adapted to autonomous agents.
  https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html
- **OWASP Top 10 for LLM Applications 2025** (current edition as of Sept 2026;
  the 2026 edition is in draft - grade against 2025 until it is final).
  https://genai.owasp.org/llm-top-10/
  and the PDF: https://owasp.org/www-project-top-10-for-large-language-model-applications/

**INSPIRATION, not copy.** The pillar and item *names* below are from those
sources; the control themes and the "where we address it" pointers are our own
mapping onto the app-* family. Verify a line against the source before you
claim it, and where the family has a **GAP**, this checklist says so - an honest
"not covered" is worth more than a green box that is not true.

## Table of contents

- [How to run this](#how-to-run)
- [The security floor the two sources converge on](#the-floor)
- [Part A - AWS Well-Architected Agentic AI Lens (6 pillars)](#part-a)
- [Part B - OWASP Top 10 for LLM Applications 2025](#part-b)
- [Known gaps in the family (as of this writing)](#gaps)
- [Sign-off](#sign-off)

---

<a name="how-to-run"></a>
## How to run this

1. For each line, mark one of: **PASS** (control present and verified),
   **PARTIAL** (present but incomplete - note what is missing), **GAP** (not
   addressed - file it), **N/A** (does not apply to this tool - say why).
2. **Verify, do not assume.** "The family documents it" is not "this tool does
   it." Open the tool's code/config and confirm. A PASS you did not verify is a
   GAP you have not found yet.
3. A tool ships when every line is PASS or a consciously-accepted N/A, and every
   PARTIAL/GAP has an owner and a follow-up. GAPs do not block a *demo*; they
   block a tool that touches a **customer tenant or real data**.
4. Re-run on any change to the tool's tools, prompts, data surfaces, or provider.

---

<a name="the-floor"></a>
## The security floor the two sources converge on

Both frameworks, from different directions, land on the same minimum. If you
remember nothing else, enforce these three - most OWASP items and the Security
pillar reduce to them:

1. **Least-privilege tooling.** An agent gets the narrowest set of tools, each
   with the narrowest permissions, and a capability (call this endpoint) rather
   than a credential. Fewer tools, smaller blast radius.
2. **Input-validate and output-filter.** Treat every tool-delivered / retrieved /
   user payload as untrusted DATA on the way in (frame it, never execute it), and
   validate/schema-check every model output on the way out before it drives a side
   effect or reaches a browser.
3. **Human approval gated to reversibility.** The more irreversible the action,
   the more a human must stand between the model and the effect. Reads and
   reversible writes can be autonomous; irreversible or customer-facing side
   effects require an explicit human yes. This is the same reversibility gate the
   harness applies to the build itself.

Everything below is a specific application of one of those three, plus the AWS
operational/reliability/cost disciplines that keep a passing tool passing.

---

<a name="part-a"></a>
## Part A - AWS Well-Architected Agentic AI Lens (6 pillars)

Source:
https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html
Grade each pillar's key control themes. "Where" points at the family reference
that owns the control.

### 1. Operational Excellence
Running and improving the agent through disciplined operations.

- [ ] **Prompt / agent-spec lifecycle managed as versioned artifacts** - system
  prompts and agent config are data under version control, reviewable in one
  place. Where: app-agentic `agent-loop.md` (AgentSpec model card - frozen,
  `extra="forbid"`, one reviewable object per agent).
- [ ] **Behavioral observability** - every run records why it stopped and what it
  spent. Where: `agent-loop.md` (`stop_reason`, per-call usage rows in the ledger).
- [ ] **Human-in-the-loop governance for risky actions** - a defined gate before
  irreversible/customer-facing effects. Where: app-harness `complexity-routing.md`
  (Complex -> human design; security carve-out) + this file's floor #3.
- [ ] **Repeatable, disciplined build/release** - complexity routing, read-only
  reviewers, commit-at-every-green, PR-only completion. Where: `complexity-routing.md`,
  `security-hooks.md` (branch guard).

### 2. Security
Securing agent identity, tool access, and data flows against injection,
privilege escalation, and manipulation.

- [ ] **Identity at the edge, default-deny** - Entra JWT validated once at the
  composition root; only `/health` and `/api/v1/auth/config` are exempt. Where:
  app-hosting `aws-architecture.md`; app-architecture `module-contract.md`.
- [ ] **Least-privilege tools + capability-not-credential** - agent holds an
  endpoint, not the tool's secrets; MCP auth is a fail-closed seam. Where:
  app-agentic `mcp-hosting.md` (auth seam, trust boundary).
- [ ] **Prompt-injection defense** - tool-delivered/untrusted content framed as
  data, structurally escaped, never executed. Where: `mcp-hosting.md`
  (trust-boundary framing).
- [ ] **Secrets never in plaintext or context** - credentials via secret store,
  a bash guard that blocks leaking them. Where: `aws-architecture.md`
  (RuntimeEnvironmentSecret); app-harness `security-hooks.md` (secrets guard).
- [ ] **Network boundary + private ingress** - reachable only behind the VPN;
  identity and network boundaries both always on. Where: `aws-architecture.md`.

### 3. Reliability
Executing predictably, recovering from failure, degrading gracefully.

- [ ] **Bounded runs, graceful degrade** - turn / tool-call / wall-time caps; a
  stopped run returns None, never a partial/fabricated answer. Where:
  `agent-loop.md` (the three caps, graceful degrade).
- [ ] **Transient-vs-deterministic retry discipline** - retry a throttle/5xx with
  backoff; never retry a validation/access-denied. Where: `agent-loop.md`
  (`_generate_with_retry`, separate retry budget).
- [ ] **Durability across restarts** - long runs return a run id, heartbeat to
  Postgres, resume orphans after a restart. Where: app-agentic `durable-runs.md`.
- [ ] **Independent deploy/rollback** - per-module schema + private migration
  tree, so one module rolls back without another. Where: `module-contract.md`.

### 4. Performance Efficiency
Right-sizing the cognitive pipeline and coordination.

- [ ] **Model tier matched to task** - cheap tier for mechanical/prefilter work,
  flagship reserved for design/deep review; every dispatch names its tier. Where:
  app-harness `complexity-routing.md` (tier table); app-agentic
  `provider-seam.md` (ModelId registry).
- [ ] **Slow model I/O off the event loop** - boto3 (sync) offloaded to a thread
  so one Bedrock call does not block every request. Where: `provider-seam.md`.
- [ ] **Bounded fan-out** - supervisor fan-out has a concurrency cap and a
  knowable total-spend ceiling. Where: `agent-loop.md` (FanoutSpec).

### 5. Cost Optimization
Spend is bounded, metered, and attributable.

- [ ] **Hard spend cap, fail-closed** - reserve-before-call; a breached budget
  raises 429 and the model call never happens. Where: `agent-loop.md`
  (SpendGuard + SpendLedger, "budget not an invoice").
- [ ] **Per-call metering in an auditable unit** - micro-dollar integer ledger row
  per call, keyed to a subject. Where: `agent-loop.md`.
- [ ] **Cheapest adequate tier** - see Performance #1; tiering is a cost control
  as much as a latency one.
- [ ] **No idle premium infra** - App Runner (no idle load balancer/node pool),
  one shared RDS instance with schema-per-module. Where: `aws-architecture.md`.

### 6. Sustainability
Minimize resources consumed per unit of useful work.

- [ ] **Avoid wasted tokens/compute** - caps stop runaway loops; smaller tiers do
  the easy work; no retry storms on deterministic errors. Where: `agent-loop.md`,
  `complexity-routing.md`.
- [ ] **Shared over duplicated infrastructure** - one shared Postgres, one image
  promoted across environments (no rebuild-per-env). Where: `aws-architecture.md`
  (one-image principle), `module-contract.md` (schema-per-module).
- [ ] **In-process before hosted** - do not stand up an MCP server (a whole extra
  service) when an in-process tool suffices. Where: `mcp-hosting.md`.

---

<a name="part-b"></a>
## Part B - OWASP Top 10 for LLM Applications 2025

Source: https://genai.owasp.org/llm-top-10/ (2025 edition). One line per item:
the risk, how the app-* family addresses it and **where**, and an honest note
where it does not.

- [ ] **LLM01 Prompt Injection** - untrusted input steering the model. Addressed:
  app-agentic `mcp-hosting.md` trust-boundary framing (structural escaping =
  the guarantee, authority-phrase neutralizing = defense-in-depth) + human approval
  on side effects (floor #3). Verify per tool that EVERY untrusted-content path is
  framed, not just the MCP one.

- [ ] **LLM02 Sensitive Information Disclosure** - leaking PII/secrets/business
  data. Addressed: app-hosting `aws-architecture.md` (secrets as
  RuntimeEnvironmentSecret, never plaintext/context); app-architecture
  `module-contract.md` (schema-per-module - no cross-module row reads);
  app-harness `security-hooks.md` (secrets/client-data bash guard). Floor #2.

- [ ] **LLM03 Supply Chain** - compromised models, deps, or components. PARTIAL:
  `provider-seam.md` pins model ids in one registry (verify profile ids against
  the account) and `module-contract.md` "scaffold, don't copy" + import-linter
  reduce internal coupling. **GAP:** the family has no explicit dependency-pinning
  / lockfile-audit / SBOM / base-image-scanning control written down. Treat SBOM +
  pinned lockfiles + image scanning as a per-tool requirement until the family
  documents it. See Gaps.

- [ ] **LLM04 Data and Model Poisoning** - manipulated training/fine-tune/embedding
  data. Largely **N/A**: the family uses foundation models via Bedrock/Anthropic
  and does no training or fine-tuning, so the classic poisoning surface is absent.
  The residual surface is retrieval/embedding data - now addressed by
  app-agentic `retrieval.md` (provenance-checked, access-controlled ingestion).
  If a tool adds RAG, this line is live: validate and provenance-check ingested
  content per that reference.

- [ ] **LLM05 Improper Output Handling** - trusting model output as safe
  downstream. Addressed: app-agentic `agent-loop.md` (`validate_terminal`
  rejects a bad terminal payload; graceful degrade returns None, never a partial);
  app-architecture `module-contract.md` (frozen Pydantic contracts on the shell
  boundary; RFC-9457 error bodies). Floor #2 (output-filter). Verify any output
  rendered in the SPA is escaped by the client, not injected as HTML.

- [ ] **LLM06 Excessive Agency** - too much autonomy / permission / tools.
  Addressed: app-harness `complexity-routing.md` (complexity gate + security
  carve-out) + `security-hooks.md` (branch/secrets guards) + least-privilege tools;
  app-agentic `agent-loop.md` (tool-call cap = the side-effect budget; terminal
  tool is the only trusted exit); `mcp-hosting.md` (capability-not-credential).
  Floor #1 + #3. This is the family's strongest area.

- [ ] **LLM07 System Prompt Leakage** - secrets/logic exposed via the system
  prompt. PARTIAL: `agent-loop.md` AgentSpec treats the system prompt as reviewable
  data (so a secret placed there is visible in review) and the hosting one-image
  pattern keeps real secrets server-side out of anything shipped to the browser.
  **No explicit control** forbids putting a secret/credential in a system prompt -
  enforce by review: prompts carry instructions, never secrets. Note as PARTIAL.

- [ ] **LLM08 Vector and Embedding Weaknesses** - RAG/embedding store access
  control, poisoning, cross-tenant leakage. Addressed: app-agentic
  `retrieval.md` documents pgvector on the schema-per-module Postgres (per-module
  schema = no cross-module/cross-tenant reads), retrieved-text-is-untrusted-data
  framing (cross-links `mcp-hosting.md`), and required-citation provenance. Verify
  a specific tool applies the per-module access boundary to its vector store and
  provenance-checks ingested content (LLM04 live surface).

- [ ] **LLM09 Misinformation** - confident wrong output acted on as fact.
  Addressed: app-agentic `agent-loop.md` (graceful degrade returns None, never a
  fabricated/partial answer - "the second is worse than the first when a consultant
  will act on it"); app-harness `complexity-routing.md` (verify-don't-trust when
  relaying delegated work; mutation-proof testing) + human approval (floor #3).
  Application-level grounding/citation for a specific tool's claims is per-tool -
  verify the tool does not present ungrounded output as authoritative.

- [ ] **LLM10 Unbounded Consumption** - runaway cost / DoS / resource exhaustion.
  Addressed: app-agentic `agent-loop.md` (SpendGuard hard budget cap, fail-closed
  429; three distinct caps - turn / tool-call / wall-time; bounded retry budget) +
  `provider-seam.md` / Bedrock throttle handling (transient-retry with backoff).
  Floor - this and LLM06 are the family's best-covered items.

---

<a name="gaps"></a>
## Known gaps in the family (as of this writing)

State these plainly rather than green-boxing them. Each is a candidate follow-up
for the app-* family and a per-tool requirement until then:

- **Supply-chain hygiene (LLM03 / AWS Security).** No documented dependency
  lockfile-pinning, `pip-audit`/dependency-scan, SBOM, or base-image-scanning
  control. Per-tool requirement now; candidate for a app-hosting or app-harness
  reference.
- **Retrieval / vector store (LLM08).** Now covered by app-agentic
  `retrieval.md` (pgvector on schema-per-module Postgres, access boundary,
  citation provenance, trust-boundary framing). Residual per-tool work: apply the
  access boundary to the tool's own store and provenance-check ingestion; a
  RAG-ingestion pipeline-hardening control is still per-tool.
- **System-prompt secret hygiene (LLM07).** No mechanical control that a secret is
  never placed in a system prompt; enforced only by review. Candidate: a lint/guard
  that flags secret-shaped strings in an AgentSpec's `system_prompt`.
- **Output grounding / citation (LLM09).** No family-level pattern for requiring
  citations or grounding on factual output; handled per-tool. Candidate for
  app-agentic if a common pattern emerges.

If a tool's use of the family closes one of these locally, tell the suite maintainer so the family reference catches up.

---

<a name="sign-off"></a>
## Sign-off

A tool is conformant when:

- [ ] Every Part A pillar line is PASS or consciously-accepted N/A.
- [ ] Every Part B item is PASS, or PARTIAL/GAP with a named owner and follow-up.
- [ ] The three floor controls (least-privilege tooling, input-validate/
  output-filter, human-approval-gated-to-reversibility) are verified present.
- [ ] No GAP that touches a customer tenant or real data is left open at ship.
- [ ] Re-run scheduled for the next change to tools, prompts, data surfaces, or
  provider.
- [ ] **Self-QA before handoff (track-neutral gate):** every deliverable this
  tool's build produces - and this checklist itself - passed a correctness pass +
  a presentation-polish pass before it reached a human (no typos/broken links/
  stale values; renders correctly; reads clean). This is the suite-wide self-QA
  gate (wd-extend-lifecycle `references/quality-gates.md` "Self-QA before
  handoff") applied to Track 2 - presentation matters on a hosted tool as much as
  on a Workday design doc.

Reviewer: __________  Date: __________  Tool + version: __________

> Two sources on purpose - AWS for architecture quality, OWASP for the threat
> model. The floor both converge on is least-privilege tooling, validate-in /
> filter-out, and human approval scaled to irreversibility. Grade honestly: a
> named GAP is a finding, a false PASS is a liability.
