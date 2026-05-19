# CLI/Bash Workspace Starter

Use with the CLI/Bash, ZEN, or hybrid pipeline recipes.

Example prompt:

```text
Use nxuskit-cli to prototype this workflow as a Bash/JSON pipeline before adding app code.
```

Expected first checks:

```bash
jq empty data/request.json
bash -n scripts/run.sh
bash scripts/run.sh
```
