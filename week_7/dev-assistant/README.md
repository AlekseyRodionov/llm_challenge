# Dev Assistant

RAG + MCP ассистент для документации проекта llm_challenge.

---

## Описание

Проект отвечает на вопросы о проекте llm_challenge используя:
- **RAG** — поиск по документации через FAISS
- **MCP** — получение информации о проекте (git, файлы)
- **LLM** — генерация ответов (OpenAI GPT-4o-mini)

---

## Структура

```
dev-assistant/
├── app/
│   ├── mcp/
│   │   ├── server.py       # MCP Server (JSON-RPC)
│   │   └── client.py       # MCP Client
│   ├── project_indexer.py  # Индексация документов
│   ├── cli.py             # CLI интерфейс
│   └── ...
├── docs/                  # Документация для индексации
└── main.py
```

---

## Установка

```bash
cd dev-assistant
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

Также нужно запустить Ollama для эмбеддингов:

```bash
ollama serve
```

---

## Запуск

```bash
python main.py
```

---

## Команды

| Команда | Описание |
|---------|----------|
| `/help <вопрос>` | Задать вопрос о проекте |
| `/help branch` | Показать ветку git |
| `/help files` | Показать список файлов |
| `exit` | Выйти |

---

## Возможности

- Ответы на вопросы о проекте через RAG
- Поиск по документации (FAISS + Ollama embeddings)
- Информация о git-ветке (MCP)
- Список файлов проекта (MCP)
- История коммитов в документации

---

## Как это работает

```
Пользователь
    ↓
/help <вопрос>
    ↓
MCP: git branch + files (JSON-RPC)
    ↓
RAG: FAISS search (документация)
    ↓
LLM: GPT-4o-mini → ответ
    ↓
Ответ пользователю
```

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Ollama (запущен локально)
- Модель nomic-embed-text для Ollama
