---
title: CLI Bash Prototypes And Setup Checks
description: Ask Codex to use nxuskit-cli for JSON-first prototypes and setup checks.
---

# CLI Bash Prototypes And Setup Checks

Prompt:

```text
Use nxuskit-cli to prototype this workflow as a Bash/JSON pipeline before adding app code.
```

Follow-up setup prompt:

```text
Use nxuskit-cli provider and license status checks to verify my setup before we implement SDK code.
```

Starter fixture: `examples/fixtures/starters/cli-bash-workspace/`

Expected behavior:

- Probe `nxuskit-cli --help` and `nxuskit-cli --version` before recommending subcommands.
- Probe subcommand help before use.
- Prefer JSON input and output.
- Use `jq` or structured parsing.
- Avoid arbitrary `bash -c` wrappers.
- Avoid printing credentials or asking for secrets.

Verification:

```bash
nxuskit-cli --help
nxuskit-cli --version
nxuskit-cli provider status --json
nxuskit-cli license status --json
bash scripts/json-call-prototype.sh
```

Good result:

- Provider status and license status are visible before SDK code is changed.
- The CLI prototype can be inspected and rerun.
