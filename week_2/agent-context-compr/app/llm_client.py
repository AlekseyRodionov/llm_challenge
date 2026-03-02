"""
Модуль для взаимодействия с LLM через OpenAI API.
Отвечает за отправку запросов, подсчет токенов и оценку стоимости.
"""
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

MODEL_PRICES = {
    "default": {"input": 14.0, "output": 59.0},
}

MAX_TOKENS = {
    "openai/gpt-4o-mini": 128000,
    "gpt-4o-mini": 128000,
}


def count_tokens(text: str, model: str) -> int:
    """
    Подсчитывает количество токенов в тексте.
    """
    try:
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
    except:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def count_message_tokens(role: str, content: str, model: str) -> int:
    """
    Подсчитывает токены для одного сообщения (включая служебные).
    """
    return 4 + count_tokens(content, model)


def count_messages_tokens(messages: list, model: str) -> int:
    """
    Подсчитывает общее количество токенов в списке сообщений.
    """
    total = 0
    for msg in messages:
        total += 4 + count_tokens(msg.get("content", ""), model)
    return total


def get_history_tokens(messages: list, model: str) -> int:
    """
    Подсчитывает токены всей истории диалога (без текущего запроса).
    """
    if not messages:
        return 0
    return count_messages_tokens(messages, model)


def get_request_tokens(prompt: str, model: str) -> int:
    """
    Подсчитывает токены текущего запроса пользователя.
    """
    return count_message_tokens("user", prompt, model)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Оценивает стоимость запроса на основе количества токенов.
    """
    price = MODEL_PRICES.get("default")
    
    cost = (
        (input_tokens / 1_000_000) * price["input"] +
        (output_tokens / 1_000_000) * price["output"]
    )
    return round(cost, 6)


def get_max_tokens(model: str) -> int:
    """Возвращает максимальное количество токенов для модели."""
    return MAX_TOKENS.get(model, MAX_TOKENS.get("default", 128000))


def check_token_limit(history_tokens: int, request_tokens: int, model: str) -> dict:
    """
    Проверяет не превышен ли лимит токенов.
    Применяется коэффициент для более точного соответствия с LLM API.
    """
    TOKEN_COEFFICIENT = 1.55
    
    max_tokens = get_max_tokens(model)
    total = int((history_tokens + request_tokens) * TOKEN_COEFFICIENT)
    
    return {
        "total": total,
        "max": max_tokens,
        "remaining": max_tokens - total,
        "overflow": total > max_tokens,
        "percent": round(total / max_tokens * 100, 1)
    }


def ask_llm(prompt: str,
            model: str = None,
            temperature: float = 0.7,
            max_tokens: int = None,
            stop=None,
            messages: list = None) -> dict:
    """
    Отправляет запрос к LLM и возвращает ответ с метриками.
    
    Returns:
        - text: текст ответа
        - request_tokens: токены текущего запроса
        - history_tokens: токены истории диалога
        - response_tokens: токены ответа модели
        - total_input_tokens: всего входных (history + request)
        - output_tokens: токены ответа
        - total_tokens: общее количество токенов
        - cost: примерная стоимость
        - model: название модели
        - limit_info: информация о лимите
    """
    model = model or DEFAULT_MODEL
    
    history_tokens = get_history_tokens(messages, model) if messages else 0
    request_tokens = get_request_tokens(prompt, model)
    input_tokens = history_tokens + request_tokens
    
    full_messages = messages + [{"role": "user", "content": prompt}] if messages else [
        {"role": "system", "content": "Ты полезный AI помощник."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stop=stop
    )
    
    text = response.choices[0].message.content.strip()
    response_tokens = count_tokens(text, model)
    cost = estimate_cost(model, input_tokens, response_tokens)
    limit_info = check_token_limit(history_tokens, request_tokens, model)
    
    return {
        "text": text,
        "request_tokens": request_tokens,
        "history_tokens": history_tokens,
        "response_tokens": response_tokens,
        "total_input_tokens": input_tokens,
        "output_tokens": response_tokens,
        "total_tokens": input_tokens + response_tokens,
        "cost": cost,
        "model": model,
        "limit_info": limit_info
    }
