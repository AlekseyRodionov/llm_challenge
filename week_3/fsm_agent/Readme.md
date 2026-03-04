# Agent с FSM Task Mode

CLI-агент с Deterministic FSM и профилями.

---

## Описание

Проект поддерживает два режима:

1. **Legacy режим** (state = IDLE) — AI router + профили
2. **FSM режим** (state != IDLE) — строгий конечный автомат

### Состояния FSM

```
IDLE → PLANNING → WAITING_APPROVAL → EXECUTING → VALIDATING → DONE
                                              ↓
                                            PAUSED
```

### Профили

| Профиль | Описание |
|---------|----------|
| **junior** | Подробные пошаговые объяснения |
| **senior** | Кратко, фокус на практике |
| **manager** | Концептуально, бизнес-подход |

---

## Установка

```bash
cd fsm_agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

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

### Команды

**Общие:**
| Команда | Описание |
|---------|----------|
| `help` | Справка |
| `stats` | Статистика |
| `reset` | Очистить историю |
| `clear_all` | Очистить БД |
| `profiles` | Список профилей |
| `profile use <name>` | Сменить профиль |
| `exit` | Выход |

**FSM команды:**
| Команда | Описание |
|---------|----------|
| `task start "..."` | Начать задачу |
| `approve` | Подтвердить план |
| `next` | Следующий шаг |
| `pause` | Приостановить |
| `resume` | Возобновить |
| `reset_task` | Сбросить задачу |
| `status` | Статус задачи |

---

## Пример работы FSM

```bash
# Начать задачу
task start Создать HTTP сервер на Python

# Посмотреть план (FSM переходит в WAITING_APPROVAL)
approve

# Выполнять шаги
next
next
next

# Статус
status

# Сброс
reset_task
```

---

## FSM диаграмма

```
        /task start
           |
           v
IDLE ---------> PLANNING
                  |
                  v
           WAITING_APPROVAL
            /            \
      approve          idle
        |                |
        v                v
    EXECUTING <--------+
        |
   /next|next
        v
   VALIDATING
    /        \
 VALID    NEED_FIX
   |          |
   v          v
  DONE    PLANNING
    |
 reset
    v
  IDLE

pause -> PAUSED -> resume -> EXECUTING
```

---

## Структура проекта

```
fsm_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Agent (legacy + FSM)
│   ├── llm_client.py    # LLM API
│   ├── memory_manager.py # SQLite
│   ├── router.py        # AI-маршрутизация
│   ├── state_machine.py # Переходы
│   ├── task_manager.py  # Управление задачами
│   ├── prompts.py       # Prompts для FSM
│   └── main.py          # CLI
├── memory/
│   └── memory.db
├── .env
├── requirements.txt
└── Readme.md
```

---

## Состояния

| Состояние | Описание |
|-----------|----------|
| IDLE | Нет активной задачи (legacy режим) |
| PLANNING | Генерация плана |
| WAITING_APPROVAL | Ожидание подтверждения |
| EXECUTING | Выполнение шагов |
| VALIDATING | Валидация результата |
| DONE | Задача выполнена |
| PAUSED | Приостановлена |
