# Support AI Assistant

AI-ассистент поддержки пользователей с RAG и контекстом пользователя.

---

## Описание

Система отвечает на вопросы пользователей, используя:
- RAG (FAQ документация)
- Контекст пользователя (данные из JSON)
- Данные тикета

---

## Архитектура

```
support-ai-assistant/
├── app/
│   ├── config.py           # Конфигурация
│   ├── llm_client.py       # OpenAI API клиент
│   ├── retriever.py        # FAISS поиск
│   ├── generator.py        # Генерация ответов (с user context)
│   ├── user_context.py     # MCP (чтение JSON)
│   ├── support_agent.py    # Главный агент
│   └── project_indexer.py  # Создание индекса
├── docs/
│   └── faq.md              # FAQ база знаний
├── data/
│   ├── users.json          # Данные пользователей
│   └── tickets.json        # Тикеты
├── index/
│   ├── index.faiss         # FAISS индекс
│   └── metadata.json       # Метаданные
├── scripts/
│   └── main.py             # CLI + Demo
├── requirements.txt
└── README.md
```

---

## Требования

- Python 3.10+
- Ollama (для embeddings)
- OpenAI API ключ

---

## Установка

```bash
cd week_7/support-ai-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Настройка

Создайте `.env` файл:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://routerai.ru/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Запуск

### Демо режим (10 вопросов)

```bash
python scripts/main.py demo
```

### Ручной режим (CLI)

```bash
python scripts/main.py
```

---

## Команды CLI

| Команда | Описание |
|---------|----------|
| `/user <id>` | Сменить пользователя (1, 2, 3) |
| `/info` | Показать контекст пользователя |
| `/help` | Показать примеры вопросов |
| `exit` | Выход |

---

## Как это работает

```
Пользователь спрашивает: "Почему не работает авторизация?"
         ↓
RAG ищет в FAQ (faq.md)
         ↓
MCP получает данные пользователя (users.json)
         ↓
MCP получает тикет (tickets.json)
         ↓
LLM генерирует персональный ответ
         ↓
Ответ: "Ваш аккаунт заблокирован после 5 неудачных попыток..."
```

---

## Demo сценарии

| user_id | Статус | Вопрос | Ожидаемый ответ |
|---------|--------|--------|-----------------|
| 1 | 🔴 blocked | Почему не работает авторизация? | Про блокировку (5 попыток) |
| 2 | 🟢 active | Как сбросить пароль? | Инструкция по сбросу |
| 3 | 🟢 active | Почему аккаунт заблокирован? | Про 3 попытки |

---

## Конфигурация

В `app/config.py`:

```python
INDEX_DIR = "index"
DATA_DIR = "data"
DOCS_DIR = "docs"
MAX_CONTEXT_LENGTH = 5000
OLLAMA_MODEL = "nomic-embed-text"
```

---

## Пример работы

### Ручной режим

```
user_id: 1
🔴 Пользователь: Alex (blocked)
📋 Тикет: login failed, 5 попыток

Вопрос: Почему не работает авторизация?
Ответ: Авторизация не работает, потому что ваш аккаунт заблокирован после нескольких неудачных попыток входа.

Вопрос: /user2
🟢 Пользователь: Maria (active)

Вопрос: Как сбросить пароль?
Ответ: Нажмите кнопку "Forgot password"...
```

### Демо режим

```
python scripts/main.py demo

[1/10] user_id=1 🔴
Вопрос: Почему не работает авторизация?
Ответ: Ваш аккаунт заблокирован...

[2/10] user_id=1 🔴
Вопрос: Как исправить?
Ответ: Сбросьте пароль через "Forgot password"...

...
```
