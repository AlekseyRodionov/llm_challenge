# Grounded Chat Agent

RAG-агент с памятью задачи, диалоговой историей и трассировкой.

---

## Описание

Проект реализует **chat-агента с памятью**:
- RAG на каждый вопрос
- Память задачи (goal, constraints, known_facts)
- История диалога (последние 5 сообщений)
- Sources и Quotes в каждом ответе
- Полная трассировка через логи

---

## Структура проекта

```
grounded-chat/
├── app/
│   ├── __init__.py
│   ├── agent.py         # Pipeline + task_state + history + logging
│   ├── retriever.py     # FAISS поиск + динамический top_k
│   ├── generator.py     # Контекст с task_state + history
│   ├── query_rewriter.py  # Smart rewrite с контекстом
│   ├── cli.py          # Чат-режим + демо режим
│   ├── logger.py       # JSON Lines логирование
│   └── llm_client.py
├── docs/               # Документы (Fire + MkDocs)
├── index/              # FAISS индексы
├── logs/               # Логи (ignored)
├── tests/
│   └── test_scenarios.py  # 2 сценария
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## Константы

| Параметр | Значение | Описание |
|----------|----------|----------|
| `INITIAL_TOP_K` | 10 | Количество кандидатов из FAISS |
| `FINAL_TOP_K` | 3 | Количество чанков для LLM |
| `MAX_CONTEXT` | 2000 | Максимальная длина контекста |
| `HISTORY_LIMIT` | 5 | Количество сообщений в истории |
| `MAX_DISTANCE` | 300.0 | Порог фильтрации |

---

## Pipeline

```
User Input
    ↓
Update Task State (rule-based)
    ↓
Query Rewrite (optional)
    ↓
Retrieval (FAISS, k=10)
    ↓
Filter (distance < 300)
    ↓
Context Builder:
  - TASK: goal, constraints, known_facts
  - DIALOG HISTORY: последние 5 сообщений
  - CONTEXT: chunks
    ↓
LLM
    ↓
Parse (Answer/Sources/Quotes)
    ↓
Output + Logs (JSON Lines)
```

---

## Smart Rewrite

Для коротких вопросов (< 5 слов) rewrite использует контекст задачи:

```
Вопрос: "Как настроить?"
Goal: "Хочу задеплоить MkDocs"
Constraints: ["На GitHub Pages"]

→ "How to configure MkDocs for deployment on GitHub Pages?"
```

---

## Динамический Retrieval

Количество чанков зависит от качества retrieval:

| Distance | Quality | top_k |
|----------|---------|-------|
| < 220 | high | 3 |
| 220-260 | medium | 3 |
| >= 260 | low | 5 |

---

## Task State (rule-based)

| Правило | Пример | Результат |
|---------|--------|-----------|
| `"хочу" in q` | "Хочу CLI" | goal = q |
| `"на " in q` | "на Python" | constraints.append(q) |
| `len(q.split()) < 6` | "Как?" | known_facts.append(q) |

---

## Команды CLI

| Команда | Описание |
|---------|---------|
| `help` | Показать справку |
| `reset` | Очистить историю и состояние |
| `state` | Показать task state |
| `logs` | Включить/выключить debug |
| `history` | Показать историю |
| `exit` | Выйти |

---

## Формат лога (JSON Lines)

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "question": "Как задеплоить MkDocs?",
  "rewritten_query": "Deploy MkDocs to GitHub Pages",
  "rewrite_context_used": true,
  "task_state": {
    "goal": "Хочу задеплоить MkDocs",
    "constraints": ["На GitHub Pages"],
    "known_facts": ["Проект уже есть"]
  },
  "retrieval": {
    "top_k": 10,
    "distances": [150.2, 180.5],
    "chunks_found": 10
  },
  "retrieval_quality": "high",
  "filter": {
    "before": 10,
    "after": 3,
    "fallback_used": false
  },
  "final_top_k_used": 3,
  "best_distance": 150.2,
  "context": {
    "history_used": 5,
    "context_chars": 1800
  },
  "generation": {
    "raw_response": "...",
    "parsed": true
  },
  "result": {
    "fallback": false,
    "has_sources": true,
    "has_quotes": true
  }
}
```

---

## Тестовые сценарии

### Сценарий 1: MkDocs

```
1. Хочу задеплоить MkDocs
2. На GitHub Pages
3. Проект уже есть
4. Как настроить?
5. Как обновлять?
6. Где хранится конфиг?
7. Как добавить поиск?
8. Как изменить тему?
9. Как собрать сайт?
10. Как проверить локально?
```

### Сценарий 2: Fire

```
1. Хочу CLI
2. На Python
3. Без argparse
4. Как проще?
5. Как передавать аргументы?
6. Как вызвать функцию?
7. Как обработать типы?
8. Можно ли использовать классы?
9. Как запускать из консоли?
10. Как протестировать?
```

---

## Установка

```bash
cd week_5/grounded-chat
source venv/bin/activate
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
# Терминал 1: Ollama
ollama serve

# Терминал 2: Чат
python main.py

# Или запуск тестов
python tests/test_scenarios.py
```

---

## Быстрый старт

```bash
cd week_5/grounded-chat
source venv/bin/activate

# Чат
python main.py

# Демо режим
python main.py --demo mkdocs   # MkDocs сценарий
python main.py --demo fire     # Fire сценарий

# Тесты
python tests/test_scenarios.py
```

---

## Демо режим

Демо режим автоматически запускает сценарий с вопросами и показывает память задачи:

```bash
python main.py --demo mkdocs
python main.py --demo fire
```

Каждый демо включает:
- Ответы с источниками и цитатами
- Показ состояния (`state`) после вопросов
- Итоговую статистику

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Ollama (запущен локально)
- Модель `nomic-embed-text` для Ollama
