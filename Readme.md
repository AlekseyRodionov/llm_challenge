# LLM Projects

Коллекция Python-проектов для работы с LLM через OpenAI API.

---

## Проекты

| Проект | Описание |
|--------|----------|
| [llm-cli-app](llm-cli-app/) | Базовый CLI-инструмент для запросов к LLM |
| [llm-benchmark](llm-benchmark/) | Сравнение LLM моделей по времени, токенам и стоимости |
| [llm-temp-test](llm-temp-test/) | Анализ влияния temperature на качество ответов |
| [llmsolver](llmsolver/) | Решение логических задач с помощью LLM |
| [simp-agent](simp-agent/) | Интерактивный агент с поддержкой контекста |
| [agent-memory](agent-memory/) | Агент с сохранением контекста в SQLite |
| [agent-token-count](agent-token-count/) | Агент с детальным подсчетом токенов |

---

## Общие требования

- Python 3.9+
- OpenAI-совместимый API
- Виртуальное окружение (venv)

## Установка

Для каждого проекта:

```bash
cd <project-name>
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` в папке проекта:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # или другой провайдер
OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Структура проектов

Каждый проект имеет единую структуру:

```
<project-name>/
├── app/
│   ├── __init__.py
│   ├── main.py         # Точка входа
│   ├── llm_client.py   # Работа с API
│   └── comparator.py   # Анализ/сравнение
├── .env
├── requirements.txt
└── Readme.md
```

---

## Стоимость токенов

По умолчанию используются цены:

- Входящие токены: 14 ₽ / 1M
- Исходящие токены: 59 ₽ / 1M
