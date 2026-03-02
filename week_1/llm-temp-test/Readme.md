# llm-temp-test

CLI-инструмент для анализа влияния параметра `temperature` в LLM на качество ответа.

---

## Описание

Проект исследует влияние параметра temperature на качество и характеристики ответов LLM. Выполняет один запрос с разными значениями temperature и сравнивает результаты.

## Возможности

- Тестирование temperature: 0, 0.7, 1.2
- Анализ точности, креативности и разнообразия
- Сравнительная таблица результатов
- Визуальный индикатор загрузки

---

## Установка

```bash
cd llm-temp-test
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
```

---

## Использование

```bash
python -m app.main "Ваш запрос" --temp-experiment
```

Пример:

```bash
python -m app.main "Объясни что такое нейронная сеть" --temp-experiment
```

---

## Интерпретация результатов

| Temperature | Поведение |
|-------------|-----------|
| 0 | Максимальная детерминированность, высокая точность |
| 0.7 | Баланс точности и креативности |
| 1.2 | Высокая вариативность, повышенная креативность |

---

## Структура проекта

```
llm-temp-test/
├── app/
│   ├── __init__.py
│   ├── comparator.py    # Анализ и сравнение
│   ├── llm_client.py   # Работа с API
│   └── main.py         # CLI интерфейс
├── .env
├── requirements.txt
└── Readme.md
```
