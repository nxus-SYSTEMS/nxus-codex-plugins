import os


def describe_provider() -> str:
    provider = os.environ.get("LOCAL_PROVIDER", "ollama")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("LOCAL_MODEL", "llama3.2")
    return f"{provider}:{model}@{base_url}"


def main() -> None:
    print(describe_provider())


if __name__ == "__main__":
    main()
