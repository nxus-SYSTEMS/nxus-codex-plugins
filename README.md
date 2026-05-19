# nxus Codex Plugins

**Codex-ready workflows for nxusKit SDK integrations and local intelligence.**

[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](LICENSE)
[![Plugin: nxusKit Celerat](https://img.shields.io/badge/Codex%20Plugin-nxusKit%20Celerat-6F49C6)](plugins/nxuskit/)
![Rust](https://img.shields.io/badge/Rust-000000?logo=rust&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

**[Install](INSTALL.md)** · **[nxusKit SDK](https://github.com/nxus-SYSTEMS/nxusKit)** · **[Examples](https://github.com/nxus-SYSTEMS/nxusKit-examples)** · **[Docs](https://docs.nxus.systems/nxuskit/)** · **[Website](https://nxus.systems)**

This repository publishes public Codex Plugin packages from [nxus.SYSTEMS](https://nxus.systems). The current plugin, **nxusKit Celerat**, helps Codex use the nxusKit SDK and nxusKit Examples to add provider-agnostic LLM integrations, symbolic reasoning, hybrid AI workflows, CLI/Bash prototypes, and public-safe local intelligence patterns to real applications.

**Current public release:** `v0.9.4-20260522`

nxusKit is a multi-language SDK for LLM providers, CLIPS rule engines, Z3 constraint solvers, Bayesian networks, ZEN decision tables, and JSON-first CLI automation. Celerat packages the product knowledge Codex needs to pick the right nxusKit pattern, explain Community vs. Pro boundaries before implementation, discover canonical examples through a bundled local MCP server, and verify changes using the target project's own build or smoke commands.

## Available Plugins

| Plugin | Display name | Scope |
|---|---|---|
| [`nxuskit`](plugins/nxuskit/) | nxusKit Celerat | Helps Codex implement nxusKit SDK integrations for LLMs, reasoning engines, hybrid workflows, CLI/Bash prototypes, and local intelligence workflows. |

## Install

Add this repository as a Git-backed Codex Plugin marketplace pinned to the current public release:

```bash
codex plugin marketplace add nxus-SYSTEMS/nxus-codex-plugins --ref v0.9.4-20260522
```

Then open the Codex plugin directory and install **nxusKit Celerat** from the `nxus.SYSTEMS Codex Plugins` source.

See [INSTALL.md](INSTALL.md) for verification and removal steps.

## What Celerat Helps With

- Add chat, streaming, structured output, tool calling, vision, retry/fallback, provider routing, and local-provider support with nxusKit.
- Migrate direct OpenAI, Anthropic, Ollama, or LiteLLM-style code toward a provider-agnostic nxusKit integration.
- Prototype workflows with `nxuskit-cli` and Bash/JSON before changing application code.
- Use bundled MCP discovery to pick canonical nxusKit examples and task recipes instead of relying on generic invention.
- Add Community Edition CLIPS guardrails around LLM recommendation workflows.
- Compare model/provider fitness with the model research harness pattern before live calls.
- Keep sensitive local files on the user's machine while returning only schema-level findings to Codex.
- Stay Community Edition-first when a request can be satisfied without Pro.
- Disclose Pro requirements before solver-backed what-if analysis, ZEN decision tables, runtime plugin loading, or other Pro-gated paths.
- Avoid in-chat secret handling by directing users to environment variables, credential stores, provider dashboards, and nxusKit auth helpers.

## Try It

After installing the plugin, start a Codex session inside a Rust, Go, Python, or CLI-oriented project and ask:

> Find the smallest nxusKit example or recipe for this repo with setup, smoke steps, and CE/Pro tier.

Other useful prompts:

> Use common-sense-guardrails to add Community CLIPS checks around an LLM recommendation workflow.

> Use model-research-harness to compare model/provider fitness with dry-run scoring before live calls.

For more task prompts, see [examples/](examples/).

## nxusKit SDK

The plugin is a companion to the [nxusKit SDK](https://github.com/nxus-SYSTEMS/nxusKit), not a replacement for it. Install nxusKit when you are ready to build and run application code:

- [nxusKit documentation](https://docs.nxus.systems/nxuskit/)
- [Getting started](https://docs.nxus.systems/nxuskit/getting-started/installation/)
- [nxusKit Examples](https://github.com/nxus-SYSTEMS/nxusKit-examples)
- [CLI reference](https://docs.nxus.systems/nxuskit/reference/cli-reference/)

Community Edition workflows are available for many LLM, local-provider, CLIPS, Bayesian, and CLI/Bash use cases. Some solver, ZEN, runtime plugin, and advanced workflow capabilities require nxusKit Pro; Celerat is designed to call that out before Codex generates Pro-dependent code.

## Contributing

Public contributions should focus on shipped plugin behavior, installation clarity, prompt examples, documentation, and reproducible validation. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This repository is dual-licensed under MIT or Apache 2.0, at your option. See [LICENSE](LICENSE), [LICENSE-MIT](LICENSE-MIT), and [LICENSE-APACHE](LICENSE-APACHE).

Copyright 2025-2026 nxus.SYSTEMS LLC.
