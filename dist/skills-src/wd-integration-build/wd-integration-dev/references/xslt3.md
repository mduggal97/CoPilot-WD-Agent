# XSLT 3.0 for Workday integrations - streaming, maps, and XTT/ETV

Techniques verified against a curated example library (Workday KSS decks + firm-authored
worked examples + a benchmark CLAR), distilled 2026-08-05. Studio anatomy lives in
[studio.md](studio.md); assembly-side streaming idioms in
[studio-patterns.md](studio-patterns.md) section 9. This file is the transform-side companion.

## Where XSLT 3.0 runs (and doesn't)

Studio's **XSLT+** step (`cc:xslt-plus`) = Saxon EE with XSLT 3.0 streaming. XTT (XML->text)
and ETV (XML->XML) are streamed annotation-driven transforms in the same engine family.
Historical caveat from the source decks (2017): XSLT 3.0 was NOT available in EIB or
Document Transformation - **avoid 3.0-only features if the transform might move to EIB/DT**,
and verify current-release support before assuming otherwise. Params auto-convert types in
XSLT+ (String/Float/Boolean/Node...); Saxon honors `omit-xml-declaration`; debugging is not
supported while streaming (test with Oxygen + Saxon EE streaming enabled).

## Stream or not? (decision list from the Workday deck)

**Stream** when the file may exceed ~100 MB, output follows input order, or you need
running summaries (iterate/accumulator). **Don't stream** when you must query across the
whole document arbitrarily, sort output, or group into many non-adjacent groups - instead
stream to the record level and snapshot each record (the hybrid below). XTT/ETV: use once
per pass, never inside a splitter-aggregator; GB files in tens of seconds; event messages
are held in memory, so cap message volume.

## Universal boilerplate

```xml
<xsl:output method="xml" indent="no"/>  <!-- NEVER indent="yes" in prod: up to +30% size -->
<xsl:mode streamable="yes" on-no-match="shallow-skip"/>
<xsl:mode name="in-memory" streamable="no"/>  <!-- companion mode for copy-of() snapshots -->
```

## The case study that motivates everything: the Journal evolution

One journal-lines-to-CSV transform, four versions (all in the example library):
1. **v1 (XSLT 2.0, EIB):** ran out of memory on large report output.
2. **v1 in Studio splitter-XSLT-aggregator:** hit the max time limit.
3. **Streaming with minimal change:** add the two modes above; the streamed template does
   `<xsl:apply-templates select="copy-of()" mode="in-memory"/>` and the ORIGINAL template
   gets `mode="in-memory"` - the whole conversion is ~10 lines of change, "approximately
   x-times faster than splitter-xslt-aggregator."
4. **Maps-of-functions + XTT:** column names in a sequence, per-column format functions in a
   `map(xs:string, function(xs:string) as xs:string)`, and CSV quoting delegated to XTT
   (`<Row xtt:startTag="&#10;" xtt:separator="," xtt:quotes="csv">`) instead of hand-rolled
   quote/escape logic.

A benchmark CLAR in the library routes one 25 MB PECI file down three parallel paths -
FullStream / PartialStream (stream to record, then `copy-of()` into a non-streaming mode -
**the recommended hybrid**) / classic Splitter+Aggregator - and stores each output for
memory/time comparison.

## `for-each select="X/copy-of()"` - the streaming escape hatch

The single most-used idiom: the stylesheet stays streamable and memory-safe (one record in
memory at a time) while the body gets full random access - multiple child reads, `xsl:sort`,
predicates, `sum()`/`count()`:

```xml
<xsl:for-each select="wd:Report_Entry/copy-of()"> ... </xsl:for-each>
```

`snapshot()` is the sibling that preserves ancestry (use it when the copied node must still
see its ancestors, e.g. stored as a map value). Rule of thumb inside a streamed template:
you get ONE downward selection - `copy-of()`/`snapshot()` first if you need more.

## Merge/join strategies (replacing Java hashmaps)

Same problem - enrich records from lookup data - four delivered answers. The old Studio way
(per lookup source: splitter -> Java hashmap put; then get() per record) benchmarked at
**~6.2 minutes** for 15k lookups; the XSLT 3.0 rewrites: **~27 seconds**.

| Strategy | When it wins | Core idiom |
|---|---|---|
| **`xsl:key` over an aggregated doc** | Default. Studio aggregator concatenates all sources under one root; lookup section small enough to hold | `<xsl:key name="k" match="Charge" use="Student_ID"/>` + 3-arg `key('k', $id, $ChargeData)` - returns NODES, so `copy-of` preserves structure, no array plumbing |
| **`xsl:source-document` -> map** | Lookup lives in a SEPARATE file | build `map(xs:string, element())` inside a variable via `<xsl:source-document href="..." streamable="yes">` + `xsl:map-entry` |
| **Accumulators** | Lookup data streams past BEFORE the records in one document; O(1) access with true streaming | see below |
| **`xsl:iterate` + `snapshot()` param** | Lookup section is a sibling you pass once | `<xsl:next-iteration><xsl:with-param name="ErrorsData" select="snapshot()"/>` then 3-arg `key()` against the param |

Assembly-side prep for the key strategy: XSLT-transform each source to strip unneeded fields
and guarantee a unique key, aggregate all sources into one document, then ONE merge XSLT.

## Accumulators

Registered on the mode, `streamable="yes"`, rules usually match `text()`:

```xml
<xsl:mode streamable="yes" on-no-match="shallow-skip"
          use-accumulators="WorkerIDLookup CurrentLookupValue"/>

<!-- paired-accumulator trick: element A precedes element B in document order;
     acc 1 captures A's value, acc 2 commits the map entry when B arrives -->
<xsl:accumulator name="CurrentLookupValue" as="xs:string" initial-value="''" streamable="yes">
  <xsl:accumulator-rule match="r:Employee_ID/text()" select="."/>
</xsl:accumulator>
<xsl:accumulator name="WorkerIDLookup" as="map(xs:string,xs:string)" initial-value="map{}" streamable="yes">
  <xsl:accumulator-rule match="r:Other_ID/text()"
      select="map:put($value, string(.), accumulator-before('CurrentLookupValue'))"/>
</xsl:accumulator>
<!-- lookup: map call syntax --> accumulator-before('WorkerIDLookup')(normalize-space(@id))
```

More tools: `phase="end"` rules commit an entry when a CONTAINER element closes; an
`array(xs:string)` accumulator with a reset rule on the container collects repeating
children (`array:append`, unpack with `array:flatten()`). For missing-lookup errors in a
streamed context use `<xsl:message error-code="...">` - `error()` kills the whole transform.

## `xsl:iterate` - state across a streamed pass

For-each that passes state forward. Grouping/summing a huge file without holding it:

```xml
<xsl:iterate select="PayrollResult/P010">
  <xsl:param name="groupCounts" as="map(xs:string, xs:float)" select="map{}"/>
  <xsl:on-completion>  <!-- must precede the body -->
    <xsl:for-each select="map:keys($groupCounts)"> ... totals ... </xsl:for-each>
  </xsl:on-completion>
  <xsl:variable name="rec" select="copy-of()"/>
  <xsl:next-iteration>
    <xsl:with-param name="groupCounts" select="
      if (map:contains($groupCounts, $key))
      then map:put($groupCounts, $key, map:get($groupCounts,$key) + 1)
      else map:put($groupCounts, $key, xs:float(1))"/>
  </xsl:next-iteration>
</xsl:iterate>
```

- Compound keys: `string-join((A, B), '|')`, split back with `substring-before/after`.
- **Record-store pattern** (aggregate N files' records per person in one pass): two maps -
  a count map and a `map(xs:string, item())` keyed `ID||n` holding `snapshot()`s; replay in
  `on-completion` via a recursive template over keys `ID1..IDn`. The production version of
  this (DIS worktag scrub) routes siblings into two maps with `self::tdf:PreviousWorktag`
  element tests - the DIS scrub XSLTs referenced in [studio-patterns.md](studio-patterns.md) section 2/section 4.
- **Counter loop** (numeric while, e.g. N sequential rate steps each feeding the next):
  recursive named template with `$i`/`$LoopCount` params; drive with `max(Step)`.

## `xsl:fork` - several consumers of one streamed pass

Inside a streamed template you get one downward selection; `xsl:fork` lets multiple sequence
constructors each consume the same input: branch 1 copies the streamed children
(`<xsl:sequence select="node()"/>`), branch 2 does lookups/enrichment; or wrap a
`for-each-group` whose groups each run an `xsl:iterate` for trailer/summary records.

## `for-each-group`

- Streaming + `group-adjacent` works on sorted input (e.g. group report rows by a column).
- `group-by` over `row/copy-of()` for the classic **flat multi-record-type file -> nested
  payload** rebuild (header/line/worktag rows dispatched by `RecordType`).
- In-memory dedupe: build intermediate XML in a variable, then `group-by` + `current-group()[1]`.

## One source -> many output files (Workday MDT, NOT `xsl:result-document`)

Workday's Multi Document Transform uses its own namespaces - input
`mdti:Input/mdti:Files/.../mdti:File`, output one `mdto:File` per group with control
attributes. (!) **Namespace gotcha:** the RUNTIME namespace of the input/output docs bakes
the wrapper PROJECT's name into the URI -
`urn:com.workday/INT_Studio_Multi_Document_Transform_Outbound/Input` and `.../Output` - NOT
the `urn:com.workday/multiDocumentTransform/*` URIs the documentation XSDs declare.
Stylesheets must bind the project-named URIs or nothing matches.

```xml
<mdto:File mdto:filename="{'workday_' || $school || '_' || format-date(current-date(),'[Y0001][M01][D01]') || '.csv'}"
           mdto:retentionPeriod="P90D" mdto:applyXTT="true"
           mdto:contentType="text/csv" mdto:deliverable="true" mdto:labels="...">
```

More `mdto:` control vocabulary: `mdto:discard`, `mdto:plainText`, `mdto:addBOM`,
`mdto:href`, `mdto:attachmentEventWID`, `mdto:attachmentSeverity`,
`mdto:targets`/`mdto:targetsType`, `mdto:securedInstanceReferences(-Type)`,
`mdto:description`. The transform can also emit its own log entries via the
**`mdto:CloudLog` element** (name / type=csv|html|excel / level / message / detail /
referenceId).

Pairs with the MDT wrapper assembly + `mdtUtilities` library CLAR in
[studio-patterns.md](studio-patterns.md) section 7. `||` is the XPath 3 concat operator. Optional
XTT-adjacent output: the XLSX-audit chain - `xslt-plus -> cc:xml-to-csv
line-separator="CRLF" -> cc:text-excel -> cc:store` - turns the same output into a real
spreadsheet.

## XTT / ETV - annotation-driven flat-file output

Inline `xtt:*` attributes on output elements replace hand-written padding/formatting:
`xtt:separator`, `xtt:endTag` (CRLF), `xtt:fixedLength`, `xtt:align`,
`xtt:paddingCharacter`, `xtt:dateFormat="yyyy-MM-dd"`, `xtt:quotes="csv|always"`, and
`etv:numberFormat="#000000000000.00"`. Reuse via **format classes** (with inheritance):

```xml
<File xtt:separator="&#xD;&#xA;" xtt:severity="error">
  <xtt:class xtt:name="string10" xtt:fixedLength="10" xtt:truncate="true" xtt:reportTruncation="warning"/>
  <xtt:class xtt:name="string20" xtt:class="string10" xtt:fixedLength="20"/>
  ...
<wd:UserId xtt:minLength="1" xtt:class="string10"/>
```

Validation/eventing annotations: `xtt:severity`, `xtt:minLength` (required field),
`xtt:targetWID`/`xtt:target` (link event messages to a tenant instance), `xtt:message` +
`xtt:omit="true"` (emit a message with no output). A local `xttHelper` stylesheet exists to
*approximate* XTT/ETV output during design - explicitly NOT a substitute for launching in
the tenant (it does not fully simulate DTS).

## House-style utility idioms (from the annotated samples set)

- **Custom errors - Studio splitter only:** collect missing field names, then
  `error(xsd:QName('Error'), 'The value is blank for required field(s): ...')`. The transform
  dies, Studio catches it and continues with the next split row. Do NOT use in EIB/DT or
  streamed whole-file passes (use `xsl:message` there).
- **Padding:** a FUNCTION (`this:padString($str,$chr,$len,$dir)` via `1 to $n`), not a
  recursive template; numbers via `format-number(n,'+00000000000000.00;-...')`.
- **Regex scrub:** `replace(string($v),'[^\p{P}\sa-zA-Z0-9+]','-')` - regex exists only in
  `replace`/`matches`/`tokenize`.
- **Character maps:** `<xsl:output use-character-maps="..."/>` + `xsl:output-character`
  entries (e->e ...) - applied at serialization, zero per-field calls; the declarative
  alternative to the regex scrub.
- **Dates:** wrap in `this:formatDate/formatDateTime` functions with the empty-guard
  `if (xsd:string($p)='') then '' else format-date(xsd:date($p),'[D01]-[MN,*-3]-[Y0001]')`.
- **Zoned decimal (mainframe signed numerics):** last digit encodes sign+digit
  (`{ABCDEFGHI`=+0-9, `}JKLMNOPQR`=-0-9, implied 2dp); convert both directions with
  `translate()`; NaN guard `number($v) = number($v)`; normalize first with
  `format-number(number($n),'#0.00')`.
- **Delimited multi-value cells:** `<xsl:for-each select="tokenize(Field1,'~')">` - done.
- **Choose ordering:** first true `when` wins - order threshold tests progressively instead
  of writing range tests.
- **Legacy flag:** `saxon:assignable` / `saxon:assign` mutable counters appear in old
  samples - don't replicate; use `position()`/`xsl:iterate` in 3.0.
- **Launch-EIB request builder:** a sample XSLT builds `wd:Launch_EIB_Request` (ISID
  reference, `Field_Override_Data` for Validate-Only/spreadsheet toggles, base64
  `wd:Attachment_Data`) from Studio `p_settings.*` props - the transform behind
  [studio-patterns.md](studio-patterns.md) section 1.

## Other XSLT 3.0 constructs (spec-available - verify in Workday before relying on them)

The sections above are build-verified against Workday usage. These are additional XSLT 3.0 features
from the W3C XSLT 3.0 Recommendation (reviewed 2026-08-12) that Saxon-EE - the engine behind Studio's
XSLT+ step - supports, but which are NOT independently confirmed in a Workday build here. Treat as
spec-available; the "Where XSLT 3.0 runs" caveat applies (XSLT+ yes; EIB/DT historically 2.0-only;
streaming restricts what is legal). Verify in a tenant before promoting any of these to a standard.

- **`xsl:try` / `xsl:catch`** - recover from a DYNAMIC error (bad cast, missing document, failed
  lookup) without killing the whole transform (`$err:code` / `$err:description` in the catch). A
  cleaner alternative to the "die and let Studio's splitter catch it" idiom for NON-splitter passes -
  but not usable to wrap a streamed selection; confirm the streaming interaction.
- **`xsl:merge`** - the purpose-built construct for combining SEVERAL already-sorted inputs into one
  ordered stream (`xsl:merge-source` + merge keys). An alternative to the key/map merge strategies
  above when every source is pre-sorted on the same key; streamable.
- **`xsl:evaluate`** - run an XPath expression built dynamically at runtime (from a string or a config
  doc) - data-driven mapping. Watch-item: arbitrary-XPath robustness/safety, and the processor's
  dynamic-evaluation feature must be enabled - verify in Studio.
- **JSON functions** - `parse-json`, `json-to-xml`, `xml-to-json`, `json-doc`: read or emit JSON
  directly in the transform. In Workday, JSON is usually handled O4I/MVEL-side, not in XSLT - confirm
  there is a real reason to do it in the transform before reaching for these.
- **Packages** (`xsl:package` / `xsl:use-package`; component visibility public/private/final;
  overriding) - the 3.0 module system for shareable stylesheet libraries. Studio wraps XSL inside the
  CLAR (studio-patterns.md shared-library pattern); whether Studio supports true `xsl:package` linkage
  is UNCONFIRMED - default to the CLAR shared-library approach unless verified.
- **`xsl:assert`** - dev-time assertions to catch broken assumptions (disabled in production runs).
- **Text value templates** (`expand-text="yes"` + `{ }` in text) - the `{...}` interpolation already
  used in the MDT filename example; enable per element/stylesheet with `expand-text`.

## Worked-example library (your local library)

Index of the runnable pairs (each folder = one XML input + one XSL) and what each teaches. Names are
relative to the local library path (see Engagement inputs below); open the example BEFORE writing a
new transform of the same shape - the header comments carry the production notes.

- **`accumulator example\`** - the single best exemplar: a PAIRED accumulator replaces a Java hashmap
  under streaming. `CurrentLookupValue` (xs:string) latches an ID as it streams past; `WorkerIDLookup`
  (map(xs:string,xs:string)) does `map:put($value, string(.), accumulator-before('CurrentLookupValue'))`
  when the second element arrives. Consume with `accumulator-before('WorkerIDLookup')(normalize-space(@id))`;
  miss -> `xsl:message` with an `error-code`. Production note in the header: never `indent="yes"`
  (up to ~30% output inflation).
- **`different ways to merge data example\`** - the 4 merge strategies side by side on the same data:
  `use_key_to_merge_data_XSLT.xsl` (xsl:key + xsl:iterate carrying a `snapshot()` param + xsl:fork per
  record), `accumulate_map_to_merge_data_XSLT.xsl` (three chained accumulators incl. `array(xs:string)`
  via `array:append` and a `phase="end"` rule; `use-accumulators="#all"`), and the build-a-map-up-front
  variant `create_map_to_merge_data_XSLT.xsl`.
- **`iterate example\`** - xsl:iterate state accumulation: two `map(xs:string, xs:float)` params
  (counts + sums), composite key via `string-join(...,'|')`, emitted in `xsl:on-completion`. Streamable.
- **`fork and iterate example\`** - `xsl:fork` wrapping `for-each-group select="Record/copy-of()"` +
  nested iterate: control totals (count + `format-number`) per key in ONE streamed pass.
- **`multi document transformation one source to many output example\`** - the correct Workday MDT
  idiom (NOT `xsl:result-document`): emit `mdto:File` with computed `mdto:filename`, `mdto:retentionPeriod`,
  `mdto:applyXTT="true"`, `mdto:contentType`/`deliverable`/`labels`, XTT annotations nested inside.
- **Smaller idiom folders** - `key example`, `for-each copy-of example`, `for-each-group copy-of example`,
  `execute a loop using a counter`, `parse a delimited field` (`tokenize(Field1,'~')` fan-out),
  `use iterate and map to aggregate records from multiple files` (cross-file aggregation).
- **`XSLT Samples\` (16 annotated basics)** - one file per idiom: apply-templates, character maps,
  choose, counters, Custom Errors (Studio only), date/datetime formatting, for-each(-group),
  if-then-else, padding, regex, variables, zoned-decimal conversion. Plus two production patterns:
  - **`WriteLaunchEIBRequest.xsl`** - launch-integration-from-integration: builds `wd:Launch_EIB_Request`
    with `wd:Service_Component_Data`/`wd:Field_Override_Data`, driven entirely by `p_settings.*` params
    (`web_service_version`, `document_retention`, `current_moment`, `validate_mode`, `debug_mode`,
    `eib_integration_id`) - that parameter convention is itself the reusable framework.
  - **`ScrubWorktagsDIS.xsl`** - entry point into the DIS scrub family.
- **Journal series (root of the library)** - `Journal.xslt` -> `Journal-Streaming.xslt` ->
  `Journal-Streaming-Map.xslt` -> `Journal-Streaming-XTT.xslt`: the 4-version streaming-conversion
  case study cited in the Streaming section; `Journal-Streaming.xslt`'s header documents the
  minimal-change conversion that replaced a splitter/aggregator design.

Related corpora usually held NEAR the library (verify per machine; see Engagement inputs):

- **DIS two-moment compare pipeline** - a six-stylesheet, multi-version (v1->v6) set
  (Scrub -> Compare -> Merge -> InsertValues -> Batch -> SplitBatch -> WriteLaunchIntegrationRequest)
  WITH real input/output XML at each stage - the best end-to-end traceable pipeline exemplar
  (studio-patterns.md pattern 4 names it; this corpus is the runnable version).
- **Error/audit framework loose files** (`BuildReportHeader.xslt`, `BuildSingleError.xslt`,
  `CreateAuditData.xsl`, `ScrubErrors.xsl`, `TrimToImportRequests.xsl`) - `BuildSingleError.xslt`
  teaches BATCH LINE-NUMBER RECONCILIATION: `Row_Number mod $batch.size` maps a Workday
  `wd:Import_Process_Message_Data/wd:Line_Number` back to the true source row.
- **Starter templates** (a client-derived "XSLT Templates" set) - boilerplate starters for
  DT delimited/fixed-length output, Core Connector Worker, PICOF (+ Time Off), EIB delimited/
  fixed-length output, and a copy-paste functions library (incl. signed-number handling). Fastest
  scaffold for a NEW transform; genericize any client residue before reuse.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Your local XSLT library path** - the folder holding the runnable pairs behind every section above (example - your paths differ; on the author's machine this is `Documents\xslt 3\`).
- **Related-corpora paths** - where the DIS pipeline set, the error/audit framework loose files, sample CLAR archives (Workday-delivered INT00xx references + firm/client examples; `.clar` = zip, readable without Studio), and the starter-template set live (author's machine: `Documents\Sample Integration Documents\DIS KSS Files\`, `Documents\Sample clar\`, and a client-folder `XSLT Templates\` set respectively - your paths differ). A typical library holds ~11 example folders (accumulator, three-way merge, iterate, fork, keys, for-each-group, counter loop, multi-doc/MDT, delimited parse, cross-file aggregation), an annotated "XSLT Samples" basics set, a multi-version Journal series, a streaming-comparison benchmark CLAR (`INT_XSLT3_Compare_Collection_0.clar`), `XTTDemo.clar`, `xttHelper1.xsl`, and source decks (KSS XSLT/ETV; "Replacing the Java Hashmap in Studio"); a `.zip` may duplicate the folders. Upstream home is typically a firm methodology library (e.g. a SharePoint "Methodology - XSLT 3" library). Example inputs carry demo/client-shaped data (student records, admissions outbound, burden journals) - treat as shapes, genericize before reuse in deliverables.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
