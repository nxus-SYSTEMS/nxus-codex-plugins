"""PHI boundary enforcement (FR-019, FR-021, FR-022, FR-023, FR-023a, FR-023b, FR-028).

Implements the runtime side of `contracts/phi-boundary.md`:

- :func:`enforce_schema_level` — strip every field that is not in the
  recipe's ``redaction_boundary.schema_level_allowlist`` AND not declared
  as a ``correlation_handle.field_name``.  Emits a structured log line
  per stripped field (field NAME only, never VALUE).
- :func:`assert_correlation_handle_declared` — true iff ``field_name``
  appears in ``recipe.correlation_handles[*].field_name``.
- :func:`disclosure_copy` — FR-023b verbatim non-claim string.
- :func:`remote_mcp_warning_copy` — FR-022 third-party warning.
- :func:`cloud_model_phi_refusal_copy` — FR-021 BAA + local-provider
  alternative.

All copy constants are frozen module-level strings; tests assert
verbatim equality.
"""

from __future__ import annotations

from typing import Any

from .logging_config import get_logger
from .models import Recipe

# ---------------------------------------------------------------------------
# Frozen copy (FR-019, FR-021, FR-022, FR-023b)
# ---------------------------------------------------------------------------


_DISCLOSURE_COPY: str = (
    "Celerat does not perform HIPAA Safe Harbor de-identification, does not "
    "ship a de-identification scrubber, and does not certify any output as "
    '"de-identified." Schema-level filtering on this recipe\'s output is a '
    "safety net, not a compliance guarantee. Responsibility for ensuring any "
    "declared correlation_handle meets Safe Harbor's "
    '"non-identifying record code" criterion (45 CFR §164.514(b)(2)(i)(R)) '
    "rests with the recipe author and the auditor's organization. Installing "
    "this plugin does not make Codex HIPAA-compliant or constitute a "
    "covered-entity / business-associate solution."
)


_REMOTE_MCP_WARNING_COPY: str = (
    "Remote MCP servers are third-party services. Data you send them is "
    "subject to the third party's retention and residency policies, which "
    "may differ from Celerat's local-only defaults. For PHI-sensitive "
    "workflows, prefer a local stdio MCP and a local provider through "
    "nxusKit. (Sources: OpenAI data-control docs at "
    "https://platform.openai.com/docs/guides/your-data ; "
    "HHS HIPAA de-identification guidance at "
    "https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html .)"
)


_CLOUD_MODEL_PHI_REFUSAL_COPY: str = (
    "Real PHI workflows require customer compliance review and appropriate "
    "agreements (e.g., a Business Associate Agreement) before any "
    "OpenAI-hosted model or remote MCP receives PHI. Until that's in place, "
    "here's a local-provider alternative through nxusKit (Ollama / LM Studio): "
    "use `recommend_recipe_for_task` with workflow_tags=[\"phi-sensitive\", "
    "\"local-only\"] to find the right `kw-` recipe."
)


_CHAT_PHI_REFUSAL_COPY: str = (
    "Celerat doesn't accept patient information in chat. Please keep PHI in "
    "your local files or your authorized workspace (EMR or case-management "
    "system). I can help you set up a local nxusKit pipeline that reads those "
    "files locally; the only thing that comes back to me is a schema-level "
    "summary or a draft I can help you review."
)


# ---------------------------------------------------------------------------
# Public copy accessors
# ---------------------------------------------------------------------------


def disclosure_copy() -> str:
    """FR-023b verbatim non-claim string. Returns the same constant on every call."""
    return _DISCLOSURE_COPY


def remote_mcp_warning_copy() -> str:
    """FR-022 third-party warning."""
    return _REMOTE_MCP_WARNING_COPY


def cloud_model_phi_refusal_copy() -> str:
    """FR-021 BAA + local-provider alternative."""
    return _CLOUD_MODEL_PHI_REFUSAL_COPY


def chat_phi_refusal_copy() -> str:
    """FR-019 in-chat PHI refusal copy."""
    return _CHAT_PHI_REFUSAL_COPY


# ---------------------------------------------------------------------------
# Schema-level enforcement (FR-023)
# ---------------------------------------------------------------------------


def assert_correlation_handle_declared(field_name: str, recipe: Recipe) -> bool:
    """True iff ``field_name`` matches a declared ``correlation_handles[*].field_name``."""
    return any(h.field_name == field_name for h in recipe.correlation_handles)


def enforce_schema_level(payload: dict[str, Any], recipe: Recipe) -> dict[str, Any]:
    """Filter ``payload`` keeping only fields permitted by the recipe.

    Allow rules (logical OR):

    1. ``recipe.redaction_boundary.mode == "passthrough"`` — return the
       payload unchanged (non-PHI recipes use this).
    2. The field name is in ``recipe.redaction_boundary.schema_level_allowlist``.
    3. The field name is declared as a ``correlation_handle.field_name``.

    Anything else is stripped, and one ``phi_redaction_strip`` log line is
    emitted per stripped field (field NAME only — never the value).
    """
    if recipe.redaction_boundary.mode == "passthrough":
        return dict(payload)

    allowlist = set(recipe.redaction_boundary.schema_level_allowlist)
    declared_handles = {h.field_name for h in recipe.correlation_handles}
    permitted = allowlist | declared_handles

    out: dict[str, Any] = {}
    log = get_logger()
    for field_name, value in payload.items():
        if field_name in permitted:
            out[field_name] = value
        else:
            log.info(
                "phi_redaction_strip",
                recipe_id=recipe.id,
                field=field_name,
                # Intentionally no `value` key — only field names are logged.
            )
    return out


__all__ = [
    "assert_correlation_handle_declared",
    "chat_phi_refusal_copy",
    "cloud_model_phi_refusal_copy",
    "disclosure_copy",
    "enforce_schema_level",
    "remote_mcp_warning_copy",
]
