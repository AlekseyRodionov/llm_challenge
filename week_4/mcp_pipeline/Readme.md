# MCP Pipeline Agent

CLI-агент с Deterministic FSM, профилями пользователей и MCP (Model Context Protocol).
Включает **MCP Pipeline** для автоматической обработки данных.

---

## Быстрый старт Pipeline

```bash
# 1. Запустить scheduler (сбор данных каждые N секунд)
mcp_call schedule_report interval_seconds=5

# 2. Подождать накопления данных (15-30 секунд)

# 3. Запустить pipeline (автоматическая обработка)
mcp_call run_monitoring_pipeline

# 4. Проверить результат
cat memory/monitoring_summary.txt
```

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
|--------|----------|
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

#### Инструменты

| Инструмент | Описание |
|------------|----------|
| `current_time` | Возвращает текущее время в формате YYYY-MM-DD HH:MM:SS |
| `get_mock_issues` | Возвращает список демо-задач |
| `mock_random_tip` | Возвращает случайный учебный совет |
| `schedule_report` | Запускает периодический сбор отчётов (interval_seconds=N, по умолчанию 20) |
| `stop_reports` | Останавливает периодический сбор отчётов |
| `get_reports_summary` | Возвращает агрегированную статистику |
| `get_last_reports` | Возвращает последние 5 отчётов |
| `fetch_recent_reports` | Получить последние отчёты из БД (MCP инструмент) |
| `analyze_reports` | Анализировать отчёты (MCP инструмент) |
| `save_summary` | Сохранить summary в файл (MCP инструмент) |
| `run_monitoring_pipeline` | Автоматический запуск всего pipeline |

#### Scheduler

Scheduler периодически собирает отчёты и сохраняет их в SQLite. Все операции логируются в файл `scheduler.log`.

**Логируемые события:**
- `MCP Server started` — старт сервера
- `Scheduler] Thread started` — старт потока scheduler
- `Scheduler] Activated with interval=Ns` — активация scheduler
- `Collecting report...` — начало сбора отчёта
- `Saved report (N issues)` — сохранение отчёта
- `Scheduler] Stopped` — остановка scheduler
- `get_reports_summary called` — вызов инструмента
- `get_last_reports called` — вызов инструмента
- `[Pipeline] === Starting monitoring pipeline ===` — старт pipeline
- `[Pipeline] Fetching reports from DB` — получение данных
- `[Pipeline] Analyzing reports` — анализ данных
- `[Pipeline] Generating summary` — формирование summary
- `[Pipeline] Saving summary` — сохранение summary
- `[Pipeline] === Pipeline completed ===` — завершение pipeline

**Просмотр логов:**
```bash
tail -f scheduler.log
```

Для подключения используйте команды: `mcp_start`, `mcp_list`, `mcp_call`, `mcp_disconnect`.

---

### MCP Pipeline

MCP Pipeline — автоматическая цепочка из нескольких инструментов для обработки данных.

**Архитектура pipeline:**

```
SQLite → fetch_recent_reports → analyze_reports → generate_summary → save_summary → memory/monitoring_summary.txt
```

**Автоматическая цепочка:**

```
run_monitoring_pipeline
  ├── fetch_recent_reports()  → list[dict]
  ├── analyze_reports()       → dict  
  ├── generate_summary()      → str
  └── save_summary()          → path
```

**Логирование:**

```
[Pipeline] === Starting monitoring pipeline ===
[Pipeline] Fetching reports from DB
[Pipeline] fetched 5 reports
[Pipeline] Analyzing reports
[Pipeline] avg=4.2 max=6
[Pipeline] Generating summary
[Pipeline] Saving summary
[Pipeline] saved to memory/monitoring_summary.txt
[Pipeline] === Pipeline completed ===
```

---

## Установка

```bash
cd mcp_pipeline
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
| `mcp_start` | Подключиться к MCP серверу |
| `mcp_list` | Показать доступные инструменты |
| `mcp_call <tool>` | Вызвать инструмент (можно с аргументами: `mcp_call schedule_report interval_seconds=5`) |
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

### MCP Pipeline Workflow

```
> mcp_start
MCP server started

> mcp_call schedule_report interval_seconds=5
Result: Report scheduled every 5 seconds

# Подождать 15-30 секунд для накопления данных

# В другом терминале смотреть логи:
# tail -f scheduler.log
# [Pipeline] === Starting monitoring pipeline ===
# [Pipeline] Fetching reports from DB
# [Pipeline] fetched 5 reports
# [Pipeline] Analyzing reports
# [Pipeline] avg=4.2 max=6
# [Pipeline] Generating summary
# [Pipeline] Saving summary
# [Pipeline] saved to memory/monitoring_summary.txt
# [Pipeline] === Pipeline completed ===

> mcp_call run_monitoring_pipeline
Result: Pipeline completed. Summary saved to: memory/monitoring_summary.txt

> cat memory/monitoring_summary.txt
System Monitoring Summary

Reports analyzed: 5
Average issues: 4.2
Peak issues: 6

> mcp_disconnect
MCP disconnected
```

---

## Структура проекта

```
mcp_pipeline/
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
│   └── demo_server.py    # Демо MCP сервер (FastMCP) + Scheduler + Pipeline
├── memory/
│   ├── memory.db         # SQLite база данных
│   └── monitoring_summary.txt  # Результат работы pipeline
├── scheduler.log         # Логи scheduler
├── .env
├── requirements.txt
└── Readme.md
```

