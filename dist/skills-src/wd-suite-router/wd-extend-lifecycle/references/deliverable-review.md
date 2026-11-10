# Deliverable review - read it as the reviewer, before it ships (suite-wide)

The writing-quality-gate scrubs AI tells; the document/design gates check presentation.
This gate is the third and highest: does the CONTENT hold up in front of the person who
receives it. Run it on any client-facing or senior-facing deliverable - design doc,
estimate, proposal, deck, status/escalation email, KT guide - before calling it final.

(Adapted 2026-08-28 from an internal firm skill (deliverable-qa) + a read-the-room flags
pattern; genericized. The mechanical presentation gate is wd-design-doc document-quality-gates.md;
the AI-tell sweep is writing-quality-gate.md; this is the content/narrative layer above both.)

## 1. Set the bar first (calibrate intensity to purpose)

Ask, or infer from context, which bar applies - it sets how hard to push:
  - internal working draft - "is the direction right"
  - first client share - no gaps that would embarrass us, not yet final
  - senior sign-off needed before it goes anywhere
  - going to the client this week - must be defensible in the room
  - final / paid / production - airtight
Do not grade harder or softer than the declared bar. If none is declared, say so and review
observationally rather than inventing a standard.

## 2. Review in the receiver's voice (pick the lens)

State who receives it, then read as them, not as a generic rubric:
  - Partner / senior leader - Is the story right? Is every claim defensible? Does it sound
    like our best thinking? They read for judgment, not grammar. Most common send-back: the
    "so what" is buried, or a recommendation outruns its evidence.
  - Functional / domain lead - Is it correct against current platform/domain reality, not just
    internally consistent? (Verify against current standards - see 4.)
  - Client - Does it answer the question they have NOW, not the one asked at kickoff? Any
    jargon not yet adopted? Anything that prompts a hard question with no answer in the doc?
  - Peer - Is the direction sound before more effort goes in?
Write feedback as that person would actually say it: specific and direct, not softened to
"overall strong, minor suggestions."

## 3. Pre-mortem - assume it already failed

Assume the deliverable has ALREADY fallen over in the review meeting, and work backward:
  - What does a skeptic attack first?
  - Which assumptions were never validated with the client?
  - What is the single weakest claim or section? Name its exact location.
End with "the one thing the reviewer will push back on hardest" - and pre-answer it. This is
forward-looking (what will go wrong), distinct from an error hunt (what is already wrong) -
do both.

## 4. Verify claims and currency (do not review from memory)

For a functional/technical/regulated deliverable, check the content against CURRENT standards,
not training recall. A code review that skips current platform practice is a syntax check, not
a review. (Factual-fidelity mechanics - never invent, trace every number - live in
writing-quality-gate.md; run them here too.)

## 5. Verdict + specific fixes

Close with one verdict - Ready / Needs work / Not ready - a one-sentence rationale, and a
ranked list where EVERY finding names a location and a specific fix. "This could be stronger"
is not a finding; "the ROI figure on slide 7 has no source - add the citation or cut the
number" is.

## Independence - name it, don't fake it

A review is strongest when a DIFFERENT model runs it with no memory of how the deliverable was
built. For high-stakes or self-authored work, recommend the independent pass: fresh chat,
switch model, paste the deliverable cold, and ask the section-2 reviewer-persona questions. If
the user keeps the review inline, that is fine - but say plainly that an inline pass on your own
work is a self-check, not an independent one. Never present a self-check as independent.

## Floor (client-facing / final work only)

Regardless of a low declared bar, these cap the verdict below "Ready" if any fails:
  1. Confidentiality - nothing that should not leave the firm or reach this client.
  2. Sourced hard claims - figures, benchmarks, and regulatory statements are sourced or
     removed, not asserted; no competitor-firm citation and no named quote / client / logo
     used without a permission record.
  3. Brand- and AI-tell-shippable - passes writing-quality-gate.md.
Internal working drafts are exempt - honor the declared bar as-is.

## Strategic flags - the read-the-room pass (customer-facing artifacts)

For anything going to a CLIENT (deck, proposal, discovery/demo output, high-stakes message),
close with 3-5 blunt flags that prepare the OWNER for the live conversation. Flags ADD context;
they never restate the deliverable. Pick only what genuinely matters this time:
  - Framing risk - where the buyer may read the material differently than intended ("if they
    see themselves as X first, this bullet may feel like we're pushing a position they don't claim").
  - Missing context - foundational facts that shape the talk but are not in the data (geography,
    competitor history, political reality).
  - Owner prep - what to verify before sending; what the meeting will REALLY turn on vs. the
    deck's lead framing.
  - Segment/tier mismatch - where our standard template strains for this account.
Rules: direct not hedged; specific not generic (name the data point + the implication + the
action); every flag ends in a DO (verify / prep / raise). 3-5 total, one tight paragraph each.
No flattery, no filler, no sandbagging - the reader is senior and wants real pushback. If
everything is flagged, nothing is flagged.

## Cross-refs

Cited by wd-comms (client messages), wd-estimate proposal-content, wd-design-doc, wd-kt, and the
bow-sales-enablement GTM outputs as the pre-ship content review. Enforced via the
"Deliverable content review" row in quality-gates.md.
