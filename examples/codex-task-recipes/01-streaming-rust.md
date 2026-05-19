---
title: Streaming Chat In Rust
description: Ask Codex to add nxusKit streaming chat to a Rust CLI.
---

# Streaming Chat In Rust

Prompt:

```text
Use nxusKit to add streaming chat to this Rust CLI.
```

Starter fixture: `examples/fixtures/starters/rust-cli/`

Expected behavior:

- Inspect `Cargo.toml` and `src/main.rs` before editing.
- Consult the `streaming` row in the nxusKit example index.
- Prefer Community Edition paths.
- Add a small CLI that supports a no-secret smoke path such as loopback or local Ollama.
- Read cloud-provider credentials only from environment variables.

Verification:

```bash
cargo check
cargo run -- "Say hello from nxusKit streaming."
```

Good result:

- The project builds.
- The command prints streamed content or a clear local-provider prerequisite.
- No credential is requested in chat.
