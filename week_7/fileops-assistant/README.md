# FileOps Assistant

AI-ассистент для работы с файлами проекта.

---

## Описание

Ассистент который:
- Читает файлы проекта
- Анализирует код
- Ищет информацию
- Генерирует новые файлы

---

## Структура

```
fileops-assistant/
├── app/
│   ├── llm_client.py      # OpenAI API клиент
│   ├── file_tools.py     # Инструменты для работы с файлами
│   ├── analyzer.py       # Анализ кода
│   ├── llm_tasks.py       # LLM задачи
│   ├── file_agent.py     # Главный агент
│   └── config.py          # Конфигурация
├── workspace/             # Тестовые файлы
│   └── app/
│       ├── service.py
│       ├── api.py
│       └── utils.py
├── outputs/               # Результаты
├── scripts/
│   └── demo.py            # Demo скрипт
├── requirements.txt
└── README.md
```

---

## Требования

- Python 3.10+
- OpenAI API ключ

---

## Установка

```bash
cd week_7/fileops-assistant
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

```bash
python scripts/demo.py
```

---

## Demo сценарии

| # | Задача | Результат |
|---|--------|-----------|
| 1 | "Найди где используется get_user" | outputs/api_usage_report.txt |
| 2 | "Сгенерируй README для проекта" | outputs/generated_readme.md |
| 3 | "Предложи улучшения кода" | outputs/improvements.txt |

---

## Как это работает

```
1. Задача: "Найди где используется get_user"
2. file_agent определяет тип задачи (поиск)
3. analyzer ищет в workspace/
4. Результат сохраняется в outputs/
```

---

## Компоненты

### file_tools.py
- list_files() — список файлов
- read_file() — чтение файла
- search_in_files() — поиск по файлам
- write_file() — запись файла

### analyzer.py
- find_api_usage() — поиск использования API
- analyze_project_structure() — структура проекта
- collect_code_context() — сбор контекста

### llm_tasks.py
- generate_readme() — генерация README
- suggest_improvements() — предложения по улучшению

### file_agent.py
- run_task() — главная функция
