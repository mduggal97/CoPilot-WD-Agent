# Writing quality gate - the "AI draft -> release-ready" check (suite-wide)

AI-assisted drafting is fine and productive, but what it produces is a **draft, not a deliverable**. Run
this gate on any client-facing or external text before it is treated as ready: emails, Teams posts,
proposals, SOWs, decks, user/admin guides, CVs, listing copy, LinkedIn posts, meeting recaps. It is the
single owner of the suite's plain-voice / anti-AI-tell standard; wd-comms (tone), wd-estimate
`proposal-content.md`, bow-sales-enablement (its section 4 plain-voice grep is the short version), and wd-kt all
point here.

> Adapted 2026-08-13 from the `ai-writing-quality-gate` skill (a colleague's submission);
> vendor-neutral. The source skill has the exhaustive word tables and file-review code - keep it handy for
> the full list; this reference is the distilled standard the suite enforces.

## Human-in-the-loop - required on every pass (this is the point, not a formality)

After any rewrite/review, before calling it done:
1. **Ask the author to add or rewrite 2-3 sentences in their own words** - the opening, the key
   recommendation, or any claim they personally stand behind. Suggest which sentences most need their voice.
2. **Ask one question:** "What do you know about this audience or situation that isn't in the text?" - it
   usually produces the most valuable edit.
3. **For client/external material:** state plainly this is a reviewed DRAFT; the author must read it end to
   end and verify facts, numbers, names, and commitments. The gate checks style; it cannot verify facts.
4. **Never present output as send-ready.** This is a quality/accountability control, not a "make it
   undetectable" tool.

## Hard rule - no em dash

The em dash (U+2014) and the "--" substitute never appear in output (the suite is ASCII-clean anyway).
Replace by context: list/elaboration -> colon; contrast -> comma; aside -> commas or parentheses; two
clauses -> period or semicolon; number/date range -> hyphen. Default to a period when unsure.

## Kill the AI tells

**Words (replace on sight - Tier 1, representative; full list in the source skill):** delve, leverage
(verb) -> use, robust -> strong, comprehensive -> thorough, seamless(ly) -> smooth, utilize -> use,
pivotal -> key, underscores -> shows, meticulous -> careful, game-changer -> say what changed, deep
dive/unpack -> examine/explain, holistic, actionable -> practical, impactful -> effective, learnings ->
lessons, best practices -> what works, in order to -> to, serves as -> is, boasts -> has, testament to ->
shows, landscape/realm/tapestry (metaphors) -> name the actual thing. **Tier 2 (flag in clusters of 2+):**
harness, navigate, foster, elevate, streamline, empower, facilitate, nuanced, crucial, myriad, plethora,
ecosystem (metaphor), transformative, cornerstone, paramount, burgeoning, overarching. **Tier 3 (only at
high density):** significant, innovative, effective, dynamic, scalable, compelling, unprecedented,
remarkable, sophisticated, world-class.

**Structure and phrasing:** cut "it's not X, it's Y" (max one, only if it earns it); hollow intensifiers
(genuine, truly, quite frankly, it's worth noting); hedging (perhaps, could potentially); transition filler
(Moreover/Furthermore/Additionally, "In today's...", "That said"); significance inflation ("marking a
pivotal moment..."); chatbot artifacts ("Great question!", "I hope this helps!", "Let me know if...");
"Let's explore/break this down" openers; rhetorical-question openers; generic conclusions ("The future
looks bright", "Only time will tell"); vague attributions ("studies show" with no source); copula avoidance
(serves as/features/boasts -> is/has); the compulsive rule of three; inline-header bullet lists.

**Rhythm (the #1 detection signal):** vary sentence length (mix 3-8 word punches with 20+ word flows;
fragments are fine) and paragraph length. Read-aloud test: if a TTS engine could read it without sounding
odd, it is too uniform. Don't over-polish away all personality.

## Context profiles (strictness dial)

Auto-detect or take a hint; default to `blog` strength.

| Profile | Loosen |
|---|---|
| linkedin | 1-2 emoji end-of-line OK, one rhetorical hook, punchy fragments |
| blog (default) | full strength |
| technical-blog | technical terms + some hedging OK (robust/comprehensive/leverage pass); still kill delve/tapestry/game-changer |
| investor-email | tighten everything; promotional language + significance inflation are the biggest risks |
| docs | relax em-dash/bold/bullets (structure aids clarity) |
| casual (Slack/Teams) | only the worst offenders (P0) |

## Modes (decided by input, not asked)

- **Pasted text, no prefix -> rewrite:** return only the clean result, no preamble.
- **"review this:" or a file with no instruction -> review:** inline `~~original~~ **replacement**`, or for
  Office files a tracked-changes output file (python-docx/python-pptx/openpyxl - run code, don't hand-markup
  in chat). Return the full text, unchanged parts passing through.
- **"detect:" -> detect:** list every tell grouped P0/P1/P2, no rewriting.
- File + explicit "humanize/clean this file" -> in-place rewrite preserving formatting, save a new file.

**Severity:** P0 = chatbot artifacts, cutoff disclaimers, unsourced attributions, significance inflation
(fix now). P1 = Tier-1 words, template phrases, "Let's" openers, bold overuse (fix before publishing).
P2 = generic conclusions, rule of three, uniform paragraphs (fix when time allows).

## Rewrite-from-scratch trigger

If 5+ word hits across categories AND 3+ structural patterns AND uniform rhythm: patching won't save it -
state the core point in one sentence and rebuild.

After any rewrite, do a SECOND PASS: re-read your own output for tells that survived the first sweep
(they routinely do), fix them, and note the pass ran. If it is clean, say so.

## Factual fidelity (distinct from the AI-tell sweep)

The word/pattern sweep checks how it READS; this checks whether it is TRUE-to-source (adapted from an
internal firm writing skill, 2026-08-28):

- Never invent a fact, figure, quote, date, contract clause, cause, or commitment. If a value is not
  known, mark it (yellow-TBD in a doc; a flag in chat) - never assert one.
- Walk every number, benchmark, and regulatory statement to a source. Unsourced -> source it or cut it.
  A benchmark more than ~2-3 years old is stale - refresh or drop.
- Replace blanket "always/never" claims with a default plus its exceptions.

The gate checks style and sourcing traceability; it cannot verify the facts themselves - the author
still owns the end-to-end read for accuracy. Full content/argument review: deliverable-review.md.

**Quality-gate rule:** this gate is itself a registry entry in `quality-gates.md`; run it before any
deliverable is presented as final, and report that you did.
