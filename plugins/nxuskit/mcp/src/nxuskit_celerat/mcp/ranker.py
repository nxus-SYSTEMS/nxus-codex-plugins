"""Pure-function fuzzy ranking over examples and recipes.

Backed by ``rapidfuzz.fuzz.WRatio`` (Phase 0 R-003).  Every function
takes the data it needs as arguments — no module-level state, no I/O —
so tests can drive it deterministically.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from rapidfuzz import fuzz

from .models import (
    AudienceTagLiteral,
    Example,
    ExampleSummary,
    RankedExample,
    RankedRecipe,
    Recipe,
    RecipeSummary,
)

# Difficulty ordering: starter is preferred when scores tie (US1 acceptance scenario 2).
_DIFFICULTY_ORDER: dict[str, int] = {"starter": 0, "intermediate": 1, "advanced": 2}

# When recipe metadata has multiple audience tags overlapping the user filter,
# add this many points per overlap on top of the fuzzy score.
_AUDIENCE_TAG_OVERLAP_BONUS = 10.0

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_GENERIC_RECIPE_QUERY_TERMS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "and",
        "bash",
        "cli",
        "for",
        "me",
        "recipe",
        "recommend",
        "run",
        "show",
        "smoke",
        "test",
        "the",
        "this",
        "with",
    }
)


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _meaningful_recipe_query_tokens(query: str) -> set[str]:
    return {t for t in _tokens(query) if len(t) > 2 and t not in _GENERIC_RECIPE_QUERY_TERMS}


def _example_strong_haystack(example: Example) -> str:
    """High-signal text for an example: name + id + tech_tags + groups + description."""
    parts: list[str] = [example.name, example.id, example.description]
    parts.extend(example.tech_tags)
    parts.extend(example.groups)
    return " ".join(parts)


def _example_long_haystack(example: Example) -> str:
    """Lower-signal marketing text: tagline + blurb."""
    parts: list[str] = []
    if example.tagline:
        parts.append(example.tagline)
    if example.blurb:
        parts.append(example.blurb)
    return " ".join(parts)


def _recipe_strong_haystack(recipe: Recipe) -> str:
    """High-signal recipe text: name + id + description."""
    return " ".join([recipe.name, recipe.id, recipe.description])


def _recipe_long_haystack(recipe: Recipe) -> str:
    """Lower-signal recipe text: safety_notes."""
    return " ".join(recipe.safety_notes)


def score_example(query: str, example: Example) -> float:
    """Fuzzy match score in [0.0, 100.0].

    Combine ``token_set_ratio`` over the strong haystack (heavily weighted)
    with ``partial_ratio`` over the long marketing haystack (lightly
    weighted).  This makes terms in the example name / id / tech_tags
    drive ranking, while marketing copy still contributes when relevant.
    """
    strong = float(fuzz.token_set_ratio(query, _example_strong_haystack(example)))
    long_text = _example_long_haystack(example)
    weak = float(fuzz.partial_ratio(query, long_text)) if long_text else 0.0
    return 0.75 * strong + 0.25 * weak


def score_recipe(query: str, recipe: Recipe) -> float:
    """Fuzzy match score in [0.0, 100.0]."""
    strong_haystack = _recipe_strong_haystack(recipe)
    strong = float(fuzz.token_set_ratio(query, strong_haystack))
    long_text = _recipe_long_haystack(recipe)
    weak = float(fuzz.partial_ratio(query, long_text)) if long_text else 0.0
    overlap = _meaningful_recipe_query_tokens(query) & _tokens(strong_haystack)
    return 0.75 * strong + 0.25 * weak + (4.0 * len(overlap))


def _example_haystack(example: Example) -> str:
    """Backward-compat: combined haystack used by why_example."""
    return f"{_example_strong_haystack(example)} {_example_long_haystack(example)}".strip()


def _recipe_haystack(recipe: Recipe) -> str:
    """Backward-compat: combined haystack used by why_recipe."""
    return f"{_recipe_strong_haystack(recipe)} {_recipe_long_haystack(recipe)}".strip()


def rank_examples(
    query: str,
    candidates: Iterable[Example],
    *,
    limit: int = 10,
    prefer_starter: bool = True,
) -> list[RankedExample]:
    """Score and sort examples by relevance to ``query``.

    Tiebreak: ``starter`` difficulty first when scores are within 0.5 (US1 ACS-2).
    """
    scored: list[tuple[float, Example]] = [(score_example(query, ex), ex) for ex in candidates]

    def sort_key(item: tuple[float, Example]) -> tuple[float, int, str]:
        score, ex = item
        # Negate score so higher scores sort first; then difficulty asc; then id for determinism.
        difficulty_rank = _DIFFICULTY_ORDER.get(ex.difficulty, 99) if prefer_starter else 0
        return (-score, difficulty_rank, ex.id)

    scored.sort(key=sort_key)
    top = scored[:limit]
    return [
        RankedExample(
            id=ex.id,
            name=ex.name,
            tier=ex.tier,
            languages=ex.languages,
            audience_tags=ex.audience_tags,
            tagline=ex.tagline,
            score=round(score, 2),
            why_this_one=why_example(query, ex, score),
        )
        for score, ex in top
    ]


def rank_recipes(
    query: str,
    candidates: Iterable[Recipe],
    *,
    limit: int = 10,
    audience_tag_filter: Iterable[AudienceTagLiteral] | None = None,
    audience_tag_overlap_bonus: float = _AUDIENCE_TAG_OVERLAP_BONUS,
    disclosure_for: dict[str, str] | None = None,
) -> list[RankedRecipe]:
    """Score and sort recipes.

    If ``audience_tag_filter`` is provided, recipes get a per-tag-overlap
    bonus on top of the fuzzy score (so a recipe with all the requested
    tags ranks above one with only some).

    If ``disclosure_for`` maps recipe-id → disclosure copy (i.e., the
    PHI-boundary FR-023b non-claim string for ``phi-sensitive`` recipes),
    the relevant ``disclosure`` field is populated; otherwise it is None.
    """
    filter_tags = set(audience_tag_filter or [])
    disclosure_for = disclosure_for or {}
    scored: list[tuple[float, Recipe]] = []
    for r in candidates:
        base = score_recipe(query, r)
        bonus = audience_tag_overlap_bonus * len(filter_tags & set(r.audience_tags))
        scored.append((base + bonus, r))

    scored.sort(key=lambda item: (-item[0], item[1].id))
    top = scored[:limit]
    return [
        RankedRecipe(
            id=r.id,
            name=r.name,
            tier=r.tier,
            audience_tags=r.audience_tags,
            workflow_tags=r.workflow_tags,
            score=round(score, 2),
            why_this_one=why_recipe(query, r, score),
            disclosure=disclosure_for.get(r.id),
        )
        for score, r in top
    ]


def summarize_example(query: str, example: Example) -> ExampleSummary:
    return ExampleSummary(
        id=example.id,
        name=example.name,
        tier=example.tier,
        languages=example.languages,
        audience_tags=example.audience_tags,
        tagline=example.tagline,
        score=round(score_example(query, example), 2),
    )


def summarize_recipe(query: str, recipe: Recipe) -> RecipeSummary:
    return RecipeSummary(
        id=recipe.id,
        name=recipe.name,
        tier=recipe.tier,
        audience_tags=recipe.audience_tags,
        workflow_tags=recipe.workflow_tags,
        score=round(score_recipe(query, recipe), 2),
    )


def why_example(query: str, example: Example, score: float) -> str:
    """1-2 sentence explanation referencing matched terms, difficulty, tier."""
    tier_label = "Community Edition" if example.tier == "community" else "Pro"
    qwords = {w.lower() for w in query.split() if len(w) > 2}
    haystack_words = {w.lower().strip(",.;:") for w in _example_haystack(example).split()}
    overlap = sorted(qwords & haystack_words)
    matched = ", ".join(f"`{w}`" for w in overlap[:3]) if overlap else "your task description"
    return (
        f"{example.name} ({example.difficulty}, {tier_label}) — score {score:.0f}. "
        f"Matched on {matched}; languages: {', '.join(example.languages)}."
    )


def why_recipe(query: str, recipe: Recipe, score: float) -> str:
    """1-2 sentence explanation for a recipe."""
    tier_label = "Community Edition" if recipe.tier == "community" else "Pro"
    audience = ", ".join(recipe.audience_tags)
    workflow = ", ".join(recipe.workflow_tags) if recipe.workflow_tags else "no workflow tags"
    return (
        f"{recipe.name} (audience: {audience}; workflow: {workflow}; {tier_label}) "
        f"— score {score:.0f}. Smoke command: `{recipe.smoke_command}`."
    )


__all__ = [
    "rank_examples",
    "rank_recipes",
    "score_example",
    "score_recipe",
    "summarize_example",
    "summarize_recipe",
    "why_example",
    "why_recipe",
]
