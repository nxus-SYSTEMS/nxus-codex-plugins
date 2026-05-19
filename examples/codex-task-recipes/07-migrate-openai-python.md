---
title: Migrate Direct OpenAI Usage
description: Ask Codex to migrate a direct OpenAI Python integration to nxusKit.
---

# Migrate Direct OpenAI Usage

Prompt:

```text
Migrate this OpenAI-only integration to nxusKit without changing app behavior.
```

Starter fixture: `examples/fixtures/starters/direct-openai-python/`

Expected behavior:

- Inspect imports, client construction, model selection, message shape, retry behavior, and public function signatures.
- Present a preserved-behavior contract before editing.
- Keep `OPENAI_API_KEY` and `OPENAI_MODEL` conventions unless the project already uses different names.
- Replace direct provider SDK calls with nxusKit provider calls.
- Avoid adding new abstractions that the project did not need.

Verification:

```bash
python -m py_compile app.py
python -c "import inspect, app; print(inspect.signature(app.summarize))"
```

Good result:

- The public API remains `summarize(text: str) -> str`.
- No direct OpenAI SDK import remains in the implementation.
