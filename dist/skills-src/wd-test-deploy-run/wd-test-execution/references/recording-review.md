# Reviewing a tester's screen recording

**When:** a defect report links a screen recording, and the claim depends on what the screen
showed ("the caption read X", "the message only appears the first time").

**Why it matters:** a recording is the tester's evidence, not a summary of it. Their written steps
can misquote the screen. Read the frames, then check the app's log for the same moments, before
classifying the defect.

**Verified 2026-10-06:** a reported "wrong caption" turned out to be a tab opened before a settings
change. The tester's own screenshot, shown later in the same recording, had the right caption.
The log showed the "first time only" message had nothing left to warn about. Both parts were
working as designed, and the recording plus the log proved it in under an hour.

---

## Steps

1. **Ask before downloading.** Downloading needs the user's OK. Give the file name, the source
   and the size; the Drive metadata call returns all three.
2. **Download to the scratchpad and check the copy.** The size must match the metadata. An MP4
   starts with an `ftyp` box in its first 12 bytes. A public Drive file downloads from
   `drive.usercontent.google.com/download?id=<id>&export=download&confirm=t`.
3. **Pass 1, the storyline.** Run `scripts/extract_frames.py <video> <out>` and read the contact
   sheets. Note which page is on screen when.
4. **Pass 2, the part that matters.** Run it again with `--region` around the dialog or notice,
   `--threshold 1.0`, and `--start`/`--end` around the moment. A small notice barely moves the
   whole-screen average, so pass 1 can miss it.
5. **Read the claim at full size.** Crop the frames that carry the claim and upscale them by 1.5x.
   Thumbnails are too small to read text.
6. **Tell a stale tab from a fresh open.** Crop the browser's tab strip across the key frames and
   compare the active tab and its title. A page opened before a settings change keeps the old
   state until it is opened again.
7. **Match the recording to the log.**
    - The taskbar clock gives the tester's local time and date. Watch for DD-MM against MM-DD.
    - Convert that time to the log view's time zone (see app-log-stream.md, "Time zones").
    - Find the page loads at those times.
    - If the page logs the data it loaded, each line shows what was saved at that open. That
      tells "never saved" from "saved, then cleared".
8. **Read the close prompts.** A "Discard Changes?" prompt on close means the screen held unsaved
   edits. A value visible on screen may never have been saved; the log settles it.

---

## Secrets in recordings

- **Testers often record admin pages,** such as an app's attribute edit page, with credentials in
  clear.
- **Never transcribe a secret value.** Not in notes, docs, evidence or chat.
- **Build evidence images from crops** of the region that matters only. Check each one before
  saving it next to the triage doc.
- **Record the exposure as a finding,** with the recording's timestamps, so the secret is rotated.

## Evidence

- **One labelled crop per point.** Add a dark bar above the crop with the recording timestamp and
  what it shows, for example "0:34 Same tab, screen opened again at 03:40".
- **Pair it with the log line** that proves the stored state, read from the record's JSON view.
