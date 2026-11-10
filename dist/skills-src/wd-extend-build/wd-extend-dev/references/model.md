# Business objects, fields, BO REST API, security domains

## model/ file types (verified schema)

```
model/
  <Name>.businessobject    # {id, name, label, defaultSecurityDomains[], defaultCollection{name,label},
                           #  fields[], derivedFields[]}
  <Name>.securitydomain    # {id, name, enabledForPageSecurity, enabledForOrchestrationSecurity}
  <Name>.attachment        # BO with file storage
  <Name>.task              # {id, name, label, securityDomains[], routePath} - registers the app as a
                           #  searchable tenant task at a route (routePath "/" = app home). A PLAIN
                           #  launcher: no business object involved.
                           #  HOUSE STANDARD (MANDATORY): every app with a home page ships one - it is
                           #  the ONLY thing that makes the app show up in the tenant SEARCH bar and
                           #  launch its home. Without it the app is reachable by URL but INVISIBLE to
                           #  users (confirmed 2026-08-11: an expiry-tracking product was reachable by URL yet absent
                           #  from search until a "/" .task was added). Ship MULTIPLE .task files for
                           #  multiple entry points (one per landing route, each its own label -
                           #  e.g. "/" home + "/portfolioDashboard").
                           #  (!!) CLONE CAVEAT: `wdcli app copy` / porting source from an app built
                           #  BEFORE this standard inherits the ABSENCE - the home .task does NOT come
                           #  along for free. ALWAYS verify a home .task exists after app create/copy
                           #  and add one if missing (this is exactly how an expiry-tracking product missed it).
                           #  id space: pick HIGH values (90/91) to stay clear of BO ids - VERIFIED
                           #  2026-08-11 on a dev tenant: a .task id:90 built + deployed
                           #  clean alongside BO ids 1-4 and securitydomain ids 1-5, so high ints are
                           #  safe whether the id space is shared or per-artifact-type. Securing: list
                           #  ALL page-security domains a launcher persona could hold (OR semantics) so
                           #  every persona finds it - e.g. manager + specialist + admin page domains.
                           #  Adding a .task adds a new securable item, so re-run "Activate Pending
                           #  Security Policy Changes" after deploy or it stays hidden.
                           #  BUILD VALIDATIONS (build-verified Sep 2026): `name` must be UpperCamel
                           #  (E102 - "assetRequestHome" fails, "AssetRequestHome" builds); `label`
                           #  must start with an uppercase letter or a digit and hold only letters,
                           #  digits, spaces, hyphens and colons (E103 - no parentheses; use a hyphen).
                           #  Build+deploy verified 2026-08-06 and 2026-08-11. NOT the same as the tenant-side
                           #  "Create Custom Task" screen, which builds an INSTANCE-CONTEXTUAL launch
                           #  (asks for a Business Object; for related-action entry on a BO instance)
                           #  - wrong tool for a plain app entry point. See wd-deployment R12.
  <Name>.businessprocess   # custom BPs (see model-bp.md)
```

- `.securitydomain` `enabledForPageSecurity` / `enabledForOrchestrationSecurity` are the model half of a pair: they take effect via page-level `securityDomains: []` on PMDs (pmd.md) and flow-level `securityDomains: []` on `.orchestration` roots (orchestration.md).

## Other source file types (per Workday App Catalog samples)

The samples surface source artifact types beyond the `model/` and `presentation/` files we build daily (sample-verified - above doc-sourced, below build-verified; build-verify a type before shipping it):

- **`.report`** - a BO-backed report definition IN the app source (`columns`, `sortConfigs`, `isSelfReferencing`). This removes the "reports promote separately" gap for BO-sourced reports: a report defined this way ships and promotes WITH the app, no separate report-writer promotion step.
- **`.graphquery`** - GraphQL queries AND mutations against app data. Portability gotcha: the generated type/field names embed the app referenceId and are HARDCODED in the query text, so a `.graphquery` does NOT survive `app copy` / refId change without a find-replace. Prefer WQL where portability matters.
- **`.wqlquery`** - externalized reusable WQL (already documented under `presentation/wqlQueries/` in pmd.md and efficiency.md; listed here for completeness of the source-type map).
- **`.mock_response` + `.mock_config`** - endpoint mocking: canned responses so pages/flows build and demo without the live endpoint. ALSO cross-ref wd-testing - this is the sample-verified way to stub an integration during unit test / demo staging.
- **`.carddefinition` + `.cardtenantsetting`** (top-level `cards/`) - a TENANT home-page / worklet card (the tile a user pins to their Workday home), DISTINCT from `presentation/cards/*.card` (the in-app `cardContainer` template - see pmd.md "Cards & hub pages"). Don't confuse the two `cards/` locations.
- **`presentationLabels/<locale>.properties`** - native i18n string bundles (key=value per locale). Read in a page as `<% presentationLabels.<Key> %>`. This is the platform-native alternative to the custom Translation-BO pattern (pmd.md) - weigh it before hand-rolling a translation store.

**Custom objects as a BO alternative (per Workday App Catalog samples `giftRegistry` / `cloudCommute`):** some samples put the Extend UI/flow layer over TENANT custom objects (the `workday-custom-objects` provider) instead of Extend BOs - upsert via `?updateIfExists=true&bulk=true`, composite delete via a `;item=` key segment. This is a design ALTERNATIVE to modeling `.businessobject`s: reach for it when the data must ALSO be reportable/usable as a native tenant custom object outside the app; stick with Extend BOs when the data is app-private. Sample-verified; build-verify the provider/URL grammar before committing an app to it. **(official-docs - developer.workday.com, 2026-08-25):** the v2 grammar is now officially documented (Custom Object REST APIs v2): `?bulk=true` create max 200 items, `?updateIfExists=true` upsert, compound-ID addressing/delete `{businessObjectID};{referenceId}={value}`, `x-validate-only: 1` dry-run, and effective-dated custom objects are SOAP-ONLY (REST unsupported). This UPGRADES the URL/param grammar from sample-verified to official-docs; behavior (and the 100-vs-200 bulk cap - see rest-api-catalog.md reconciliation) still warrants an in-tenant build-verify before committing an app to it.

## App Attributes source file - `attributes/default.attributes`

App-level attributes are a first-class source artifact, not just tenant setup: `attributes/default.attributes` is an array of `{name, type: "string"|"boolean"|"numeric", alias}`. Values are set per tenant (App Attributes task) and read at runtime as `attrstore` from BOTH pages and orchestrations - read syntax in pmd.md and orchestration.md. Good practice verified in a delivered production app (2026-08-05): store the SOAP API version as an attribute so a release-impact bump is a tenant config change, not a redeploy.

- **`appProperties` vs `attrstore` - two different constant stores (per Workday App Catalog samples):** `appProperties` (declared in the AMD, read as `site.appProperties.<X>`) are SOURCE-CONTROLLED constants - same value in every tenant, changed only by a redeploy. `attrstore` (App Attributes, above) is PER-TENANT config, changed without a code change. Rule: an environment-invariant constant belongs in `appProperties`; anything a tenant admin should tune (URLs, keys, limits, feature flags) belongs in App Attributes.

## Field types

TEXT / DATE (`precision`: DAY or SECOND - SECOND = full timestamp) / BOOLEAN / INTEGER / CURRENCY (`{value, currency}` JSON; `value` comes back as a STRING) / SINGLE_INSTANCE (`target` = another BO name or a Workday type) / MULTI_INSTANCE / derivedFields with `expression`. Reference-ID text fields via `isReferenceId: true`.

- **Verified SINGLE_INSTANCE targets that build:** LOCATION, PURCHASE_ITEM, WORKER, LEARNING_CONTENT, LEARNING_ENROLLMENT, PROJECT, FEEDBACK_TEMPLATE (the last four verified in delivered production apps, 2026-08-05), and BO-to-BO (e.g. `target: "ExpiryTransaction"`). MULTI_INSTANCE target WORKER verified (multi-assign).
- **DECIMAL declaration shape (per Workday App Catalog samples):** `{"type": "DECIMAL", "decimals": 1}` - the `decimals` prop fixes scale; an optional `description` prop documents the field. Read-back is a STRING, not a number (serialization asymmetry note under the BO REST API below).
- **`secureByTarget: true`** field prop (per Workday App Catalog samples) - scopes the field's visibility by the target instance's own security rather than the app domain alone; sample-verified shape, build-verify before relying on it as a security boundary.
- SINGLE_INSTANCE GET returns `{id, descriptor}`; writes accept `{"id": <WID>}`.
- **A STORED-null SINGLE_INSTANCE reference crashes the collection GET serializer** (verified 2026-08-25): a BO with a SINGLE_INSTANCE field that no create ever populates POSTs fine, but GET on the collection returns null/crashes the page when it hits a record with the null reference. Never ship a SINGLE_INSTANCE field you don't populate on EVERY create path; if the reference is genuinely optional, prefer a TEXT id/name field. (Distinct from pmd-gotchas #12, which is about SENDING JSON null on POST.)
- **Descriptor-snapshot-as-TEXT - the recommended way to persist a reference you only need to display/filter on** (verified in two delivered apps, 2026-08-26): instead of a SINGLE_INSTANCE field, capture the referenced instance's WID/descriptor into a TEXT field at write time. Two wins: one clean POST (no two-step parent/child create), and it sidesteps the stored-null-crashes-GET landmine above. The snapshot WID then drives child reads as a reference-field filter. Reach for a live SINGLE_INSTANCE link only when you need the platform relationship (related actions, cascading security), not just the id/label. Full load/read context: [data-loading-and-retrieval.md](data-loading-and-retrieval.md).
- **Removing a reference field strands ZOMBIE records** (verified 2026-08-25): instances created while a since-removed SINGLE_INSTANCE field existed stay in the index but can no longer be GET-serialized, throw `DuplicateIndexException` on re-insert of the same values (corrupted index entries), and cannot be recovered or deleted via the API. Recovery = point the app at a FRESH collection name (a schema-change deploy that can't migrate the old collection may also return `Success: false` - the fresh name clears that too). See dev-tenant-migration.md for planned migrations; this is the unplanned-failure variant.
- **Tenant calculated fields (`cf_*`) can be created in-tenant AGAINST an Extend BO** and consumed through the BO's WQL data source. They never appear in the `.businessobject` file - a WQL query selecting `cf_*` fields is not a source bug (but IS per-tenant setup to record in the design doc / tenant-setup list). WQL on Extend BOs also supports nested related-object projection, e.g. `learningEnrollment{learner, cf_learnerPhoto} as learningEnrollment`. Verified in a delivered production app (2026-08-05).
- **`isReferenceId: true` enforces GLOBAL uniqueness across the app - not per-parent.** A per-parent numbering scheme (two parents each containing "M000001") 500s with `DuplicateIndexException: Duplicate insert` on the second insert. If values can repeat across parents, don't flag the field as a reference id (keep it indexed/searchable instead); dropping the flag is a redeploy-safe change (verified in a delivered build session, 2026-08-05). **Prefer auto-generated ids over client-supplied ones** (2026-08-25): in a delivered app the only BO whose page POSTs silently failed to persist was the only one with an `isReferenceId` field receiving a custom id in the payload; every working POST targeted BOs with no isReferenceId fields and sent NO id (Extend auto-generates). Fix bundle that shipped: drop the flag, drop the id from the payload, fresh collection name (partially entangled with the zombie-record issue above - suspected-to-partially-verified).
- **[BV 2026-09-04] Security-domain NAMING validations S101/S102:** a `.securitydomain` may not share a name with a BUSINESS OBJECT (S101) or with any BO's DEFAULT COLLECTION - case-insensitively (S102). Older deployed apps pre-date the rule (their source fails a FRESH build unchanged), so any clone/port of an older app must rename such domains (e.g. `VendorCardType` domain beside a `VendorCardType` BO -> `ManageVendorCardTypes`) and update every reference: BO defaultSecurityDomains, `.task` securityDomains, page-level securityDomains, cards.
- **[BV 2026-09-04] More verified targets:** MULTI_INSTANCE `JOB_PROFILE` and `LEARNING_CONTENT` build; `enableIndex: true` IS accepted on a SINGLE_INSTANCE field (built on two fields). Generic `ORGANIZATION` and `SECURITY_GROUP` are NOT valid targets (B300) - use the descriptor-snapshot-as-TEXT pattern (WID|descriptor lists) for those dimensions.
- **[BV 2026-09-04] `.attachment` BOs declare METADATA ONLY** - the platform adds binary storage implicitly plus delivered filename/fileLength/contentType (which is why those names are reserved); do not declare your own file-size/name fields.
- Build gates (verified in a delivered build session, 2026-08-05): a BO's top-level `id` must be unique across ALL BOs in the app; `enableSearch` is allowed on max 3 fields app-wide (Validation Error A100 above that).
- Field labels (E103): alphanumeric, space, hyphen, colon only.
- Field names that collide with reserved words (`site` etc.) cause script-file grief - avoid.

### BO field build constraints (`.businessobject` compile-time)

Each of these fails the model compile - and the compiler failure is a bare, unhelpful **"model failed compilation"** with no line detail in the wdcli output, so isolate by diffing against a known-good BO (e.g. the same BO in a sibling app).

- **[BV] A `.businessobject` field object rejects a `"_comment"` key.** PMD tolerates `_comment` everywhere; BO field definitions do NOT - a single `_comment` inside a field object breaks the model compile. Put KT notes in the design doc or a top-of-file note, never inside a field object.
- **[BV] The display field (`useForDisplay: true`) is effectively IMMUTABLE after BO creation.** Moving it (setting the old display field `false` + a new field `true`) also fails the compile. Leave the original display field as-is and add new fields with `useForDisplay: false`; drive any display/label logic in the page grid (e.g. `!empty row.name ? row.name : (row.a + ' -> ' + row.b)`) instead of relying on the BO display flag. (Consistent with the additive-only rule 6 below - existing field metadata is not freely editable on a deployed BO.)
- **[BV] A BO allows at MOST ONE `CURRENCY` field** - two or more `CURRENCY` fields fail the build deterministically (one builds). Store extra monetary values as TEXT (CURRENCY serializes as a string anyway).
- **[BV] The field name `unitPrice` is rejected** even as a lone `CURRENCY` field (a reserved/delivered name); `unitCost` builds fine. This is not a field-count cap - many all-TEXT fields build.
- Additive field changes are safe: appending new fields (next sequential id) deploys cleanly (existing rows read null for the new fields, so pages must null-guard). See the additive-only rule 6 and the change-a-field-shape recipe below.

## Auto-generated BO REST API

`https://api.workday.com/apps/<refId>/v1/<collectionName>` (region-direct: `api.us.wcp.workday.com`).

- GET collection -> `{data[], total}`; GET instance -> fields at top level (no `.data`).
- POST create, PUT full-replace (send the COMPLETE payload - anything omitted is cleared), DELETE per instance (a parent delete 500s while ANY child row still references it via SINGLE_INSTANCE - delete children first, or design soft-delete/status flags instead of hard deletes; bulk flow pattern below).
- **PATCH = partial update** (only the fields sent change) - verified in delivered production apps (2026-08-05). Prefer it over PUT when back-writing a status field so you can't accidentally clear the rest of the record.
- **Bulk PATCH and bulk DELETE via `?bulk=true`** on the collection URL, body = an array of instances (typically sent in batches of ~100 from an orchestration BatchLoop). To bulk-DELETE children referenced by a parent's SINGLE_INSTANCE, PATCH the parent to drop the reference FIRST, then bulk-DELETE - otherwise the dependency 500 above bites.
- **Bulk CREATE via `?bulk=true` POST** - the same switch works on POST, but the body is wrapped: `{"data": [ ... ]}` (a `data` object, NOT the bare array that bulk PATCH/DELETE take). BUILD-VERIFIED 2026-08-25: a bare array fails deserialization, and >100 items returns `statusCode 400, code S25, "This operation is limited to 100 instance updates at a time"` - the hard cap is 100 per call, batch on the caller side (from a page: cascading forEach, pmd-gotchas #6; from a flow: BatchLoop `iterator("$.data[*]", 100)`).
- Instance addressing: by WID (`/v1/<collection>/<WID>`) or **by reference ID** - `/v1/<collection>/<RefIdType>=<value>` (RefIdType is typically `<AppRefIdCapitalized>_<BOName>_ID`); handy for well-known config rows with `isReferenceId` keys.
- `limit` 1-100 only (the BO REST collection limit; headline + error mode owned by pmd-gotchas.md #15) - and the cap **silently truncates**: a collection GET in an orchestration/page that reads-all-then-filters loses every row past 100 with NO error (verified 2026-08-06: a 111-line collection import dropped the tail rows). **Filter server-side by a reference field instead**: `?<fieldName>=<WID>` works (e.g. `blueprintTasks?blueprint=<id>` returns only that parent's rows); the dotted form `?<fieldName>.id=<WID>` does NOT filter - it silently returns the unfiltered first 100. Rule: filter at the query, never read-all-then-filter. **Query-param filtering works for REFERENCE fields ONLY**: a TEXT-field param (`?roomName=value`) is SILENTLY IGNORED - unfiltered data comes back with no error (verified 2026-08-25). For text criteria: fetch + client-side filter, or WQL where the BO is actually indexed (next bullet).
- **WQL is NOT guaranteed to index an app's BO instances** (verified 2026-08-25): `SELECT ... FROM <collectionDataSource>` returned 0 rows while the BO REST collection GET returned every item - in that app ALL pages reading own-BO data had to switch to REST. WQL and BO REST are separate paths (`/api/wql/v1/` vs `/api/apps/{appRefId}/v1/`); a BO can be REST-readable but absent from WQL and vice versa. Rule: for reading YOUR OWN app's BO instances from pages, default to the BO REST collection GET; treat WQL-on-custom-BO as verify-per-app before building on it (this nuances the "BO data auto-publishes WQL data sources" claim elsewhere - publication is not guaranteed/immediate).
- ISO timestamps accepted, normalized to UTC.
- **Attachment-field BOs (per Workday/extend-js-example, official sample):** create = one multipart `FormData` POST with part `data` (the JSON metadata, attachment field set to **`"file": "cid:attachment"`**) + part `attachment` (the binary, with filename). Do **NOT** set Content-Type on the request - the browser/client must supply the multipart boundary (explicitly setting it fails). Optional header `x-wd-image-max-dimension: <px>` server-side-resizes images on upload. **Instance GET on such a BO returns the BINARY** (consume as blob), while the collection GET returns JSON metadata - don't assume JSON per-instance.
- **Serialization typing asymmetry: DECIMAL fields come back as JSON STRINGS; INTEGER fields as JSON numbers** (verified in a delivered build session, 2026-08-05). Consequences downstream: an orchestration's `numberAtJsonPath*` on a DECIMAL fails at render ("Expected number but found string"); PMD `+` on a DECIMAL string-concatenates. Read decimals as strings and coerce where arithmetic is needed (see orchestration.md and pmd.md). If a numeric field will feed orchestration arithmetic or bulk-body templates, consider modeling it as INTEGER where the domain allows.
- **STANDARD - design data retention + export/purge into any record-ACCUMULATING app, from day one.** Custom BO instances pile up and Extend caps how much custom-object data an app/tenant holds (official-docs, Workday Extend for Developers course manual, 2026-08-25: **10M instances per TENANT, shared across ALL Extend BOs** - plus per-BO caps: 50 fields, 40 derived fields, 5 indexable regular fields, 10 combined SINGLE+MULTI_INSTANCE fields; 25 delivered-object-target fields and 10 security domains per APP. Verify against current docs at design time; treat the tenant ceiling as a real shared budget, not just a perf concern). A high-volume transactional BO (an expiry-line, transaction log, audit row at 10^5-10^6 rows/yr) WILL hit it. The answer, sized as its OWN build/LOE line (never folded into "orchestrations"): a scheduled **export** that offloads aged rows to a durable sink (Prism / a RaaS custom report / SFTP / document store - the auto-published WQL data sources make BO data queryable for the extract), then a **purge** (bulk-DELETE via `?bulk=true`, children-before-parents per the dependency rule above) of the exported rows, gated by an admin-set **retention period** (a Config field or App Attribute) plus, for compliance-relevant data, a hold/approval before purge. This is BOTH a compliance inclusion (proposal-content treats retention export/purge as standard) AND the mechanism that keeps the app under the object ceiling. Put it on the design's Technical Spec orchestrations + an Open Item for the export target/format and purge schedule/gate. (Flagged 2026-08-11 on an expiry-tracking product: `retentionPeriodDays` config + `dataRetention{Export,Purge}Flow` were designed but the LOE folded them and the object-limit rationale was unstated - both are the standard.)

## Official BO limits & reserved field names (official-docs - Workday Education course manuals, crawled 2026-08-25; spot-verify load-bearing numbers in-tenant)

(The 10M-instances-per-tenant ceiling and the per-BO caps are already folded into the retention STANDARD above - not repeated here.)

- Reserved / restricted field names - three tiers (naming a field one of these fails or misbehaves):
  - Case-SENSITIVE reserved: attachmentContent, contentType, descriptor, displayID, filename, fileLength, id, wid, workdayID.
  - Case-INSENSITIVE reserved (WQL keywords): select, from, where, limit, order, having, group, by, asc, desc, as, and, or, not, is, null, empty, in, datasourcefilter, entrymoment, effectivemoment.
  - Additionally banned on SINGLE_INSTANCE / indexed fields (case-sensitive): offset, bulk, search, sort, type, view, name.
- secureByTarget is allowed on only ONE field per business object definition (extends the secureByTarget shape note above).
- MULTI_INSTANCE sizing guidance: keep the instance count per MULTI_INSTANCE field below 1,000 (performance recommendation, not a hard limit). MULTI_INSTANCE fields cannot carry enableIndex, secureByTarget, or useForDisplay; not indexed; no contextual security.
- Attachment limits: 10 MB max per file (fileUploader maxFileSize default 10,485,760 bytes, range 1-10,485,760); 5 files per upload session; 50 MB total per upload session; 10 million attachment instances per tenant. fileUploader = POST endpoints only. Multipart ordering matters: JSON part BEFORE the file part, or the call returns a 500.
- Extend business objects do NOT support effective dating (stated flatly in the manual).

## Security domains - the S22 rule

**After first deploy to ANY tenant, BO data access returns `permission denied` (S22) until a tenant admin grants the app's security domains**: Domain Security Policies for Functional Area -> app name -> edit permissions -> add security group with View+Modify and Get+Put integration permissions -> Activate Pending Security Policy Changes. Page-level access works before this; data calls don't. This recurs on every new tenant and every `app copy` (new identity = new grants). Design domains role-aligned (e.g. ManagePages / SpecialistPages / Data) so grants map to client role groups cleanly. When you hit S22 right after a deploy and want the grant DONE in a dev/sandbox tenant (not just documented), the **wd-tenant-config** skill drives this live in the browser (the grant + Activate Pending are security commits it hands to you, then reads back that S22 is gone); the recipe content is wd-deployment tenant-task-recipes R1/R2. Two-domain (Pages + Data) with persona-split page domains is the norm.

**Row-level security is in-app / display-only (MED-HIGH).** "You only see your own projects/tasks" filtering is a nested-membership filter in the PAGE, not domain-enforced - the auto-generated Extend BO REST is not row-aware, so a determined BO-REST caller can reach across rows. Don't rely on page filtering as a data-security boundary. For a Marketplace/BoW product, either record this as an accepted limitation or harden it with BP/domain controls (a delivered O4I app recorded it as an accepted limitation).

## Design-time checklist when adding/changing a field

1. Null guards on every page/report that reads it (pre-existing records have it null - see pmd-gotchas #7/8).
2. Backfill plan (PUT loop) or explicit "old rows excluded" decision recorded as a design open item.
3. Every create/update path sets it - **BOOLEANs especially: an UNSET boolean on POST or full-replace PUT stores `false`, not null** (verified the hard way, 2026-08-05). If the boolean is a visibility/soft-delete gate (e.g. `active` where false = hidden), any create or PUT that omits it makes records SILENTLY VANISH from every filtered list. Rule: set it explicitly on create (`active: true`) and carry it on every edit PUT (`'active': (empty a.active ? true : a.active)`). **Adding a soft-delete boolean is a cross-cutting change: grep EVERY POST/PUT body in the app (pages, flows, imports) for the field before shipping.** Symptom map (verified 2026-08-25): the failure often surfaces FAR from the data - e.g. config rows loaded without their Active flag produced a downstream "no active configuration" functional error on a different page; when a filtered read comes back empty, check the gate boolean on the source rows before debugging the reader.
4. PUT is full-replace: every existing PUT payload in the app must now carry the new field forward.
5. Update the design doc Object Model tab (wd-design-doc) in the same change.
6. **Model changes must be ADDITIVE - append new fields at the END; never insert, reorder, or remove a field on a deployed BO.** Inserting/reordering/removing renumbers existing field IDs and makes redeploy fail with **"Error 10: duplicate metadata"** (the App Builder UI shows the real cause; wdcli MASKS it as `Cannot read properties of undefined (reading 'success')` - see wdcli-workflow.md). Field IDs must stay stable across redeploys.
7. **Verify the change is LIVE by writing a record with the new field over REST (MED-HIGH).** The tenant can keep serving the PRIOR build while the CLI reports "success"; the definitive check is POSTing a record that uses the new field and seeing it accepted (vs. an "unrecognized field" S5). A DEV tenant serves the latest build immediately.

### Changing a field's shape on a live BO (type/target changes)

A field that must change type or SINGLE_INSTANCE target: **NEVER repurpose it in place.** Deployed-BO fields can't be removed (rule 6), so the recipe is:

1. **Append** a NEW field (at the end, per rule 6) with the correct type/target.
2. **Migrate** existing data into it - bulk PATCH loop (`?bulk=true`, ~100/batch) via a one-off sync flow or conversion script.
3. **Dual-read window** - readers fall back while the migration runs: `newField ?: oldField` in scripts/pages.
4. **Deprecate the old field in place** - stop writing it, mark it deprecated in the `.businessobject` comment/label and the design doc Object Model tab. It stays in the schema forever; that's the cost of a live BO.

### (!) confirm - metadata changes on POPULATED BOs (unverified)

Which metadata edits redeploy cleanly over a BO that already holds data is only partly build-verified. **`defaultSecurityDomains` changes: VERIFIED 2026-11-05** on a dev tenant (two populated BOs, 4 and 2 rows, re-pointed from their own domains to the app's main domain; build succeeded into the existing version, rows identical before and after, no pending security change, no activation needed, and a user without the old domain could read the records through the page at once). Label changes and `derivedField` expression changes are still unconfirmed. Treat these as unverified defaults - **the only safe assumption is additive-only** (new fields appended at the end). Before relying on any in-place metadata edit for a live app, build-verify it on a DEV tenant with populated records first (and use rule 7's REST write check to confirm the build is actually serving).

## Calculated field type selector
> Folded in from a config-guide distillation sweep (2026-08-10). Vendor-neutral; no client specifics.
> Owner for the calc-field-type reference across the suite; wd-integration-dev points here.

Compact "which calculated-field type do I use" table for Workday calc fields (applies equally to
Extend page/orchestration logic, reports, integrations, and time/absence calcs):

| Type | Use it when you need to... | Returns |
|---|---|---|
| Extract Single Instance | Pull ONE instance from many, filtered by a True/False condition and sortable to pick the exact one | Single-instance field |
| True/False | Evaluate a Boolean condition on the current business object; typically nested inside another calc field | Yes / empty |
| Look Up Related Value | Reach a value on a business object ONE hop away from the current object | Value from the related object |
| Sum Related Instance | Total a numeric field across related instances, optionally gated by a True/False condition | Number |
| Count Related Instance | Count related instances, optionally gated by a True/False condition | Number |
| Aggregate Related Instance | Concatenate related values into one list, de-duplicated | Multi-instance field |
| Evaluate Expression | Return different results for different cases off the SAME object; the standard bridge into a calc/eval engine | Result of the matching branch |
| Extract Multi Instance | Pull a multi-instance field from a set of them, filtered by a True/False condition | Multi-instance field |
| Format (Date / Number / Text / Substring) | Reshape or convert a value - case change, concatenation, date/number formatting, substring, date math (Build/Difference/Increment) | Text/date/number |

Quick routing: one object away -> Look Up Related Value; pick one of many -> Extract Single/Multi
Instance; how many / total -> Count / Sum; list them -> Aggregate; branching result or engine
bridge -> Evaluate Expression; Boolean gate -> True/False (nest it). Date Difference rounds DOWN to
the nearest whole unit.

CROSS-CUTTING CALC-FIELD GOTCHA (multi-job "block-create lands on the wrong position"): when a
worker holds multiple concurrent jobs/positions, a calculation that CREATES a new derived block
(e.g. an auto-generated meal-break deduction) attributes that created block to the worker's PRIMARY
position - even when it was generated from a block tagged to a non-primary position. Avoid
create-style calcs in multi-position scenarios; instead tag the source blocks and use
threshold/overtime-style calcs so the derived amount stays on the correct position. More broadly,
calc fields that must feed a pay/eval engine generally have to sit on the WORKER object, which means
they can tell you IF any position meets a condition but not always WHICH position - design around
that limitation rather than fighting it.
