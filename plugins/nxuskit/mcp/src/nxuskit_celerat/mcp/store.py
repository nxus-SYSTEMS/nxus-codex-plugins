"""MetadataStore: load the bundled snapshot once, expose typed lookups.

FR-009 + Phase 0 R-007: the MCP reads ``snapshot.json`` (generated from
``examples_manifest.json`` + companions) at startup using ``orjson`` for
speed, validates against the Pydantic ``MetadataSnapshot`` model, and
builds O(1) lookup tables.  Read-only; nothing mutates after load.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Final

import orjson

from .logging_config import get_logger
from .models import (
    AudienceTagLiteral,
    Example,
    Feature,
    LanguageLiteral,
    MetadataSnapshot,
    Recipe,
    RecipeLanguageLiteral,
    Tier,
    TierLiteral,
    WorkflowTagLiteral,
)


class SnapshotMissingError(RuntimeError):
    """Raised when ``snapshot.json`` cannot be loaded.

    The MCP server treats this as fatal at startup; the skill falls back
    to the shipped reference index.
    """


# Default location relative to this module's installed package: walk
# up three parents to reach ``plugins/nxuskit/mcp/`` and then into
# ``metadata/snapshot.json``.
_DEFAULT_SNAPSHOT_RELPATH: Final[str] = "metadata/snapshot.json"


def default_snapshot_path() -> Path:
    """Compute the bundled snapshot path relative to this package install.

    Layout: ``plugins/nxuskit/mcp/src/nxuskit_celerat/mcp/store.py`` →
    ``plugins/nxuskit/mcp/metadata/snapshot.json``.
    """
    here = Path(__file__).resolve()
    # here = .../mcp/src/nxuskit_celerat/mcp/store.py
    # parents[0] = mcp/, parents[1] = nxuskit_celerat/, parents[2] = src/, parents[3] = mcp/
    package_root = here.parents[3]
    return (package_root / _DEFAULT_SNAPSHOT_RELPATH).resolve()


class MetadataStore:
    """In-memory read-only store loaded from a single JSON snapshot."""

    def __init__(self, snapshot: MetadataSnapshot, *, source_path: Path) -> None:
        self._snapshot = snapshot
        self._source_path = source_path

        # Indices, computed once.
        self._examples_by_id: dict[str, Example] = {ex.id: ex for ex in snapshot.examples}
        self._recipes_by_id: dict[str, Recipe] = {r.id: r for r in snapshot.recipes}
        self._features_by_id: dict[str, Feature] = {f.id: f for f in snapshot.features}
        self._tiers_by_id: dict[TierLiteral, Tier] = {t.id: t for t in snapshot.tiers}

        self._examples_by_tier: dict[TierLiteral, set[str]] = defaultdict(set)
        self._examples_by_language: dict[LanguageLiteral, set[str]] = defaultdict(set)
        self._examples_by_audience_tag: dict[AudienceTagLiteral, set[str]] = defaultdict(set)
        self._examples_by_tech_tag: dict[str, set[str]] = defaultdict(set)
        for ex in snapshot.examples:
            self._examples_by_tier[ex.tier].add(ex.id)
            for lang in ex.languages:
                self._examples_by_language[lang].add(ex.id)
            for atag in ex.audience_tags:
                self._examples_by_audience_tag[atag].add(ex.id)
            for ttag in ex.tech_tags:
                self._examples_by_tech_tag[ttag].add(ex.id)

        self._recipes_by_tier: dict[TierLiteral, set[str]] = defaultdict(set)
        self._recipes_by_language: dict[RecipeLanguageLiteral, set[str]] = defaultdict(set)
        self._recipes_by_audience_tag: dict[AudienceTagLiteral, set[str]] = defaultdict(set)
        self._recipes_by_workflow_tag: dict[WorkflowTagLiteral, set[str]] = defaultdict(set)
        for r in snapshot.recipes:
            self._recipes_by_tier[r.tier].add(r.id)
            for rlang in r.languages:
                self._recipes_by_language[rlang].add(r.id)
            for r_atag in r.audience_tags:
                self._recipes_by_audience_tag[r_atag].add(r.id)
            for r_wtag in r.workflow_tags:
                self._recipes_by_workflow_tag[r_wtag].add(r.id)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, snapshot_path: Path | None = None) -> MetadataStore:
        """Load and validate ``snapshot.json``.  Raises ``SnapshotMissingError``."""
        path = (snapshot_path or default_snapshot_path()).resolve()
        log = get_logger()
        if not path.is_file():
            log.error("snapshot_missing", path=str(path))
            raise SnapshotMissingError(
                f"Metadata snapshot not found at {path!s}.  "
                "Set NXUSKIT_CELERAT_METADATA or regenerate via "
                "scripts/generate-mcp-metadata.py."
            )
        try:
            raw = path.read_bytes()
            data = orjson.loads(raw)
        except orjson.JSONDecodeError as exc:
            log.error("snapshot_invalid_json", path=str(path), error=str(exc))
            raise SnapshotMissingError(f"snapshot.json at {path!s} is not valid JSON: {exc}") from exc

        try:
            snap = MetadataSnapshot.model_validate(data)
        except Exception as exc:  # pydantic.ValidationError is unwieldy; re-raise as our type
            log.error("snapshot_schema_violation", path=str(path), error=str(exc))
            raise SnapshotMissingError(
                f"snapshot.json at {path!s} does not match the MetadataSnapshot schema: {exc}"
            ) from exc

        log.info(
            "snapshot_loaded",
            path=str(path),
            snapshot_identifier=snap.meta.identifier,
            examples=len(snap.examples),
            recipes=len(snap.recipes),
            features=len(snap.features),
        )
        return cls(snap, source_path=path)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def snapshot(self) -> MetadataSnapshot:
        return self._snapshot

    @property
    def snapshot_identifier(self) -> str:
        return self._snapshot.meta.identifier

    @property
    def source_path(self) -> Path:
        return self._source_path

    @property
    def is_loaded(self) -> bool:
        return True  # if a Store instance exists, it's loaded; load() raises otherwise.

    # ------------------------------------------------------------------
    # ID lookups
    # ------------------------------------------------------------------

    def get_example(self, example_id: str) -> Example | None:
        return self._examples_by_id.get(example_id)

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        return self._recipes_by_id.get(recipe_id)

    def get_feature(self, feature_id: str) -> Feature | None:
        return self._features_by_id.get(feature_id)

    def get_tier(self, tier_id: TierLiteral) -> Tier | None:
        return self._tiers_by_id.get(tier_id)

    def list_examples(self) -> list[Example]:
        return list(self._snapshot.examples)

    def list_recipes(self) -> list[Recipe]:
        return list(self._snapshot.recipes)

    def list_features(self) -> list[Feature]:
        # Sorted by tier (community first), then name (data-model.md spec for list_features)
        ordering = {"community": 0, "pro": 1}
        return sorted(self._snapshot.features, key=lambda f: (ordering[f.tier], f.name))

    def list_tiers(self) -> list[Tier]:
        return list(self._snapshot.tiers)

    # ------------------------------------------------------------------
    # Filtered iteration
    # ------------------------------------------------------------------

    def iter_examples(
        self,
        *,
        languages: Iterable[LanguageLiteral] | None = None,
        tiers: Iterable[TierLiteral] | None = None,
        audience_tags: Iterable[AudienceTagLiteral] | None = None,
        tech_tags: Iterable[str] | None = None,
    ) -> list[Example]:
        ids = set(self._examples_by_id.keys())
        if languages:
            lang_ids: set[str] = set()
            for lang in languages:
                lang_ids |= self._examples_by_language.get(lang, set())
            ids &= lang_ids
        if tiers:
            tier_ids: set[str] = set()
            for tier in tiers:
                tier_ids |= self._examples_by_tier.get(tier, set())
            ids &= tier_ids
        if audience_tags:
            aud_ids: set[str] = set()
            for atag in audience_tags:
                aud_ids |= self._examples_by_audience_tag.get(atag, set())
            ids &= aud_ids
        if tech_tags:
            tech_ids: set[str] = set()
            for ttag in tech_tags:
                tech_ids |= self._examples_by_tech_tag.get(ttag, set())
            ids &= tech_ids
        return [self._examples_by_id[i] for i in ids]

    def iter_recipes(
        self,
        *,
        languages: Iterable[RecipeLanguageLiteral] | None = None,
        tiers: Iterable[TierLiteral] | None = None,
        audience_tags: Iterable[AudienceTagLiteral] | None = None,
        workflow_tags: Iterable[WorkflowTagLiteral] | None = None,
    ) -> list[Recipe]:
        ids = set(self._recipes_by_id.keys())
        if languages:
            lang_ids: set[str] = set()
            for lang in languages:
                lang_ids |= self._recipes_by_language.get(lang, set())
            ids &= lang_ids
        if tiers:
            tier_ids: set[str] = set()
            for tier in tiers:
                tier_ids |= self._recipes_by_tier.get(tier, set())
            ids &= tier_ids
        if audience_tags:
            aud_ids: set[str] = set()
            for r_atag in audience_tags:
                aud_ids |= self._recipes_by_audience_tag.get(r_atag, set())
            ids &= aud_ids
        if workflow_tags:
            wf_ids: set[str] = set()
            for r_wtag in workflow_tags:
                wf_ids |= self._recipes_by_workflow_tag.get(r_wtag, set())
            ids &= wf_ids
        return [self._recipes_by_id[i] for i in ids]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def self_check(self) -> dict[str, object]:
        return {
            "snapshot_identifier": self.snapshot_identifier,
            "source_path": str(self._source_path),
            "examples": len(self._snapshot.examples),
            "recipes": len(self._snapshot.recipes),
            "features": len(self._snapshot.features),
            "tiers": len(self._snapshot.tiers),
            "plugin_version": self._snapshot.meta.plugin_version,
            "source_repo_commit": self._snapshot.meta.source_repo_commit,
        }


__all__ = ["MetadataStore", "SnapshotMissingError", "default_snapshot_path"]
