# llm-cli-app

Простой CLI-инструмент для взаимодействия с LLM.

---

## Описание

Базовый CLI-инструмент для отправки запросов к LLM и получения ответов. Позволяет сравнивать контролируемый и обычный режим генерации.

## Возможности

- Отправка запросов к LLM
- Подсчет токенов и стоимости
- Сравнение режимов (обычный / контролируемый)
- Вывод метрик

---

## Установка

```bash
cd llm-cli-app
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

### Обычный запрос

```bash
python -m app.main "Расскажи о Python CLI инструментах"
```

### Сравнение с контролируемым режимом

```bash
python -m app.main "Расскажи о Python CLI инструментах" --compare
```

---

## Метрики

Программа подсчитывает:

- **Input tokens** — токены в запросе
- **Output tokens** — токены в ответе
- **Total tokens** — суммарное количество
- **Cost** — примерная стоимость

---

## Структура проекта

```
llm-cli-app/
├── app/
│   ├── __init__.py
│   ├── comparator.py    # Анализ и сравнение
│   ├── llm_client.py   # Работа с API
│   └── main.py         # CLI интерфейс
├── .env
├── requirements.txt
└── Readme.md
```
