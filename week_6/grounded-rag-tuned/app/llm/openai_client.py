"""
Модуль для взаимодействия с LLM через OpenAI API.
Отвечает за отправку запросов, подсчет токенов и оценку стоимости.
"""
import os
import time

import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

from app.config import get_llm_config

# Загрузка переменных окружения из .env файла
load_dotenv()

# Конфигурация API
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

# Инициализация клиента OpenAI
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)

# Цены (за 1M токенов, в рублях)
MODEL_PRICES = {
    "default": {"input": 14.0, "output": 59.0},
}


def count_tokens(text: str, model: str) -> int:
    """
    Подсчитывает количество токенов в тексте.
    
    Args:
        text: Текст для подсчета токенов
        model: Название модели (влияет на кодировку)
    
    Returns:
        Количество токенов
    """
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def count_messages_tokens(messages: list, model: str) -> int:
    """
    Подсчитывает общее количество токенов в списке сообщений.
    
    Args:
        messages: Список сообщений [{role, content}, ...]
        model: Название модели
    
    Returns:
        Общее количество токенов
    """
    total = 0
    for msg in messages:
        total += 4 + count_tokens(msg.get("content", ""), model)
    return total


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Оценивает стоимость запроса на основе количества токенов.
    """
    price = MODEL_PRICES.get("default", MODEL_PRICES.get(model, {"input": 14.0, "output": 59.0}))
    cost = (
        (input_tokens / 1_000_000) * price["input"] +
        (output_tokens / 1_000_000) * price["output"]
    )
    return round(cost, 6)


def ask_llm(prompt: str,
            model: str = None,
            max_tokens: int = None,
            stop=None,
            messages: list = None) -> dict:
    """
    Отправляет запрос к LLM и возвращает ответ с метриками.
    """
    model = model or DEFAULT_MODEL

    config = get_llm_config()
    temperature = config["temperature"]
    max_tokens = max_tokens or config["num_predict"]

    if messages is None:
        full_messages = [
            {"role": "system", "content": "Ты полезный AI помощник."},
            {"role": "user", "content": prompt}
        ]
    else:
        full_messages = messages + [{"role": "user", "content": prompt}]

    input_tokens = count_messages_tokens(full_messages, model)

    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop
    )
    latency = time.time() - start

    text = response.choices[0].message.content.strip()
    output_tokens = count_tokens(text, model)
    cost = estimate_cost(model, input_tokens, output_tokens)

    from app.llm_logger import log_llm
    log_llm(
        mode="cloud",
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        latency=latency,
        prompt_len=len(prompt),
        success=True
    )

    return {
        "text": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
        "model": model,
        "latency": latency,
        "success": True
    }
