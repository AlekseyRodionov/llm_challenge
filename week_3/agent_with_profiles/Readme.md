# Agent с профилями

CLI-агент с трёхслойной памятью и системой профилей.

---

## Описание

Проект расширяет `agent_managed_memory` системой профилей:

- **Трёхслойная память** (short-term, working, long-term)
- **Система профилей** — адаптация ответов LLM под пользователя
- **AI-маршрутизация** сообщений по типам памяти

### Профили

| Профиль | Описание |
|---------|----------|
| **junior** | Подробные пошаговые объяснения, простой язык |
| **senior** | Кратко, без базовых объяснений, фокус на практике |
| **manager** | Концептуально, с точки зрения бизнеса, минимум кода |

---

## Установка

```bash
cd agent_with_profiles
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
| `profiles` | Список профилей |
| `profile use <name>` | Сменить профиль |
| `profile show` | Показать активный профиль |
| `demo` | Запустить демонстрацию |
| `exit` | Выйти |

---

## Пример использования

```bash
# Показать профили
profiles

# Сменить профиль на senior
profile use senior

# Задать вопрос
Объясни что такое decorator в Python

# Переключиться на junior
profile use junior

# Повторить вопрос
Объясни что такое decorator в Python
```

Ответы будут отличаться по стилю и глубине в зависимости от профиля.

---

## Структура БД

```sql
-- Профили пользователей
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

-- Настройки (активный профиль)
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Память (из agent_managed_memory)
CREATE TABLE long_term_memory (...);
CREATE TABLE working_memory (...);
```

---

## Структура проекта

```
agent_with_profiles/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Agent с профилями
│   ├── llm_client.py    # Работа с LLM API
│   ├── memory_manager.py # SQLite + профили
│   ├── router.py        # LLM-маршрутизатор
│   └── main.py          # CLI интерфейс
├── memory/
│   └── memory.db         # SQLite база
├── .env
├── requirements.txt
└── Readme.md
```
