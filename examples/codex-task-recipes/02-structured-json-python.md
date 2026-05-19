---
title: Structured JSON Output In Python
description: Ask Codex to add typed structured output to a Python app.
---

# Structured JSON Output In Python

Prompt:

```text
Use nxusKit to add structured JSON output to this Python app.
```

Starter fixture: `examples/fixtures/starters/python-app/`

Expected behavior:

- Inspect `pyproject.toml` and the package layout before editing.
- Consult the `structured-output` example.
- Add a typed schema plus validation.
- Keep provider configuration in environment variables or project config.
- Include an offline or fixture-driven parsing smoke if a model is unavailable.

Verification:

```bash
python -m py_compile src/example_app/__init__.py src/example_app/__main__.py
python -m example_app --provider offline
```

Good result:

- The output is valid JSON that matches the declared schema.
- Real provider use is optional and explicitly configured.
