---
name: wd-comms
description: >-
  Draft CLIENT-FACING project communications for Workday Extend engagements -
  status emails, Teams posts, escalation notes, decision-needed emails, meeting
  recaps, announcements, go-live comms, stakeholder updates. Trigger on: "draft
  an email to the client", "Teams post", "status email", "escalation note",
  "announcement", "go-live comms", "stakeholder update", "let the client know".
  Owns message content, tone, and per-client branding profiles. For
  firm-internal deliverables (decks, proposals), use neutral formatting; for
  Word/PowerPoint file mechanics use the docx/pptx skills - this skill owns message content, tone, and client-branding
  profiles. Meeting recaps here are authored WITHOUT source input; if a
  transcript, recording, or meeting notes are PROVIDED, wd-pm owns the
  extraction and delegates the recap.
---

# wd-comms - Client-Facing Project Communications

Drafts emails, Teams posts, and announcements sent to **client** stakeholders
on Workday Extend engagements. Every draft should be ready to paste and send
after the delivery lead's read-through - correct names, real dates, no `[TBD]` left behind
unless flagged.

## Workflow

1. **Identify the message type** and pull the matching skeleton from
   [references/templates.md](references/templates.md). Don't freestyle
   structure when a template exists.
2. **Check for a client branding profile** in `references/clients/<name>.md`
   (pattern documented in
   [references/client-branding.md](references/client-branding.md)). Apply its
   terminology, sign-off, and distribution norms. If none exists, draft with
   sensible defaults and tell the user a profile hasn't been captured yet.
3. **If a communications PLAN/matrix exists, inherit from it** - audience,
   channel, sender, cadence, and theme all come from the program-level comms
   plan; `wd-change-adoption/references/comms-and-training-plan.md` owns the
   plan (the who/what/when/channel), this skill writes the individual message.
   Don't reinvent audience or timing a plan already sets.
4. **Draft, then self-check** against the voice standards below.
5. **If a Word document is requested**, write markdown then convert via the
   `convert_md_to_docx.ps1` converter - regenerate it from `references/scripts.md`
   if it isn't on your machine (Windows/Word-COM; ask for a pandoc/python-docx
   variant on other OSes) - or invoke the docx skill for richer formatting needs
   (tracked changes, letterhead, tables of contents).

## Voice and structure standards

**Register.** Professional consulting voice: confident, plain, warm but not
chatty. No hedging stacks ("we think it might possibly"). No exclamation
points in status or escalation content.

**Lead with the ask or the answer.** Busy executives read one paragraph. The
first 1-2 sentences must carry the decision needed, the headline status, or
the key change. Background goes below, never first.

**One topic per email.** If a draft covers two decisions, split it into two
emails. Mixed-topic emails get half-answered.

**Bullets over prose walls.** Any list of three or more items becomes bullets.
Keep bullets to one line where possible; bold the lead word when scanning
matters ("**Timeline:** ...").

**Explicit next steps at the bottom.** Every email that expects action ends
with a "Next steps" block: one line per action, each with an **owner** and a
**date**. "We'll follow up soon" is not a next step.

**Subject lines carry state.** Prefix tells the reader what to do before they
open it:
- `[Action needed by Fri] Approve Cost Center routing design`
- `[Decision needed] Worktag default for CC-386`
- `[FYI] UAT defect summary - week of 8/3`
- `[Resolved] Statement-load timeout fixed in build 14`

**Teams posts are not emails.** Shorter - a headline line plus 3-5 bullets
max. Link the artifact (SharePoint/Smartsheet/design doc) rather than
attaching files. @-mention only the owners of actions, never the whole
channel or "the room". If it needs more than ~10 lines, it's an email.

**No unadopted jargon.** (Plain-language standard owned by wd-extend-lifecycle
SKILL.md.) Application here: never use an Extend/Workday term the client hasn't
already adopted without a one-line plain-English gloss on first use. Examples:
- "an orchestration (the automated behind-the-scenes process that moves the
  data)"
- "a business object (the app's stored record of each request)"
- "PMD page (the screen users see in Workday)"
After the gloss, use the client's own name for it if their branding profile
defines one.

**Honesty in escalations.** State impact and root cause plainly, including
firm-side causes. Options with trade-offs, then one specific ask. Never bury
bad news in paragraph three.

**No sensitive data the recipients aren't entitled to.** Before sending, confirm
the message and any attachment/screenshot carry no PHI/PII/FERPA person detail or
secrets beyond what the named recipients should see - match the audience to the
data's sensitivity, use the least-identifying form where a reference is needed, and
scrub/synthesize screenshots. Owner rule: wd-extend-lifecycle
`references/ai-data-governance.md` section 6.

## Reference map - read what you need

- [references/templates.md](references/templates.md) - ready-to-adapt
  skeletons: weekly status, meeting recap, decision-needed, escalation,
  design-review invite, go-live announcement, end-user "what's changing",
  UAT defect update.
- [references/client-branding.md](references/client-branding.md) - the
  capture-once client branding profile pattern; per-client profiles live in
  `references/clients/<name>.md`. **No client branding profile captured yet** - prompt for the
  source artifacts on the first branded request.

## Lifecycle neighbors

Cross-cutting skill - most other wd-* skills produce artifacts this skill
communicates. Heaviest use at:
- **Status cadence** - wd-pm owns the status data; wd-comms turns it into the
  weekly client status email.
- **Go-live** - wd-deployment owns the cutover mechanics; wd-comms owns the
  announcement and end-user "what's changing" note.
- **Knowledge transfer** - wd-kt owns KT content; wd-comms drafts the
  scheduling, invite, and wrap-up messages around it.
- **Change / adoption** - wd-change-adoption owns the communications PLAN/matrix
  (audience, channel, sender, cadence, theme); wd-comms writes each individual
  message that plan calls for. Inherit from the plan when one exists (workflow
  step 3).

**Before send, run the writing quality gate** on any AI-assisted draft: wd-extend-lifecycle `references/writing-quality-gate.md` (no em dash, AI-tell word/pattern sweep, human-in-the-loop). This skill owns client-message TONE; that gate owns the anti-AI-tell release check shared across all deliverables.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
