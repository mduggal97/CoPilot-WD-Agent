# Training / facilitator deck

A standard skeleton + presenter-notes discipline for a facilitator-led training or
enablement deck (an instructor running a session, not a self-serve user guide). The user
guide teaches by reading; this deck teaches by facilitation, so the talk-track lives in the
notes, not on the slides. Rendering uses the **pptx** skill (neutral formatting);
this reference owns the structure and the notes rule. (adapted from an internal firm skill,
2026-08-28)

## Skeleton

```
Cover | Agenda (this day) | Roles & Responsibilities | Running the session
  (pre-flight checklist -> notes) | [per module: Section divider -> content cards ->
  exercise/demo] | Day summary | Q&A
```

- **Cover** - session title, audience, date, facilitator.
- **Agenda** - just this day's modules, in order.
- **Roles & Responsibilities** - who does what in the session (facilitator, SME on call,
  note-taker) and post-session.
- **Running the session** - the pre-flight checklist (tenant/test-user access, links,
  recording on), kept as a notes-only slide.
- **Per module:** a section divider, then content cards, then an exercise or live demo -
  every module ends in a do, not just a read.
- **Day summary** and **Q&A** to close.

## Presenter notes on EVERY content slide

Three things, every content slide:

1. **Facilitator talk-track** - what to say / walk through.
2. **Timing estimate** - minutes for the slide (so the day fits the agenda).
3. **SME-validation flag** if any - e.g. "confirm with functional lead" - where the content
   still needs a subject-matter expert to verify before the session.

## Hard rules

- **Draft / "pending review with <name>" notes go in presenter notes ONLY** - never on a
  visible slide. The audience sees finished content; the caveats live in the notes.
- **System fonts for an externally-shared deck**; internal-brand fonts only when the deck
  stays inside the firm (the engagement's brand rules govern which applies).
- **The agenda must match the built structure** - if the modules changed, fix the agenda.
- **Credit SME contributors with their real titles.**

## Where this sits

- **wd-kt** owns the training deliverable; this is the DECK layout + notes discipline
  (`kt-sessions.md` owns session structure, competencies, and teach-back tracking - a
  different artifact).
- **Rendering** (brand, fonts, cover, layout) -> **pptx** (neutral formatting).
- **Quality-gate tie-in:** the deck is a KT deliverable, so it runs the wd-kt patterns +
  document-polish check in the quality-gate registry (wd-extend-lifecycle
  `references/quality-gates.md`, Client guides row); the agenda-matches-structure and
  SME-credit rules above are part of that self-check.
