---
title: Codex Task Examples
description: Public Codex task recipes and starter fixtures for nxusKit Celerat.
---

# Codex Task Examples

These examples show how to use `nxusKit Celerat` with Codex. They are not a replacement for the nxusKit SDK examples; they are prompt-and-workflow recipes that show what to ask Codex, what the plugin should do, and how to verify the result.

## Task Recipes

The task recipes cover the public `v0.9.4-20260520` Celerat release surface:

- [Streaming chat in Rust](./codex-task-recipes/01-streaming-rust.md)
- [Structured JSON output in Python](./codex-task-recipes/02-structured-json-python.md)
- [OpenAI plus Ollama in Go](./codex-task-recipes/03-multi-provider-go.md)
- [Retry and fallback](./codex-task-recipes/04-retry-fallback.md)
- [Community Edition rule validation](./codex-task-recipes/05-ce-rule-validation.md)
- [Pro solver-backed what-if planner](./codex-task-recipes/06-pro-solver-what-if.md)
- [Migrate direct OpenAI usage](./codex-task-recipes/07-migrate-openai-python.md)
- [Vision with capability detection](./codex-task-recipes/08-vision-capability-detection.md)
- [ZEN decision table workflow](./codex-task-recipes/09-zen-decision-table.md)
- [Community Edition options](./codex-task-recipes/10-community-edition-options.md)
- [Bayesian, solver, and CLIPS hybrid](./codex-task-recipes/11-bayesian-solver-clips.md)
- [Continue after license activation](./codex-task-recipes/12-post-activation-pro.md)
- [Local Ollama through nxusKit](./codex-task-recipes/13-local-ollama.md)
- [CLI/Bash JSON prototype and setup checks](./codex-task-recipes/14-cli-bash-setup.md)

## Starter Fixtures

The starter fixtures are small projects that give Codex something concrete to inspect and edit:

- `fixtures/starters/rust-cli/`
- `fixtures/starters/go-service/`
- `fixtures/starters/python-app/`
- `fixtures/starters/cli-bash-workspace/`
- `fixtures/starters/direct-openai-python/`
- `fixtures/starters/local-provider-python/`

They intentionally avoid machine-specific SDK paths, generated artifacts, caches, and credentials.

## Secret Handling

Do not paste API keys, license keys, tokens, passwords, or other credentials into chat. Use environment variables, credential stores, or `nxuskit-cli` auth helpers.
