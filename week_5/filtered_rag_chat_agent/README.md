# Filtered RAG Chat Agent

Гибридный RAG-агент с улучшенным поиском: фильтрация по distance и перезапись запросов (query rewrite).

---

## Описание

Проект объединяет:
- **RAG** — поиск релевантных документов через FAISS + Ollama embeddings
- **Filter** — фильтрация чанков по порогу расстояния (MAX_DISTANCE)
- **Rewrite** — улучшение запросов для лучшего поиска
- **Agent** — интерактивный чат с LLM (OpenAI API)

### 3 режима работы

| Режим | RAG | Filter | Rewrite | Описание |
|-------|-----|--------|---------|---------|
| RAG | ✅ | ❌ | ❌ | Базовый RAG |
| RAG+Filter | ✅ | ✅ | ❌ | RAG с фильтрацией по distance |
| RAG+Filter+Rewrite | ✅ | ✅ | ✅ | Полный pipeline |

---

## Структура проекта

```
filtered_rag_chat_agent/
├── docs/                    # Документы для индексации
│   ├── fire_dataset.txt
│   └── mkdocs_dataset.txt
├── index/                   # FAISS индексы
│   ├── faiss_fixed.index
│   └── metadata_fixed.json
├── app/
│   ├── agent.py            # Agent с поддержкой RAG/Filter/Rewrite
│   ├── llm_client.py      # OpenAI API клиент
│   ├── retriever.py        # FAISS поиск + фильтрация
│   ├── query_rewriter.py   # Перезапись запросов
│   ├── generator.py         # Генерация ответов (русский)
│   ├── evaluator.py         # Сравнение 3 режимов
│   └── cli.py              # CLI интерфейс
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

## Константы

| Параметр | Значение | Описание |
|----------|----------|----------|
| `INITIAL_TOP_K` | 5 | Количество кандидатов из FAISS |
| `FINAL_TOP_K` | 2 | Количество чанков для LLM |
| `MAX_DISTANCE` | 300.0 | Порог фильтрации (меньше = лучше) |
| `MAX_CONTEXT` | 2000 | Максимальная длина контекста |

---

## Установка

```bash
cd filtered_rag_chat_agent
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
| `filter_on` | Включить фильтрацию по distance (MAX_DISTANCE=300.0) |
| `filter_off` | Выключить фильтрацию |
| `rewrite_on` | Включить перезапись запросов |
| `rewrite_off` | Выключить перезапись запросов |
| `eval` | Запустить сравнение 3 режимов |
| `help` | Показать справку |
| `stats` | Показать статистику |
| `reset` | Очистить историю |
| `exit` | Выйти |

---

## Как это работает

### Pipeline

```
Пользователь
    ↓
[Rewrite] (если включен)
    ↓
Ollama (embed query) → FAISS (search)
    ↓
[Filter] (если включен) — отсеивает чанки с distance > MAX_DISTANCE
    ↓
Top-K чанки + вопрос → OpenAI (generate)
    ↓
Ответ пользователю
```

### Метрика: Полнота ключевых слов

```
Полнота = (найдено_ключевых_слов / ожидаемых_ключевых_слов) × 100%
```

---

## Пример использования

### CLI

```
=== RAG Chat Agent ===
Гибридный AI ассистент

Индекс: Fire + MkDocs (fixed)
Embeddings: Ollama (nomic-embed)
LLM: OpenAI (GPT-4o-mini)

Команды: rag_on/off, filter_on/off, rewrite_on/off, eval, help, stats, reset, history, exit

Вы ([RAG ON] [FILTER OFF] [REWRITE OFF]): filter_on
Filter enabled (MAX_DISTANCE=300.0)

Вы ([RAG ON] [FILTER ON] [REWRITE OFF]): rewrite_on
Query rewrite enabled

Вы ([RAG ON] [FILTER ON] [REWRITE ON]): Как настроить поиск в MkDocs?

Агент: Для настройки поиска в MkDocs вам нужно изменить конфигурационный файл...
```

### Evaluation

```
================================================================================
ОЦЕНКА: Сравнение 3 режимов RAG
================================================================================

Какие способы вызова fire.Fire() существуют? ..............
Полнота ключевых слов [RAG] 100% | [RAG+Filter] 100% | [RAG+Rewrite] 100%

  Лучший ответ (RAG, 100%):
  Существует несколько способов вызова функции `fire.Fire()` в библиотеке Python Fire...

Как в Fire получить справку? ..............
Полнота ключевых слов [RAG] 33% | [RAG+Filter] 33% | [RAG+Rewrite] 100%

  Лучший ответ (RAG+Rewrite, 100%):
  В Fire вы можете получить справку, используя флаг --help или -h...

================================================================================
ИТОГОВАЯ СТАТИСТИКА
================================================================================
  RAG                  17/30 (57%)
  RAG+Filter           15/30 (50%)
  RAG+Rewrite          20/30 (67%)
================================================================================
```

---

## Технические детали

### Query Rewrite

Добавляет английские технические термины для лучшего retrieval:

```
Русский: "Как задеплоить MkDocs?"
Rewrite:  "How to deploy MkDocs (Python static site generator for documentation)?"
```

### Distance Filtering

FAISS возвращает distance для каждого чанка. Чем меньше — тем релевантнее:

```
[retrieval] found: 5, distances: ['200.5', '250.3', '280.1', '310.2', '350.8']
[filter] threshold=300, before=5, after=3, kept=['200.5', '250.3', '280.1']
```

### Вопросы для Evaluation

10 вопросов с ожидаемыми ключевыми словами для сравнения режимов.

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Ollama (запущен локально)
- Модель `nomic-embed-text` для Ollama

---

## Быстрый старт

```bash
# 1. Клонировать проект
cd week_5/filtered_rag_chat_agent

# 2. Активировать venv
source venv/bin/activate

# 3. Убедиться что Ollama запущен
ollama serve

# 4. Запустить eval
python -c "from app.agent import Agent; from app.evaluator import run_evaluation; agent = Agent(rag_enabled=True); run_evaluation(agent)"
```
