"""Pydantic v2 models for nxuskit-celerat-mcp.

Single source of truth for all data shapes consumed and produced by the MCP
server. Runtime validation uses ``model_json_schema()``-compatible Pydantic
models for the bundled metadata snapshot and tool responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

# ---------------------------------------------------------------------------
# Vocabularies (FR-011)
# ---------------------------------------------------------------------------

TierLiteral = Literal["community", "pro"]

LanguageLiteral = Literal["rust", "go", "python", "bash"]

CategoryLiteral = Literal["patterns", "integrations", "apps"]

DifficultyLiteral = Literal["starter", "intermediate", "advanced"]

AudienceTagLiteral = Literal[
    "developer",
    "cli-automation",
    "knowledge-work",
    "decision-support",
    "audit",
    "forecasting",
    "healthcare",
]

WorkflowTagLiteral = Literal[
    "local-only",
    "de-identified",
    "phi-sensitive",
]

RecipeLanguageLiteral = Literal["bash", "python"]

RedactionModeLiteral = Literal["passthrough", "schema_level"]

RecipeInputTypeLiteral = Literal["file_path", "string", "json", "number", "boolean"]

# Reused string constraints
NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
ContentHash = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
GitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]


# ---------------------------------------------------------------------------
# Base config — strict by default
# ---------------------------------------------------------------------------


class _Strict(BaseModel):
    """Base model: forbid unknown fields, validate on assignment."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=False,
        str_strip_whitespace=False,
    )


# ---------------------------------------------------------------------------
# Tier (data-model.md Tier)
# ---------------------------------------------------------------------------


class Tier(_Strict):
    id: TierLiteral
    display_label: NonEmptyStr
    disclosure_copy_ref: NonEmptyStr


# ---------------------------------------------------------------------------
# Example (data-model.md Example)
# ---------------------------------------------------------------------------


class Example(_Strict):
    id: NonEmptyStr
    name: NonEmptyStr
    description: NonEmptyStr
    category: CategoryLiteral
    tier: TierLiteral
    languages: list[LanguageLiteral] = Field(min_length=1)
    tech_tags: list[str] = Field(default_factory=list)
    audience_tags: list[AudienceTagLiteral] = Field(min_length=1)
    implementations: dict[str, str] = Field(min_length=1)
    difficulty: DifficultyLiteral
    tagline: str | None = None
    blurb: str | None = None
    smoke_command: str | None = None
    smoke_cwd: str | None = None
    smoke_requires: dict[str, bool] = Field(default_factory=dict)
    groups: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    content_hash: ContentHash


# ---------------------------------------------------------------------------
# Recipe (data-model.md Recipe + FR-023a)
# ---------------------------------------------------------------------------


class RecipeInput(_Strict):
    name: NonEmptyStr
    type: RecipeInputTypeLiteral
    description: NonEmptyStr
    required: bool = True
    accepts_phi: bool = False


class RedactionBoundary(_Strict):
    mode: RedactionModeLiteral
    schema_level_allowlist: list[str] = Field(default_factory=list)


class CorrelationHandleDeclaration(_Strict):
    """FR-023a: declared passthrough field for ``phi-sensitive`` recipes.

    The ``author_assertion_not_derived_from_phi`` field MUST be ``True``;
    a recipe that omits the assertion or sets it to ``False`` is rejected
    at load time (Pydantic ``Literal[True]`` is the runtime gate, mirrored
    by ``const: true`` in the JSON Schema).
    """

    field_name: NonEmptyStr
    description: NonEmptyStr
    author_assertion_not_derived_from_phi: Literal[True]
    workspace_context: Annotated[str, StringConstraints(min_length=5)]


class Recipe(_Strict):
    id: NonEmptyStr
    name: NonEmptyStr
    description: NonEmptyStr
    audience_tags: list[AudienceTagLiteral] = Field(min_length=1)
    workflow_tags: list[WorkflowTagLiteral] = Field(default_factory=list)
    tier: TierLiteral
    languages: list[RecipeLanguageLiteral] = Field(min_length=1)
    required_inputs: list[RecipeInput] = Field(default_factory=list)
    expected_output_schema: dict[str, object]
    smoke_command: NonEmptyStr
    verification_command: str | None = None
    requires_cli_at_least: str | None = None
    redaction_boundary: RedactionBoundary
    correlation_handles: list[CorrelationHandleDeclaration] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _phi_sensitive_requires_schema_level(self) -> Recipe:
        """FR-023 cross-field invariant.

        A ``phi-sensitive`` recipe MUST use ``schema_level`` redaction.
        This is the runtime second-line of defense behind the JSON-Schema
        ``allOf`` constraint in ``contracts/metadata-snapshot.schema.json``.
        """
        if "phi-sensitive" in self.workflow_tags and self.redaction_boundary.mode != "schema_level":
            raise ValueError(
                "Recipe carries 'phi-sensitive' workflow tag but "
                "redaction_boundary.mode is not 'schema_level' "
                "(FR-023 / contracts/phi-boundary.md §2)."
            )
        return self

    @field_validator("correlation_handles")
    @classmethod
    def _unique_handle_names(
        cls, value: list[CorrelationHandleDeclaration]
    ) -> list[CorrelationHandleDeclaration]:
        """Each declared correlation_handle field_name must be unique within a recipe."""
        names = [h.field_name for h in value]
        if len(names) != len(set(names)):
            duplicates = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(
                f"Duplicate correlation_handle field_name(s): {duplicates}"
            )
        return value


# ---------------------------------------------------------------------------
# Feature (data-model.md Feature)
# ---------------------------------------------------------------------------


class Feature(_Strict):
    id: NonEmptyStr
    name: NonEmptyStr
    description: NonEmptyStr
    tier: TierLiteral
    tech_tag_aliases: list[str] = Field(default_factory=list)
    related_examples: list[str] = Field(default_factory=list)
    related_recipes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Snapshot (data-model.md MetadataSnapshot)
# ---------------------------------------------------------------------------


class SnapshotMeta(_Strict):
    identifier: NonEmptyStr
    source_repo_commit: GitSha
    source_files: list[str] = Field(min_length=1)
    generation_timestamp: datetime
    generator_version: NonEmptyStr
    content_hash: ContentHash
    plugin_version: NonEmptyStr


class MetadataSnapshot(_Strict):
    meta: SnapshotMeta
    examples: list[Example]
    recipes: list[Recipe]
    features: list[Feature]
    tiers: list[Tier] = Field(min_length=2, max_length=2)


# ---------------------------------------------------------------------------
# Tool I/O models (contracts/mcp-tools.md)
# ---------------------------------------------------------------------------


class ExampleSummary(_Strict):
    id: NonEmptyStr
    name: NonEmptyStr
    tier: TierLiteral
    languages: list[LanguageLiteral]
    audience_tags: list[AudienceTagLiteral]
    tagline: str | None
    score: float


class RankedExample(ExampleSummary):
    why_this_one: NonEmptyStr


class RecipeSummary(_Strict):
    id: NonEmptyStr
    name: NonEmptyStr
    tier: TierLiteral
    audience_tags: list[AudienceTagLiteral]
    workflow_tags: list[WorkflowTagLiteral]
    score: float


class RankedRecipe(RecipeSummary):
    why_this_one: NonEmptyStr
    disclosure: str | None


# search_examples


class SearchExamplesIn(_Strict):
    query: NonEmptyStr
    languages: list[LanguageLiteral] | None = None
    tiers: list[TierLiteral] | None = None
    audience_tags: list[AudienceTagLiteral] | None = None
    tech_tags: list[str] | None = None
    limit: int = Field(default=10, ge=1, le=50)


class SearchExamplesOut(_Strict):
    results: list[ExampleSummary]
    snapshot_identifier: NonEmptyStr


# get_example


class GetExampleIn(_Strict):
    id: NonEmptyStr


class GetExampleOut(_Strict):
    example: Example
    snapshot_identifier: NonEmptyStr


# list_features


class ListFeaturesOut(_Strict):
    features: list[Feature]
    snapshot_identifier: NonEmptyStr


# list_tiers


class ListTiersOut(_Strict):
    tiers: list[Tier]


# get_setup_steps


class GetSetupStepsIn(_Strict):
    example_id: NonEmptyStr
    language: LanguageLiteral | None = None


class GetSetupStepsOut(_Strict):
    example_id: NonEmptyStr
    language: LanguageLiteral
    steps: list[str]
    source_path: NonEmptyStr
    snapshot_identifier: NonEmptyStr


# get_smoke_command


class GetSmokeCommandIn(_Strict):
    example_id: NonEmptyStr
    language: LanguageLiteral | None = None


class GetSmokeCommandOut(_Strict):
    example_id: NonEmptyStr
    language: LanguageLiteral | None
    command: str | None
    cwd: str | None
    requires: dict[str, bool] = Field(default_factory=dict)


# recommend_example_for_task


class RecommendExampleIn(_Strict):
    task_description: Annotated[str, StringConstraints(min_length=10)]
    languages: list[LanguageLiteral] | None = None
    tiers: list[TierLiteral] | None = None
    audience_tags: list[AudienceTagLiteral] | None = None


class RecommendExampleOut(_Strict):
    ranked: list[RankedExample]
    snapshot_identifier: NonEmptyStr


# search_recipes


class SearchRecipesIn(_Strict):
    query: NonEmptyStr
    audience_tags: list[AudienceTagLiteral] | None = None
    workflow_tags: list[WorkflowTagLiteral] | None = None
    tiers: list[TierLiteral] | None = None
    languages: list[RecipeLanguageLiteral] | None = None
    limit: int = Field(default=10, ge=1, le=50)


class SearchRecipesOut(_Strict):
    results: list[RecipeSummary]
    snapshot_identifier: NonEmptyStr


# get_recipe


class GetRecipeIn(_Strict):
    id: NonEmptyStr


class GetRecipeOut(_Strict):
    recipe: Recipe
    disclosure: str | None
    snapshot_identifier: NonEmptyStr


# recommend_recipe_for_task


class RecommendRecipeIn(_Strict):
    task_description: Annotated[str, StringConstraints(min_length=10)]
    audience_tags: list[AudienceTagLiteral] | None = None
    workflow_tags: list[WorkflowTagLiteral] | None = None
    tiers: list[TierLiteral] | None = None


class RecommendRecipeOut(_Strict):
    ranked: list[RankedRecipe]
    snapshot_identifier: NonEmptyStr


__all__ = [
    "AudienceTagLiteral",
    "CategoryLiteral",
    "CorrelationHandleDeclaration",
    "DifficultyLiteral",
    "Example",
    # Tool I/O
    "ExampleSummary",
    "Feature",
    "GetExampleIn",
    "GetExampleOut",
    "GetRecipeIn",
    "GetRecipeOut",
    "GetSetupStepsIn",
    "GetSetupStepsOut",
    "GetSmokeCommandIn",
    "GetSmokeCommandOut",
    "LanguageLiteral",
    "ListFeaturesOut",
    "ListTiersOut",
    "MetadataSnapshot",
    "RankedExample",
    "RankedRecipe",
    "Recipe",
    "RecipeInput",
    "RecipeInputTypeLiteral",
    "RecipeLanguageLiteral",
    "RecipeSummary",
    "RecommendExampleIn",
    "RecommendExampleOut",
    "RecommendRecipeIn",
    "RecommendRecipeOut",
    "RedactionBoundary",
    "RedactionModeLiteral",
    "SearchExamplesIn",
    "SearchExamplesOut",
    "SearchRecipesIn",
    "SearchRecipesOut",
    "SnapshotMeta",
    # Core entities
    "Tier",
    # Vocabularies
    "TierLiteral",
    "WorkflowTagLiteral",
]
