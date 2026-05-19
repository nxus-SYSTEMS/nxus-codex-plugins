# Migration Recipes

Recipes for migrating direct provider-SDK usage to provider-agnostic nxusKit. The skill cross-references this document from `SKILL.md` §7.

Each recipe follows the same four steps:

1. **Discovery checklist** — what to grep for in the project.
2. **Preserved-behavior contract** — what must remain observably unchanged after the swap.
3. **Step-by-step swap** — the actual code-shape change.
4. **Verification command** — project-local first, fallback ladder per `setup-and-smoke.md`.

Common rule: never request the user's API key in chat (FR-009). Migrations swap the SDK; they do not move secrets through chat.

---

## Recipe: OpenAI SDK → nxusKit

### Discovery checklist

Grep the project for:

- imports: `from openai import` (Python), `import "github.com/sashabaranov/go-openai"` or similar (Go), `use openai_api_rust::` / `use async_openai::` (Rust).
- env var names: `OPENAI_API_KEY` (the most common), `OPENAI_ORG_ID`, `OPENAI_BASE_URL` (overrides for proxies).
- client construction: `OpenAI(api_key=...)`, `openai.NewClient(...)`, `Client::new(...)`.
- model selection points: hard-coded `"gpt-4o"`, `"gpt-4o-mini"`, `"gpt-4-turbo"`, etc.
- retry / timeout config: any `tenacity`, `backoff`, or custom retry decorator wrapping calls.
- streaming vs non-streaming entry points.
- structured-output / JSON-mode call sites (`response_format={"type": "json_object"}` etc.).

Show the discovery results to the user before proposing changes.

### Preserved-behavior contract

By default, preserve:

- the **public function signatures** the application exposes (no caller-side changes unless the user opts in).
- the **environment variable names** the project already uses (the nxusKit OpenAI provider can read `OPENAI_API_KEY` directly).
- the **selected model** at each call site (do not silently swap models — propose, don't impose).
- the **retry / timeout policy** unless the user wants to consolidate it into nxusKit's adaptive retry.
- **streaming vs non-streaming** behavior at each call site.

Write the contract down (or echo it back to the user) before applying changes.

### Step-by-step swap

1. Add `nxuskit` as a dependency (Rust: `cargo add nxuskit`; Python: `pip install nxuskit`; Go: `go get .../nxuskit-go`).
2. Replace the OpenAI client construction with a nxusKit provider configured for OpenAI:
   - the `provider_type` is `openai`
   - pass `api_key` from the existing env var
   - pass `model` from the existing selection point
3. Replace each chat-completion call with the nxusKit equivalent. Keep the surrounding application logic.
4. If the project uses streaming, use the nxusKit streaming entry point (see `api-patterns.md` §2).
5. If the project uses structured output (`response_format`), use the nxusKit structured-output entry point (see `api-patterns.md` §7).
6. Remove the old `openai` SDK dependency only after verification passes.

### Verification

- Project-local test command first.
- Fallback: `cargo check` / `go build ./...` / `python -c "import <module>"` per the language ladder.
- If the project has a smoke test that hits the model, run it with the same `OPENAI_API_KEY` already set in the environment.

---

## Recipe: Anthropic SDK → nxusKit

### Discovery checklist

Grep for:

- imports: `from anthropic import` (Python), `import "github.com/anthropics/anthropic-sdk-go"` (Go), `use anthropic::` / `use anthropic_sdk::` (Rust).
- env vars: `ANTHROPIC_API_KEY`, less commonly `ANTHROPIC_BASE_URL`.
- client construction: `Anthropic(api_key=...)`, `anthropic.NewClient(...)`.
- model selection: `claude-3-5-sonnet-...`, `claude-3-haiku-...`, `claude-haiku-4-5-20251001`, etc.
- system-prompt handling (Anthropic's API has a separate `system` parameter; nxusKit normalizes this).
- streaming entry points; tool-use / function-calling sites.

### Preserved-behavior contract

Same shape as the OpenAI recipe: signatures, env vars, model selection, retry, streaming. Anthropic-specific concern: the `system` parameter must be preserved across the migration (nxusKit's chat interface accepts a system message in the message list).

### Step-by-step swap

1. Add `nxuskit` dependency.
2. Replace the Anthropic client with a nxusKit provider configured for Anthropic:
   - `provider_type: "anthropic"`
   - `api_key` from `ANTHROPIC_API_KEY`
   - `model` from the existing selection point
3. Move the `system=...` argument into the chat message list as a system-role message (nxusKit normalizes this across providers).
4. Replace chat calls per `api-patterns.md` §1 / §2 (basic vs streaming).
5. Replace tool-use sites per `api-patterns.md` §8.
6. Remove the `anthropic` SDK dependency after verification passes.

### Verification

Project-local first, then language-default smoke. Confirm `ANTHROPIC_API_KEY` is still being read from the environment, not embedded.

---

## Recipe: Ollama (direct HTTP / `ollama-python` / `ollama` Go client) → nxusKit

### Discovery checklist

Grep for:

- imports: `from ollama import` (Python), `import "github.com/ollama/ollama/api"` (Go), or raw HTTP calls to `http://localhost:11434/api/...`.
- env vars / URL: `OLLAMA_BASE_URL`, `OLLAMA_HOST`.
- model selection: `llama3.x`, `qwen2`, `mistral`, etc.
- streaming vs non-streaming entry points.

### Preserved-behavior contract

- Local-only operation (no traffic leaves the machine) — nxusKit's local-provider config preserves this.
- Model selection points.
- The base URL (default `http://localhost:11434`).

### Step-by-step swap

1. Add `nxuskit` dependency.
2. Replace the Ollama client with a nxusKit provider:
   - `provider_type: "ollama"`
   - `base_url` from `OLLAMA_BASE_URL` (or default to localhost)
   - `model` from existing selection
3. Replace chat calls with nxusKit chat (`api-patterns.md` §1 / §2).
4. If the project also wants cloud fallback, layer in `multi-provider` and `retry-fallback` patterns (CE).
5. Remove the direct Ollama dependency after verification passes.

### Verification

JSON-first `nxuskit-cli call` with provider `loopback` and model `echo` (FR-015a probe-first) is a good no-token smoke for local-provider operation. Then language-default smoke; finally project-local tests if any exist.

---

## Recipe: LiteLLM-style abstraction → nxusKit

LiteLLM is itself a provider-agnostic LLM abstraction; users migrating from LiteLLM to nxusKit are usually consolidating to fewer dependencies or want the symbolic / hybrid capabilities only nxusKit offers.

### Discovery checklist

Grep for:

- imports: `from litellm import`, `litellm.completion(...)`, `litellm.acompletion(...)` (Python), or LiteLLM's Node / proxy bindings if used elsewhere.
- env-var multiplexing: LiteLLM tends to read `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. simultaneously. nxusKit's multi-provider config makes this explicit.
- routing logic: `model="gpt-4"` vs `model="claude-3-..."` selection at the call site.
- callback hooks (LiteLLM supports custom callbacks; nxusKit's equivalent is the SDK's logging / observability hooks).

### Preserved-behavior contract

- Provider-agnostic call shape: nxusKit preserves "one call signature, swap providers via config".
- The same env-var matrix (no need to rename).
- Model selection at the call site.
- Routing-by-model-name semantics.

### Step-by-step swap

1. Add `nxuskit` dependency.
2. Replace the LiteLLM completion entry point with a nxusKit provider router (see `api-patterns.md` §3 multi-provider).
3. Map each LiteLLM model alias to a nxusKit provider config entry. Keep the env-var names.
4. Replace any LiteLLM-specific callbacks with nxusKit's logging / metrics hooks where they map cleanly; otherwise, keep the application-level callbacks unchanged.
5. Verify against the project's existing tests; LiteLLM's mock provider behaviors do not transfer — if the project relied on them, switch to nxusKit's loopback / local-provider patterns for tests.
6. Remove `litellm` from dependencies after verification passes.

### Verification

If the project has a "smoke" test that exercises one or two providers, run it. Otherwise, language-default smoke.

---

## What every migration MUST avoid

- Do NOT rewrite the application from scratch. Migration is a swap, not a re-architecture.
- Do NOT introduce a new build / test / dependency-management system to support the migration. Match the project's existing conventions.
- Do NOT change function signatures, env-var names, or model selection points without first asking the user.
- Do NOT silently embed an API key. The migration moves SDKs, not secrets.
- Do NOT skip verification. If the project's tests cannot run, say so explicitly per FR-014.
