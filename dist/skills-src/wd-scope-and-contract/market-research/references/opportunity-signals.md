# Move 1 - Opportunity signals: where demand shows up, and how to read it

An opportunity starts as a signal that a real need is under-served. Gather signals from several angles (one
source lies; a pattern across sources is real), then judge signal STRENGTH before investing further.

## Signal sources (strongest first)

1. **Your own delivery pattern - the strongest signal.** A capability the practice **keeps custom-building for
   client after client** is demand that already paid for itself, with a reuse head start. Start at the
   reusable-asset catalog (wd-practice-ops `reuse-and-asset-catalog.md`): high reuse-count + repeated
   from-scratch rebuilds = a productization candidate. Also mine won/lost deals and RFPs for the same ask
   recurring across prospects. To pull that won/lost + precedent signal reliably from the CRM (dead fields
   return confident false zeros), use bow-sales-enablement `references/crm-pursuit-research.md` (the
   verify-fields method; connector-gated).
2. **Marketplace gaps.** Browse the TARGET marketplace's catalog (Workday Marketplace / Built-on-Workday app
   list and the Workday DevRel catalog as a "what exists / what Workday samples" signal; or Salesforce
   AppExchange / ServiceNow Store / MS AppSource). What categories are thin, dated, or have only weak entries?
   A crowded category with poor reviews is often a better opening than an empty one (empty can mean "no
   demand" OR "the platform forbids it" - check which).
3. **Review sites & communities.** G2 / Capterra / TrustRadius reviews (read the 2-3 star reviews - they name
   the unmet need), the platform's user community/forums (Workday Community, subreddits, Slack/Discord groups),
   and support-forum recurring questions. Look for "I wish it could..." and workaround threads.
4. **Buyer pain in the wild.** Job postings (a role created to do X manually = pain worth automating), analyst
   notes (Gartner/Forrester category coverage + gaps), earnings-call/strategy mentions, and conference
   session topics (what the platform vendor and partners are pushing signals where budget is moving).
5. **Regulatory / platform change.** A new regulation, a platform release that opens an API or a new surface
   (e.g. an AI/agent capability, a new marketplace program), or a deprecation - each creates a time-boxed
   window where a well-timed app meets fresh, urgent demand.

## Reading a signal - is it real?

For each candidate need, judge:
- **Recurrence** - does it show up across multiple independent sources / buyers, or just one loud voice?
- **Severity** - painkiller (frequent, expensive, risky, or compliance-driven) vs vitamin (nice-to-have)?
  Only painkillers reliably get budget.
- **Who feels it** - a clear buyer/user segment (an ICP), or diffuse? A sharp segment is easier to reach and sell.
- **Now-ness** - is there a reason to solve it NOW (a change, a deadline, rising cost) or has it been tolerable
  for years? Now-ness beats a bigger-but-static problem.
- **Willingness to pay** - is anyone paying for a workaround today (staff time, a spreadsheet, a point tool)?
  Existing spend is the clearest willingness-to-pay evidence.

Rate each candidate signal High / Medium / Low on strength; carry only Medium+ into whitespace/sizing
(assess-and-prioritize.md). Record the source + date for every claim - this is the evidence trail the brief
and any later marketing claim (bow-sales-enablement claims register) will draw on.

## Governance - research ethically and on public sources

- **Public / permitted sources only.** Public web, published reviews, the marketplace's own catalog, analyst
  material you are licensed for, your own delivery data (genericized). Do NOT scrape behind a login, harvest a
  competitor's confidential material, or use another client's confidential work product as market intel
  (the IP-provenance rule, wd-extend-lifecycle `ai-data-governance.md`).
- **Cite everything** - a source + date per fact; this is the same verify-before-promote discipline the rest
  of the suite uses. An unsourced market number is a guess, and a guess that reaches a client or a listing is
  a liability.
- **No confidential-data ingestion** - the AI/data governance gate applies to anything you feed a tool.
