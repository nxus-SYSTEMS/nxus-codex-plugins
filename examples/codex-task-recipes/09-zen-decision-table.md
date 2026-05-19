---
title: ZEN Decision Table Workflow
description: Ask Codex to create a Pro-gated ZEN decision table workflow.
---

# ZEN Decision Table Workflow

Prompt:

```text
Use nxusKit for a ZEN decision table workflow.
```

Starter fixture: `examples/fixtures/starters/cli-bash-workspace/`

Expected behavior:

- Show the ZEN Pro disclosure block before generating ZEN-dependent code.
- Probe `nxuskit-cli` and the relevant subcommand help before use.
- Verify license status before running ZEN.
- Create JSON fixtures for the decision model, input, and expected output.
- Use `jq` or another structured JSON tool instead of ad hoc string parsing.

Verification:

```bash
jq empty data/zen/decision-model.json data/zen/input.json data/zen/expected-output.json
bash -n scripts/zen-decision.sh
bash scripts/zen-decision.sh
```

Good result:

- The script exits non-zero if Pro status or expected output is missing.
- The result matches the expected decision output.
