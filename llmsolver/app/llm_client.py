import os
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL_PRICES = {
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    }
}


def count_tokens(text: str, model: str) -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    prices = MODEL_PRICES.get(model)
    if not prices:
        return 0.0

    return (
        (input_tokens / 1_000_000) * prices["input"] +
        (output_tokens / 1_000_000) * prices["output"]
    )


def ask_llm(prompt: str, temperature: float = 0.1, max_tokens: int = 300):

    system_prompt = "You are a precise logical reasoning assistant."

    input_tokens = count_tokens(prompt + system_prompt, MODEL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    text = response.choices[0].message.content
    output_tokens = count_tokens(text, MODEL)

    return {
        "text": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": calculate_cost(input_tokens, output_tokens, MODEL),
        "model": MODEL
    }
