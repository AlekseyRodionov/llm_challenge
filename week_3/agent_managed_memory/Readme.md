# Agent с трёхслойной памятью

CLI-агент с AI-маршрутизацией памяти и SQLite-хранилищем.

---

## Описание

Учебный проект, демонстрирующий трёхслойную модель памяти:

- **Short-term** — текущий диалог (в оперативной памяти Python)
- **Working** — данные текущей задачи (SQLite)
- **Long-term** — устойчивые факты о пользователе (SQLite)

Маршрутизация сообщений по типам памяти выполняется через LLM.

---

## Возможности

- Трёхслойная модель памяти
- AI-маршрутизация (LLM определяет тип памяти)
- Интерактивный чат с LLM
- Демонстрационный режим
- Подсчёт токенов и стоимости

---

## Установка

```bash
cd agent_managed_memory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Использование

Запуск:

```bash
python -m app.main
```

### Команды

| Команда | Описание |
|---------|----------|
| `help` | Показать справку |
| `stats` | Показать статистику |
| `reset` | Очистить short-term память |
| `clear_working` | Очистить working память |
| `clear_all` | Очистить всю память из БД |
| `history` | Показать short-term память |
| `show_memory` | Показать все слои памяти |
| `demo` | Запустить демонстрацию |
| `exit` | Выйти |

---

## Демонстрация

Команда `demo` запускает автоматический сценарий (7 шагов):

1. Пользователь сообщает информацию о себе → long_term
2. Формулирует задачу → working
3. Задаёт уточняющие вопросы → short_term
4. Продолжает диалог с уточнениями
5. Добавляет предпочтения → long_term
6. Запрашивает рекомендации библиотек
7. Запрашивает бесплатные ресурсы

После демо можно посмотреть состояние памяти командой `show_memory`.

---

## Структура БД

```sql
-- long_term_memory: устойчивые факты
CREATE TABLE long_term_memory (
    id INTEGER PRIMARY KEY,
    content TEXT,
    created_at DATETIME
);

-- working_memory: текущая задача
CREATE TABLE working_memory (
    id INTEGER PRIMARY KEY,
    content TEXT,
    created_at DATETIME
);
```

---

## Структура проекта

```
agent_managed_memory/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Agent с 3 слоями памяти
│   ├── llm_client.py    # Работа с LLM API
│   ├── memory_manager.py # SQLite-менеджер
│   ├── router.py        # LLM-маршрутизатор
│   └── main.py          # CLI интерфейс
├── memory/
│   └── memory.db         # SQLite база
├── .env
├── requirements.txt
└── Readme.md
```
