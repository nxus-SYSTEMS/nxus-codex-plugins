# Tier Guide

Community-Edition (CE) vs. Pro decision tree for the 14 implementation workflows the skill supports.

> **Authority**: This document is **derived** from the canonical nxusKit tier-comparison documentation at `https://docs.nxus.systems/sdk/tier-comparison`. If a row here disagrees with the canonical tier-comparison document, **the row is in conflict and the release is blocked** until reconciliation. Do not silently override the canonical source.
>
> When in doubt, check the canonical document first and ask the user for direction if a tier classification needs to change.

## Decision-tree summary

If the user's intent fits **only** in the CE column, no Pro disclosure is needed; proceed with implementation.

If the user's intent **requires** any Pro-marked capability, `SKILL.md` §3 + §8 require Codex to show the appropriate Pro disclosure block from `pro-disclosure.md` BEFORE generating any Pro-dependent code. Offer the CE alternative if one exists.

## Workflow → tier mapping

| # | Workflow | CE-suitable? | Pro-required? | Disclosure required? | Notes |
|---|---|---|---|---|---|
| 1 | Basic chat | Yes | — | No | All providers, all editions. |
| 2 | Streaming chat | Yes | — | No | Streaming is CE for cloud and local providers. |
| 3 | Structured JSON output | Yes | — | No | Provider-driven; CE on every supported provider. |
| 4 | Tool / function calling | Yes | — | No | Capability-gated by provider; CE when supported. |
| 5 | Vision / multimodal | Yes | — | No | CE on every provider that exposes vision. |
| 6 | Retry / fallback | Yes | — | No | Adaptive retry is CE. |
| 7 | Multi-provider / cost-aware routing | Yes | — | No | Routing is CE. |
| 8 | Local-provider support (Ollama, LM Studio) | Yes | — | No | Local providers are CE. |
| 9 | Migration from direct provider SDK | Yes | — | No | Migration target is whichever workflow the user picks; tier is determined by the *target* workflow. |
| 10 | CLIPS rule evaluation (basic) | Yes | — | No | `ClipsSession` API is CE. **Note**: CLIPS Advanced (programmatic rules, session persistence) is Pro — disclose if the user asks for those features. |
| 11 | Bayesian inference | Yes | — | No | BN inference is CE up to 50 nodes per the canonical tier matrix. |
| 12 | Solver / what-if or ZEN | — | **Yes** | **Yes — Pro disclosure required before code generation** | Z3-backed solver, solver what-if, and ZEN decision tables are all Pro. CE alternative: CLIPS-only rule logic. See `pro-disclosure.md` "Z3-backed solver", "solver what-if analysis", "ZEN decision tables". |
| 13 | Hybrid LLM + symbolic | Mixed | Mixed | **Yes when solver is involved** | A pipeline of LLM extraction → CLIPS validation is fully CE (`clips-llm-hybrid`). A pipeline that includes a solver step (`llm-solver-hybrid`, `bn-solver-clips-pipeline`) is Pro for the solver portion. See `pro-disclosure.md` "BN→solver→CLIPS pipeline (solver step)". |
| 14 | `nxuskit-cli` Bash / JSON prototype | Yes | — | No | The CLI itself is CE; specific subcommands inherit the tier of the underlying capability they invoke. |

## Adjacent Pro-marked capabilities (not workflows but worth knowing)

These are not in the core workflow list but the skill MUST disclose if a user asks for them:

- **MCP (Model Context Protocol) server / client features**: This plugin does not ship MCP tools. If a user asks Codex to use MCP, explain that the installed plugin provides only skills and references.
- **nxusKit plugin loading and trust policy** (signed runtime plugins): Pro. See `pro-disclosure.md` "nxusKit plugin loading and trust policy". (This is about *nxusKit runtime plugins*, not Codex Plugins.)

## Conflict-resolution guard

If during implementation Codex discovers that the user's intended workflow:

- is marked CE here but Pro in the canonical tier-comparison document, OR
- is marked Pro here but CE in the canonical tier-comparison document, OR
- depends on an undocumented capability whose tier is unclear,

then **STOP** before generating code. Tell the user the tier classification is in conflict, cite both this document and the canonical source, and ask for direction. Do not guess — Constitution II requires that work stops at the affected boundary until the conflict is resolved.
