# Local LLM CLI

Минимальный CLI-клиент для работы с локальной LLM через Ollama API.

---

## Описание

Простое приложение, которое:
- Отправляет запросы в локальную LLM (Ollama)
- Получает и выводит ответы
- Работает в интерактивном режиме

---

## Установка

```bash
cd week_6/local-llm-cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Запуск

```bash
python main.py
```

Приложение сначала выполнит 3 тестовых запроса, затем перейдёт в интерактивный режим.

---

## Веб-интерфейс

```bash
python app/web.py
```
→ http://localhost:5001

Интерфейс на русском языке. Позволяет отправлять запросы к модели через браузер.

---

## Использование

```
Local LLM CLI (введите 'exit' для выхода)

Вы: Привет
LLM: Привет! Чем могу помочь?

Вы: Объясни что такое Python Fire
LLM: Python Fire — это библиотека для создания CLI...

Вы: exit
До свидания!
```

---

## Команды

| Команда | Описание |
|---------|---------|
| `exit`, `quit`, `выход` | Выйти из приложения |

---

## Требования

- Python 3.10+
- Ollama (запущен локально)
- Модель `mistral` (загружена в Ollama)

### Установка модели Ollama

```bash
ollama pull mistral
```

---

## Структура проекта

```
local-llm-cli/
├── app/
│   ├── __init__.py
│   ├── client.py   # OllamaClient
│   ├── cli.py      # run_cli()
│   └── web.py      # Flask веб-интерфейс
├── templates/
│   └── index.html  # HTML шаблон
├── main.py
├── requirements.txt
└── README.md
```
