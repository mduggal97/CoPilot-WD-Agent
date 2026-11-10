# Calling external APIs (incl. GenAI/LLMs) from an Extend app

Two delivered invocation styles exist for calling a **truly external** endpoint, with a real
security trade-off between them. Both were verified in production apps (2026-08-05): a GenAI
project-feedback app (direct-from-page) and a badge-scanning app's Azure Translator
integration (flow-as-proxy).

Before reaching for either, check **Style 0** below: if the AI/ML you need is one of
Workday's own in-platform models (sentiment, skills extraction, document intelligence,
forecasting), the call never leaves the tenant - no key, no App Attribute, and the
data-egress gate does not apply. Only genuinely external services (OpenAI/Azure/etc.) need
Style 1 or Style 2 and the egress gate.

## Style 0 - Workday AI Gateway (in-platform ML, no egress)

Workday hosts a family of first-party ML services behind the same API gateway your app
already calls. These are **Workday-hosted models, not external LLMs** - the request and its
data stay inside the Workday trust boundary. Reach them either through the `workday-ml`
dataProvider or by building the URL off the gateway root, e.g.
`<% system.apiGatewayEndpoint() + '/ml/sentiment-analysis/v1/predict' %>`, and authenticate
with **`authType: sso`** - the caller's own Workday session. There is **no API key, no App
Attribute endpoint/secret, and no external hop** (per Workday App Catalog samples,
AI-Gateway; sample-verified).

Because the payload never leaves the tenant, **the data-egress gate below does not apply to
`/ml/` calls** - the whole "who can see the KEY / who can see the DATA / does the vendor log
prompts" analysis is moot for these. (Contrast: any OpenAI/Azure endpoint under Style 1/2
still runs the full gate.) A `/ml/` call is a normal in-tenant service call, so the only
governance is ordinary domain security on the caller.

```json
{ "name": "scoreSentiment",
  "url": "<% system.apiGatewayEndpoint() + '/ml/sentiment-analysis/v1/predict' %>",
  "httpMethod": "POST",
  "authType": "sso",
  "onSend": "<% return { 'text': commentWidget.value }; %>" }
```

Per-use-case recipes seen across the catalog samples (all under `/ml/...`, `authType: sso`):

| Use case | Service path | Request / notes | Sample |
|---|---|---|---|
| Sentiment scoring | `/ml/sentiment-analysis/v1/predict` | POST `{input_queries:[text], return_aspects}`; returns per-sentence sentiment + aspects (sample caps input at 512 words) | `sentimentAnalysisWithTheAIGateway`, `charitableDonationsWithSentimentAnalysis`, `employeeRecognitionWithTheAIGateway` |
| Skills extraction from free text | `/ml/skills-cloud/v1/extract` | POST `{output_format:'flat', text}` -> skill entities; pair with `/ml/skills-cloud/v1/gap-analysis` (`{doc_a, doc_b}`) to compare skills against a target set | `skillsMiningWithTheAIGateway`, `documentIntelligenceWithTheAIGateway` |
| Document intelligence (parse a file) | `/ml/docint/v1/{receipt\|resume\|generic}` | Body is the raw file as **`application/octet-stream`** (not JSON); pick the endpoint variant by document type | `documentIntelligenceWithTheAIGateway` |
| Forecasting a numeric series | `/ml/forecaster/v1/predict` | POST `{model_name:'holt_winters', forecast_params:{horizon,...}, data:{...historic_data...}}` -> forward projection | `forecastingWithTheAIGateway` |
| Natural-language -> WQL | `/ml/dataQuery/v1/` (root); `GET supportedDataSources?limit=100`, `POST genWql` | `genWql` onSend body `{queryData: <plain-English text>}` -> returns `{wql: <generated WQL string>}`; `supportedDataSources` lists which sources the generator supports. Both `authType: sso`. A sanctioned no-egress way to author WQL from plain English - useful as a query-builder surface for reporting work. | `generateWQL` (confirmed 2026-08-07) |

Note on look-alikes: the `recommendedReportsWithTheAIGateway` sample **declares** an ML provider in its
manifest but never actually calls a `/ml/` endpoint - its "recommendations" are WQL analytics,
not model inference. Declaring the provider is not the same as using the AI Gateway; confirm
there is a real `/ml/...` call before you describe an app as using in-platform ML.

**Citation currency (checked 2026-08-07 against the canonical DevRel App Catalog):** the `/ml/`
SERVICES above are all real, but some sample-app NAMES in the table are from an earlier catalog
snapshot and are not in today's public repo. Present-snapshot donors: `documentIntelligenceWithTheAIGateway`
(docint octet-stream), `charitableDonationsWithSentimentAnalysis` (sentiment), `documentIntelligenceWithTheAIGateway`
(skills gap-analysis `/ml/skills-cloud/v1/gap-analysis`), `generateWQL` (dataQuery). Not in the current
snapshot: `sentimentAnalysisWithTheAIGateway`, `employeeRecognitionWithTheAIGateway`,
`skillsMiningWithTheAIGateway`, `forecastingWithTheAIGateway` (the facts still hold - the citations drifted).
Confirm the donor name against the live catalog before citing it to a client.

**Calling the AI Gateway FROM A FLOW (not just a page) - confirmed 2026-08-07.** The table shows the
PAGE shape (`system.apiGatewayEndpoint() + '/ml/...'`, `authType: sso`). From an orchestration, use a
`SendWorkdayApiRequest` node with a RELATIVE `/ml/...` path (e.g. `s"""${"/ml/docint/v1/"}${data("SetDocumentValues","scanType")}"""`,
scanType = receipt|resume|generic), set `contentType` on the NODE (`application/octet-stream` for a file
body, `application/json` for a JSON body), and let it run under the flow's default
`AccessTokenFromInitiatingUser` credential - no key, no egress gate, same in-tenant guarantee as the
page. Canonical `documentIntelligenceWithTheAIGateway/orchestration/ScanDocumentOrchestration.orchestration`
(docint + a `/ml/skills-cloud/v1/gap-analysis` call). So docint/skills flows are reachable from O4I with
the standard Workday credential.

### AWS typed nodes (adjacent delivered surface)

Orchestrations also expose **typed AWS nodes** - `AwsLambdaInvoke`, `AwsS3*`
(get/put/list), `AwsEventBridge` - as a first-class, delivered integration surface (per
Workday App Catalog samples, sample-verified). Prefer these typed nodes when a service has
one; the manual **SigV4-signed `SendHttpRequest`** pattern (noted from DevCon) is the
**fallback layer** for AWS services that lack a typed node, not the default. For event-driven
inbound work, the round-trip is AWS -> your app's orchestration `/launch` endpoint (AWS calls
back into the app), completing an event loop rather than only pushing out.

### AI Widgets (Extend Pro - in-page generative AI, no egress)

A fourth in-platform AI surface available with **Workday Extend Professional**: **AI Widgets**
embed configurable AI prompts directly into an Extend page as a PMD widget, enabling instant
summarization or content generation scoped to fields on the page - without an external hop or
App Attribute secret. The data stays inside the Workday trust boundary, so the data-egress gate
does not apply (same principle as Style 0 `/ml/` calls).

Developer defines the prompt template; Extend Pro entitlement gates the capability. Announced
GA (Workday newsroom 2025-06-03; confirmed shipping in 2026 "next wave of agentic AI" blog).

**Design note:** AI Widgets are a DIFFERENT surface from raw `/ml/` endpoint calls (Style 0).
Use a raw `/ml/` call (table above) when you need programmatic control of the request/response
in an orchestration. Use an AI Widget when the AI interaction is user-facing and form-scoped -
the widget handles the UX, not you. Fallback if the client lacks Extend Pro: a richText field
+ a flow-proxy Style 2 call to an external LLM, with the egress gate applied.

(!) Exact PMD widget name + property schema: not yet in App Catalog samples as of 2026-08-28
audit - build-verify in-tenant before relying on a specific shape. Release-impact.md has the
full GA-status row.

## Where the endpoint + secret live: App Attributes

Both styles keep the external endpoint URL and API key OUT of source, in **App Attributes**
(`attributes/default.attributes`; schema in [model.md](model.md)) set per tenant by an admin:
`openAI_Endpoint`, `apiKey`, `subscriptionKey`, etc. Read as `attrstore.apiKey` /
`attrstore['openAI_Endpoint']` in PMD expressions, `attrstore.stringValue("subscriptionKey")`
in orchestration expressions. Never hardcode either in a PMD or flow.

## Style 1 - direct from the page (simplest, key visible to page maintainers)

A PMD outbound endpoint can call an ABSOLUTE external URL with custom headers and no
Workday auth (all three capabilities are easy to miss):

```json
{ "name": "callLLM",
  "url": "<% attrstore['openAI_Endpoint'] %>",
  "httpMethod": "POST",
  "authType": "noAuth",
  "headers": [{"name": "api-key", "value": "<% attrstore.apiKey %>"}],
  "onSend": "<% return {'messages':[
                 {'role':'system','content':'Generate feedback about an Employee'},
                 {'role':'user','content': generatePrompt()}],
               'max_tokens':500, 'temperature':0.7}; %>" }
```

GenAI specifics (Azure-OpenAI chat completions shown; same shape for OpenAI-compatible APIs):
- Response read as `callLLM.choices[0].message.content`.
- **Multi-turn from a page**: regeneration passes the prior answer back as an `assistant`
  message in `messages` - conversation state lives in page variables.
- The prompt is assembled in a page script (`generatePrompt()`) from live widget values,
  using markdown-ish section headers - treat prompt-building as a script function, not
  inline expression soup.
- When a page has multiple outbound endpoints and only one should fire per action, gate the
  others with `exclude` (see [pmd.md](pmd.md)).

**Trade-off:** the API key is readable by anyone who can maintain the app's attributes or
pages. Acceptable for low-sensitivity keys; not for credentials that gate real data.

## Style 2 - sync flow as secret-holding proxy (tighter; preferred for real credentials)

The page POSTs only business inputs to a sync orchestration's `/launch`; the FLOW holds the
secret and makes the external call:

- Flow reads inputs: `data.start.request.asJSON().stringAtJsonPath(...)` / `arrayAtJsonPath(...)`.
- `SendHttpRequest` with `auth: null` and header
  `Ocp-Apim-Subscription-Key = attrstore.stringValue("subscriptionKey")`.
- `EndSync` returns `data.<Node>.response` **verbatim** - the page consumes the external
  API's JSON as if it were the flow's own response.

The secret never reaches the browser or the PMD source; page maintainers see only the flow
name. The page<->flow bridge mechanics (`workday-orchestration` dataProvider, `/launch`
contracts) are in [pmd.md](pmd.md) and [orchestration.md](orchestration.md).

## Choosing

| | Style 1: page-direct | Style 2: flow proxy |
|---|---|---|
| Build effort | Lowest (one endpoint) | One extra sync flow |
| Key exposure | Page/attribute maintainers | Flow definition only |
| Response latency | One hop | Two hops (page->flow->API) |
| Use when | Demo/PoC, low-sensitivity keys | Production, real credentials, any PII in transit |

Default to Style 2 for anything client-facing. If Style 1 ships, record the exposure in the
design doc's security section as an accepted risk.

### `SendHttpRequest` needs flowVersion 3.3.0 - RESOLVED (Epic build, 2026-08-11; supersedes an earlier wrong note)

**Root cause of "external HTTP won't build in an Extend orchestration": the flow's `flowVersion`, NOT the app
type and NOT the flow type.** A `SendHttpRequest` node fails the build in a **`flowVersion` 3.2.0** orchestration
(instant "Build failed with errors", no validation detail) and builds cleanly at **3.3.0**. Confirmed in-tenant
(a dev tenant) by isolation: the SAME sync flow that failed 3/3 with a `SendHttpRequest` at 3.2.0 built on
the first try once bumped to 3.3.0 (only change). So:

- **An EXTEND app CAN call external systems from its own orchestrations** - no companion Integration app required.
  (Two intermediate conclusions this session were WRONG and are retracted: "Extend can't egress" and "sync flows
  can't egress." Both were an artifact of authoring the flow at 3.2.0.)
- **Style 2 above STANDS** - a page-launched sync flow (`StartBasic`/`EndSync`) can proxy an external call.
  Delivered proof: `badge-scanning/azureTranslator` is a `.maya.FlowSync` that POSTs to Azure Translator, at
  **flowVersion 3.3.0**. So a synchronous page->external->page round-trip (e.g. "validate an MRN against Epic
  before submit, from the page") IS achievable - it's a Style-2 sync flow at 3.3.0. (This also retracts the old
  "sync + external is impossible" line; what's genuinely not possible is a page getting a SYNCHRONOUS answer from
  an EVENT/BP-triggered flow - choose a sync flow when you need the round-trip.)
- **Delivered external-call flows span every flow type** (all carry `SendHttpRequest`): `badge-scanning/azureTranslator`
  = FlowSync (3.3.0); `int1271` = IntegrationFrameworkTrigger (3.3.0); `requestCreditCard` = BusinessProcessTriggered
  (3.0.0). The common factor is flowVersion >= the version that introduced the external-HTTP node schema, not the
  trigger. **Rule: author ANY flow containing `SendHttpRequest` at `flowVersion` 3.3.0**, and clone the whole
  top-level scaffold from a 3.3.0 donor (`badge-scanning/azureTranslator` for sync; `int1271` for event-triggered).
  Workday-only flows are fine at 3.2.0.

**Verified pattern shipped this session** (a delivered single Extend app,
deployed to a dev tenant): inbound = sync flow, Workday-only, maps an Epic case -> launches the app's own
`Submit_Requisition_Orch` via `/orchestrate/v1/apps/${context.appReferenceId()}/orchestrations/<Name>/launch` (reuse,
no re-keying); outbound + MRN-validate = external `SendHttpRequest` flows (3.3.0) attached to an integration system
in-tenant and triggered like any O4I. (An INTEGRATION-type app, separately, rejects sync `.maya.FlowSync` flows -
so if you ever DO split, external flows in the Integration app must be event/integration-triggered - but the split
is an org/lifecycle choice, never a technical requirement for egress.)

Reusable takeaways (unchanged / still valid):
- **Mock-mode toggle:** gate external calls behind a config flag (e.g. `EpicMockMode` default "yes") so a flow
  simulates the exchange with no external call - safe and demoable in a dev tenant. Reusable for any external PoC.
- **EHR specifics (Epic):** the exchange is **FHIR** (Patient search for MRN validate; a status message back);
  supply-chain inbound needs a **GTIN -> Workday-item** lookup.
- **Build system is FLAKY** - identical source can fail then build; retry a failed build 2-3x. A genuine schema
  error (like the 3.2.0 `SendHttpRequest`) fails 3/3 deterministically; a flaky failure passes on retry.

## Data-egress gate (before ANY external/GenAI endpoint ships)

**Applies to Style 1 and Style 2 only.** Style 0 (Workday AI Gateway `/ml/`) never leaves the
tenant, so this gate is moot for those calls - see Style 0 above.

Choosing Style 2 answers "who can see the KEY" - it does nothing for the DATA. The payload
leaves the Workday tenant either way, so this gate applies to **both external styles**:

1. **Enumerate every field sent** to the external endpoint - including everything a prompt
   builder like `generatePrompt()` interpolates from widget values. "The prompt" is a data
   export; treat it like one.
2. **Classify each field** per the design doc's data-classification pass (wd-design-doc
   `references/nfr-accessibility.md` section 5: PII / PHI / FERPA / none).
3. **PHI or FERPA to an external endpoint = Red item**: requires a vendor BAA (or FERPA
   agreement) plus explicit client sign-off before build - mirroring the nfr section 5 rule that
   PHI blocks design sign-off until the BAA dependency is confirmed. Not a yellow highlight;
   a stop.
4. **Record the egress in the design doc's Security section**: endpoint, vendor, fields
   sent, classification, mitigations. This record becomes the answer when the client's
   security questionnaire asks about external data flows (wd-deployment
   `references/security-questionnaire.md`).
5. **Ask the vendor-posture questions** and file the answers with the egress record: does
   the vendor log prompts/payloads? Retention period? Is customer data used for model
   training? What region does processing run in?

## The reverse direction: custom external UI over Extend

Everything above is Extend calling OUT. Workday also sanctions the opposite - an external,
user-facing app calling INTO Extend - per Workday/extend-js-example (official sample, MIT;
single commit 2023 - re-verify the console flow before client use). The shape:

- A browser SPA (the sample uses React + Workday's Canvas Kit for native look/feel)
  authenticates the END USER via **wd-auth Mode 4** (auth-code + PKCE against
  `auth.api.workday.com`; CORS solved by the API Client's own **Authorized CORS Domains**
  setting - no proxy needed) and calls the `api.workday.com` gateway as that user (`.../me`
  aliases work; tenant security/BP policies enforce authorization - client-side route
  guards are cosmetic).
- Three call surfaces demonstrated: **Graph API** (`POST /graphql/v1`, incl. a combined
  mutation initiating feedback + a one-time payment in one request - the BP side needs the
  op added as a **"(REST Service)" Initiating Action on the BP security policy**), **app BO
  REST at the gateway** (`/apps/<refId>/v1/...`, incl. the attachment multipart contract -
  model.md), and **external orchestration launch**
  (`POST /orchestrate/v1/apps/<appId>/orchestrations/<id>/launch`, bearer user token).
- Handy pattern: `.../<createOp>/values/<prompt>` endpoints return valid prompt options
  before a create - how an external UI populates its pickers legitimately.
- **Production deltas the sample itself flags**: sessionStorage token custody is
  education-only (move token handling to a backend-for-frontend), no refresh token (JWT
  expiry = re-login), no pagination/rate/`response.ok` handling - write those in before
  shipping anything client-facing.
- When the requirement is "external users touch the app," weigh this pattern against an
  Extend external site (SMD `siteAuth`) before committing - this one buys full UI freedom
  at the cost of owning hosting, token custody, and security review.

## The other inbound direction: an external LLM/chat over MCP (reference arch)

The section above is an external **UI** calling Extend as a human user. Workday also
sanctions an external **LLM/chat** reaching into the tenant over **MCP** - a distinct inbound
direction, and a sibling to the reverse-UI pattern above. The end-to-end reference shape (per
Workday/ai-conversation-bridge, official reference arch, Apache-2.0):

> chat connector (stateless webhook) -> **Flowise** (the customer-OWNED, customer-hosted LLM
> orchestrator - tool-first prompt, temperature ~0; hosting it yourself is the
> data-sovereignty driver) -> **MCP server** (`/mcp`, streamable-HTTP) -> Workday.

The LLM does not talk to Workday directly; it calls MCP **tools**, and the MCP layer executes
them against the tenant. This is the "chat/LLM over MCP" complement to the extend-js
"custom UI over Extend" reverse direction above - same trust question (an outside caller
acting inside the tenant), different client (a model, not a browser user).

**This repo is a reference architecture, not production**, and says so explicitly. In
production the demo's hand-rolled MCP server is replaced by **Workday's official MCP endpoints
fronted by the Agent Gateway**, which does the security work the demo skips: OAuth 2.1 / mTLS,
audit, and - critically - the **Gateway resolves the per-user identity from the token and
authz-filters every tool result** to what that user may see. The demo hardcodes a worker id;
production substitutes token-resolved identity. Other production deltas the repo itself flags:
prompt-injection defenses, PII output filtering, rate-limiting, and circuit breakers. Do not
ship the demo's server as-is to a client - treat it as the wiring diagram, and route real
traffic through the Agent Gateway.

Cross-reference: the Agent Gateway and Workday's native agent surface are in
[custom-agents.md](custom-agents.md); this MCP bridge is external-LLM-into-Workday, which is a
different surface from a Workday-native agent.

## Related

- Workday's NATIVE agent/AI surface (Agent Gateway, .agent/.agentskill) is different from
  calling an external LLM: see [custom-agents.md](custom-agents.md).
- In-tenant notifications from a flow (`POST /connect/v2/sendMessage`): [orchestration.md](orchestration.md).
