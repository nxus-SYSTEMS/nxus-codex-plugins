"""MCP stdio server: registers the 10 read-only tools.

Built on the official ``mcp`` Python SDK. The server
loads the bundled metadata snapshot once at startup, registers the 10
read-only tools, and serves over stdio.

Stdout is reserved for MCP JSON-RPC framing; logs go to file via
``logging_config`` (FR-003).  Fatal startup errors (e.g.,
:class:`SnapshotMissingError`) are written to stderr and the process
exits non-zero so Codex can fall back to the shipped reference index.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import orjson
from mcp import types as mcp_types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import ValidationError

from . import __version__
from .logging_config import configure as configure_logging
from .logging_config import get_logger
from .models import (
    GetExampleIn,
    GetRecipeIn,
    GetSetupStepsIn,
    GetSmokeCommandIn,
    RecommendExampleIn,
    RecommendRecipeIn,
    SearchExamplesIn,
    SearchRecipesIn,
)
from .store import MetadataStore, SnapshotMissingError
from .tools import (
    TOOL_NAMES,
    NotFoundError,
    get_example,
    get_recipe,
    get_setup_steps,
    get_smoke_command,
    list_features,
    list_tiers,
    recommend_example_for_task,
    recommend_recipe_for_task,
    search_examples,
    search_recipes,
)

# ---------------------------------------------------------------------------
# Tool descriptions (surfaced to Codex via list_tools)
# ---------------------------------------------------------------------------

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "search_examples": (
        "Free-text search over canonical nxusKit examples in the bundled offline "
        "snapshot.  Filter by language, tier, audience tag, or tech tag.  Returns "
        "ranked summaries with tier + audience tags so the skill can apply the "
        "Pro disclosure pattern before any code generation."
    ),
    "get_example": (
        "Fetch the full Example record for a known id.  Returns tier, audience tags, "
        "implementations map, smoke command, and related examples."
    ),
    "list_features": (
        "List nxusKit feature surfaces (streaming, structured-output, CLIPS, solver, "
        "ZEN, Bayesian, hybrid, ...) with their tier and the examples/recipes that "
        "implement them."
    ),
    "list_tiers": (
        "Return the two tiers (community, pro) with their disclosure copy pointers."
    ),
    "get_setup_steps": (
        "Per-language setup steps for a given example: install, build, smoke pointers."
    ),
    "get_smoke_command": (
        "Smallest-safe smoke command for a given example, with cwd and resource "
        "requirements (local LLM, cloud LLM, etc.).  Null when no smoke command exists."
    ),
    "recommend_example_for_task": (
        "Given a task description, return the smallest relevant Example ranked by "
        "relevance + difficulty (starter preferred on ties).  Always surfaces tier so "
        "Pro disclosure can fire before code generation."
    ),
    "search_recipes": (
        "Free-text search over CLI/Bash and knowledge-work recipes.  Filter by "
        "audience tag, workflow tag, tier, or language.  Phi-sensitive recipes return "
        "the FR-023b non-claim disclosure copy."
    ),
    "get_recipe": (
        "Fetch the full Recipe record for a known id, including expected_output_schema "
        "and (for phi-sensitive recipes) the FR-023b non-claim disclosure copy."
    ),
    "recommend_recipe_for_task": (
        "Given a task description, return the most relevant recipes.  Audience-tag "
        "filtering grants per-overlap bonus to favor recipes that match the user's "
        "context (developer, cli-automation, knowledge-work, audit, healthcare, ...)."
    ),
}


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def _input_schema(model_cls: type) -> dict[str, Any]:
    """Generate JSON Schema for the tool input model."""
    schema: dict[str, Any] = model_cls.model_json_schema()  # type: ignore[attr-defined]
    # MCP Tool requires the schema to be an object schema.
    schema.setdefault("type", "object")
    return schema


def _tools_listing() -> list[mcp_types.Tool]:
    """Build the static Tool catalogue surfaced via list_tools."""
    tools = [
        mcp_types.Tool(
            name="search_examples",
            description=_TOOL_DESCRIPTIONS["search_examples"],
            inputSchema=_input_schema(SearchExamplesIn),
        ),
        mcp_types.Tool(
            name="get_example",
            description=_TOOL_DESCRIPTIONS["get_example"],
            inputSchema=_input_schema(GetExampleIn),
        ),
        mcp_types.Tool(
            name="list_features",
            description=_TOOL_DESCRIPTIONS["list_features"],
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        mcp_types.Tool(
            name="list_tiers",
            description=_TOOL_DESCRIPTIONS["list_tiers"],
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        mcp_types.Tool(
            name="get_setup_steps",
            description=_TOOL_DESCRIPTIONS["get_setup_steps"],
            inputSchema=_input_schema(GetSetupStepsIn),
        ),
        mcp_types.Tool(
            name="get_smoke_command",
            description=_TOOL_DESCRIPTIONS["get_smoke_command"],
            inputSchema=_input_schema(GetSmokeCommandIn),
        ),
        mcp_types.Tool(
            name="recommend_example_for_task",
            description=_TOOL_DESCRIPTIONS["recommend_example_for_task"],
            inputSchema=_input_schema(RecommendExampleIn),
        ),
        mcp_types.Tool(
            name="search_recipes",
            description=_TOOL_DESCRIPTIONS["search_recipes"],
            inputSchema=_input_schema(SearchRecipesIn),
        ),
        mcp_types.Tool(
            name="get_recipe",
            description=_TOOL_DESCRIPTIONS["get_recipe"],
            inputSchema=_input_schema(GetRecipeIn),
        ),
        mcp_types.Tool(
            name="recommend_recipe_for_task",
            description=_TOOL_DESCRIPTIONS["recommend_recipe_for_task"],
            inputSchema=_input_schema(RecommendRecipeIn),
        ),
    ]
    internal = _internal_tools_provider()
    if internal is not None:
        tools.extend(internal.list_tools(_input_schema))
    return tools


def _to_text_payload(model_obj: Any) -> list[mcp_types.TextContent]:
    """Serialize a Pydantic output to a list[TextContent] for MCP transport."""
    serialized = model_obj.model_dump(mode="json")
    text = orjson.dumps(serialized, option=orjson.OPT_INDENT_2).decode("utf-8")
    return [mcp_types.TextContent(type="text", text=text)]


def _disclosure_provider() -> Any:
    """Return the FR-023b non-claim copy callable.

    In Phase 4 (M6 / T049) this returns ``phi_boundary.disclosure_copy``.
    Until then, the import is best-effort: if the module is absent we
    pass ``None`` and the tools simply omit the disclosure field.
    """
    try:
        from . import (
            phi_boundary,  # local import to avoid cycle and to allow Phase-2-only operation
        )

        return phi_boundary.disclosure_copy
    except ImportError:
        return None


def _internal_tools_provider() -> Any:
    """Return internal-only tool provider when explicitly enabled."""
    if os.environ.get("NXUSKIT_CELERAT_INTERNAL") != "1":
        return None
    try:
        from . import internal_tools  # type: ignore[attr-defined]

        return internal_tools
    except ImportError:
        return None


def build_server(store: MetadataStore) -> Server:
    """Construct the MCP server with all 10 tools wired to ``store``."""
    server: Server = Server(
        name="nxuskit-celerat",
        version=__version__,
        instructions=(
            "Read-only nxusKit Celerat MCP.  Use `search_examples` / "
            "`recommend_example_for_task` to discover canonical nxusKit examples; "
            "use `search_recipes` / `recommend_recipe_for_task` for CLI/Bash "
            "and knowledge-work recipes.  Every Example/Recipe response carries "
            "`tier` and `audience_tags`; PHI-sensitive recipes also carry the "
            "FR-023b non-claim `disclosure` field."
        ),
    )
    log = get_logger()
    disclosure_fn = _disclosure_provider()
    internal_tools = _internal_tools_provider()

    @server.list_tools()  # type: ignore[no-untyped-call,untyped-decorator]
    async def _list_tools() -> list[mcp_types.Tool]:
        return _tools_listing()

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def _call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[mcp_types.TextContent]:
        internal_names: set[str] = set()
        if internal_tools is not None:
            internal_names = set(internal_tools.TOOL_NAMES)

        if name not in TOOL_NAMES and name not in internal_names:
            log.warning("unknown_tool_call", tool_name=name)
            raise ValueError(f"Unknown tool: {name!r}")

        payload: Any
        out: Any
        try:
            if name == "search_examples":
                payload = SearchExamplesIn.model_validate(arguments)
                out = search_examples(payload, store=store)
            elif name == "get_example":
                payload = GetExampleIn.model_validate(arguments)
                out = get_example(payload, store=store)
            elif name == "list_features":
                out = list_features(store=store)
            elif name == "list_tiers":
                out = list_tiers(store=store)
            elif name == "get_setup_steps":
                payload = GetSetupStepsIn.model_validate(arguments)
                out = get_setup_steps(payload, store=store)
            elif name == "get_smoke_command":
                payload = GetSmokeCommandIn.model_validate(arguments)
                out = get_smoke_command(payload, store=store)
            elif name == "recommend_example_for_task":
                payload = RecommendExampleIn.model_validate(arguments)
                out = recommend_example_for_task(payload, store=store)
            elif name == "search_recipes":
                payload = SearchRecipesIn.model_validate(arguments)
                out = search_recipes(payload, store=store, disclosure_fn=disclosure_fn)
            elif name == "get_recipe":
                payload = GetRecipeIn.model_validate(arguments)
                out = get_recipe(payload, store=store, disclosure_fn=disclosure_fn)
            elif name == "recommend_recipe_for_task":
                payload = RecommendRecipeIn.model_validate(arguments)
                out = recommend_recipe_for_task(payload, store=store, disclosure_fn=disclosure_fn)
            elif internal_tools is not None and name in internal_names:
                out = internal_tools.call_tool(name, arguments, store=store)
            else:  # pragma: no cover — guarded by TOOL_NAMES check above
                raise ValueError(f"Unhandled tool: {name!r}")
        except ValidationError as exc:
            log.warning("tool_input_invalid", tool_name=name, error=str(exc))
            raise ValueError(f"Invalid input for {name}: {exc}") from exc
        except NotFoundError as exc:
            log.info("tool_not_found", tool_name=name, error=str(exc))
            raise ValueError(str(exc)) from exc

        return _to_text_payload(out)

    return server


async def _run(snapshot_path: Path | None) -> int:
    log = get_logger()
    try:
        store = MetadataStore.load(snapshot_path)
    except SnapshotMissingError as exc:
        # Stderr is allowed for fatal startup errors; Codex sees this and the skill
        # fall-back kicks in (FR-005 / SC-011).
        sys.stderr.write(f"nxuskit-celerat-mcp: snapshot missing — {exc}\n")
        log.error("startup_snapshot_missing", error=str(exc))
        return 2

    server = build_server(store)
    log.info("server_starting", snapshot_identifier=store.snapshot_identifier)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
    log.info("server_stopped")
    return 0


def run(snapshot_path: Path | None = None) -> int:
    """Synchronous entry point used by ``__main__.main()``."""
    configure_logging()
    try:
        return asyncio.run(_run(snapshot_path))
    except KeyboardInterrupt:
        get_logger().info("server_interrupted")
        return 130


__all__ = ["build_server", "run"]
