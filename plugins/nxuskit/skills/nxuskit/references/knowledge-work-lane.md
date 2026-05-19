# Public-Safe Local Intelligence Lane

The public `nxuskit` plugin supports a local intelligence pattern for workflows
where Codex is the supervisor and nxusKit performs the local work. The public
lane is intentionally generic: evidence organization, checklist review,
forecasting support, diagnostics, source-packet analysis, and other
knowledge-work tasks that can be represented through structured recipes.

Persona-specific regulated workflows, fixtures, and prompts are internal-only
unless a later productization decision approves them for public release.

## The Five-Step Supervision Pattern

Every public-safe knowledge-work recipe follows the same flow:

1. **Codex selects or generates a local Python or CLI/Bash pipeline.**
   The MCP recommends a recipe; the recipe is a pipeline scaffold, not a
   chat-paste workflow.
2. **The pipeline reads local files and calls nxusKit.**
   Source documents stay on the user's machine or in the user's authorized
   workspace.
3. **nxusKit routes sensitive work to a local provider when required.**
   Use Ollama, LM Studio, or another nxusKit-registered local provider when
   inputs may contain regulated or confidential data.
4. **The pipeline emits schema-level outputs back to Codex.**
   `phi_boundary.enforce_schema_level()` keeps only fields declared by the
   recipe's allowlist plus explicitly declared `correlation_handles`.
5. **The human expert reviews and approves final use.**
   Celerat produces structured drafts and findings. The responsible human owns
   the final decision and communication.

## Public Recipe Boundaries

Public recipes may use these audience tags:

- `knowledge-work`
- `audit`
- `decision-support`
- `forecasting`
- `healthcare`

Public recipes may use these workflow tags:

- `local-only`
- `de-identified`
- `phi-sensitive`

The `phi-sensitive` tag triggers the
`redaction_boundary.mode == "schema_level"` invariant and requires any
passthrough correlation handle to be declared explicitly.

## Correlation Handles

A correlation handle is a recipe-declared opt-in passthrough field that Codex is
allowed to receive even when the recipe is `phi-sensitive`.

Three rules apply:

1. The field name must appear in `recipe.correlation_handles[*].field_name`.
2. The declaration must set `author_assertion_not_derived_from_phi: true`.
3. The declaration must describe the authorized workspace context that maps the
   handle back to the underlying local record.

If a field looks like a handle but is not declared, it is stripped. There is no
implicit pattern match.

## Expert-Review Framing

Every public knowledge-work output must be framed as an expert-review draft or
structured finding. Celerat must not claim:

- to make medical determinations;
- to make legal determinations;
- to make billing or reimbursement determinations;
- to make payer-contract determinations;
- to be HIPAA-compliant on the user's behalf; or
- to perform Safe Harbor de-identification on raw inputs.

The disclosure returned for every `phi-sensitive` recipe is the authoritative
non-claim copy. The skill surfaces it before any such recipe runs.

## Source-Packet Pattern

For current research or market-analysis workflows, gather facts first through
browser/search tooling, save the source material as a structured packet, then
use local nxusKit analysis over that packet. Do not claim that a local model
browses unless a concrete tool/search path is selected and capability-validated.

## Cross-Links

- `phi-boundary.md` — end-user PHI and regulated-data boundary.
- `mcp-overview.md` — MCP tool list and fallback behavior.
- `setup-and-smoke.md` — local-provider and CLI/Bash setup.
