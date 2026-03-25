# App Module

Модуль приложения с RAG, фильтрацией и перезаписью запросов.

---

## Файлы

### agent.py

Основной класс `Agent` с поддержкой 3 режимов:

```python
agent = Agent(rag_enabled=True, use_filter=True, use_rewrite=True)
result = agent.ask("Как настроить поиск в MkDocs?")
```

**Методы:**
- `enable_rag()` / `disable_rag()` — включить/выключить RAG
- `enable_filter()` / `disable_filter()` — включить/выключить фильтрацию
- `enable_rewrite()` / `disable_rewrite()` — включить/выключить rewrite
- `ask(question)` — задать вопрос
- `get_status()` — получить текущий статус

---

### retriever.py

FAISS поиск с фильтрацией:

```python
from retriever import create_retriever, INITIAL_TOP_K, FINAL_TOP_K, MAX_DISTANCE

retriever = create_retriever()
chunks = retriever.retrieve("query", k=INITIAL_TOP_K)
```

**Константы:**
- `INITIAL_TOP_K = 5` — количество кандидатов из FAISS
- `FINAL_TOP_K = 2` — количество чанков после фильтрации
- `MAX_DISTANCE = 300.0` — порог фильтрации

**Функции:**
- `filter_chunks(chunks, max_distance, top_k)` — фильтрация по distance
- `create_retriever()` — создание retriever

---

### query_rewriter.py

Перезапись запросов для лучшего retrieval:

```python
from query_rewriter import rewrite_query

rewritten = rewrite_query("Как задеплоить MkDocs?")
# "How to deploy MkDocs (Python static site generator)?"
```

**Особенности:**
- Добавляет английские технические термины
- Сохраняет оригинальный вопрос для LLM
- Использует отдельный LLM вызов

---

### generator.py

Генерация ответов с контекстом:

```python
from generator import generate_answer_with_context, build_context

context = build_context(chunks, max_len=2000)
result = generate_answer_with_context(question, chunks)
```

**Промпт:** Русский (для русскоязычных пользователей)

---

### evaluator.py

Сравнение 3 режимов RAG:

```python
from evaluator import run_evaluation

agent = Agent(rag_enabled=True)
run_evaluation(agent)
```

**Вывод:**
- Полнота ключевых слов для каждого режима
- Лучший ответ (300 символов)
- Итоговая статистика

**Вопросы:** 10 специализированных вопросов с keywords

---

### cli.py

CLI интерфейс для интерактивного использования:

```bash
python main.py
```

---

## Pipeline

```
Вопрос (русский)
    ↓
[Query Rewrite] → Добавляет английские термины
    ↓
[Embedding] → Ollama nomic-embed-text
    ↓
[FAISS Search] → Top-5 кандидатов
    ↓
[Distance Filter] → Убирает чанки с distance > 300
    ↓
[Top-K Selection] → Берёт top-2 чанка
    ↓
[LLM Generation] → GPT-4o-mini с контекстом
    ↓
Ответ (русский)
```

---

## Метрики

### Полнота ключевых слов

```
Полнота = hits / total × 100%
```

Где:
- `hits` — сколько ожидаемых keywords найдено в ответе
- `total` — общее количество ожидаемых keywords

### Пример

Вопрос: "Как настроить поиск в MkDocs?"
Keywords: `["search", "индекс", "настройк"]`

Ответ LLM: "Для настройки поиска используйте файл конфигурации..."
- "search" ✅ найдено
- "индекс" ❌ не найдено
- "настройк" ✅ найдено

Результат: `2/3 = 67%`
