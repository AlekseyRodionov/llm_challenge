````markdown
# LogicCLI

Простое CLI-приложение для решения логических задач с помощью LLM (OpenAI).


## Установка и запуск

git clone <repository_url>
cd <repository_folder>
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt


Создайте `.env` файл с ключом OpenAI:

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

Запуск приложения:

```bash
python app/main.py
```

