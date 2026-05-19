# Install nxusKit Celerat

This repository publishes Codex Plugin packages from nxus.SYSTEMS. The current public plugin is **nxusKit Celerat** `v0.9.4-20260522`.

## Requirements

- Codex app or Codex CLI with plugin support.
- Network access to GitHub for Git-backed marketplace installation.
- Python 3.11+ for the bundled local MCP discovery server.
- nxusKit SDK only when you are ready to build or run nxusKit application code. The Codex Plugin itself does not install the SDK.

## Add the Marketplace

Add the public marketplace at the current release tag:

```bash
codex plugin marketplace add nxus-SYSTEMS/nxus-codex-plugins --ref v0.9.4-20260522
```

Then open the Codex plugin directory and install **nxusKit Celerat** from the `nxus.SYSTEMS Codex Plugins` source.

## Verify the Plugin

Start a new Codex session in a project that can use nxusKit, then ask:

> Find the smallest nxusKit example or recipe for this repo with setup, smoke steps, and CE/Pro tier.

Codex should inspect the project before editing, consult the bundled local MCP server when available, choose a Community Edition path when it fits, avoid asking for secrets in chat, and recommend a project-local verification command.

For a CLI/Bash-first check, ask:

> Use nxuskit-cli to verify my setup before we implement SDK code.

The plugin should guide Codex to probe `nxuskit-cli` availability and use JSON-first setup or smoke commands when supported.

For an MCP package self-check from an installed plugin directory:

```bash
cd <plugin-install-dir>/mcp
python3 -m pip install -e .
python -m nxuskit_celerat.mcp --self-check
```

## Remove the Marketplace

```bash
codex plugin marketplace remove nxus-codex-plugins
```

Plugin install and uninstall are handled from the Codex plugin directory UI in current Codex builds. The command above removes the marketplace source from your Codex configuration.
