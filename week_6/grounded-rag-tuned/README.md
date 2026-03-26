# Grounded RAG (Tuned)

RAG-агент с проверкой ответов: источники, цитаты и анти-галлюцинация.
Оптимизированная версия с настраиваемыми параметрами LLM.

---

## Режимы LLM

| Режим | Запуск | Описание |
|-------|--------|---------|
| Cloud | `LLM_MODE=cloud python main.py` | OpenAI (GPT-4o-mini) |
| Local | `LLM_MODE=local python main.py` | Ollama (mistral) |

---

## Конфигурации LLM

| Конфиг | temperature | num_predict | num_ctx | top_p |
|--------|-------------|-------------|---------|--------|
| fast | 0.1 | 128 | 1024 | 0.9 |
| balanced | 0.1 | 256 | 2048 | 0.9 |
| strict | 0.1 | 320 | 4096 | 0.8 |

Переключение: `LLM_CONFIG=fast|balanced|strict`

**Важно:** `num_ctx` - ключевой параметр для скорости. Меньший контекст = быстрее.

---

## Тестовые результаты (Ollama/mistral)

| Config | num_ctx | Fallback | Sources | Quotes | Latency |
|--------|---------|----------|---------|--------|---------|
| **fast** | 1024 | 0% | 100% | 100% | **10.94s** |
| balanced | 2048 | 0% | 100% | 100% | 12.92s |
| strict | 4096 | 0% | 100% | 100% | 13.14s |

Все конфиги с 100% качеством. **fast** быстрее strict на ~2.2s.

---

## Структура

```
grounded-rag-tuned/
├── app/
│   ├── config.py               # Конфигурации LLM
│   ├── llm/
│   │   ├── ollama_client.py   # Ollama API
│   │   └── openai_client.py   # OpenAI API
│   ├── llm_client.py          # Wrapper
│   ├── llm_logger.py         # Логирование метрик
│   ├── generator.py           # Генерация ответов
│   └── ...
├── logs/                       # Логи LLM метрик
├── run_tests.sh              # Автотест всех конфигов
└── ...
```

---

## Логи

Логи сохраняются в `logs/llm_*.log` (JSON Lines):

```json
{
  "mode": "local",
  "model": "mistral",
  "config": "balanced",
  "temperature": 0.3,
  "num_predict": 512,
  "latency": 8.2,
  "prompt_len": 1500,
  "success": true
}
```

---

## Запуск

```bash
# Local + конфиг
LLM_MODE=local LLM_CONFIG=balanced python main.py
LLM_MODE=local LLM_CONFIG=fast python main.py
LLM_MODE=local LLM_CONFIG=strict python main.py

# Cloud
LLM_MODE=cloud python main.py
```

---

## Автотест

```bash
./run_tests.sh
```

Тестирует все 3 конфига (fast, balanced, strict), результаты сохраняются в `test_results.txt`.

---

## Evaluator

Интерактивный режим (CLI):
```
> eval
```

Неинтерактивный режим:
```bash
LLM_MODE=local LLM_CONFIG=balanced python main.py --eval-only
```

Выводит:
- Fallback %
- Sources %
- Quotes %
- Средний latency
- Парсируемые метрики: `__CONFIG__`, `__FALLBACK__`, `__SOURCES__`, `__QUOTES__`, `__LATENCY__`

---

## 3 режима RAG

| Режим | RAG | Filter | Rewrite |
|-------|-----|--------|---------|
| RAG | ✅ | ❌ | ❌ |
| RAG+Filter | ✅ | ✅ | ❌ |
| RAG+Filter+Rewrite | ✅ | ✅ | ✅ |

---

## Требования

- Python 3.10+
- OpenAI API ключ (.env)
- Ollama (запущен локально)
- Модель `nomic-embed-text` для Ollama (embeddings)
- Модель `mistral` для Ollama (генерация)
