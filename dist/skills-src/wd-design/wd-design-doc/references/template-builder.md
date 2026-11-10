# Template builder & rebrander - get a fresh template, or rebrand it for a customer

Two jobs live here:

1. **"I don't have a template handy"** - produce a fresh Extend or Integration design template, styled in the neutral default (or a client brand).
2. **"Rebrand this for the customer"** - apply the customer's colours and logo, producing a rebranded document (a source is never edited in place).

**Get a working template one of two ways** - this skill no longer ships proprietary binary masters:

1. **Regenerate a working structural template from text** (default, always available, cross-platform) - run the bundled builder for the family you need. Output is **neutral / unbranded**; style it separately (below).
2. **Obtain a branded master per engagement** - when the engagement supplies one (a client's mandated template, or a macro master from the engagement store - see the environment memory).

| Family | Regenerate with | Then style with | Notes |
|---|---|---|---|
| **Extend** | `python scripts/build_extend_design_doc.py [out.xlsx]` | `scripts/xlsx_brand_style.py` | Full **17 tabs** (16-tab structure + KPI & Reporting), neutral grayscale. No macros, no embedded logo - a faithful, complete rebuild. |
| **Integration (IDD)** | `python scripts/build_idd_structure.py [out.xlsx]` | `scripts/xlsx_brand_style.py` | **Structural `.xlsx` equivalent** of the 22-sheet IDD (headings + structure + READ ME as cells). **NOT the macro workbook** - see the honest limits under section 1 (IDD). |

> Any `.xlsm`/`.xlsx` master files still present under `assets/` in a stale copy of this skill are legacy proprietary binaries; do not treat them as the source of truth. Regenerate, or obtain a master per engagement.

---

## 1. Getting a fresh template

### Default path = regenerate the structural template, then style it

- **Extend** -> `python scripts/build_extend_design_doc.py MyApp.xlsx`, rename per the naming standard (`<CODE>_<Name>_Design_Document_v0.1.xlsx`), style it (`scripts/xlsx_brand_style.py`, neutral by default) or leave it unstyled, and start filling. This is a faithful, complete rebuild (the Extend workbook has no macros and no embedded logo, so nothing is lost).
- **IDD** -> `python scripts/build_idd_structure.py MyINT.xlsx` produces a **structural `.xlsx`** skeleton (all 22 sheets, correct order + visibility, titles, section bands, column headers, per-tab column widths (`TAB_WIDTHS`), Overview Key Details, Unit Testing summary, READ ME as cells). It is a **working structural equivalent, not the macro `.xlsm`** - read the honest limits below before relying on it. Then set the Integration Type by hand (no macro) and fill per [idd-template.md](idd-template.md).

### When you need a branded / macro master

- **Extend** -> if the engagement supplies a branded Extend template, rename per standard and start filling. Otherwise regenerate and style it - the result is equivalent.
- **IDD** -> obtain the macro master per engagement, then **open it in Excel (macros enabled) and set the Integration Type in the Overview Key Details (J10)** so the `Worksheet_Change` macro hides/unhides the matching solution sheets (O4I -> `WD Solution - O4I`; Studio/EIB -> `WD Solution - General`; Connector/Connector+DT -> `WD Solution - CC` + `Field Overrides - CC` + `Mappings - CC`). Set Integration ID (J8) + Name (J9) too, so the ISU/ISSG names auto-build before you touch the security sections. See [idd-template.md](idd-template.md) for the full fill order.

### Palettes (for verification / manual edits)

The builders emit **neutral placeholder fills**: title `FF404040`, section `FFD9D9D9`, header `FFF2F2F2`.

- **Section and header are recoloured by role.** `templates/idd.json` maps them to `band` and `header`. Without those two entries a regenerated doc keeps grey bands and gets no table borders - `xlsx_normalize_layout.py` finds tables by the brand's fills.
- **The title strip is in no role, on purpose.** The styler finds the tab title by position, not by fill. The contrast gate clears the dark `FF404040` strip to paper on every run.
- **`scripts/check_profiles.py` enforces both.** It fails if a builder placeholder is unmapped, or if the title strip gains a role.

Palettes you will meet:
  - **Neutral default** (`brands/neutral.json`, what `xlsx_brand_style.py` applies with no `--brand-profile`): section band **`FF1F2A37`**, masthead and header text **`FF111827`**, sub-section and table-header fill **`FFE5E7EB`**, body text **`FF1F2937`**, open-items **yellow `FFFFFF00`** (the yellow is the skill's open-items convention, not a brand color; **never** remap it).
  - **A client brand** - whatever its `brands/<client>.json` profile holds.
  - **A client program template** (16-tab-spec house-style spec): title `FF0070C0` (blue), section `FF78DED4`, header `FFF2F2F2`. Match whichever the engagement uses.

### IDD - honest limits of the structural rebuild

`build_idd_structure.py` gives you the sheet structure and headings, but **three things in the real IDD `.xlsm` cannot be regenerated from text** - openpyxl row-writes and COM rebuilds both drop shapes and macros (**this is exactly what went wrong on delivered IDDs: the READ ME and the macro behavior were lost**):
  1. **The VBA Integration-Type visibility macro** (Overview!J10). In the structural `.xlsx` all solution sheets are simply present at their default O4I visibility; set visibility by hand for your type.
  2. **The ISU/ISSG auto-naming formulas** and other cross-sheet CONCAT formulas built from Overview!J8/J9. In the structural build those are blank cells to type.
  3. **The READ ME text box.** The builder writes the READ ME **as cells** (the durable form - cells survive every path), but the original floating shape is gone.

So: use the structural builder for a working skeleton, and when you need the true macro workbook, **obtain the macro master per engagement** (engagement store - see the environment memory), verify the READ ME and the Integration-Type macro fire, and keep it in the engagement's store - do not re-bundle it into this skill.

---

## 2. Rebranding to customer colors / logo

Use this when the user explicitly directs a customer rebrand. **Default with no override = the neutral brand** - never rebrand unprompted.

### Preferred path - style straight into the client brand

1. Copy `brands/_example-customer.json` to `brands/<client>.json` and fill it in (it lists exactly what to request from the client: hex values, a cleared wordmark, its locked ratio, font licensing).
2. Style the **pre-style** workbook: `python scripts/xlsx_brand_style.py <workbook> --brand-profile <client>`. Every structural gate stays identical; only colours and fonts change.
3. If the brand has a logo: `python scripts/xlsx_place_wordmark.py <workbook> --brand-profile <client>`, then `python scripts/xlsx_brand_style.py <workbook> --brand-profile <client> --wordmark-only` to anchor it.

### Recolour an already-styled copy - `scripts/rebrand_template.py`

Use this when the document is ALREADY styled and only its colours need swapping, or on a machine without Excel (the `.xlsx` path is pure openpyxl). It produces a rebranded **copy** and refuses to overwrite the source.

```
python scripts/rebrand_template.py --in <workbook> [--out <path>] [--palette <json|file>] [--logo <image>] [--dump-palette]
```

- `--in` - the source workbook (`.xlsx` Extend design doc or `.xlsm` IDD). Required.
- `--out` - output path for the rebranded copy (must differ from `--in`). Required unless `--dump-palette`.
- `--palette` - a **role->hex map**, given as either a `.json` file path or an inline JSON string. Keys are role names (preferred) or explicit source-hex values; values are the customer hex (`#RRGGBB`, `RRGGBB`, or 8-hex ARGB). Omitted roles keep their current colour (partial rebrands are fine).
- `--logo` - optional customer logo image to swap in for the header logo.
- `--dump-palette` - print the distinct fill colors currently in `--in` (annotated with the known role for each) and exit, so the user can see what to remap.

**Roles** (the palette map keys) are the brand profile's own palette names - `band`, `accent_dark`, `header_fill`, `body_text` - resolved to the **neutral default's** colours (see `NEUTRAL_ROLES` in the script). So a document styled with the default brand can be recoloured straight from a client's profile palette. For a document in any other palette, use explicit hex keys from `--dump-palette`. Roles that share one source colour move together (the band colour is both the band fill and the title/label text, by design).

**Safety rails built in:** the open-items yellow (`FFFFFF00`) is protected from remapping (it's the skill's "still needs input" signal); if a color in the map isn't found in the workbook, the script **reports it** rather than silently skipping; and it will not overwrite the source.

```bash
# 1. See what's there
python scripts/rebrand_template.py --in "$SRC" --dump-palette

# 2. Recolour a neutral-styled Extend (.xlsx) with an inline palette
python scripts/rebrand_template.py \
  --in "$SRC_EXTEND.xlsx" \
  --out Acme_Extend_Design_Document.xlsx \
  --palette '{"band":"#1B2A4A","accent_dark":"#0F1A2E","header_fill":"#EDEDED","body_text":"#222222"}'

# 3. Recolour an IDD (.xlsm) from a palette file, swapping the logo too
python scripts/rebrand_template.py \
  --in "$SRC_IDD.xlsm" \
  --out Acme_IDD.xlsm \
  --palette acme_palette.json --logo acme_logo.png
```

### How the Extend (.xlsx) and IDD (.xlsm) paths differ

| | Extend `.xlsx` (openpyxl) | IDD `.xlsm` (Excel COM) |
|---|---|---|
| Recolor | Walks every cell; remaps fills **and** font colors matching the source colors. | Excel **format-based find/replace** (`FindFormat`/`ReplaceFormat` + `Range.Replace(SearchFormat=True)`) - recolors each source color across a whole sheet in one call, format-only so **values/formulas are untouched**. |
| Logo | Swaps embedded image bytes. Builder output has **no embedded logo** (branding is cell-based), so this typically reports "nothing to swap" - that's correct, not an error. | A logo image may appear on **every tab**; the COM path deletes each picture shape and re-adds the new logo at the same geometry. On a filled doc this would also match embedded diagram pictures, so rebrand before diagrams are embedded (or verify per tab). |
| Macros/formulas | No macros; openpyxl preserves the template formulas. | **VBA project, macros, and the ISU/ISSG formulas are preserved** - verified by SaveAs `FileFormat=52` (xlOpenXMLWorkbookMacroEnabled). |
| Verify | Re-open, confirm bands recolored and yellow intact. | **Open in Excel and spot-check 2-3 tabs**: macros fire, ISU/ISSG formulas intact, bands + logo recolored, READ ME text box present. |

Validated end-to-end (2026-08-04, on the former firm masters): Extend rebrand recolored 17/50/203 role cells + 38 instruction-font cells, yellow untouched, formulas preserved; IDD rebrand recolored all three role colors across tabs with `vbaProject.bin`, the 22 drawings, the 5 media images, and all 23 formulas preserved byte-for-byte.

### Honest limits

- The **IDD macro workbook cannot be recreated from scratch** - `build_idd_structure.py` gives a structural `.xlsx` skeleton, not the `.xlsm`, and `rebrand_template.py` can only rebrand an existing macro workbook (see section 1). If you have no IDD `.xlsm`, obtain one per engagement; you cannot script the macro/formulas/text-box into existence.
- On a **filled** IDD, the COM logo swap can't tell the logo apart from embedded diagram pictures - rebrand the blank/early doc, or verify each tab after.
- The Extend logo swap is a no-op unless a logo image has been added to the workbook (the neutral builder output is cell-branded, with no embedded logo).
