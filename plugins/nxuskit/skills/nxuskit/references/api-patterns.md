# API Patterns

Catalog of recurring nxusKit SDK patterns the skill recommends. Each pattern names: the user intent, the canonical example name (cross-reference into `example-index.md`), the high-level shape of the integration, and notes on credentials and verification.

The skill MUST prefer linking to a canonical example over inventing code. Use this catalog to choose the right starting example, then defer to the example's source for the actual code.

For language-specific setup and credentials, see `setup-and-smoke.md`. For tier classification, see `tier-guide.md`.

---

## 1. Basic chat (CE)

- **Intent**: send a prompt, receive a response.
- **Canonical example**: `basic-chat`.
- **Shape**: build a provider config (env-var-driven), open a chat session, send a single user message, read the response.
- **Credentials**: provider API key from environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, …) or a local provider URL. Never embedded in source.
- **Verification**: language-default smoke from `setup-and-smoke.md`. With a configured provider key, `cargo run -p basic-chat` (or analogous) produces a single response.

## 2. Streaming chat (CE)

- **Intent**: stream tokens as they are generated rather than waiting for a complete response.
- **Canonical example**: `streaming`.
- **Shape**: like basic chat, but the response is consumed as a stream / async iterator. Print or accumulate tokens incrementally.
- **Credentials**: same as basic chat.
- **Companion patterns**: `retry-fallback`, `multi-provider`. Recommend layering streaming on top of those for production-quality code.
- **Verification**: short stream from a small prompt; confirms transport works and tokens arrive without buffering.

## 3. Multi-provider routing (CE)

- **Intent**: same application code runs against OpenAI, Anthropic, Ollama, etc. by changing configuration.
- **Canonical example**: `multi-provider`.
- **Shape**: maintain a registry of provider configs (read from environment or config file); pick at runtime by environment, cost, or capability. The application code talks to the SDK's unified interface.
- **Credentials**: each configured provider needs its own env var.
- **Companion**: `cost-routing` (selection by cost), `capability-detection` (selection by feature).

## 4. Cost-aware routing (CE)

- **Intent**: prefer the cheapest provider that satisfies the request's cost / latency budget.
- **Canonical example**: `cost-routing`.
- **Shape**: annotate provider configs with cost-per-million-token figures; route based on the active token budget.
- **Note**: cost numbers change frequently; the skill should recommend reading them from a config file or shared catalog rather than hard-coding.

## 5. Capability detection (CE)

- **Intent**: ask the SDK which capabilities (vision, tool calling, JSON mode, streaming) a given provider/model supports.
- **Canonical example**: `capability-detection`.
- **Shape**: query capability flags before issuing a request; degrade gracefully if a capability is missing.

## 6. Retry / fallback (CE)

- **Intent**: handle transient failures by retrying, and persistent failures by falling back to a different provider.
- **Canonical example**: `retry-fallback`.
- **Shape**: configure retry policy (max attempts, backoff) at the request layer; configure fallback chain at the provider layer.
- **Common pairing**: stack on top of `streaming` and `multi-provider` for production code.

## 7. Structured output (CE)

- **Intent**: receive a response constrained to a JSON schema rather than free-form text.
- **Canonical example**: `structured-output`.
- **Shape**: declare a response schema; pass it alongside the prompt; receive a typed object on the response. In `nxuskit-cli call`, this is surfaced as `response_format` with `text`, `json_object`, or `json_schema` shapes when supported by the installed CLI.
- **Verification**: validate the parsed response against the declared schema; reject and retry if it does not parse.

## 8. Tool / function calling (CE)

- **Intent**: let the model call developer-defined functions and consume their output.
- **Canonical example**: covered as patterns within `structured-output` and `multi-provider`; the SDK exposes a unified tool-call interface.
- **Shape**: declare tool signatures (name, description, parameter schema); on each model turn, dispatch tool invocations to local functions; feed results back into the conversation. In `nxuskit-cli call`, probe for `tool_definitions` and `tool_choice` support before relying on CLI-driven tool calls.
- **Capability check**: not all providers/models support tool calling; gate via `capability-detection` before relying on it.

## 9. Vision / multimodal (CE)

- **Intent**: send images alongside text and receive responses that condition on them.
- **Canonical example**: `vision`.
- **Shape**: encode images per provider conventions (typically base64 or URL); confirm the model supports vision via `capability-detection`.

## 10. Local providers (Ollama, LM Studio) (CE)

- **Intent**: run a local model for offline use, privacy, or cost control.
- **Canonical example**: refer to `multi-provider` and the `ollama`/`lmstudio` entries in the examples manifest.
- **Shape**: configure a local-provider entry pointing at the local URL; use it like any cloud provider.
- **Credentials**: typically none, just the URL. Prefer `OLLAMA_HOST=http://127.0.0.1:11434` for current Ollama examples unless the installed SDK/CLI documents another setting.

## 11. Auth helper (CE)

- **Intent**: walk the user through provider auth without asking for keys in chat.
- **Canonical example**: `auth-helper`.
- **Shape**: opens the provider's OAuth (or device-auth) flow in a browser; stores the resulting credential in the OS credential store; the SDK reads it from there on subsequent runs.
- **Critical rule**: never instruct the user to paste a key into chat. The auth helper is the alternative.

## 12. CLIPS basics (CE)

- **Intent**: use the CLIPS rule engine for symbolic, deterministic decisions.
- **Canonical example**: `clips-basics`.
- **Shape**: load a `.clp` rules file; assert facts; run; read the resulting facts back. The SDK wraps CLIPS in a Rust-friendly interface.

## 13. CLIPS + LLM hybrid (CE)

- **Intent**: combine LLM extraction with CLIPS-rule validation.
- **Canonical example**: `clips-llm-hybrid`.
- **Shape**: LLM extracts structured facts from unstructured input; assert the facts into CLIPS; run rules; treat the resulting fact base as the system's verified state.
- **Companion**: `arbiter`, `ruler` apps illustrate this at app scale.

## 14. Bayesian inference (CE)

- **Intent**: probabilistic reasoning over a Bayesian network.
- **Canonical example**: `bayesian-inference`.
- **Shape**: define network structure and conditional probability tables; pass observations; receive posterior probabilities.

## 15. Solver / what-if (Pro)

- **Intent**: solve constraint-optimization problems with Z3 (or solver / what-if scoping).
- **Canonical example**: `solver`, `solver-what-if`.
- **Shape**: declare variables and constraints; call solve; inspect the resulting model. What-if scopes a baseline solution and re-solves under altered constraints.
- **Tier**: Pro. The skill MUST present the Pro disclosure block (see `pro-disclosure.md`) before generating solver code.

## 16. ZEN decision tables (Pro)

- **Intent**: evaluate a JDM (JSON Decision Model) decision table.
- **Canonical example**: `zen-decisions`.
- **Tier**: Pro. Disclosure required.

## 17. Hybrid LLM + symbolic (mixed)

- **Intent**: combine LLM extraction or generation with one or more symbolic engines.
- **Canonical examples**: `llm-solver-hybrid` (Pro because solver is Pro), `bn-solver-clips-pipeline` (Pro), `clips-llm-hybrid` (CE — no solver step).
- **Shape**: pipeline the steps; treat each step as a stage with a single contract (input/output schema). Surface failures from each stage independently.
- **Tier**: pipelines that include a solver step are Pro. Disclosure required for the solver portion. CE alternative: `clips-llm-hybrid` (no solver).

---

## Cross-cutting notes

- **Model IDs change**: avoid hard-coding model IDs (e.g., `gpt-4o-2024-05-13`). Prefer reading the model name from project config, environment, or `capability-detection` / model-discovery output.
- **Thinking controls are provider-specific**: when the user needs thinking/reasoning policy, use SDK capability detection or probe for `thinking_mode` in the installed `nxuskit-cli call` surface. Do not assume every provider accepts it.
- **No mock providers in production code**: examples may use mock providers for offline testing; do not ship mocks into the user's application unless they explicitly want them.
- **Verification before "done"**: every code change should be followed by a verification step from the fallback ladder in `setup-and-smoke.md`. If verification cannot run, say so explicitly.
- **Keep the user's conventions**: respect existing project lint, format, and test commands. Do not introduce new build infrastructure to support a single integration.
