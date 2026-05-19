# nxusKit Celerat

nxusKit Celerat is a Codex Plugin for accelerating nxusKit SDK integrations across LLMs, symbolic reasoning, hybrid AI workflows, CLI/Bash prototypes, and public-safe local intelligence patterns in Rust, Go, Python, and Bash.

## v0.9.4 — current release

v0.9.4 includes:

- **A local read-only Model Context Protocol (MCP) server** under `mcp/` (Python stdio; **requires Python 3.11+**) that lets Codex discover canonical nxusKit examples and CLI/Bash recipes from a bundled offline metadata snapshot — no cloud microservice, no live cross-repo querying.
- **CLI/Bash recipes** with declared input/output JSON schemas and smallest-safe smoke commands.
- **Public-safe local intelligence patterns** for Codex-supervised nxusKit pipelines that process sensitive files locally and return only schema-level findings to Codex.
- **A PHI boundary** — schema-level outputs only for `phi-sensitive` recipes, with explicit `correlation_handle` passthrough; remote-MCP and cloud-model PHI requests are refused with clear disclosures.

Persona-specific recipes and fixtures are not part of the public plugin.

If the MCP fails to start, Codex falls back to the bundled reference index with a visible "MCP unavailable" message.

## Scope

This plugin ships:

- one Codex Plugin manifest at `.codex-plugin/plugin.json` (now declares an `mcpServers` block)
- one primary skill at `skills/nxuskit/SKILL.md` (MCP awareness, PHI boundary, and public-safe local intelligence guidance)
- curated reference docs under `skills/nxuskit/references/`
- the MCP server package under `mcp/`
- plugin assets under `assets/`

## Codex Plugins vs. nxusKit Runtime Plugins

These are distinct product surfaces:

- Codex Plugins package skills, references, MCP servers, and install metadata for OpenAI Codex.
- nxusKit runtime plugins are signed shared-library SDK extensions loaded by nxusKit itself.

This plugin helps developers and knowledge-work analysts use nxusKit through Codex. It is not a nxusKit runtime plugin.

## Install

Install the pinned public release:

```bash
codex plugin marketplace add nxus-SYSTEMS/nxus-codex-plugins --ref v0.9.4-20260522
```

Then install `nxusKit Celerat` from the Codex plugin directory.

The MCP server requires Python 3.11+ on PATH. After install, the first launch may prompt to install the MCP package; alternately, install ahead of time:

```bash
cd <plugin-install-dir>/mcp
python3 -m pip install -e .
python -m nxuskit_celerat.mcp --self-check  # expect "ok"
```

## Verify

Ask Codex:

> Find me the smallest nxusKit streaming-chat example with retry and provider fallback.

The skill should:

- inspect your project before editing
- consult the local MCP first (if available) for canonical examples
- fall back gracefully to the bundled reference index if the MCP is unavailable
- choose a Community Edition example when it satisfies the request
- read credentials from environment variables or credential stores, never from chat
- recommend a verification step that fits your project
- disclose nxusKit Pro requirements before generating Pro-dependent code

## Logs

The MCP writes structured logs to `~/.nxuskit-celerat/logs/`. Nothing is written outside that directory.

## Remove

```bash
codex plugin marketplace remove nxus-codex-plugins
```

Plugin install and uninstall are handled from the Codex plugin directory in current Codex builds. The CLI command above removes the marketplace source if you added it directly.

## License

`MIT OR Apache-2.0`.

## See also

- `mcp/README.md` — MCP-side install, run, and troubleshooting
- `skills/nxuskit/references/mcp-overview.md` — how Codex uses MCP discovery and fallback
