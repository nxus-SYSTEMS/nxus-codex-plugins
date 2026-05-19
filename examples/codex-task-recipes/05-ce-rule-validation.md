---
title: Community Edition Rule Validation
description: Ask Codex to add CE-safe CLIPS validation after model output.
---

# Community Edition Rule Validation

Prompt:

```text
Use nxusKit Community Edition to add rule-based validation to this workflow.
```

Starter fixture: `examples/fixtures/starters/python-app/`

Expected behavior:

- Identify the current data or model-output shape.
- Consult `clips-basics` or `clips-llm-hybrid`.
- Explain that basic CLIPS rule evaluation is Community Edition.
- Add deterministic validation after extraction or classification.
- Avoid solver, ZEN, runtime plugin loading, and other Pro-gated features unless the user asks for them.

Verification:

```bash
python -m py_compile src/example_app/__init__.py
python -m example_app --provider offline --validate-rules
```

Good result:

- The rule validation emits pass/review/fail status.
- The model-output schema and rule facts are easy to inspect.
