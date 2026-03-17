# RAG Chat Agent

Гибридный RAG-агент с CLI интерфейсом. Объединяет возможности RAG (FAISS + Ollama) с LLM (OpenAI API).

---

## Описание

Проект объединяет:
- **RAG** — поиск релевантных документов через FAISS + Ollama embeddings
- **Agent** — интерактивный чат с LLM (OpenAI API)

### Режимы работы

1. **Без RAG** — прямой запрос к LLM
2. **С RAG** — поиск релевантных чанков + LLM с контекстом

---

## Структура проекта

```
rag_chat_agent/
├── docs/                    # Документы для индексации
│   ├── fire_dataset.txt
│   └── mkdocs_dataset.txt
├── index/                   # FAISS индексы
│   ├── faiss_fixed.index
│   ├── faiss_structure.index
│   ├── metadata_fixed.json
│   └── metadata_structure.json
├── app/
│   ├── agent.py            # Agent с поддержкой RAG
│   ├── llm_client.py       # OpenAI API клиент
│   ├── retriever.py       # FAISS поиск (Ollama embeddings)
│   ├── generator.py       # Генерация ответов
│   ├── evaluator.py       # Сравнение RAG vs Non-RAG
│   └── cli.py            # CLI интерфейс
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## Установка

```bash
cd rag_chat_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Настройка

Создайте файл `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Запуск

```bash
# Терминал 1: Запустить Ollama (для embeddings)
ollama serve

# Терминал 2: Запустить агента
python main.py
```

---

## Команды

| Команда | Описание |
|---------|----------|
| `rag_on` | Включить RAG режим |
| `rag_off` | Выключить RAG режим |
| `eval` | Запустить оценку (10 вопросов) |
| `help` | Показать справку |
| `stats` | Показать статистику |
| `reset` | Очистить историю |
| `history` | Показать историю |
| `exit` | Выйти |

---

## Пример использования

```
=== RAG Chat Agent ===
Гибридный AI ассистент

Индекс: Fire + MkDocs (fixed)
Embeddings: Ollama (nomic-embed)
LLM: OpenAI (GPT-4o-mini)

Команды: rag_on, rag_off, eval, help, stats, reset, history, exit

Вы (RAG OFF): Что такое Fire?

Агент: Fire — это библиотека для создания CLI...

Вы (RAG ON): Что такое Fire?

Агент: Fire — это библиотека Google для автоматического создания интерфейсов командной строки...

Найдено чанков: 3
```

---

## Как это работает

```
Пользователь
    ↓
Ollama (embed query) → FAISS (search)
    ↓
Найденные чанки + вопрос → OpenAI (generate)
    ↓
Ответ пользователю
```

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Ollama (запущен локально)
- Модель nomic-embed-text для Ollama
