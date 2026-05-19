# Python App Starter

Use with the structured JSON or CE rule-validation recipes.

Example prompt:

```text
Use nxusKit to add structured JSON output to this Python app.
```

Expected first checks:

```bash
python -m py_compile src/example_app/__init__.py src/example_app/__main__.py
python -m example_app
```
