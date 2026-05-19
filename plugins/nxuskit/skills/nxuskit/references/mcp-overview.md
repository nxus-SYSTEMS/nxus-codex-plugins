# MCP Overview — `nxuskit-celerat`

The current plugin ships a single local stdio MCP server,
`nxuskit-celerat`, that exposes the bundled examples + recipes
metadata as ten read-only tools. The server runs entirely on the
user's machine: no sockets, no cloud round-trip, no telemetry.

## What the MCP does

It serves a **bundled JSON snapshot** of the nxusKit examples and
recipes (sourced from the nxusKit examples manifest at a pinned commit,
plus `recipes-source.yaml`). At
load time the server validates the snapshot against the Pydantic
models in `models.py` and refuses to start if validation fails
(fail-closed; this triggers the §13 fallback in SKILL.md).

It does NOT execute commands, run examples, or modify files. It is
strictly a metadata lookup surface.

## The ten tools

| Tool | Purpose |
|---|---|
| `search_examples` | Fuzzy-rank examples by query, language, tier, audience, workflow tag. |
| `get_example` | Full record for a known example id. |
| `list_features` | Group examples by tech-tag overlap (Hybrid LLM+symbolic, Streaming, etc.). |
| `list_tiers` | Enumerate `community` and `pro`. |
| `get_setup_steps` | Per-language setup walkthrough for an example. |
| `get_smoke_command` | The smallest-safe command that proves the example runs. |
| `recommend_example_for_task` | Rank examples for a free-form task description. |
| `search_recipes` | Fuzzy-rank CLI/Bash + knowledge-work recipes by query and audience tag. |
| `get_recipe` | Full record for a known recipe id, including PHI `disclosure` when applicable. |
| `recommend_recipe_for_task` | Rank recipes for a free-form task description. |

Every Example/Recipe-bearing payload includes `tier` and
`audience_tags` (FR-007). Every PHI-relevant Recipe payload includes
the `disclosure` field (FR-023b).

## How Codex picks MCP-vs-fallback

Codex SHOULD call MCP tools first. The skill is wired (SKILL.md §13)
to fall back to `references/example-index.md`,
`references/api-patterns.md`, `references/migration-recipes.md`, and
`references/setup-and-smoke.md` when the MCP is unavailable, with the
visible message:

> MCP unavailable; using shipped reference index. Some example/recipe
> metadata may be less detailed.

PHI Boundary (§14) and Knowledge-Work Lane (§15) rules apply equally
in MCP-up and MCP-down modes.

## Where logs land

`~/.nxuskit-celerat/logs/` (mode 0700). Per-tool-call records carry
`tool_name`, `input_hash`, `latency_ms`, `result_count`,
`snapshot_identifier`. Stripped-field redactions log the field NAME
only (FR-023b).

## Manual self-check

```bash
python -m nxuskit_celerat.mcp --self-check
```

Expected output (Quickstart §1 contract):

```
nxuskit-celerat-mcp <version>
snapshot: <identifier>  examples: <N>  recipes: <M>  tiers: 2
ok
```

If self-check fails, the skill falls back to the reference index per
§13. To force the fallback path for testing, point
`NXUSKIT_CELERAT_METADATA` at a non-existent file:

```bash
NXUSKIT_CELERAT_METADATA=/tmp/does-not-exist python -m nxuskit_celerat.mcp --self-check
# exits non-zero with a stderr "snapshot missing" diagnostic.
```

## Cross-links

- SKILL.md §12 — MCP Boundary
- SKILL.md §13 — MCP Awareness + fallback protocol
- SKILL.md §14 — PHI Boundary
- SKILL.md §15 — Knowledge-Work Lane
- `references/phi-boundary.md`
- `references/knowledge-work-lane.md`
