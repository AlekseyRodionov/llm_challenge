# simp-agent

Простой CLI-агент для взаимодействия с LLM.

---

## Описание

`simp-agent` — это Python CLI-инструмент для интерактивного общения с LLM.  
Агент поддерживает историю сообщений, что позволяет вести контекстный диалог.

## Возможности

- Интерактивный чат с LLM
- Сохранение контекста диалога
- Подсчет токенов и стоимости
- Команды управления (help, reset, history)

---

## Установка

```bash
cd simp-agent
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

Запуск чата:

```bash
python -m app.main
```

### Команды чата

| Команда | Описание |
|---------|----------|
| `help` | Показать справку |
| `stats` | Показать статистику запросов |
| `reset` | Очистить историю разговора |
| `history` | Показать историю сообщений |
| `exit` | Выйти из чата |

### Пример сессии

```
SimpAgent CLI — Чат с LLM
Введите 'help' для списка команд

Команды: help, reset, history, exit

Вы: Привет! Кто ты?
[Думаю...]

Агент: Привет! Я AI помощник...

Метрики
================== =====
Модель              ...
Input tokens        ...
Output tokens       ...
Total tokens        ...
Оценка стоимости (₽) ...

Вы: Что я только что спросил?
[Думаю...]

Агент: Вы спросили "Привет! Кто ты?"...

Вы: reset
История очищена.
```

---

## Метрики

Программа подсчитывает:

- **Input tokens** — токены в запросе (включая историю)
- **Output tokens** — токены в ответе
- **Total tokens** — суммарное количество
- **Cost** — примерная стоимость

---

## Структура проекта

```
simp-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py        # Класс Agent
│   ├── llm_client.py  # Работа с API
│   ├── main.py        # CLI интерфейс
│   └── comparator.py  # Анализ ответов
├── .env
├── requirements.txt
└── Readme.md
```
