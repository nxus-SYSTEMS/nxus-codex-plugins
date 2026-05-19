---
title: Community Edition Options
description: Ask Codex what nxusKit work can proceed without Pro.
---

# Community Edition Options

Prompt:

```text
I do not have a Pro license. What can we still implement with Community Edition?
```

Starter fixture: any project.

Expected behavior:

- Treat "no Pro license" as a hard boundary.
- Enumerate CE-suitable workflows: chat, streaming, structured output, tool calling when supported, vision when supported, retry/fallback, routing, local providers, direct-provider migration to CE targets, basic CLIPS, CLIPS plus LLM validation, Bayesian inference within CE limits, and CLI/Bash prototypes for CE capabilities.
- Offer CE alternatives for solver, what-if, ZEN, and solver-containing hybrid workflows.
- Do not generate Pro-dependent code.

Verification:

No code change is required. Review the answer for tier correctness and absence of Pro implementation.

Good result:

- The response gives a useful CE path forward without upsell pressure or hidden Pro dependencies.
