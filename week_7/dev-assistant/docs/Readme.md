# LLM Projects

Коллекция Python-проектов для работы с LLM через OpenAI API и Ollama.

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

### Week 4

| Проект | Описание |
|--------|----------|
| [scheduling_mcp_agent](week_4/scheduling_mcp_agent/) | Агент с FSM, профилями и MCP (FastMCP SDK) + Scheduler |
| [mcp_multi_server](week_4/mcp_multi_server/) | **MCP Multi-Server Agent** — интерактивный агент с LLM анализом запросов, multi-server MCP (demo_server + external_api_server) |

### Week 5

| Проект | Описание |
|--------|----------|
| [rag_project](week_5/rag_project/) | **RAG Document Indexing** — индексация документов с эмбеддингами (FAISS + Ollama), 2 стратегии chunking |
| [rag_chat_agent](week_5/rag_chat_agent/) | **RAG Chat Agent** — гибридный агент с RAG (FAISS + Ollama) и LLM (OpenAI), CLI интерфейс |
| [filtered_rag_chat_agent](week_5/filtered_rag_chat_agent/) | **Filtered RAG Agent** — RAG с фильтрацией по distance и query rewrite |
| [grounded-rag](week_5/grounded-rag/) | **Grounded RAG** — RAG с Sources, Quotes, отступлением (fallback) и оценкой качества |
| [grounded-chat](week_5/grounded-chat/) | **Grounded Chat** — RAG + память задачи + демо режим |

### Week 6

| Проект | Описание |
|--------|---------|
| [local-llm-cli](week_6/local-llm-cli/) | **Local LLM CLI** — минимальный CLI и веб-интерфейс для работы с Ollama |
| [grounded-rag-ollama](week_6/grounded-rag-ollama/) | **Grounded RAG (Ollama)** — RAG с переключением cloud/local, Sources, Quotes, evaluator |
| [vps-llm-service](week_6/vps-llm-service/) | **VPS LLM Service** — Flask API + Ollama на VPS с rate limiting, retry, fallback. Стабильный сервис на tinyllama. |

> Примечание: требуется Python 3.10+

---

## Общие требования

- Python 3.10+
- OpenAI-совместимый API (для большинства проектов)
- Виртуальное окружение (venv)
- Ollama (для проектов с Ollama: rag_project, rag_chat_agent, filtered_rag_chat_agent, grounded-rag, grounded-chat, local-llm-cli, grounded-rag-ollama, vps-llm-service)

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

Проект rag_project имеет другую структуру:

```
rag_project/
├── docs/                    # Исходные документы
│   ├── fire_dataset.txt
│   └── mkdocs_dataset.txt
├── src/                    # Исходный код
│   ├── loader.py
│   ├── chunking_fixed.py
│   ├── chunking_structure.py
│   ├── embedder.py
│   ├── index_store.py
│   └── main.py
├── index/                  # Созданные индексы (FAISS)
├── requirements.txt
└── README.md
```

Проект rag_chat_agent:

```
rag_chat_agent/
├── docs/                    # Документы для индексации
├── index/                   # FAISS индексы
├── app/
│   ├── agent.py            # Agent с поддержкой RAG
│   ├── llm_client.py       # OpenAI API
│   ├── retriever.py        # FAISS поиск
│   ├── generator.py        # Генерация ответов
│   ├── evaluator.py        # Сравнение RAG vs Non-RAG
│   └── cli.py              # CLI интерфейс
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## Стоимость токенов

Стоимость зависит от используемой модели. Проверяйте актуальные цены на сайте провайдера API.
