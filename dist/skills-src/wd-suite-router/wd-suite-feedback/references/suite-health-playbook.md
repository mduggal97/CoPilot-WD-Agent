# Suite-health playbook - diagnosing and fixing suite-LEVEL problems (maintainer)

Triage mode (in SKILL.md) handles individual feedback records. This playbook handles SYSTEMIC health -
when the suite "covers a lot but is clunky to start", routes a plain question to the wrong skill, drifts,
or strands knowledge that never ships. Run these after a big batch of additions, when the suite feels
off, or on a periodic cadence. Apply every fix through the normal gates (validator + ASCII + leak sweep).

## 1. Is it easy to GET STARTED? (the first mile)

Symptom: "covers a lot but kinda clunky to get started."

- **Check the front door.** Does the README / entry skill LEAD WITH HELP, or with governance? A newcomer
  should hit a 30-second quickstart and a plain "what do you want to do?" - not a wall of gates,
  preflights, and caveats first.
- **Fix = progressive disclosure.** Lead with help; DEFER the quality gates / preflights to clearly
  labeled "session start and ship time" sections lower down. The rigor stays; it just stops greeting
  newcomers at the door. (Worked example: the README opens with a Quickstart; wd-extend-lifecycle opens
  with "What do you want to do?" and moves its gate-companions to a "The rigor" section below.)

## 2. Does it TRIGGER to the right skill? (routing)

A skill fires on its `description`. To measure routing objectively:

- **The triggering eval.** Extract each skill's `name` + `description` (nothing else - that is all the
  auto-router sees). Give a FRESH, context-free classifier ONLY those pairs plus a labeled set of
  realistic PLAIN-LANGUAGE prompts (how a novice actually asks, not expert jargon). Have it route each to
  one skill (or NONE) with a confidence. Score the top pick against the intended skill and track the
  HIGH/MED/LOW confidence profile. **HIGH-confidence-clean is the health metric; a stall (NONE) or a
  mis-route is a failure.** Keep the prompt set + answer key as a harness and RE-RUN after any description
  change - it is the regression guard.
- **Common failure modes and their fixes:**
  - Two skills claim the same everyday verb ("set up the tenant", "test the app") -> add a `Use THIS for
    X; for Y see <sibling>` boundary line to BOTH, and remove the bare verb from the one that should not
    own it (e.g. reframe "tenant setup" to "the tenant-setup recipe").
  - A plain ask has NO owner ("pull a list of employees") -> add the literal user phrasing to the owning
    skill's description so it routes instead of stalling.
  - A description is a keyword WALL (over ~1100 chars) -> trim to a lead clause + the real trigger phrases
    + one boundary line (~600-950 chars). Longer is not better; it dilutes the match.
  - One skill is a "sink" that grabs anything adjacent -> tighten its scope phrasing and add outward
    boundaries to the siblings it over-reaches into.
- **The anti-overfit rule (important).** Do NOT tune descriptions to ace your specific test prompts. Some
  asks are genuinely ambiguous (they legitimately span discover -> design -> build); the CORRECT behavior
  there is a smart one-question clarify, NOT a forced route. Chasing 100% HIGH by memorizing the test set
  mis-routes the infinite set of prompts you did not test. Target: HIGH wherever a decisive answer is
  correct; a good clarify elsewhere. Mark the genuinely-ambiguous prompts in the key so the metric stays
  honest.

## 3. Is knowledge in the SKILLS, not stranded in personal memory?

Symptom: on a fresh install (a new machine, or a colleague who received the zip), things that felt smooth
before now need re-figuring.

- **Cause.** A portable fact (a Workday gotcha, a tool flag, a setup step) got written to the maintainer's
  personal memory instead of a skill. Memory does not ship; skills do. On the maintainer's own machine the
  memory filled the gap, so the friction was invisible until a skills-only load exposed it.
- **Fix.** Periodically sweep memory for PORTABLE reference/feedback items and fold the genericized nugget
  into the owning skill (STRIP every client / tenant / app / personal token first). Mark drift-prone
  memories with a "skills-sweep" flag so a sweep does not miss them; clear the flag once folded.
  Client-specific, working-state, and personal context legitimately STAYS in memory - only portable
  knowledge migrates.

## 4. Has it DRIFTED? (single-owner + consistency)

- A shared fact stated in 2+ places WILL drift. Keep ONE owner file per drift-prone fact (auth, pricing,
  browser mechanics, a security model); everyone else POINTS to it rather than restating. After any change
  to a shared value, grep the whole suite and reconcile every copy.
- Run the mechanical validator (frontmatter name==folder, broken links, ASCII, .py parse, ghost skill
  tokens) plus a client-token leak sweep after any batch of edits.

## 5. Making suite-wide edits safely

- For a large multi-skill change, partition the work so no two editors touch the same FILE. A clean split:
  descriptions live in SKILL.md frontmatter; content lives in `references/*.md` - so a "descriptions"
  workstream and a "content" workstream never collide even within one skill. Cross-skill fixes only ADD a
  pointer line into the owning file.
- Always finish with the validator + ASCII + leak sweep, and MEASURE before/after wherever a metric exists
  (the triggering eval for routing; file/section counts for coverage). "Better" should be shown, not
  asserted.
