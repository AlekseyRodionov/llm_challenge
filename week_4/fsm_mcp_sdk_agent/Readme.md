# Agent с FSM, профилями и MCP SDK

CLI-агент с Deterministic FSM, профилями пользователей и поддержкой MCP (Model Context Protocol) через официальный SDK.

---

## Описание

Проект поддерживает два режима:

1. **Legacy режим** (state = IDLE) — AI router + профили + инварианты
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

### Системные инварианты

Агент проверяет все ответы LLM на соответствие системным инвариантам:

| ID | Тип | Правило |
|----|-----|---------|
| ARCH_001 | architecture | Архитектура агента должна использовать FSM workflow |
| STACK_001 | tech_stack | Проект должен оставаться Python CLI приложением |
| STACK_002 | database | Проект должен использовать SQLite в качестве базы данных |
| BUS_001 | business_rule | Задачи должны следовать FSM workflow |

### MCP (Model Context Protocol)

Агент подключается к локальному MCP серверу и использует доступные инструменты.

Сервер: **FastMCP** (modelcontextprotocol/python-sdk)
Клиент: упрощённая реализация (subprocess + JSON-RPC)

| Инструмент | Описание |
|------------|----------|
| `current_time` | Возвращает текущее время в формате YYYY-MM-DD HH:MM:SS |
| `get_mock_issues` | Возвращает список демо-задач |
| `mock_random_tip` | Возвращает случайный учебный совет |

Для подключения используйте команды: `mcp_connect`, `mcp_list`, `mcp_call`, `mcp_disconnect`.

---

## Установка

```bash
cd fsm_mcp_sdk_agent
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

**Основные:**
| Команда | Описание |
|---------|----------|
| `help` | Показать справку |
| `stats` | Статистика запросов |
| `exit` | Выйти |

**Память:**
| Команда | Описание |
|---------|----------|
| `reset` | Очистить историю |
| `clear_working` | Очистить рабочую память |
| `clear_all` | Очистить всю память |
| `history` | Показать историю |
| `show_memory` | Показать все слои памяти |

**Профили:**
| Команда | Описание |
|---------|----------|
| `profiles` | Список профилей |
| `profile_use <name>` | Сменить профиль |
| `profile_show` | Активный профиль |

**Инварианты:**
| Команда | Описание |
|---------|----------|
| `show_invariants` | Показать инварианты |
| `add_invariant "правило"` | Добавить инвариант |
| `remove_invariant <id>` | Удалить инвариант |

**FSM:**
| Команда | Описание |
|---------|----------|
| `task_start "задача"` | Начать задачу |
| `approve` | Подтвердить план |
| `next` | Следующий шаг |
| `pause` | Приостановить |
| `resume` | Возобновить |
| `reset_task` | Сбросить задачу |
| `status` | Статус задачи |

**Демо:**
| Команда | Описание |
|---------|----------|
| `demo` | Запустить демонстрацию |

**MCP:**
| Команда | Описание |
|---------|----------|
| `mcp_connect` | Подключиться к MCP серверу |
| `mcp_list` | Показать доступные инструменты |
| `mcp_call <tool>` | Вызвать инструмент |
| `mcp_disconnect` | Отключиться от MCP сервера |

---

## Пример работы

### Добавление инварианта

```
> add_invariant "Запрещено использовать eval"
✓ Инвариант добавлен
  ID: INV_001
  Rule: Запрещено использовать eval
```

### Тест инварианта

```
> Давай добавим функцию eval
❌ Предложенное решение нарушает системные инварианты проекта.

Нарушенные правила:
* INV_001 — Запрещено использовать eval
```

### FSM Workflow

```
> task_start "Создать калькулятор"
План:
1. Определить класс Calculator
2. Добавить методы
3. Добавить тесты

> approve
Начинаю выполнение.

> next
Шаг 1 выполнен...

> status
Задача: Создать калькулятор
Состояние: EXECUTING
Шаг: 2/3
```

### MCP Workflow

```
> mcp_connect
MCP connected

> mcp_list
Available MCP tools:
  * current_time
  * get_mock_issues
  * mock_random_tip

> mcp_call get_mock_issues
Result: ['Issue 1 in default', 'Issue 2 in default']

> mcp_call current_time
Result: 2026-03-10 16:45:30

> mcp_disconnect
MCP disconnected
```

---

## FSM диаграмма

```
        /task_start
           |
           v
IDLE ---------> PLANNING
               |
               v
       WAITING_APPROVAL
        /            \
  approve          reset_task
    |                |
    v                v
EXECUTING <---------+
    |
   /next
    v
VALIDATING
    |
 confirm (или next на последнем шаге)
    v
  DONE
    |
 reset_task
    v
  IDLE

pause -> PAUSED -> resume -> EXECUTING
```

---

## Структура проекта

```
fsm_mcp_sdk_agent/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Agent (legacy + FSM)
│   ├── llm_client.py     # LLM API
│   ├── memory_manager.py # SQLite + память
│   ├── router.py         # AI-маршрутизация
│   ├── state_machine.py  # Переходы
│   ├── task_manager.py   # Управление задачами
│   ├── prompts.py        # Prompts для FSM
│   ├── invariants.py     # Системные инварианты
│   ├── mcp_client.py    # MCP клиент
│   └── main.py           # CLI
├── mcp_servers/
│   ├── __init__.py
│   └── demo_server.py    # Демо MCP сервер (FastMCP)
├── memory/
│   └── memory.db
├── .env
├── requirements.txt
└── Readme.md
```

---

## Состояния FSM

| Состояние | Описание |
|-----------|----------|
| IDLE | Нет активной задачи (legacy режим) |
| PLANNING | Генерация плана |
| WAITING_APPROVAL | Ожидание подтверждения |
| EXECUTING | Выполнение шагов |
| VALIDATING | Валидация результата |
| DONE | Задача выполнена |
| PAUSED | Приостановлена |
