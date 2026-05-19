---
title: Bayesian Solver CLIPS Hybrid
description: Ask Codex to combine CE and Pro reasoning stages safely.
---

# Bayesian Solver CLIPS Hybrid

Prompt:

```text
Combine a Bayesian forecast with solver optimization and CLIPS safety rules.
```

Starter fixture: `examples/fixtures/starters/cli-bash-workspace/`

Expected behavior:

- Label stages before implementation: Bayesian is CE, solver is Pro, CLIPS validation is CE.
- Show the `BN -> solver -> CLIPS pipeline` Pro disclosure before solver work.
- Verify license status before the solver stage.
- Use structured JSON and explicit stage outputs.
- Keep the CLIPS validation independent enough to inspect without re-running the model.

Verification:

```bash
jq empty data/hybrid/bn-input.json
bash -n scripts/bn-solver-clips.sh
bash scripts/bn-solver-clips.sh
```

Good result:

- The script prints each tier-labeled stage.
- Solver output feeds CLIPS validation.
- The final validation status is explicit.
