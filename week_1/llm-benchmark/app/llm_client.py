import os
import time
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

BENCHMARK_MODELS = {
    "weak": os.getenv("BENCHMARK_WEAK", "qwen/qwen3.5-plus-02-15"),
    "medium": os.getenv("BENCHMARK_MEDIUM", "qwen/qwen3-coder-next"),
    "strong": os.getenv("BENCHMARK_STRONG", "qwen/qwen3.5-397b-a17b")
}

MODEL_PRICES = {
    "qwen/qwen3.5-plus-02-15": {"input": 39.0, "output": 239.0, "context": 1_000_000},
    "qwen/qwen3-coder-next": {"input": 11.0, "output": 74.0, "context": 262_000},
    "qwen/qwen3.5-397b-a17b": {"input": 14.0, "output": 99.0, "context": 262_000},
    "openai/gpt-4o": {"input": 5.0, "output": 15.0},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-4.1-mini": {"input": 0.20, "output": 0.80},
    "openai/gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}


def count_tokens(text: str, model: str):
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_cost(model: str, input_tokens: int, output_tokens: int):
    if model not in MODEL_PRICES:
        return 0.0

    price = MODEL_PRICES[model]
    cost = (
        (input_tokens / 1_000_000) * price["input"] +
        (output_tokens / 1_000_000) * price["output"]
    )
    return round(cost, 6)


def ask_llm(prompt: str,
            model: str = None,
            temperature: float = 0.7,
            max_tokens: int = None,
            stop=None,
            timeout: int = 300):

    model = model or DEFAULT_MODEL

    input_tokens = count_tokens(prompt, model)

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты полезный AI помощник."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            timeout=timeout
        )
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "text": f"[ОШИБКА: {str(e)}]",
            "input_tokens": input_tokens,
            "output_tokens": 0,
            "total_tokens": input_tokens,
            "cost": 0,
            "model": model,
            "elapsed_time": round(elapsed_time, 2),
            "error": True
        }

    elapsed_time = time.time() - start_time

    text = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
    output_tokens = count_tokens(text, model)
    cost = estimate_cost(model, input_tokens, output_tokens)

    return {
        "text": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
        "model": model,
        "elapsed_time": round(elapsed_time, 2)
    }


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)