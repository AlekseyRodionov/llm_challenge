# AI Code Review Agent

Автоматический AI-ревьюер кода для Pull Request на базе LLM.

---

## Описание

Система анализирует изменения в коде и возвращает структурированный review:
- Bugs (потенциальные ошибки)
- Architecture (архитектурные проблемы)
- Code Quality (качество кода)
- Suggestions (рекомендации)

---

## Структура

```
code-review-agent/
├── app/
│   ├── reviewer.py        # Главный модуль (всё в одном)
│   ├── diff_parser.py    # Парсинг git diff
│   ├── rag_context.py   # Сбор контекста (docs + code)
│   ├── llm_client.py    # OpenAI API клиент
│   └── config.py        # Конфигурация
├── scripts/
│   ├── run_review.py     # CLI скрипт
│   ├── run_demo.sh       # Запуск демо
│   └── demo_diff.txt     # Demo diff с ошибками
├── .github/workflows/
│   └── review.yml        # GitHub Action (в корне репозитория)
├── requirements.txt
└── README.md
```

---

## Требования

- Python 3.10+
- OpenAI API ключ
- Токен GitHub (для Actions)

---

## Установка

```bash
cd code-review-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Настройка

Создайте файл `.env`:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Запуск локально

### 1. Получить diff

```bash
# Diff между ветками
git diff origin/main...HEAD > diff.txt

# Или для конкретного PR
git diff main...HEAD > diff.txt
```

### 2. Запустить review

```bash
python scripts/run_review.py diff.txt
```

---

## Пример использования

### Входной diff (diff.txt):

```diff
diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -1,5 +1,8 @@
+import new_module
+
 def main():
     print("Hello")
+    print("New feature")
```

### Результат:

```
Bugs:
- Unused import 'new_module' may cause import errors
- Unused function parameter

Architecture:
- main() is doing multiple things - consider splitting

Code Quality:
- Consider adding type hints
- Function name could be more descriptive

Suggestions:
- Extract print statements to separate function
- Add docstring to main()
```

---

## GitHub Action

Workflow запускается автоматически при Pull Request и добавляет комментарий с ревью.

### Secrets (настройка в Settings → Secrets and variables → Actions):

| Secret | Описание |
|--------|----------|
| `OPENAI_API_KEY` | API ключ OpenAI |
| `OPENAI_BASE_URL` | URL API (например https://routerai.ru/api/v1) |
| `OPENAI_MODEL` | Модель (например openai/gpt-4o-mini) |
| `GH_TOKEN` | GitHub token с правами repo для записи комментариев в PR |

### Как это работает:

1. Пушится код в PR
2. GitHub Action получает diff
3. Запускается review
4. Результат добавляется как комментарий в PR

---

## Конфигурация

### Ограничения (config):

| Параметр | Значение |
|----------|----------|
| MAX_CONTEXT_LENGTH | 8000 символов |
| MAX_CODE_FILES | 20 файлов |
| MAX_DIFF_LENGTH | 5000 символов |

Изменить можно в `app/rag_context.py`.

---

## Как это работает

```
1. GitHub Action → git diff
2. diff_parser.py → структура {files, changes}
3. rag_context.py → docs + code → контекст
4. reviewer.py → prompt → LLM
5. Результат → в лог
```

---

## Лимиты

- Один вызов LLM
- Контекст до 8000 символов
- Не более 20 .py файлов в контексте

---

## Пример реального использования

```bash
# Получить diff для PR
git fetch origin
git diff origin/main...HEAD > /tmp/pr_diff.txt

# Запустить review
python scripts/run_review.py /tmp/pr_diff.txt
```

---

## Troubleshooting

### Ошибка: No changes detected
- Убедитесь что есть изменения: `git diff --stat`

### Ошибка: API key not found
- Проверьте файл `.env`

### Ошибка: Rate limit
- Подождите или используйте более дешёвую модель

---

## Demo

Запустить демонстрацию:

```bash
bash scripts/run_demo.sh
```

Или вручную:

```bash
python scripts/run_review.py scripts/demo_diff.txt
```

Содержит 3 файла с типичными ошибками:
- `app/services/user_service.py` — SQL Injection
- `app/agent.py` — eval() уязвимость
- `app/api/handlers.py` — утечка паролей
