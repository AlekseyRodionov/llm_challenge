# llmsolver

CLI-инструмент для решения логических задач с помощью LLM.

---

## Описание

Инструмент для тестирования различных подходов к решению логических задач. Использует несколько промтов и сравнивает результаты, находит оптимальный формат.

## Возможности

- Тестирование различных промтов для решения задач
- Генерация улучшенных промтов через LLM
- Сравнительный анализ ответов
- Проверка структуры и полноты решений

---

## Установка

```bash
cd llmsolver
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
python -m app.main
```

---

## Структура проекта

```
llmsolver/
├── app/
│   ├── __init__.py
│   ├── comparator.py    # Анализ и сравнение
│   ├── llm_client.py   # Работа с API
│   └── main.py         # CLI интерфейс
├── .env
├── requirements.txt
└── Readme.md
```
