# LLM Logical Solver CLI

Простое CLI-приложение для решения логических задач с использованием LLM (OpenAI).  
Проект демонстрирует несколько подходов к построению промтов, генерацию улучшенного промта и сравнительный анализ ответов.

---

## Структура проекта



├── app
│ ├── init.py
│ ├── comparator.py # Анализ ответов модели
│ ├── llm_client.py # Работа с OpenAI API
│ └── main.py # Основной скрипт
├── Readme.md
├── requirements.txt
└── venv


---

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository_url>
cd <repository_folder>


Создайте виртуальное окружение и активируйте его:

python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows


Установите зависимости:

pip install -r requirements.txt


Создайте .env файл с настройками OpenAI:

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1

Запуск
python app/main.py


Программа:

Выполнит несколько вариантов промтов для задачи.

Сгенерирует улучшенный промт для первого запроса.

Выведет ответы моделей и таблицу анализа с токенами.