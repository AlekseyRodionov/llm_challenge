# llm-benchmark

CLI-инструмент для сравнения LLM моделей по времени, токенам и стоимости.

---

## Описание

Инструмент для сравнения производительности и качества различных LLM моделей. Позволяет запускать один запрос на нескольких моделях и сравнивать результаты.

## Возможности

- Сравнение 3 уровней моделей (weak/medium/strong)
- Измерение времени выполнения
- Подсчет токенов и стоимости
- Гибкая настройка моделей

---

## Установка

```bash
cd llm-benchmark
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=openai/gpt-4o-mini

BENCHMARK_WEAK=qwen/qwen3.5-plus-02-15
BENCHMARK_MEDIUM=qwen/qwen3-coder-next
BENCHMARK_STRONG=qwen/qwen3.5-397b-a17b
```

---

## Использование

### Обычный запрос

```bash
python -m app.main "Ваш запрос"
```

### Benchmark (сравнение 3 моделей)

```bash
python -m app.main "Ваш запрос" --benchmark
```

### Benchmark с выбором моделей

```bash
python -m app.main "Ваш запрос" --benchmark --levels weak medium
python -m app.main "Ваш запрос" --benchmark --levels weak strong
```

### Benchmark с лимитом токенов

```bash
python -m app.main "Ваш запрос" --benchmark --max-tokens 200
```

### Контролируемый режим

```bash
python -m app.main "Ваш запрос" --compare
```

---

## Модели для Benchmark

| Уровень | Модель |
|---------|--------|
| weak | qwen/qwen3.5-plus-02-15 |
| medium | qwen/qwen3-coder-next |
| strong | qwen/qwen3.5-397b-a17b |

---

## Метрики

Программа измеряет:

- **Время** — время выполнения запроса в секундах
- **Input tokens** — количество токенов в запросе
- **Output tokens** — количество токенов в ответе
- **Total tokens** — суммарное количество токенов
- **Цена** — стоимость запроса в рублях

---

## Структура проекта

```
llm-benchmark/
├── app/
│   ├── __init__.py
│   ├── comparator.py    # Сравнение результатов
│   ├── llm_client.py   # Работа с API
│   └── main.py         # CLI интерфейс
├── .env
├── requirements.txt
└── Readme.md
```
