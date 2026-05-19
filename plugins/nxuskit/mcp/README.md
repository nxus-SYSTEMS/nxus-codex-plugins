# nxuskit-celerat-mcp

Local read-only Model Context Protocol (MCP) server for the **nxusKit Celerat** Codex Plugin.

This package ships **inside** the Codex plugin under `plugins/nxuskit/mcp/`. Codex launches it as a stdio child process per the plugin manifest. It is read-only, offline-capable, and reads a bundled metadata snapshot — no cloud microservice, no live cross-repo querying, no arbitrary shell execution.

## Install

Requires Python 3.11+.

```bash
cd plugins/nxuskit/mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Verify:

```bash
python -m nxuskit_celerat.mcp --self-check
# expected:
#   nxuskit-celerat-mcp 0.9.4
#   snapshot: <identifier>  examples: <N>  recipes: <M>  tiers: 2
#   ok
```

## Run (manually)

Codex normally starts the server for you, but for debugging:

```bash
python -m nxuskit_celerat.mcp
```

The server speaks MCP over stdio. To inspect the tool surface:

```bash
npx @modelcontextprotocol/inspector python -m nxuskit_celerat.mcp
```

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `NXUSKIT_CELERAT_METADATA` | `<package>/../metadata/snapshot.json` | Override the metadata snapshot path for tests and fallback scenarios. |
| `XDG_CACHE_HOME` | `~/.cache` | Resolves the cache root; we use `<root>/nxuskit-celerat/`. |

## Logs and cache

All writes are confined to `~/.nxuskit-celerat/`:

- `logs/<date>.jsonl` — structured stdio-safe logs (FR-003)
- `cache/` — reserved for future use
- `audit/<timestamp>.json` — pre-publish PHI-scan findings (when run)

The server refuses any write outside this root (`LogDirBoundaryError`).

## Tools

10 read-only MCP tools, all typed via Pydantic v2:

`search_examples`, `get_example`, `list_features`, `list_tiers`,
`get_setup_steps`, `get_smoke_command`, `recommend_example_for_task`,
`search_recipes`, `get_recipe`, `recommend_recipe_for_task`.

Per-tool I/O contracts are represented by the Pydantic models in `src/nxuskit_celerat/mcp/models.py` and the JSON-RPC handlers in `src/nxuskit_celerat/mcp/server.py`.

## Troubleshooting

- **`python -m nxuskit_celerat.mcp` says "module not found"** — confirm `pip install -e .` succeeded in the active venv; check `python -c "import nxuskit_celerat.mcp; print(nxuskit_celerat.mcp.__version__)"`.
- **`SnapshotMissingError` at startup** — the bundled snapshot at `plugins/nxuskit/mcp/metadata/snapshot.json` is missing. Regenerate via `python scripts/generate-mcp-metadata.py …` or set `NXUSKIT_CELERAT_METADATA` to a valid path.
- **MCP unavailable in Codex** — Codex falls back to the shipped reference index automatically and surfaces "MCP unavailable, using shipped reference index." Check `~/.nxuskit-celerat/logs/` for the startup error.
- **Wrong Python version** — requires 3.11+; check `python --version`.

## License

`MIT OR Apache-2.0` — see top-level `LICENSE-MIT` and `LICENSE-APACHE`.

## See also

- `plugins/nxuskit/skills/nxuskit/SKILL.md` — the Codex skill that consumes this MCP
- `plugins/nxuskit/skills/nxuskit/references/mcp-overview.md` — Codex-facing MCP usage notes
- `plugins/nxuskit/skills/nxuskit/references/phi-boundary.md` — public PHI-boundary behavior
