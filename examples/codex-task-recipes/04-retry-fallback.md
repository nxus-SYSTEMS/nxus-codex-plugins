---
title: Retry And Fallback
description: Ask Codex to implement the smallest nxusKit retry/fallback pattern.
---

# Retry And Fallback

Prompt:

```text
Use nxusKit Examples to find the smallest retry/fallback example and implement that pattern here.
```

Starter fixture: any fixture with an existing provider call; `examples/fixtures/starters/go-service/` is a good target.

Expected behavior:

- Inspect the current provider call first.
- Consult the `retry-fallback` example.
- Implement the smallest fallback chain that fits the project.
- Preserve existing provider flags and environment variables.
- Add tests for first-provider success, fallback success, all-fail, and empty-chain cases when the project has test coverage.

Verification:

```bash
go test ./...
go run . -provider fallback -prompt "Confirm fallback."
```

Good result:

- Failed providers are reported clearly.
- The first successful provider response is returned.
