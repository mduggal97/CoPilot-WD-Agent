# Rebrand a deliverable + OCR-mask sensitive data in screenshots

Turning a real client deliverable (user/admin guide, training doc, runbook - often 100-200+ pages with
hundreds of embedded screenshots) into a reusable template or a different-client version means removing the
old branding AND the old client's data. Text is the easy part; the trap is the **screenshots**, which carry
client names, worker names, IDs, addresses, and currencies as pixels no find-and-replace can touch. This
pipeline handles both.

> Adapted 2026-08-13 from the `docx-rebrand-ocr-mask` skill (a colleague's submission);
> vendor-neutral. Use it whenever you genericize a deliverable for the reuse catalog (wd-practice-ops
> `reuse-and-asset-catalog.md`), transfer a doc between engagements, or scrub screens for a demo/marketing
> asset (wd-demo, bow-sales-enablement "use real screens, scrubbed"). It operationalizes the suite's
> no-client-data rule (wd-extend-lifecycle `ai-data-governance.md`) for image content.

## Two layers

**Text layer (.docx XML):** swap cover/header logos (image replace in `word/media/`, match dimensions to
avoid reflow); replace footer company name, document reference numbers, cover title; update author metadata
(`docProps/core.xml`: `dc:creator`, `cp:lastModifiedBy`) and the "last updated" date (preserve "prepared
on"); **remove tracked changes and review comments entirely**. Text runs are often split across adjacent
`<w:r>` elements - search across runs and patch every one, or the string won't match. Cross-reference
`w:blip r:embed` / `v:imagedata r:id` against `word/_rels/document.xml.rels` to map an image reference to
its `media/` file.

**Screenshot layer (OCR masking):** for every embedded PNG/JPEG, OCR-detect and mask old vendor/client
names, personal names (all case variants), emails, city/country references, currency symbols, street
addresses, avatar initials, and in-image logos.

## Masking pipeline (the reliable recipe)

1. **Upscale before OCR** - resize 4x (5x for very small fonts) with LANCZOS, run `pytesseract.image_to_data`,
   then scale the hit coordinates back to the original resolution. Small UI text is the usual miss.
2. **Mask by sampling local background** - fill the hit rectangle (plus a few px padding) with a colour
   sampled from the region corner, so the box blends instead of leaving a black bar.
3. **Multi-scale passes** - run at 3x/4x/5x to catch small-font residuals.
4. **Template-match logos/avatars** with OpenCV (`matchTemplate`, TM_CCOEFF_NORMED, confidence >= ~0.80),
   mask the matched region.
5. **Always run a final OCR verification pass** (>= 2x) after masking to catch residuals. Skip cover/header
   images (already replaced as logos).

## Repack + verify

Repack with `zip -Xrq` (the `-X` flag - no extra attributes - is required for Word to open it). Convert to
PDF (LibreOffice) and spot-check key pages by CONTENT reference, not page number (PDF pagination can differ
from Word).

## Dependencies (state them; not all environments have them)

`python-docx`, `lxml`, `Pillow`, `pytesseract`, `opencv-python` (+ `cairosvg` if rasterizing SVG); system
`tesseract-ocr` (plus the language pack for non-English screenshots, e.g. `tesseract-ocr-fra`), LibreOffice,
poppler. On claude.ai the Python libs are usually present; the system `tesseract`/LibreOffice binaries may
not be - if OCR isn't available, fall back to manual screenshot review and say so (do not claim a doc is
scrubbed if the image pass didn't run).

## The one hard rule

**A rebrand is not done until the screenshots are verified clean.** A text-only pass leaves client data
sitting in the images - exactly the leak the suite's data-governance rule exists to prevent. Verify by the
final OCR pass AND a human eyeball on a sample before the asset is reused or shared.
