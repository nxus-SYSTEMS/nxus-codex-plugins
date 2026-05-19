---
title: OpenAI Plus Ollama In Go
description: Ask Codex to add cloud and local provider routing to a Go service.
---

# OpenAI Plus Ollama In Go

Prompt:

```text
Use nxusKit to make this Go service support OpenAI and Ollama.
```

Starter fixture: `examples/fixtures/starters/go-service/`

Expected behavior:

- Inspect `go.mod` and `main.go`.
- Consult the `multi-provider` example.
- Preserve existing command-line behavior.
- Add provider selection for OpenAI and Ollama.
- Read `OPENAI_API_KEY` only from the environment.
- Use local-provider settings such as `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.

Verification:

```bash
go test ./...
go run . -provider ollama -prompt "Reply in one short sentence."
```

Good result:

- The Go package tests pass.
- Ollama works without cloud credentials when it is running locally.
