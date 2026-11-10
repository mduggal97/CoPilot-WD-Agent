# Scripts - build-specs + usage

Bundled helper scripts for this skill. If a script is missing on your machine, regenerate it
from the build-spec here (the suite convention: reference documents the spec so Claude can
rebuild the file rather than pointing at a dead path).

## extract_frames.py (bundled)

**What it is:** pulls the distinct screens out of a screen recording and lays them out on contact
sheets, timestamp on each. The method that uses it is in
[recording-review.md](recording-review.md).

**Usage:**

```
python scripts/extract_frames.py <video> <out_dir> [options]
  --every 0.5          seconds between frames looked at
  --threshold 4.0      mean pixel change (0-255) that counts as a new screen
  --region x0,y0,x1,y1 compare and save only this rectangle (use --threshold 1.0 with it)
  --start S --end S    seconds; --end 0 means the end of the recording
  --cols 3 --rows 3    thumbnails per contact sheet
  --thumb 640          thumbnail width
```

Exit code 1 if the video cannot be opened.

**Verified 2026-10-06** on a 69-second 1920x1080 recording at 30 fps. The whole-screen pass kept
24 screens, the same set as the manual pass it replaced. The region pass at threshold 1.0 kept 31,
including notice changes the whole-screen pass merged. Byte-compiles clean.

**Deps:** opencv-python and numpy.

**Build-spec (to regenerate if absent):** one Python CLI on OpenCV. Open the video with
`cv2.VideoCapture` and read fps, frame count and size. Look at every round(fps x every)-th frame
between start and end. Compare a 320x180 greyscale copy of the frame, or of the region, with the
last kept copy, and keep the frame when the mean absolute difference exceeds the threshold. Save
kept frames as `frame_<mm>m<ss.s>s.png`. Then tile them cols x rows per JPEG sheet, with a black
timestamp label on each thumbnail. Keep the header, change-log block and KT comments (exemplar
bar, wd-extend-dev standards.md).

## validate_output_file.py (bundled)

**What it is:** a byte-level validator for a DOWNLOADED integration output file or log - the
SF-11 content check when the in-app browser cannot inspect the bytes. Point it at the file on
disk; it parses the format, reports what is in it, and PASS/FAILs against expectations.

**When to use:** SF-11 (scenario-flows.md) - after an integration event's output/log attachment
is downloaded from the Browser pane. Get the file's path first (confirm the pane's download
location, or have the user save it to a known path).

**Usage:**

```
python scripts/validate_output_file.py <path> [options]
  --format auto|delimited|csv|fixed|xml|json|xlsx|log   (default auto: by extension + sniff)
  --delimiter ","                 force a delimiter (else auto-detected)
  --expect-header "A,B,C"          header must match, in order
  --min-rows N / --exact-rows N    record-count checks
  --required-cols "A,C"            these columns must be non-empty in every row
  --record-tag Import_Process_Message   XML element to count as a record
  --log-patterns "ERROR,CRITICAL,Fault,FAILED,Exception"   log severity markers to scan
  --sample N                       rows to echo (default 3)
  --json                           machine-readable report
```

Exit code: 0 = all supplied checks passed (or info-only when no checks given); 1 = a check
failed or the file could not be read - so it gates a test step.

**What it reports:** encoding + UTF-8 BOM; delimiter (delimited); record count; header/columns;
a sample of rows (as dicts when a header lines up); for XML: record count by tag (given or the
most-common repeating child) plus Workday fault/error markers (Validation_Fault, Fault,
Processing_Error) and Import_Process_Message count; for JSON: RaaS `Report_Entry` or list count
+ keys; for XLSX: sheet + header + count + sample; for a log: total lines + severity-marker hits
+ the matched lines.

**Deps:** stdlib only, EXCEPT `.xlsx` needs `openpyxl` (degrades with a clear message if absent -
see wd-extend-lifecycle prerequisites.md). Cross-platform.

**Formats + limits:** delimited (CSV/pipe/tab, auto-detect), XML (WWS/EIB output + Import_Process),
JSON (RaaS), XLSX (report/RaaS export), text log. Fixed-width is line-count + sample only (a
column spec is out of scope). A truly opaque binary (PDF/encrypted/PGP) or a proprietary format
it cannot parse is handed off per SF-11's honesty note - never content-verified from metadata alone.

**Verified 2026-08-27** against synthetic samples across every format + the pass/fail paths
(header mismatch, short count, required-column-empty naming the offending row, log severity,
malformed XML, missing file, BOM) and byte-compiles clean.

**Build-spec (to regenerate if absent):** a single stdlib Python CLI. Read the file with
`utf-8-sig` (strip BOM) falling back to `utf-8` then `latin-1`; detect format by extension then a
content sniff. Parse per format (csv.reader with Sniffer-or-forced delimiter; ElementTree for XML
counting local-name element occurrences + fault markers; json for RaaS/list; openpyxl read-only
for xlsx; line scan for logs). Collect findings + a list of (check-name, ok, detail); apply the
tabular checks (expect-header equality, min/exact rows, required-cols non-empty per row reporting
the first offending row+col); emit a human report or `--json`; `sys.exit(1)` if any check failed
or a hard read/parse error occurred. Full commented source is the shipped file; keep the header +
change-log block and the KT comments (exemplar bar, wd-extend-dev standards.md).
