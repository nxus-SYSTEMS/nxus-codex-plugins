<!-- generated: 2026-04-30; manifest: nxusKit-examples/conformance/examples_manifest.json; covered: 19/19; guidance-only: 0/19 -->

# nxusKit Example Index

> **MCP note**: the local MCP `nxuskit-celerat`
> supersedes this index when available — call `search_examples`,
> `recommend_example_for_task`, or `get_example` first
> (see SKILL.md §13). This file remains as the MCP-down fallback per
> SC-011.

Curated index of canonical nxusKit examples, generated from the examples manifest. Use this when selecting a starting point for an integration. The skill instructions cross-reference rows here by `name`.

> **Generated artifact.** Do not hand-edit individual rows — re-run `scripts/generate-example-index.py` instead. Source data lives in the nxusKit examples manifest.

**Tier legend**: `CE` = Community Edition (free, included in nxusKit SDK). `Pro` = nxusKit Pro (eligible trial or license required; the skill MUST show the Pro disclosure block before generating Pro-dependent code).

**Languages legend**: `rust`, `go`, `python`, `cli/bash`. Multiple values comma-separated.

| name | category | tier | languages | tags | description | source_path | run_command | related |
|---|---|---|---|---|---|---|---|---|
| basic-chat | llm | CE | rust,go,python | llm | Basic chat completion with a simple prompt | examples/patterns/basic-chat/rust | n/a | - |
| streaming | llm | CE | rust,go,python | llm,streaming | Streaming chat completion with real-time output | examples/patterns/streaming/rust | n/a | - |
| multi-provider | llm | CE | rust,go,python,cli/bash | llm | Using multiple providers in one application | examples/patterns/multi-provider/rust | n/a | - |
| capability-detection | llm | CE | rust,go,cli/bash | llm | Detecting provider capabilities at runtime | examples/patterns/capability-detection/rust | n/a | - |
| cost-routing | llm | CE | rust,go,python,cli/bash | llm | Cost-aware provider routing and selection | examples/patterns/cost-routing/rust | n/a | - |
| retry-fallback | llm | CE | rust,go,python,cli/bash | llm | Retry and fallback strategies across providers | examples/patterns/retry-fallback/rust | n/a | - |
| structured-output | llm | CE | rust,go,python,cli/bash | llm | JSON mode and structured output generation | examples/patterns/structured-output/rust | n/a | - |
| vision | llm | CE | rust,go,python | llm,vision | Vision and multimodal capabilities with images | examples/patterns/vision/rust | n/a | - |
| auth-helper | llm | CE | rust,go | auth,oauth | OAuth login flow and credential management helper | examples/patterns/auth-helper/cli | n/a | - |
| clips-basics | reasoning | CE | rust,go,cli/bash | clips | CLIPS rule engine basics via nxusKit SDK | examples/integrations/clips-basics/rust | n/a | - |
| clips-llm-hybrid | hybrid | CE | rust,go,python,cli/bash | llm,clips | Hybrid CLIPS rules + LLM reasoning | examples/integrations/clips-llm-hybrid/rust | n/a | - |
| bayesian-inference | llm | CE | rust,go,python,cli/bash | bn | Bayesian network inference via nxusKit SDK | examples/patterns/bayesian-inference/rust | n/a | - |
| solver | reasoning | Pro | rust,go,python,cli/bash | solver | Z3 constraint solver integration via nxusKit SDK | examples/patterns/solver/rust | n/a | - |
| solver-what-if | reasoning | Pro | rust,go,python | solver | What-if scenario analysis with solver scoping | examples/patterns/solver-what-if/rust | n/a | - |
| llm-solver-hybrid | hybrid | Pro | rust,go,python,cli/bash | llm,solver | Hybrid LLM + Z3 solver problem solving | examples/integrations/llm-solver-hybrid/rust | n/a | - |
| bn-solver-clips-pipeline | reasoning | Pro | rust,go,cli/bash | clips,solver,bn | Three-stage BN prediction → Solver optimization → CLIPS safety pipeline | examples/integrations/bn-solver-clips-pipeline/rust | n/a | - |
| zen-decisions | reasoning | Pro | rust,go,python,cli/bash | zen | ZEN decision table evaluation via nxusKit SDK | examples/integrations/zen-decisions/rust | n/a | - |
| ruler | hybrid | Pro | rust,go,cli/bash | llm,clips | LLM-powered CLIPS rule generator with automatic validation | examples/apps/ruler/rust | n/a | - |
| arbiter | hybrid | Pro | rust,go,cli/bash | llm,clips | CLIPS-validated LLM retry app with rule-based answer verification | examples/apps/arbiter/rust | n/a | - |

## Run-command convention

The `run_command` column is `n/a` because run commands are language-specific and project-specific. Use the per-language smoke recipes in `setup-and-smoke.md` when selecting a verification command:

- Rust: `cargo run -p <example>` from the example's workspace, or `cargo check` if running is gated by credentials.
- Go: `go run ./examples/...` or `go test ./...` against the example's directory.
- Python: import-smoke (`python -c "import <module>"`) or the example's pytest target.
- CLI/Bash: `nxuskit-cli` probe-first per FR-015a, then JSON-first `nxuskit-cli call` with provider `loopback`, or a local-provider reachability smoke.

## Coverage report

- Total required names: 19
- Covered by examples manifest: 19
- Marked guidance-only: 0
