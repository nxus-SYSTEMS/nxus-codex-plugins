---
title: Vision With Capability Detection
description: Ask Codex to add multimodal support and verify capabilities.
---

# Vision With Capability Detection

Prompt:

```text
Add vision support with nxusKit and verify model capability detection.
```

Starter fixture: `examples/fixtures/starters/go-service/`

Expected behavior:

- Consult `vision` and `capability-detection`.
- Treat vision as Community Edition when the provider/model supports it.
- Add image input through URL or base64.
- Check model-level capabilities when available, then provider-level capabilities.
- Include a tiny local image fixture or documented image input so smoke testing does not depend on a random external URL.

Verification:

```bash
go test ./...
go run . -provider ollama -model llama3.2-vision:latest -vision
```

Good result:

- The app refuses text-only models clearly.
- A vision-capable model receives an image and returns content.
