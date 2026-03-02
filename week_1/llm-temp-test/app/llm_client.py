import os
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Цены (за 1M токенов, в рублях)
MODEL_PRICES = {
    "default": {"input": 14.0, "output": 59.0},
}


def count_tokens(text: str, model: str):
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_cost(model: str, input_tokens: int, output_tokens: int):
    price = MODEL_PRICES.get("default", {"input": 14.0, "output": 59.0})
    cost = (
        (input_tokens / 1_000_000) * price["input"] +
        (output_tokens / 1_000_000) * price["output"]
    )
    return round(cost, 6)


def ask_llm(prompt: str,
            model: str = None,
            temperature: float = 0.7,
            max_tokens: int = None,
            stop=None):

    model = model or DEFAULT_MODEL

    input_tokens = count_tokens(prompt, model)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Ты полезный AI помощник."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop
    )

    text = response.choices[0].message.content.strip()
    output_tokens = count_tokens(text, model)
    cost = estimate_cost(model, input_tokens, output_tokens)

    return {
        "text": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
        "model": model
    }