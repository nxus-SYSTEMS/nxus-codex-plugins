import os

from openai import OpenAI


def summarize(text: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": "Summarize in one short sentence."},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    print(summarize("nxusKit migration starter"))
