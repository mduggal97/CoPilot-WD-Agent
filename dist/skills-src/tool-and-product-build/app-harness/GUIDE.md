---
name: app-harness
description: >-
  Run the build with discipline when developing a hosted tool with Claude Code - the "how we
  build" layer, distinct from the "what we host" layers. Owns complexity routing (Simple:
  implement; Standard: plan first; Complex: stop for a human design), the stateless-worker model
  (a supervisor dispatches one-shot workers that coordinate through git and issues), read-only
  reviewers, commit-at-every-green, mutation-proof testing, and guard-hook templates
  (secrets/client-data, branch guard, Bedrock/AWS-SSO credential preflight). START HERE to set up
  a repeatable Claude Code build loop or add guard hooks. TRIGGERS: "build discipline", "how
  should the agents work", "supervisor", "complexity routing", "review loop", "guard hook",
  "pre-commit hook", "secrets hook", "client-data guard", "branch guard", "model tier". Hands off
  to app-architecture, app-hosting and app-agentic for what gets built. Modeled on the jackal,
  ed3d and superpowers harnesses - patterns only, not copied.
---

# Hosted App Build Harness & Guard Hooks

This skill is a thin index over a build-discipline layer for developing hosted tools with Claude
Code - modeled on the jackal harness (a private fork of ed3d-plugins / obra-superpowers). It governs
**how the build runs**, not what gets hosted. Read the reference for the piece you need.

## The single best idea to adopt - complexity routing

Route every task by complexity before doing any work:

- **Simple** - implement directly, one review pass, no design or plan doc.
- **Standard** - plan into phases first, then implement, then review.
- **Complex** - STOP. Require a human-run design before any autonomous work. Never build a Complex
  task straight through.

This one table prevents both over-ceremony on trivial changes and under-thinking on risky ones.
Full model in [references/complexity-routing.md](references/complexity-routing.md).

## The orchestration invariants (steal these)

- **One supervisor, stateless workers.** A single long-lived conversation holds all state and
  dispatches one-shot workers; workers coordinate only through git (worktrees, commits) and issues -
  never shared memory. **Workers never spawn workers** (belt-and-braces: disallow the Agent tool,
  say so in the prompt).
- **Every dispatch names its model tier explicitly** - a `model=null` dispatch is a defect, not a
  style choice. Cheap models (Haiku) for mechanical slices; strongest (Opus) for design/deep review.
- **Reviewers are read-only** - no Edit/Write, no tree-mutating git. A reviewer that "fixes" a file
  another agent is committing corrupts the build.
- **Honest stopping point + commit at every green** - a token/context death should leave resumable
  work on disk, never a half-written tree.
- **Mutation proof** - prove a test can actually fail (revert the impl, quote the failure, restore)
  before trusting a green run.

## The guard hooks - reusable templates

Three pure-Python, zero-dependency, fail-open hooks, adaptable to any repo. Read
[references/security-hooks.md](references/security-hooks.md). The highest-value one here:

- **Secrets / client-data bash guard** - tokenize a bash command, split pipelines, deny/ask on
  secret-or-client-data leakage (echo of a secret, `cat .env`, token-in-URL, curl exfil). This is
  the clean template to **upgrade the existing wd-* client-data git guard** - swap the secret-word
  set for client/tenant/PII patterns.
- **Branch guard** - deny Edit/Write and commit/push on `main`/`master` and in the shared primary
  worktree, so "the PR is the only completion path" is enforced, not just documented.
- **Credential preflight** - warn before a long agent dispatch if the shared AWS SSO token is near
  expiry (Bedrock fleets share one token; its expiry kills every in-flight agent).

## Reference map - read what you need

| You need | Read |
|---|---|
| **Complexity routing + orchestration discipline** - the routing table, stateless-worker model, model tiers, read-only reviewer, honest stopping point, mutation proof, conflict gate | [references/complexity-routing.md](references/complexity-routing.md) |
| **The guard hooks** - the three hook templates, the hook JSON wiring, the deny/ask/fail-open contract, how to adapt the secrets hook into a client-data guard | [references/security-hooks.md](references/security-hooks.md) |
| **Conformance checklist** - grade a hosted agentic tool against the AWS Well-Architected Agentic AI Lens (6 pillars) and the OWASP Top 10 for LLM Apps (LLM01-10), with a per-item "where we address it / gap" pointer and a sign-off block. Run before a tool ships | [references/conformance-checklist.md](references/conformance-checklist.md) |
| **Testing the app itself** - the test pyramid for a hosted tool (unit / integration / contract / E2E-UI via Playwright / UAT), the pipeline Test stage, and the boundary vs app-agentic evals (code-works vs agent-answers-well) | [references/testing.md](references/testing.md) |
| **GitHub Actions as a CI/CD alternative** - evaluation vs CodePipeline (cost, OIDC security, Enterprise controls, runner/proxy tradeoffs) + working recipes (PR CI, OIDC, ECR push, App Runner deploy, prod approvals) | [references/github-actions.md](references/github-actions.md) |

## Boundaries

- **What actually gets built (architecture/hosting/agent code):** app-architecture, app-hosting, app-agentic
- **The GENERAL forking + model-routing decision** (fork any work to subagents/sessions/models, up or down) is **session-orchestration**. This skill's complexity-routing + model tiers are the BUILD-LOOP specialization of that; session-orchestration owns the cross-cutting version for any Claude Code work.
- **The existing wd-* repo client-data git guard** (already built): its home is the wd-* suite repo; this skill's secrets hook is the pattern to *upgrade* it, not a replacement.
- **Workday delivery build discipline (Extend/O4I):** wd-extend-dev workflow rules

## Lifecycle neighbors

Wraps the other three app-* skills - it's the process they run inside, not a build target itself.
Optional: a small tool can skip the harness entirely and just use the architecture/hosting/agentic
skills directly.

**Ship gate for this track (not the Workday `quality-gates.md` registry):** this skill OWNS the conformance checklist (`references/conformance-checklist.md` - AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps) that a hosted tool runs before it ships. The app-* family deliberately does not use the Workday delivery quality-gate footer.

> Modeled on the jackal / ed3d-plugins / obra-superpowers harnesses. **License caution:** upstream
> is CC-BY-SA-4.0 (copyleft, attribution + share-alike) with an MIT superpowers core, while the
> jackal manifests confusingly say "UNLICENSED". Until that is resolved with the jackal author, we
> **model the patterns and write our own** - we copy no source. Do not copy internal identifiers
> (the reference project's GitHub org, SSO role/profile names, author local paths) either.
