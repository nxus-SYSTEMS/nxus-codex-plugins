---
title: Continue After License Activation
description: Ask Codex to continue Pro work after activation without skipping verification.
---

# Continue After License Activation

Prompt:

```text
I have activated my license now. Continue with the solver-backed what-if planner.
```

Starter fixture: the same project used for the original Pro request.

Expected behavior:

- Do not take the user's statement alone as proof of active Pro status.
- Run or recommend `nxuskit-cli license status --json` before continuing.
- Continue only when status is valid and the needed feature is present.
- If status is not valid, stop at the boundary and provide the recovery command.

Verification:

```bash
nxuskit-cli license status --json
```

Good result:

- Pro work resumes only after status verification.
- The user gets a clear next step if activation did not take effect.
