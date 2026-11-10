# Provider Seam - one model-call interface, two swappable backends

This is the single most valuable pattern in `app-agentic`. Everything else
in the skill (the tool loop, spend metering, durable runs) calls the model
through ONE narrow interface. Which backend actually answers - Amazon Bedrock
or the Anthropic API direct - is chosen by CONFIG, never by a code change at
the call site.

Read this first. The rest of the skill assumes the seam exists.

---

## Why the seam exists at all

A hosted tool that hardcodes `boto3.client("bedrock-runtime")` at every call
site is welded to one provider. When you need to run the same tool on a laptop
without AWS credentials, in a client tenant that only allows Anthropic-direct,
or in a demo environment, you are rewriting call sites instead of flipping an
env var.

The seam collapses that to a factory decision:

- One interface (`ModelProvider`) that the agent loop, the metering layer, and
  every route depend on.
- Two thin implementations behind it (`BedrockProvider`, `AnthropicProvider`).
- One factory (`get_model_provider`) that reads config and returns the right
  one. Nothing else in the codebase names a concrete provider.

The blast radius of "switch providers" becomes exactly one function.

---

## THE corporate-TLS reason - why Bedrock is the default

This is the load-bearing insight, so it gets its own section.

**On a corporate-managed machine, the Anthropic Python SDK fails TLS certificate
verification while boto3 (AWS) succeeds - an empirically observed, reproducible
difference. Treat the EMPIRICAL FACT as the load-bearing insight; confirm the
exact mechanism in your own environment before repeating any one explanation as
gospel.**

Here is what is going on, and where to be careful:

- Most large enterprises run a **TLS-inspection proxy**. It
  terminates outbound HTTPS, re-signs each connection with a **corporate root
  CA**, and only that corporate root is trusted by the machine. The real
  upstream certificate is never what your process sees. Any client that does
  not trust that corporate root will get `SSL: CERTIFICATE_VERIFY_FAILED`.
- The Anthropic SDK is **httpx-based**, and httpx verifies against its own
  bundled CA store (certifi), which does **not** contain the corporate root -
  so it fails on the first call. The SDK is behaving correctly; it just cannot
  see the CA the proxy signed with.
- **Do NOT assume boto3 works because it "reads the OS system trust store."**
  That is a common but INACCURATE explanation: botocore ships its own vendored
  CA bundle (or uses certifi) and does **not** read the OS trust store by
  default (see https://github.com/boto/botocore/issues/2611). The real reason
  boto3 works behind a TLS-inspection proxy is almost certainly that the AWS client
  IS pointed at the corporate root - via an `AWS_CA_BUNDLE` env var / `ca_bundle`
  config setting that IT sets, an IT-repackaged botocore, or the proxy exempting
  AWS API endpoints. **Verify which** with `python -c "import botocore, ssl;
  print(botocore.__file__)"` + checking `AWS_CA_BUNDLE`/`~/.aws/config` before
  you rely on it.

So on-network, the AWS path is the one that works out of the box in practice.
That is why **Bedrock via boto3 is the default** and Anthropic-direct is
the alternative (fine for a machine outside the corporate proxy, or one where
the corporate root has been wired into the httpx path via `SSL_CERT_FILE` - see
the AnthropicProvider notes; do not use `REQUESTS_CA_BUNDLE`, which only the
`requests` library reads, not httpx).

Do not "fix" the Anthropic SDK path by disabling verification. That trades a
working default for a silently insecure one. The correct fix is to point the
client at the corporate root (`AWS_CA_BUNDLE` for AWS, `SSL_CERT_FILE` for the
httpx/Anthropic path). The seam exists so you can pick whichever client is
already correctly trusted in the target environment.

Two smaller consequences of choosing Bedrock worth knowing up front:

- **boto3 is synchronous.** Bedrock calls are slow I/O. In an async web
  framework, offload them off the event loop (for example
  `await run_in_threadpool(provider.generate, ...)`), rather than calling them
  inline and blocking every other request.
- **Bedrock needs cross-region inference-profile ids, not bare model ids** -
  see the registry section.

---

## The interface (invented, generic)

One method that matters: turn messages + tools into a normalized reply. Keep
it small. A wide interface is a wide thing to keep two backends agreeing on.

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class ModelReply:
    """Normalized reply shape both backends must produce.

    Deliberately provider-neutral: the agent loop reads THESE fields and never
    a raw Bedrock `output.message` or a raw Anthropic `content` block. Adding a
    backend later means mapping its native response onto this, not teaching the
    loop a third shape.
    """

    text: str                      # concatenated text blocks
    tool_calls: list[dict[str, Any]]  # normalized [{id, name, input}, ...]
    stop_reason: str               # "end_turn" | "tool_use" | "max_tokens" | ...
    input_tokens: int              # for metering (see agent-loop.md / SpendLedger)
    output_tokens: int


class ModelProvider(Protocol):
    """The ONE seam every call site depends on.

    Declared as a Protocol (structural), so a test can pass a hand-built fake
    with the same shape and neither real backend has to be imported to unit-test
    the loop. Concrete providers below are the only code that touches a vendor
    SDK.
    """

    def generate(
        self,
        *,
        model: "ModelId",
        system: str | None,
        messages: Sequence[dict[str, Any]],
        tools: Sequence[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> ModelReply: ...
```

Note the interface takes a `ModelId` enum member, not a raw id string. Call
sites say "give me Sonnet"; the provider maps that logical tier to whatever id
its backend actually needs. That mapping is the registry.

---

## The model-id registry (one-line enums)

One file is the only place a real model id appears. Onboarding a newly released
model is one added line; retiring one is a deleted line. Nothing else in the
codebase hardcodes an id, so the blast radius of a model change is this file.

```python
class ModelId(StrEnum):
    """Logical model tiers. Call sites name a TIER, never a vendor id."""

    HAIKU = "haiku"    # cheap/fast - prefilter, classification, cheap tool turns
    SONNET = "sonnet"  # the house default - most agent work
    OPUS = "opus"      # deepest reasoning - expensive, use deliberately
    TITAN = "titan"    # embeddings (Bedrock-only in this illustration)


DEFAULT_MODEL = ModelId.SONNET  # callers that do not care stay stable across a bump


# --- Bedrock: cross-region inference-profile ids (the `us.` prefix) ---------
#
# Bedrock requires the cross-region INFERENCE PROFILE id (the `us.` prefix) for
# on-demand throughput in us-east-2 - the bare foundation-model id would demand
# provisioned capacity. These strings are illustrative/generic; confirm the
# exact profile ids against your own account with:
#   aws bedrock list-inference-profiles --region us-east-2
_BEDROCK_IDS: dict[ModelId, str] = {
    ModelId.HAIKU:  "us.anthropic.claude-haiku-<ver>",
    ModelId.SONNET: "us.anthropic.claude-sonnet-<ver>",
    ModelId.OPUS:   "us.anthropic.claude-opus-<ver>",
    ModelId.TITAN:  "amazon.titan-embed-text-<ver>",  # embeddings: bare id, no profile
}

# --- Anthropic direct: plain model names ------------------------------------
_ANTHROPIC_IDS: dict[ModelId, str] = {
    ModelId.HAIKU:  "claude-haiku-<ver>",
    ModelId.SONNET: "claude-sonnet-<ver>",
    ModelId.OPUS:   "claude-opus-<ver>",
    # Titan is a Bedrock/AWS embedding family with no Anthropic-direct twin;
    # a provider that is asked for a tier it cannot serve raises, loudly.
}
```

KT note on the `us.` prefix: this catches people. A profile id that looks right
but is not a real profile (a mistyped suffix, a made-up "long-context" variant)
does not fail at config time - it 404s at CALL time, in production. Verify
against `list-inference-profiles`, do not infer the string.

KT note on context/output ceilings: tiers are NOT uniform. A small/fast tier
typically has a much smaller context window than the flagship tiers. Any
windowing math that assumes every tier holds the same budget is wrong the
moment it runs on the small tier. If you enforce input/output ceilings, key
them by `ModelId`, not one global constant.

---

## Backend A - Bedrock via boto3 (the default)

Thin. It maps the normalized request onto the Bedrock **Converse** API and maps
the Converse response back onto `ModelReply`. Converse is the right choice
because it gives one request/response shape across model families and
first-class tool-use - you do not hand-build a per-family `invoke_model` body.

```python
class BedrockProvider:
    """ModelProvider backed by boto3 bedrock-runtime + the Converse API.

    The AWS client is the one that works behind the corporate TLS proxy
    (via AWS_CA_BUNDLE/ca_bundle - see this file's TLS section),
    which is why this is the default. Synchronous, because boto3 is; an
    async caller offloads it to a thread.
    """

    def __init__(self, runtime: Any, *, region: str) -> None:
        self._runtime = runtime      # boto3.client("bedrock-runtime", ...)
        self._region = region

    def generate(self, *, model, system, messages, tools=None, max_tokens=1024) -> ModelReply:
        kwargs: dict[str, Any] = {
            "modelId": _BEDROCK_IDS[model],
            "messages": _to_converse_messages(messages),
            "inferenceConfig": {"maxTokens": max_tokens},
        }
        # boto3 rejects `system=None` / `toolConfig=None` outright - include a
        # key only when there is a value for it.
        if system is not None:
            kwargs["system"] = [{"text": system}]
        if tools:
            kwargs["toolConfig"] = {"tools": _to_converse_tools(tools)}

        resp = self._runtime.converse(**kwargs)  # slow I/O; offload in async code
        return _converse_to_reply(resp)
```

`_to_converse_*` / `_converse_to_reply` are small pure adapters (message-role
mapping, tool-spec shaping, pulling `usage.inputTokens` / `usage.outputTokens`
and the tool-use blocks out of `output.message.content`). Keep them pure and
unit-test them without a network.

---

## Backend B - Anthropic API direct (the alternative)

Same interface, different SDK. Use it off the corporate proxy, or where the
corporate root CA has been wired into the process trust store.

```python
class AnthropicProvider:
    """ModelProvider backed by the Anthropic Messages API.

    Alternative backend. On a corporate TLS-inspection network this typically
    fails cert verification (see this file's TLS section) unless the corporate
    root CA is on the process trust path (e.g. SSL_CERT_FILE) - which is exactly
    why it is the alternative, not the default.
    """

    def __init__(self, client: Any) -> None:
        self._client = client        # anthropic.Anthropic(...)

    def generate(self, *, model, system, messages, tools=None, max_tokens=1024) -> ModelReply:
        try:
            model_name = _ANTHROPIC_IDS[model]
        except KeyError:
            raise ValueError(f"{model} has no Anthropic-direct mapping")  # loud, not silent

        resp = self._client.messages.create(
            model=model_name,
            system=system or "",
            messages=list(messages),
            tools=list(tools) if tools else [],
            max_tokens=max_tokens,
        )
        return _messages_to_reply(resp)  # pulls text, tool_use blocks, usage, stop_reason
```

---

## The factory - config picks the backend, once

```python
from functools import lru_cache


@lru_cache
def get_model_provider() -> ModelProvider:
    """Process-wide provider, chosen from config on first use.

    This is the ONLY function that names a concrete provider. Everything else -
    the tool loop, the metering wrapper, every route - depends on the
    ModelProvider Protocol and never learns which backend answered.

    settings.model_provider is "bedrock" (default) or "anthropic". A deployment
    switches backends by changing that one value, never a call site.
    """
    settings = get_settings()

    if settings.model_provider == "anthropic":
        import anthropic
        return AnthropicProvider(anthropic.Anthropic(api_key=settings.anthropic_api_key))

    # Default: Bedrock. The AWS client is the one already trusted behind the
    # corporate TLS proxy in this environment (AWS_CA_BUNDLE/ca_bundle), where
    # the Anthropic httpx/certifi path cannot verify certs. See the TLS section.
    import boto3
    runtime = boto3.client("bedrock-runtime", region_name=settings.bedrock_region)  # us-east-2
    return BedrockProvider(runtime, region=settings.bedrock_region)
```

---

## What to remember

- **One interface, two backends, config picks.** Call sites depend on
  `ModelProvider`, never a concrete class.
- **Bedrock/boto3 is the default** because the AWS client is the one
  already trusted behind the corporate TLS-inspection proxy (via
  `AWS_CA_BUNDLE`/`ca_bundle`), while the Anthropic SDK's httpx/certifi stack is
  not - so the SDK fails cert verification. (It is NOT because "boto3 reads the
  OS trust store" - it does not; verify the real cause in your environment.)
- **The registry is the routing table.** One file, one line per model, `us.`
  cross-region inference-profile ids for Bedrock, plain names for Anthropic.
  Verify profile ids against the account - a wrong one 404s at call time.
- **Keep the normalized reply provider-neutral.** The loop reads `ModelReply`,
  not a raw vendor response. A third backend is then a new adapter, not a new
  shape everything downstream has to learn.
