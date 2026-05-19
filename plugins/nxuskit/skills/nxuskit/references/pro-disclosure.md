# Pro Disclosure

Required disclosure copy for nxusKit Pro features. The skill (`SKILL.md` §3, §8) cross-references this document and MUST present the appropriate block BEFORE generating any Pro-dependent code.

**Wording rule (FR-012)**: trial-and-license copy uses the phrase "**eligible trial or license**". Do not promise a specific trial duration in plugin copy. For the canonical, current trial / EULA wording, see the nxusKit license activation guide at `https://docs.nxus.systems/sdk/licensing`.

---

## Master block

Use this when the user has asked for a Pro capability without naming a specific feature, or when multiple Pro features apply.

### Pro disclosure: nxusKit Pro features

**Feature**: nxusKit Pro capability set (Z3-backed solver, solver what-if analysis, ZEN decision tables, and plugin loading / trust-policy capabilities).

**Why Pro**: These capabilities are gated to nxusKit Pro. To use them, sign in and activate an **eligible trial or license**, then verify status before continuing.

**Community-Edition alternative**: For deterministic decision logic that does not require constraint solving, see `clips-basics` and `clips-llm-hybrid` in `references/example-index.md`. For probabilistic reasoning, see `bayesian-inference`. The skill MUST offer these alternatives if the user's intent permits.

**Activate**:

```bash
nxuskit-cli license login
nxuskit-cli license activate --key <purchase-id> --accept-eula --json
nxuskit-cli license status --json
```

**What Codex can still do without Pro**: Codex can still scaffold the data-modeling and pre-/post-processing parts of the workflow with CE-only patterns (LLM extraction, CLIPS validation, Bayesian inference) and stub the Pro-dependent step so it can be wired up after activation.

---

## Per-feature variants

Each variant is a thin specialization of the master block. They MUST satisfy the same five-section structure (feature name / why Pro / CE alternative / activation commands / what Codex can still do without Pro).

### Pro disclosure: Z3-backed solver

**Feature**: Z3-backed solver (constraint solving over Boolean, integer, and arithmetic theories).

**Why Pro**: Z3 solver integration is gated to nxusKit Pro. To use it, sign in and activate an **eligible trial or license**, then verify status before continuing.

**Community-Edition alternative**: For rule-based decision logic that does not require a constraint solver, see `clips-basics` and `clips-llm-hybrid` in the example index. There is no CE equivalent for actual constraint solving.

**Activate**: see the master-block bash fence above.

**What Codex can still do without Pro**: Codex can scaffold the data-modeling and pre-/post-processing layers (LLM extraction, CLIPS validation) and leave a clearly-labeled stub where the solver call belongs.

### Pro disclosure: solver what-if analysis

**Feature**: solver what-if analysis (scoped re-solving against a baseline solution under altered constraints).

**Why Pro**: What-if analysis depends on the Z3 solver and is gated to nxusKit Pro along with it. To use it, sign in and activate an **eligible trial or license**, then verify status before continuing.

**Community-Edition alternative**: There is no Community-Edition equivalent for what-if analysis. The closest CE workflow is repeated CLIPS rule evaluation under different fact bases.

**Activate**: see the master-block bash fence above.

**What Codex can still do without Pro**: Codex can model the baseline scenario and the altered constraints as data, and leave the solver invocation as a stub for activation.

### Pro disclosure: ZEN decision tables

**Feature**: ZEN decision tables (JSON Decision Model evaluation).

**Why Pro**: ZEN decision-table evaluation is gated to nxusKit Pro. To use it, sign in and activate an **eligible trial or license**, then verify status before continuing.

**Community-Edition alternative**: For rule-based decisions, see `clips-basics` in the example index. CLIPS does not match ZEN's tabular representation, but it covers the same decision-logic territory.

**Activate**: see the master-block bash fence above.

**What Codex can still do without Pro**: Codex can transcribe the decision table into a CLIPS rule set as a CE alternative, or leave a stub at the ZEN evaluation point for later activation.

### Pro disclosure: BN→solver→CLIPS pipeline (solver step)

**Feature**: BN→solver→CLIPS pipeline (Bayesian inference, then constraint optimization, then CLIPS validation). The solver step is the Pro-gated portion.

**Why Pro**: The solver stage of the pipeline depends on Z3 and is gated to nxusKit Pro. To use it, sign in and activate an **eligible trial or license**, then verify status before continuing.

**Community-Edition alternative**: A `BN → CLIPS` pipeline (skipping the solver step) is fully CE-suitable. See `clips-llm-hybrid` and `bayesian-inference` in the example index.

**Activate**: see the master-block bash fence above.

**What Codex can still do without Pro**: Codex can implement the BN and CLIPS stages and the I/O contracts on either side of the solver, leaving the solver call as a clearly-labeled stub.

### Pro disclosure: nxusKit plugin loading and trust policy

**Feature**: nxusKit plugin loading and trust policy (signed shared-library SDK extensions loaded through the nxusKit ABI).

**Why Pro**: The plugin loader and trust-policy enforcement are gated to nxusKit Pro. To use them, sign in and activate an **eligible trial or license**, then verify status before continuing. (Note: this is about *nxusKit runtime plugins*, not Codex Plugins. See `SKILL.md` §11.)

**Community-Edition alternative**: There is no Community-Edition equivalent for loading signed runtime plugins. CE applications can still consume nxusKit's built-in providers and reasoning engines without runtime-plugin loading.

**Activate**: see the master-block bash fence above.

**What Codex can still do without Pro**: Codex can scaffold the application layer that *would* consume runtime-plugin output, using a CE-only nxusKit configuration that does not load runtime plugins.
