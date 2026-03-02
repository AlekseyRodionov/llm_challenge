# agent-context-compr

CLI-агент для взаимодействия с LLM со сжатием контекста.

---

## Описание

`agent-context-compr` — это CLI-инструмент для интерактивного общения с LLM.  
Поддерживает сжатие контекста через summarization для экономии токенов.

## Возможности

- Интерактивный чат с LLM
- Детальный подсчет токенов
- Сжатие контекста (summary)
- Сравнение режимов: без сжатия / со сжатием
- Сохранение контекста между сессиями

---

## Установка

```bash
cd agent-context-compr
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Настройка

```bash
cp .env.example .env
```

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

| Команда | Описание |
|---------|----------|
| `help` | Показать справку |
| `stats` | Показать статистику сессии |
| `reset` | Очистить историю |
| `history` | Показать историю |
| `tokens` | Показать текущие токены |
| `compress` | Запустить демо-сравнение (без сжатия vs со сжатием) |
| `context` | Показать контекст агентов |
| `fill` | Добавить ~80K мусорных токенов |
| `exit` | Выйти |

### Как работает сжатие

1. Последние 5 сообщений хранятся "как есть"
2. При накоплении >10 сообщений — старые заменяются summary
3. Summary генерируется через LLM
4. Экономия токенов: старые сообщения заменяются кратким summary

---

## Структура

```
agent-context-compr/
├── app/
│   ├── agent.py        # Логика агента
│   ├── llm_client.py   # Подсчет токенов
│   ├── main.py         # CLI интерфейс
│   ├── storage.py      # SQLite хранилище
│   └── summarizer.py  # Сжатие контекста
├── memory/
│   └── conversation.db
├── .env
├── requirements.txt
└── Readme.md
```
