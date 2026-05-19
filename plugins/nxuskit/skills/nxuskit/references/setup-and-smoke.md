# Setup and Smoke

Per-language setup, credential handling, and smoke-verification recipes for nxusKit integrations. The skill instructions reference this document by section name; do not embed the contents inline in `SKILL.md`.

This document covers:

- [Rust](#rust)
- [Go](#go)
- [Python](#python)
- [CLI/Bash with `nxuskit-cli`](#clibash-with-nxuskit-cli)
- [Verification fallback ladder](#verification-fallback-ladder)

---

## Common credential rules

The skill MUST NOT request API keys, tokens, license keys, or other secrets in chat. Direct users to one of:

- **Environment variables** (most projects): export `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc., in the shell before invoking the application. Document the exact names in the project's README.
- **Credential stores** (macOS keychain, Linux secret-service, Windows DPAPI): if the project already integrates with a credential store, prefer it.
- **`nxuskit-cli` auth helpers** (where applicable): the CLI's auth/login flow stores credentials outside chat.
- **Provider dashboards**: link the user to the provider's key-rotation or usage page rather than discussing keys in chat.

If the user volunteers a secret in chat, follow the FR-009a protocol: acknowledge receipt, refuse to embed/use it, advise rotation (the secret is now exposed), and redirect to one of the safer paths above.

---

## Rust

For the canonical, up-to-date Rust setup walkthrough, see the nxusKit SDK getting-started documentation at `https://docs.nxus.systems/nxuskit/getting-started/installation/`.

The public Community Edition SDK is distributed from the public
`nxus-SYSTEMS/nxusKit` GitHub release. GitHub CLI authentication is optional for
normal public downloads, but useful for CI reliability, higher API limits, and
entitlement-gated or private assets.

### Install

The nxusKit SDK ships as a Rust crate. Add it to `Cargo.toml`:

```toml
[dependencies]
nxuskit = "0.9"
```

If the project uses workspace inheritance, add `nxuskit` to the workspace `[workspace.dependencies]` and reference it as `nxuskit.workspace = true` in member crates.

For Pro features (solver, ZEN, etc.), the same crate is used; the SDK is gated by the active license at runtime, not by feature flag.

### Credential setup

Provider keys are read from environment variables by default:

```bash
export OPENAI_API_KEY=...     # if using the OpenAI provider
export ANTHROPIC_API_KEY=...  # if using Anthropic
```

For local providers (Ollama, LM Studio), the URL is the only required setting.
Prefer `OLLAMA_HOST=http://127.0.0.1:11434` for local Ollama walkthroughs unless
the user's installed SDK or project documents a different local-provider setting.
Older nxusKit docs/examples used `OLLAMA_BASE_URL` or `OLLAMA_API_URL` on some
surfaces; follow the installed SDK/CLI help and fall back to explicit
builder/config `base_url` when available.

```bash
export OLLAMA_HOST=http://127.0.0.1:11434
```

Do NOT request the user's key in chat (FR-009).

### Smoke recipe

After adding the dependency and setting credentials:

```bash
cargo check        # fastest path; confirms imports + types compile
cargo build        # full build if check passes
cargo test         # if the project already has nxusKit-touching tests
cargo run -p <bin> # run a specific binary
```

`cargo check` is the lowest-cost smoke; promote to `cargo run` only when credentials are wired and the user has opted in to making a real provider call.

---

## Go

### Install

```bash
go get github.com/nxus-SYSTEMS/nxuskit-go@latest
```

The Go module mirrors the Rust SDK's surface and is generated from the same C ABI.

### Credential setup

Same env-var conventions as Rust. The Go SDK reads provider credentials and local-provider URL settings from the process environment unless overridden via the SDK's config struct.

### Smoke recipe

```bash
go vet ./...           # static checks; no execution
go build ./...         # confirms compile
go test ./...          # if tests exist
go run ./cmd/<name>    # to execute
```

Use `go vet` and `go build` as the lowest-cost smoke before any test that issues real provider calls.

---

## Python

### Install

```bash
pip install nxuskit
# or, in a project using uv / poetry / hatch:
uv add nxuskit
```

The Python SDK wraps the same C ABI used by Rust and Go; the runtime calls into the shared library.

### Credential setup

Same env-var conventions. For projects using `python-dotenv`, add credentials to `.env` (which is `.gitignore`'d by default in this repo) and load them at startup. Do NOT request the user's key in chat.

### Smoke recipe

```bash
python -c "import nxuskit; print(nxuskit.__version__)"   # import smoke
python -m pytest                                          # if tests exist
python -m mypy <module>                                   # if mypy configured
python <entry-point.py> --help                            # without making real calls
```

Import-smoke is the lowest-cost verification. Avoid running entry points that make real provider calls until the user has confirmed credentials are wired.

---

## CLI/Bash with `nxuskit-cli`

`nxuskit-cli` is a first-class prototyping surface (FR-015). Use it for license-status checks, provider discovery, loopback smoke, and JSON-first Bash workflows BEFORE editing application code.

### FR-015a probe-first behavior

Before recommending any specific `nxuskit-cli` subcommand for execution, instruct the user (and Codex) to probe availability:

```bash
nxuskit-cli --help                       # confirms CLI is installed
nxuskit-cli --version                    # confirms minimum version (if printed)
nxuskit-cli license --help               # confirms `license` namespace is present
nxuskit-cli provider --help              # confirms `provider` namespace
```

If a recommended subcommand is NOT present in the user's installed CLI, label the command as guidance ("requires `nxuskit-cli` ≥ X") and fall back to the language-specific smoke path above.

### License status (always safe to run)

```bash
nxuskit-cli license status --json
```

JSON output is suitable for `jq` filtering in Bash scripts. Use this BEFORE generating Pro-dependent code to confirm tier.

### Provider discovery

```bash
nxuskit-cli provider list --json         # enumerate configured providers
nxuskit-cli provider status [PROVIDER] --json  # auth/config state
nxuskit-cli provider ping --provider ollama --json  # reachability
```

In `nxuskit-cli` 0.9.x, `provider status` is auth/config focused. Use
`provider ping --provider <provider> --json` for local-provider reachability
when the installed CLI supports it. If `provider list` or `provider ping` is
not present in the installed CLI, treat as guidance-only and recommend the
user upgrade `nxuskit-cli` or use language-level provider listing.

### Structured output, tool choice, and thinking controls

Current `nxuskit-cli call` inputs may include:

- `response_format`: `{"type":"text"}`, `{"type":"json_object"}`, or
  `{"type":"json_schema","schema":{...}}`.
- `tool_definitions` plus `tool_choice`: provider-compatible tool/function
  schemas and choice policy.
- `thinking_mode`: `auto`, `enabled`, `disabled`, or `omit`.

Probe `nxuskit-cli call --help` before relying on these fields. If the installed
CLI does not accept one of them, treat that field as a minimum-version feature
and fall back to the language SDK or a prompt-only smoke.

Minimal JSON-object smoke:

```bash
printf '{"prompt":"Return {\"ok\":true} as JSON only.","provider":"loopback","model":"echo","response_format":{"type":"json_object"}}' \
  | nxuskit-cli call --input - --format json
```

### Loopback / local-provider smoke

```bash
printf '{"prompt":"hello","provider":"loopback","model":"echo"}' \
  | nxuskit-cli call --input - --format json

# With a local provider, first ping reachability:
nxuskit-cli provider ping --provider ollama --json

# Then run a small already-pulled model if the ping passes:
printf '{"prompt":"ping","provider":"ollama","model":"llama3.2:latest"}' \
  | nxuskit-cli call --input - --format json
```

For the `common-sense-guardrails` walkthrough, current examples guidance prefers
`qwen3.5:4b` when available and `qwen3.5:2b` for lower-resource local runs:

```bash
export NXUSKIT_PROVIDER=ollama
export NXUSKIT_MODEL=qwen3.5:4b
export OLLAMA_HOST=http://127.0.0.1:11434
```

The JSON-first `call` command with provider `loopback` and model `echo` is the
no-credential smoke path. Use it when the user does not yet have a remote
provider key configured. Probe first and prefer the stable `call` surface.

### JSON-first Bash workflow

Pipe `--json` output into `jq`. Example: confirm the user has at least one configured provider before scaffolding SDK code:

```bash
if ! nxuskit-cli provider list --json | jq -e '.result.providers | length > 0' >/dev/null; then
  echo "no providers configured; run setup first" >&2
  exit 1
fi
```

This pattern lets a Bash prototype validate workflow logic before any Rust/Go/Python code is written.

---

## `nxuskit-cli` CLI/Bash prototype recipes (MCP-first)

The local Examples & Recipes MCP (`nxuskit-celerat-mcp`) ships
CLI/Bash prototype recipes reachable via `search_recipes` and
`recommend_recipe_for_task` (audience tag `cli-automation`). Codex should call
the MCP first; this index is the MCP-down fallback (see SKILL.md §13).

| Recipe ID | One-line purpose |
|---|---|
| `cli-license-status-probe` | Probe license tier via `nxuskit-cli license status --json` before recommending Pro-tier features. |
| `cli-provider-list-status` | Enumerate configured providers + reachability via `provider list/status --json` for failover prototyping. |
| `cli-local-provider-smoke-ollama` | Local-only smoke against an Ollama provider (no cloud round-trip). |
| `cli-local-provider-smoke-lmstudio` | Local-only smoke against an LM Studio provider (loopback `http://localhost:1234`). |
| `cli-loopback-smoke` | Loopback smoke through `nxuskit-cli call` with provider `loopback` and model `echo`. |
| `cli-json-recipe-selection` | JSON-first recipe selection scaffold for `nxuskit-cli recipe` workflows. |
| `cli-input-output-file-workflow` | File-in / file-out Bash pipeline for batch JSON workflows (no chat-pasted secrets). |

Knowledge-work recipes use audience tags such as `knowledge-work`, `audit`, and
`decision-support`. Public recipes stay generic and public-safe. Domain-specific
regulated workflows are internal-only until a later productization decision.

---

## Verification fallback ladder

When verifying a change, prefer the user's project-local commands first. Only fall back to the smallest-safe smoke path defined here when no project command is obvious. Order:

1. **Project-local**: run the exact build/test command the project already documents (e.g., `make test`, `npm test`, `cargo make ci`).
2. **Language-default**: `cargo check` (Rust), `go test ./...` (Go), `python -c "import <module>"` (Python).
3. **`nxuskit-cli` smoke** (with FR-015a probe): `nxuskit-cli license status --json`, then JSON-first `call` with provider `loopback`, or `provider ping` followed by a tiny local-provider call.
4. **Cannot verify**: explicitly tell the user verification could not run, why, and what they would need to do to enable it.

Do NOT fabricate verification output. If a step cannot run (no credentials, missing tooling, locked-down environment), say so plainly.
