---
title: Local Ollama Through nxusKit
description: Ask Codex to use a local provider without cloud credentials.
---

# Local Ollama Through nxusKit

Prompt:

```text
Use local Ollama through nxusKit for this app.
```

Starter fixture: `examples/fixtures/starters/local-provider-python/`

Expected behavior:

- Preserve existing local-provider environment variable names when present.
- Treat local-provider support as Community Edition.
- Use `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, or project-local equivalents.
- Do not ask for cloud credentials.
- Add a clear error if Ollama is not reachable.

Verification:

```bash
python -m py_compile app.py
python app.py
```

Good result:

- The app prints the provider configuration and returns content from local Ollama.
- Missing Ollama setup produces an actionable message.
