"""LLM Tasks module - генерация с использованием LLM."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm


def generate_with_context(task: str, context: str) -> dict:
    """Сгенерировать ответ с использованием контекста.
    
    Args:
        task: Задача пользователя
        context: Контекст (код проекта)
    
    Returns:
        dict с ответом и метриками
    """
    prompt = f"""Ты — AI ассистент, работающий с кодовой базой.

ЗАДАЧА:
{task}

КОНТЕКСТ ПРОЕКТА:
{context}

Сделай:
- анализ
- рекомендации
- если нужно — сгенерируй новый код

Ответ должен быть структурированным."""

    return ask_llm(prompt=prompt)


def generate_readme(files_content: str) -> str:
    """Сгенерировать README для проекта.
    
    Args:
        files_content: Содержимое файлов проекта
    
    Returns:
        Текст README
    """
    prompt = f"""Сгенерируй README.md для проекта на основе предоставленного кода.

Требования к README:
- Описание проекта
- Структура файлов
- Основные функции
- Как использовать

Код проекта:
{files_content[:4000]}

Сгенерируй качественный README:"""

    result = ask_llm(prompt=prompt, max_tokens=1500)
    return result["text"]


def suggest_improvements(code: str) -> dict:
    """Предложить улучшения кода.
    
    Args:
        code: Код для анализа
    
    Returns:
        dict с предложениями и diff
    """
    prompt = f"""Проанализируй код и предложи улучшения.

Для каждой проблемы:
1. Опиши проблему
2. Предложи решение
3. Сгенерируй исправленный код

Код:
{code[:3000]}

Формат ответа:
## Проблемы и решения

### Проблема 1: [описание]
Исправление:
```python
[исправленный код]
```

### Проблема 2: ...
"""

    return ask_llm(prompt=prompt, max_tokens=2000)


def analyze_api_usage(api_name: str, results: dict) -> str:
    """Проанализировать использование API с помощью LLM.
    
    Args:
        api_name: Имя искомого API
        results: Словарь {file: [(line_num, code), ...]}
    
    Returns:
        Текст анализа от LLM
    """
    MAX_LINES = 50
    
    formatted_matches = []
    total_matches = 0
    
    for file_path, matches in results.items():
        file_name = os.path.basename(file_path)
        for line_num, code in matches[:MAX_LINES]:
            formatted_matches.append(f"{file_name}:{line_num}: {code}")
            total_matches += 1
    
    raw_text = '\n'.join(formatted_matches)
    
    prompt = f"""Проанализируй использование API "{api_name}" в коде.

НАЙДЕННЫЕ ОБРАЩЕНИЯ:
{raw_text}

Дай ответ в структурированном формате с использованием emoji:

📍 ИСПОЛЬЗОВАНИЕ:
🔹 [кратко где используется]

⚠️ ПРОБЛЕМЫ:
🔴 [критичная проблема]
🟡 [средняя проблема]

💡 РЕКОМЕНДАЦИИ:
🔹 [конкретный совет]

ВАЖНО:
- Не придумывай факты
- Используй только предоставленный код
- Если данных недостаточно — так и скажи
- Отвечай кратко (до 5 строк)
- Используй 🔴 для критичных, 🟡 для средних, 🟢 для рекомендаций"""

    result = ask_llm(prompt=prompt, max_tokens=500)
    return result["text"]


def analyze_code(task: str, context: str) -> dict:
    """Общая функция анализа кода через LLM.
    
    Args:
        task: Задача
        context: Контекст (код)
    
    Returns:
        dict с ответом
    """
    prompt = f"""Ты — эксперт по Python коду.

Проанализируй код и дай рекомендации.

ЗАДАЧА: {task}

КОД:
{context}

Дай структурированный ответ:"""

    return ask_llm(prompt=prompt, max_tokens=1500)
