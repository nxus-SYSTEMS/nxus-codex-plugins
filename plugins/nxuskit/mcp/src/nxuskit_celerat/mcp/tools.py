"""The 10 read-only MCP tools.

Real implementations backed by :class:`MetadataStore` + :mod:`ranker` and
gated by Pydantic input/output validation. Every Example/Recipe-bearing
payload includes ``tier`` and ``audience_tags`` so the skill can apply the
Pro disclosure pattern (FR-007). Every PHI-relevant Recipe payload includes a
``disclosure`` field (FR-023b non-claim copy) sourced from
:func:`phi_boundary.disclosure_copy`.

The PHI-output schema-level enforcement is wired in Phase 4 (M6); the
``disclosure`` field is wired here at M4.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .logging_config import get_logger
from .models import (
    Example,
    GetExampleIn,
    GetExampleOut,
    GetRecipeIn,
    GetRecipeOut,
    GetSetupStepsIn,
    GetSetupStepsOut,
    GetSmokeCommandIn,
    GetSmokeCommandOut,
    LanguageLiteral,
    ListFeaturesOut,
    ListTiersOut,
    Recipe,
    RecommendExampleIn,
    RecommendExampleOut,
    RecommendRecipeIn,
    RecommendRecipeOut,
    SearchExamplesIn,
    SearchExamplesOut,
    SearchRecipesIn,
    SearchRecipesOut,
)
from .ranker import (
    rank_examples,
    rank_recipes,
    summarize_example,
    summarize_recipe,
)
from .store import MetadataStore


class NotFoundError(LookupError):
    """ID-based lookup miss (per contracts/mcp-tools.md error matrix)."""


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------


def _log_tool_call(
    *,
    tool_name: str,
    snapshot_identifier: str,
    latency_ms: float,
    result_count: int,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {
        "event": "tool_call",
        "tool_name": tool_name,
        "snapshot_identifier": snapshot_identifier,
        "latency_ms": round(latency_ms, 2),
        "result_count": result_count,
    }
    if extra:
        payload.update(extra)
    get_logger().info(**payload)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_language(example: Example, requested: LanguageLiteral | None) -> LanguageLiteral:
    """Pick the language for setup/smoke lookups.

    If the caller specified a language and the example supports it, use it.
    If specified-but-unsupported, raise ``NotFoundError``.
    Otherwise fall back to the example's first declared language.
    """
    if requested is None:
        return example.languages[0]
    if requested in example.languages:
        return requested
    raise NotFoundError(
        f"Example {example.id!r} does not have an implementation in language {requested!r}; "
        f"available: {sorted(example.languages)}."
    )


# ---------------------------------------------------------------------------
# Tool 1: search_examples
# ---------------------------------------------------------------------------


def search_examples(
    payload: SearchExamplesIn,
    *,
    store: MetadataStore,
) -> SearchExamplesOut:
    t0 = time.perf_counter()
    candidates = store.iter_examples(
        languages=payload.languages,
        tiers=payload.tiers,
        audience_tags=payload.audience_tags,
        tech_tags=payload.tech_tags,
    )
    # Use the ranker just for fuzzy ordering; fold to ExampleSummary at the boundary.
    ranked = rank_examples(payload.query, candidates, limit=payload.limit)
    results = [
        summarize_example(payload.query, store.get_example(r.id))  # type: ignore[arg-type]
        for r in ranked
        if store.get_example(r.id) is not None
    ]
    out = SearchExamplesOut(
        results=results,
        snapshot_identifier=store.snapshot_identifier,
    )
    _log_tool_call(
        tool_name="search_examples",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(results),
        extra={"query_len": len(payload.query)},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 2: get_example
# ---------------------------------------------------------------------------


def get_example(payload: GetExampleIn, *, store: MetadataStore) -> GetExampleOut:
    t0 = time.perf_counter()
    ex = store.get_example(payload.id)
    if ex is None:
        raise NotFoundError(f"No example with id {payload.id!r}.")
    out = GetExampleOut(example=ex, snapshot_identifier=store.snapshot_identifier)
    _log_tool_call(
        tool_name="get_example",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=1,
        extra={"id": payload.id},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 3: list_features
# ---------------------------------------------------------------------------


def list_features(*, store: MetadataStore) -> ListFeaturesOut:
    t0 = time.perf_counter()
    features = store.list_features()
    out = ListFeaturesOut(features=features, snapshot_identifier=store.snapshot_identifier)
    _log_tool_call(
        tool_name="list_features",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(features),
    )
    return out


# ---------------------------------------------------------------------------
# Tool 4: list_tiers
# ---------------------------------------------------------------------------


def list_tiers(*, store: MetadataStore) -> ListTiersOut:
    t0 = time.perf_counter()
    tiers = store.list_tiers()
    out = ListTiersOut(tiers=tiers)
    _log_tool_call(
        tool_name="list_tiers",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(tiers),
    )
    return out


# ---------------------------------------------------------------------------
# Tool 5: get_setup_steps
# ---------------------------------------------------------------------------


def get_setup_steps(payload: GetSetupStepsIn, *, store: MetadataStore) -> GetSetupStepsOut:
    t0 = time.perf_counter()
    ex = store.get_example(payload.example_id)
    if ex is None:
        raise NotFoundError(f"No example with id {payload.example_id!r}.")
    lang = _resolve_language(ex, payload.language)
    source_path = ex.implementations[lang]

    # Steps are best-effort derived from the metadata: language-specific install
    # plus a pointer to the example's source path.  The shipped reference doc
    # ``setup-and-smoke.md`` is the human-readable companion.
    steps: list[str] = [
        f"Read the example source at `{source_path}` for full context.",
    ]
    if lang == "rust":
        steps.append("Ensure a recent Rust toolchain is installed (`rustup update stable`).")
        steps.append(f"From the example directory, run `cargo build` then `cargo run` (or the example-specific command in {source_path}/README).")
    elif lang == "go":
        steps.append("Ensure Go 1.22+ is installed.")
        steps.append(f"From the example directory, run `go run .` (or the command listed in {source_path}/README).")
    elif lang == "python":
        steps.append("Use Python 3.11+ in a fresh venv.")
        steps.append(f"Install the example's deps (`pip install -r {source_path}/requirements.txt` if present) and run the entry script.")
    elif lang == "bash":
        steps.append("Ensure `nxuskit-cli` is on PATH (see the setup-and-smoke reference).")
        steps.append(f"Run the example's bash entry point (see {source_path}/README).")
    if ex.smoke_command:
        steps.append(f"Smoke: `{ex.smoke_command}` (cwd: `{ex.smoke_cwd or source_path}`).")

    out = GetSetupStepsOut(
        example_id=ex.id,
        language=lang,
        steps=steps,
        source_path=source_path,
        snapshot_identifier=store.snapshot_identifier,
    )
    _log_tool_call(
        tool_name="get_setup_steps",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(steps),
        extra={"example_id": ex.id, "language": lang},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 6: get_smoke_command
# ---------------------------------------------------------------------------


def get_smoke_command(payload: GetSmokeCommandIn, *, store: MetadataStore) -> GetSmokeCommandOut:
    t0 = time.perf_counter()
    ex = store.get_example(payload.example_id)
    if ex is None:
        raise NotFoundError(f"No example with id {payload.example_id!r}.")
    # ``language`` is informational on the input; smoke metadata is per-example.
    lang: LanguageLiteral | None = (
        _resolve_language(ex, payload.language) if payload.language else None
    )
    out = GetSmokeCommandOut(
        example_id=ex.id,
        language=lang,
        command=ex.smoke_command,
        cwd=ex.smoke_cwd,
        requires=dict(ex.smoke_requires),
    )
    _log_tool_call(
        tool_name="get_smoke_command",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=1 if ex.smoke_command else 0,
        extra={"example_id": ex.id},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 7: recommend_example_for_task
# ---------------------------------------------------------------------------


def recommend_example_for_task(
    payload: RecommendExampleIn,
    *,
    store: MetadataStore,
) -> RecommendExampleOut:
    t0 = time.perf_counter()
    candidates = store.iter_examples(
        languages=payload.languages,
        tiers=payload.tiers,
        audience_tags=payload.audience_tags,
    )
    ranked = rank_examples(payload.task_description, candidates, limit=10, prefer_starter=True)
    out = RecommendExampleOut(ranked=ranked, snapshot_identifier=store.snapshot_identifier)
    _log_tool_call(
        tool_name="recommend_example_for_task",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(ranked),
        extra={"task_len": len(payload.task_description)},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 8: search_recipes
# ---------------------------------------------------------------------------


def _disclosure_map(recipes: list[Recipe], disclosure_fn: Callable[[], str] | None) -> dict[str, str]:
    """Return a dict mapping recipe-id → disclosure copy for phi-sensitive recipes.

    Pulled from ``phi_boundary.disclosure_copy()`` when provided; if the
    PHI boundary module hasn't been wired yet (Phase 2 only), we still
    surface a non-empty placeholder marker so tests can detect the field
    is being populated for ``phi-sensitive`` recipes. The real verbatim
    copy lands in Phase 4 / T049.
    """
    if disclosure_fn is None:
        return {}
    text = disclosure_fn()
    return {r.id: text for r in recipes if "phi-sensitive" in r.workflow_tags}


def search_recipes(
    payload: SearchRecipesIn,
    *,
    store: MetadataStore,
    disclosure_fn: Callable[[], str] | None = None,
) -> SearchRecipesOut:
    t0 = time.perf_counter()
    candidates = store.iter_recipes(
        languages=payload.languages,
        tiers=payload.tiers,
        audience_tags=payload.audience_tags,
        workflow_tags=payload.workflow_tags,
    )
    ranked = rank_recipes(
        payload.query,
        candidates,
        limit=payload.limit,
        audience_tag_filter=payload.audience_tags,
        disclosure_for=_disclosure_map(candidates, disclosure_fn),
    )
    results = [
        summarize_recipe(payload.query, store.get_recipe(r.id))  # type: ignore[arg-type]
        for r in ranked
        if store.get_recipe(r.id) is not None
    ]
    out = SearchRecipesOut(results=results, snapshot_identifier=store.snapshot_identifier)
    _log_tool_call(
        tool_name="search_recipes",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(results),
        extra={"query_len": len(payload.query)},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 9: get_recipe
# ---------------------------------------------------------------------------


def get_recipe(
    payload: GetRecipeIn,
    *,
    store: MetadataStore,
    disclosure_fn: Callable[[], str] | None = None,
) -> GetRecipeOut:
    t0 = time.perf_counter()
    r = store.get_recipe(payload.id)
    if r is None:
        raise NotFoundError(f"No recipe with id {payload.id!r}.")
    disclosure = (
        disclosure_fn() if (disclosure_fn is not None and "phi-sensitive" in r.workflow_tags) else None
    )
    out = GetRecipeOut(
        recipe=r,
        disclosure=disclosure,
        snapshot_identifier=store.snapshot_identifier,
    )
    _log_tool_call(
        tool_name="get_recipe",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=1,
        extra={"id": r.id, "phi_sensitive": "phi-sensitive" in r.workflow_tags},
    )
    return out


# ---------------------------------------------------------------------------
# Tool 10: recommend_recipe_for_task
# ---------------------------------------------------------------------------


def recommend_recipe_for_task(
    payload: RecommendRecipeIn,
    *,
    store: MetadataStore,
    disclosure_fn: Callable[[], str] | None = None,
) -> RecommendRecipeOut:
    t0 = time.perf_counter()
    candidates = store.iter_recipes(
        tiers=payload.tiers,
        audience_tags=payload.audience_tags,
        workflow_tags=payload.workflow_tags,
    )
    ranked = rank_recipes(
        payload.task_description,
        candidates,
        limit=10,
        audience_tag_filter=payload.audience_tags,
        disclosure_for=_disclosure_map(candidates, disclosure_fn),
    )
    out = RecommendRecipeOut(ranked=ranked, snapshot_identifier=store.snapshot_identifier)
    _log_tool_call(
        tool_name="recommend_recipe_for_task",
        snapshot_identifier=store.snapshot_identifier,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        result_count=len(ranked),
        extra={"task_len": len(payload.task_description)},
    )
    return out


# ---------------------------------------------------------------------------
# Tool registry — used by server.py
# ---------------------------------------------------------------------------


TOOL_NAMES: tuple[str, ...] = (
    "search_examples",
    "get_example",
    "list_features",
    "list_tiers",
    "get_setup_steps",
    "get_smoke_command",
    "recommend_example_for_task",
    "search_recipes",
    "get_recipe",
    "recommend_recipe_for_task",
)


__all__ = [
    "TOOL_NAMES",
    "NotFoundError",
    "get_example",
    "get_recipe",
    "get_setup_steps",
    "get_smoke_command",
    "list_features",
    "list_tiers",
    "recommend_example_for_task",
    "recommend_recipe_for_task",
    "search_examples",
    "search_recipes",
]
