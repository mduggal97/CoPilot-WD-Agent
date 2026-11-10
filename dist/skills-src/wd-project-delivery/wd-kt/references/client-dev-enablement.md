# Client-Developer Enablement

The proven pattern for handing code ownership of an Extend app to a client
developer. The canonical precedent is a delivered app that a client-org developer
actively edits (see Engagement inputs). Goal:
the client dev can make, build, and deploy changes safely - and the delivery team can still
collaborate without clobbering their work.

> **Enablement is one half of a pair.** *Who* the client's technical counterparts are
> (integrations / Extend / Prism / reporting / security), *what access* each needs, and
> *when* to provision it live in the staged model at wd-extend-lifecycle
> `references/customer-technical-roles.md` - that's a day-one, plan-driven artifact.
> This skill owns the *make-them-productive* half: run the NS->U->D->R ladder + teach-back
> per role, on the tracks that model lists (Extend/Integrations certs, Prism sandbox
> practice, the Security Partner's grant runbook). Provision early per that model so a
> counterpart has runway to learn before their workstream demands output.

## 1. The change-list workflow

Once a client developer is active on an app, the firm's default is to **deliver changes
as a list for the developer to implement, not to edit directly**. Each item states:

- **Page/file** - exactly where (page name, script, orchestration).
- **What** - the concrete change (before -> after where useful).
- **Why** - the intent, so the developer can adapt if the file has drifted.

wd-extend-dev owns the mechanics of this workflow (pull-latest + diff, list format,
when direct edits are still allowed). The KT job is to make the client dev fluent in
*receiving* change lists: walk the first list together, let them implement it, and
review the result jointly.

## 2. Joint working sessions on their first changes

Don't hand over a repo and a wiki. Schedule 2-3 joint working sessions where the
client developer makes their **first real changes** with the delivery team on the call:

1. **Session 1 - delivery team drives, dev navigates.** Full code walkthrough: app structure,
   pages, orchestrations, business objects, where each design-doc decision landed in
   code. Record it.
2. **Session 2 - dev drives, delivery team navigates.** The developer implements a small
   change-list item live; the delivery team narrates the build loop and catches habits early.
3. **Session 3 - dev solo, delivery team reviews.** The developer implements an item alone,
   then walks the delivery team through the diff. This is the **teach-back** that counts toward
   KT sign-off (see kt-sessions.md).

## 3. Verify KT-level comments before handoff

KT-level comments (block-by-block intent, descriptive variable names - standard
defined and applied by wd-extend-dev DURING development) are the **durable KT
artifact**: they're what the client dev reads at 5pm on a Friday when nobody from
the delivery team is reachable.

Before handoff, sweep **every script and orchestration** in the app:

- Every non-trivial block has a comment explaining intent (why), not restating code.
- No single-letter / throwaway variable names where a real name conveys meaning.
- A developer who has never seen the file can follow it cold.

Any file that fails goes back through wd-extend-dev's workflow for a comment/naming
pass before the code walkthrough session - walking through uncommented code wastes
the session on narration that should be in the file.

## 4. Client-dev environment onboarding checklist

Get the developer to a working build loop (details in wd-extend-dev; this is the
KT-side checklist to run with them):

- [ ] Workday developer account in the client org with Extend developer access.
- [ ] `wdcli` installed and authenticated against the client tenant
      (`wdcli auth login`). Note: **auth expires** - teach the re-auth step now, not
      when their first download fails.
- [ ] `wdcli app download <appReferenceId> <dir>` pulls the app successfully - this
      is both their "clone" and the sync mechanism.
- [ ] Full build loop demonstrated end-to-end by the developer: download -> edit ->
      validate/build -> deploy to the dev environment.
- [ ] They know where the design doc, user guide, deployment guide, and process flow
      live (the app's document folder) and that the design doc's Open Items tab is
      the change backlog's context.

## 5. Co-ownership etiquette

While the delivery team and the client dev share a codebase, both sides follow the same rule
(defined in wd-extend-dev, taught here):

- **Pull latest + diff before EVERY edit.** `wdcli app download` the deployed app and
  diff against your local copy to catch the other party's in-flight changes - never
  clobber. On any co-owned app this is mandatory in both directions.
- Direct delivery-team edits to a client-dev-owned app happen only when the delivery lead explicitly asks;
  otherwise deliver a change list.
- If parallel copies exist (e.g. a frozen delivery-team tree alongside the client org's
  live tree), agree explicitly which tree is authoritative and when changes get
  copied across - divergence is fine only when it's intentional and dated.

## Handoff is done when

- The developer has completed a solo change (Session 3 teach-back) end-to-end.
- The comment sweep passed on every script/orchestration.
- The onboarding checklist is fully checked with the developer's name and date.
- These three facts are recorded in the KT sign-off artifact (kt-sessions.md).

## Engagement inputs (pull from project memory; never hardcode)
This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- The current client / engagement.
- The client-developer precedent: a delivered app (with its app reference ID) that a
  client-org developer actively edits - the canonical example for the change-list and
  co-ownership workflows above.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
