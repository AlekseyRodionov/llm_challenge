"""
Модуль LLM-маршрутизации сообщений по типам памяти.
"""
import json
import re
from app.llm_client import ask_llm

ROUTER_MODEL = "openai/gpt-4o-mini"


def route_message(user_message: str) -> list:
    """
    Маршрутизирует сообщение пользователя по типам памяти.
    
    Args:
        user_message: Сообщение от пользователя
        
    Returns:
        Список словарей [{"text": "...", "memory_type": "long_term|working"}, ...]
    """
    system_prompt = """Ты - маршрутизатор сообщений по типам памяти агента.

Для каждого сообщения определи, какую информацию из него нужно сохранить:

1. **long_term** - факты о пользователе, его предпочтения, профиль, устойчивые данные
2. **working** - текущая задача, промежуточные цели, формулировки задачи

Правила:
- Одно сообщение может содержать данные для нескольких типов памяти
- Возвращай JSON массив объектов
- Если сообщение не содержит информации для сохранения, верни пустой массив []

Формат ответа:
```json
[
  {"text": "текст для сохранения", "memory_type": "long_term"},
  {"text": "другой текст", "memory_type": "working"}
]
```

Проанализируй сообщение и верни только JSON массив:"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    result = ask_llm(
        prompt="",
        model=ROUTER_MODEL,
        temperature=0.3,
        messages=messages
    )

    return parse_router_response(result["text"])


def parse_router_response(response: str) -> list:
    """
    Парсит ответ маршрутизатора в список словарей.
    
    Args:
        response: Текст ответа от LLM
        
    Returns:
        Список словарей с памятью
    """
    try:
        # Пытаемся найти JSON в ответе
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            data = json.loads(json_match.group())
            return data
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return []
