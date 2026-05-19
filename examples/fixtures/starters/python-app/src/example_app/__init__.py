import json


def classify(text: str) -> dict[str, object]:
    """Offline placeholder that Codex can replace with nxusKit structured output."""
    return {
        "category": "example",
        "severity": "info",
        "actionable": False,
        "summary": text.strip() or "no input",
    }


def main() -> None:
    print(json.dumps(classify("starter input"), sort_keys=True))
