# Agent с FSM и системными инвариантами

CLI-агент с Deterministic FSM, профилями и системными инвариантами.

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

---

## Установка

```bash
cd agent_with_invariants
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
 /        \
VALID    NEED_FIX
  |          |
  v          v
 DONE     PLANNING
   |
reset_task
   v
 IDLE

pause -> PAUSED -> resume -> EXECUTING
```

---

## Структура проекта

```
agent_with_invariants/
├── app/
│   ├── __init__.py
│   ├── agent.py          # Agent (legacy + FSM)
│   ├── llm_client.py    # LLM API
│   ├── memory_manager.py # SQLite + память
│   ├── router.py        # AI-маршрутизация
│   ├── state_machine.py # Переходы
│   ├── task_manager.py  # Управление задачами
│   ├── prompts.py       # Prompts для FSM
│   ├── invariants.py    # Системные инварианты
│   └── main.py          # CLI
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
