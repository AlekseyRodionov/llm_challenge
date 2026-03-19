# Grounded RAG Chat Agent

RAG-агент с проверкой ответов: источники, цитаты и анти-галлюцинация.

---

## Описание

Проект реализует **проверяемый RAG** — каждый ответ содержит:
- Ответ на вопрос
- Список источников (source + section + chunk_id)
- Цитаты (дословные фрагменты из найденных чанков)

### Если контекст слабый

Модель возвращает: **"Не знаю. Уточните вопрос."**

---

## 3 режима работы

| Режим | RAG | Filter | Rewrite | Описание |
|-------|-----|--------|---------|---------|
| RAG | ✅ | ❌ | ❌ | Базовый RAG |
| RAG+Filter | ✅ | ✅ | ❌ | RAG с фильтрацией по distance |
| RAG+Filter+Rewrite | ✅ | ✅ | ✅ | Полный pipeline |

---

## Структура проекта

```
grounded-rag/
├── docs/                    # Документы для индексации
├── index/                   # FAISS индексы
├── app/
│   ├── agent.py            # Agent с анти-галлюцинацией
│   ├── llm_client.py      # OpenAI API клиент
│   ├── retriever.py        # FAISS поиск + chunk_id
│   ├── query_rewriter.py  # Перезапись запросов
│   ├── generator.py        # Генерация с Sources/Quotes
│   ├── evaluator.py        # Оценка Sources/Quotes coverage
│   └── cli.py              # CLI интерфейс
├── main.py
├── .env
└── README.md
```

---

## Константы

| Параметр | Значение | Описание |
|----------|----------|----------|
| `INITIAL_TOP_K` | 10 | Количество кандидатов из FAISS |
| `FINAL_TOP_K` | 2 | Количество чанков для LLM |
| `MAX_DISTANCE` | 300.0 | Порог фильтрации (меньше = лучше) |
| `MAX_CONTEXT` | 2000 | Максимальная длина контекста |

---

## Формат ответа LLM

```
Answer:
<ответ на вопрос>

Sources:
- <source | section | chunk_id>

Quotes:
1. "<дословная цитата из контекста>"
2. "<дословная цитата из контекста>"
```

---

## Pipeline

```
Вопрос
  ↓
[Rewrite] (опционально)
  ↓
Embedding → FAISS
  ↓
[Filter] (опционально) — отсеивает чанки с distance > MAX_DISTANCE
  ↓
Top-K чанков
  ↓
[Анти-галлюцинация] — если best_score > MAX_DISTANCE → "Не знаю"
  ↓
LLM (с промптом Sources/Quotes)
  ↓
[Парсинг ответа] — parse_response()
  ↓
Валидация → Fallback если ошибка
  ↓
Ответ с источниками и цитатами
```

---

## Установка

```bash
cd week_5/grounded-rag
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
# Терминал 1: Ollama для embeddings
ollama serve

# Терминал 2: Агент
python main.py
```

---

## Команды

| Команда | Описание |
|---------|----------|
| `rag_on/off` | Включить/выключить RAG |
| `filter_on/off` | Включить/выключить фильтрацию |
| `rewrite_on/off` | Включить/выключить перезапись |
| `eval` | Запустить оценку |
| `exit` | Выйти |

---

## Метрики evaluation

```
Отступление: 3/10 (30%)
Покрытие источниками: 8/10 (80%)
Покрытие цитатами: 8/10 (80%)

Полнота ключевых слов:
  RAG                  8/30 (27%)
  RAG+Filter           8/30 (27%)
  RAG+Rewrite          18/30 (60%)
```

- **Отступление** — сколько раз сработал "Не знаю"
- **Покрытие источниками** — % ответов с Sources
- **Покрытие цитатами** — % ответов с Quotes

---

## Пример вывода

```
Вопрос: Что такое Python Fire?
Отступление: НЕТ
Есть источники: ДА
Есть цитаты: ДА

┌─────────────────────────────────────────────────────────────┐
│ Лучший ответ (RAG, 100%)                                   │
│                                                             │
│ Answer:                                                    │
│ Python Fire - это библиотека для создания CLI из Python...   │
│                                                             │
│ Sources:                                                   │
│ - fire_dataset.txt | Section:                              │
│                                                             │
│ Quotes:                                                    │
│ 1. "Python Fire is a library for creating CLIs..."         │
└─────────────────────────────────────────────────────────────┘
```
Вопрос: Как настроить поиск в MkDocs?
Fallback: NO ✅
Has Sources: YES ✅
Has Quotes: YES ✅

┌─────────────────────────────────────────────────────────────┐
│ Лучший ответ (RAG+Filter+Rewrite, 100%)                    │
│                                                             │
│ Answer:                                                    │
│ Для настройки поиска используйте файл mkdocs.yml...          │
│                                                             │
│ Sources:                                                   │
│ - mkdocs_docs | configuration | 15                         │
│                                                             │
│ Quotes:                                                    │
│ 1. "include_search_page: true"                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Технические детали

### parse_response()

Гибкий regex с валидацией содержимого:

```python
# Проверяет:
# - наличие блоков Answer/Sources/Quotes
# - содержимое (> 10 символов для answer, > 5 для sources/quotes)
```

### Отступление (Fallback)

Срабатывает когда:
- Нет найденных чанков
- LLM не смог распарсить ответ в нужном формате

### Rich UI

Используется библиотека `rich` для цветного вывода в терминале.

---

## Быстрый старт

```bash
cd week_5/grounded-rag
source venv/bin/activate

# Запуск eval
python -c "from app.agent import Agent; from app.evaluator import run_evaluation; agent = Agent(rag_enabled=True, use_filter=True, use_rewrite=True); run_evaluation(agent)"

# Интерактивный режим
python main.py
```

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Ollama (запущен локально)
- Модель `nomic-embed-text` для Ollama
