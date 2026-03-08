# LLM Projects

Коллекция Python-проектов для работы с LLM через OpenAI API.

---

## Проекты

### Week 1

| Проект | Описание |
|--------|----------|
| [llm-benchmark](week_1/llm-benchmark/) | Сравнение LLM моделей по времени, токенам и стоимости |
| [llm-temp-test](week_1/llm-temp-test/) | Анализ влияния temperature на качество ответов |
| [llmsolver](week_1/llmsolver/) | Решение логических задач с помощью LLM |

### Week 2

| Проект | Описание |
|--------|----------|
| [llm-cli-app](week_2/llm-cli-app/) | Базовый CLI-инструмент для запросов к LLM |
| [simp-agent](week_2/simp-agent/) | Интерактивный агент с поддержкой контекста |
| [agent-memory](week_2/agent-memory/) | Агент с сохранением контекста в SQLite |
| [agent-token-count](week_2/agent-token-count/) | Агент с детальным подсчетом токенов |
| [agent-context-compr](week_2/agent-context-compr/) | Агент со сжатием контекста (summary) |
| [agent-managed-context](week_2/agent-managed-context/) | Агент с 3 стратегиями управления контекстом |

### Week 3

| Проект | Описание |
|--------|----------|
| [agent_managed_memory](week_3/agent_managed_memory/) | Агент с 3 слоями памяти и AI-маршрутизацией |
| [agent_with_profiles](week_3/agent_with_profiles/) | Агент с профилями и адаптацией ответов |
| [fsm_agent](week_3/fsm_agent/) | Агент с FSM — управление задачами через конечный автомат |
| [agent_with_invariants](week_3/agent_with_invariants/) | Агент с FSM, профилями пользователей и системными инвариантами |

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

Большинство проектов имеют единую структуру:

```
<project-name>/
├── app/
│   ├── __init__.py
│   ├── main.py         # Точка входа
│   ├── llm_client.py   # Работа с API
│   └── ...
├── memory/              # SQLite база данных (для некоторых проектов)
├── .env
├── requirements.txt
└── Readme.md
```

---

## Стоимость токенов

Стоимость зависит от используемой модели. Проверяйте актуальные цены на сайте провайдера API.
