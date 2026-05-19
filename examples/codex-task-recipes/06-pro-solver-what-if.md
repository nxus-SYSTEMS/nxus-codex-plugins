---
title: Pro Solver What-If Planner
description: Ask Codex to add a Pro-gated solver-backed what-if workflow.
---

# Pro Solver What-If Planner

Prompt:

```text
Use nxusKit Pro to add a solver-backed what-if planner.
```

Starter fixture: `examples/fixtures/starters/go-service/`

Expected behavior:

- Show the Pro disclosure block before generating solver-dependent code.
- Offer a Community Edition alternative if constraint solving is not required.
- Probe `nxuskit-cli --version`.
- Run or recommend `nxuskit-cli license status --json` before continuing.
- Generate solver code only after the user has an eligible trial or license and Pro status is verified.

Verification:

```bash
nxuskit-cli license status --json
go test -tags nxuskit ./...
go run -tags nxuskit . -planner
```

Good result:

- Base and what-if scenarios are reported separately.
- Unsatisfiable scenarios are handled explicitly.
- No Pro code appears before disclosure.
