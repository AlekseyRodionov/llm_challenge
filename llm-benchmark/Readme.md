# LLM CLI Benchmark Tool

CLI-инструмент для сравнения LLM моделей по времени, токенам и стоимости.

---

## Установка

Клонируйте репозиторий:
```bash
git clone https://github.com/AlekseyRodionov/llm_challenge.git
cd llm_challenge/
```

Создайте виртуальное окружение и установите зависимости:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка API

Создайте файл `.env`:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.url/v1
OPENAI_MODEL=openai/gpt-4o-mini
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

## Особенности

- Progress bar при выполнении benchmark
- Таймаут по умолчанию: 300 секунд
- Прерывание: Ctrl+C
- Ограничение токенов для strong модели

---

## Требования

- Python 3.9+
- OpenAI-совместимый API
