# VPS LLM Service

Минимальный AI-сервис для VPS с локальной LLM (Ollama).

## Возможности

- Работа с локальной LLM через Ollama API
- HTTP API с защитой по API-key
- Rate limiting (1 запрос/сек/IP)
- Веб-интерфейс
- Timeout 60 секунд
- Retry + Fallback (стабильность)
- Защита от перегрузки VPS

## Требования

- Python 3.10+
- Ollama с моделью `tinyllama`

## VPS (тестировано на)

- **CPU:** 2 vCPU
- **RAM:** 2 GB
- **Disk:** 20 GB SSD
- **OS:** Ubuntu 24.04

## Установка

```bash
cd week_6/vps-llm-service
pip install -r requirements.txt
```

## Конфигурация

Отредактируйте `.env`:

```env
API_KEY=your-secret-api-key-here
OLLAMA_URL=http://localhost:11434/api/generate
MODEL=tinyllama
RATE_LIMIT_SECONDS=1
FLASK_PORT=5000
```

## Запуск

```bash
python -m app.server
```

Сервер запустится на `http://0.0.0.0:5000`

## Запуск Ollama

В отдельном терминале:

```bash
ollama run tinyllama
```

## Тестирование

### 1. Браузер

Откройте `http://localhost:5000`

Введите вопрос и нажмите "Отправить".

### 2. curl с API-key

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"message": "Что такое Python?"}'
```

Ответ:

```json
{"response": "Python is a programming language...", "latency": 6.0}
```

### 3. Проверка rate limit

```bash
# Первый запрос — успех
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"message": "Привет"}'

# Второй запрос сразу — 429
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"message": "Пока"}'
```

Ответ при превышении лимита:

```json
{"error": "Too Many Requests", "retry_after": 0.9}
```

### 4. Проверка ошибки ключа

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"message": "Тест"}'
```

Ответ:

```json
{"error": "Unauthorized"}
```

### 5. Валидация ввода

```bash
# Пустой запрос
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"message": ""}'
# {"error": "Пустой запрос"}

# Слишком длинный запрос (>500 символов)
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"message": "x"*600}'
# {"error": "Слишком длинный запрос"}
```

## Nginx

Рекомендуется использовать Nginx как reverse proxy:

```nginx
server {
    listen 80;
    server_name YOUR_VPS_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│    Flask    │────▶│   Ollama    │
│   или curl  │◀────│  /chat API  │◀────│  (local)    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Rate Limiter │
                    │   (in-memory)│
                    └─────────────┘
```

## Качество модели tinyllama

### Результаты тестирования (10 вопросов)

| Метрика | Значение |
|---------|---------|
| Успешность | 100% |
| Latency (avg) | ~6.3s |
| Пустые ответы | 0% |
| Фактические ошибки | Редкие |

### Оценка

| Критерий | Оценка |
|----------|--------|
| Стабильность | ✅ 10/10 |
| Качество ответов | ⚠️ 7/10 |
| Latency | ⚠️ 7/10 |
| Архитектура | ✅ 9/10 |

### Примеры ответов

| Вопрос | Ответ |
|--------|-------|
| What is Python | "Python is a programming language developed by Guido van Rossum..." |
| Capital of France | "Yes, the capital of France is Paris." |
| What is AI | "AI is an acronym for Artificial Intelligence..." |
| What is Git | "Git is a version control system..." |

### Ограничения модели

- Модель иногда игнорирует формат (добавляет "Sure," в начале)
- Редкие фактические ошибки (галлюцинации)
- Ответы бывают длиннее запрошенного 1 предложения

**Примечание:** Качество ограничено моделью tinyllama (0.5B параметров, 637MB). Для улучшения качества рекомендуется замена на `qwen2.5:0.5b` или `llama3.2:1b`.

## Результаты

- **Latency:** ~6 сек (зависит от VPS и сложности вопроса)
- **Стабильность:** 100% успешных ответов (retry + fallback)
- **Rate limit:** Эффективно ограничивает нагрузку

## Финальная конфигурация

```python
OPTIONS = {
    "temperature": 0.2,
    "num_predict": 60,
    "top_p": 0.9,
}
REQUEST_TIMEOUT = 60
```

## Ограничения

- 1 запрос в секунду на IP
- Максимум 500 символов в запросе
- Timeout 60 секунд на ответ модели
- Только `tinyllama` (оптимизирована для слабого VPS)
