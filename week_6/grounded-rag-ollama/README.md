# Grounded RAG (Ollama)

RAG-агент с проверкой ответов: источники, цитаты и анти-галлюцинация.
Поддержка локальной LLM (Ollama) и облачной LLM (OpenAI).

---

## Режимы LLM

| Режим | Запуск | Описание |
|-------|--------|---------|
| Cloud | `LLM_MODE=cloud python main.py` | OpenAI (GPT-4o-mini) |
| Local | `LLM_MODE=local python main.py` | Ollama (mistral) |

---

## Структура

```
grounded-rag-ollama/
├── app/
│   ├── llm/
│   │   ├── ollama_client.py   # Ollama API (temperature=0.5)
│   │   └── openai_client.py   # OpenAI API
│   ├── llm_client.py          # Wrapper (обратная совместимость)
│   ├── llm_logger.py          # Логирование метрик
│   ├── generator.py           # Генерация ответов (с русским промптом для local)
│   └── ...
├── logs/                       # Логи LLM метрик
├── run_tests.sh               # Скрипт для запуска cloud + local тестов
└── ...
```

---

## Логи

Логи сохраняются в `logs/`:
- `logs/llm_cloud.log` — метрики OpenAI
- `logs/llm_local.log` — метрики Ollama

Формат: JSON Lines

---

## Результаты тестирования

| Метрика | Cloud (GPT-4o-mini) | Local (Mistral) |
|---------|----------------------|------------------|
| Fallback | 25% | **0%** |
| Sources | 75% | **100%** |
| Quotes | 75% | **75%** |
| Latency | ~1.4s | ~9.9s |
| Keywords | 75% | **92%** |

### Быстрый запуск

```bash
./run_tests.sh
```

---

## Установка

```bash
cd week_6/grounded-rag-ollama
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Запуск

```bash
# Cloud режим (OpenAI)
LLM_MODE=cloud python main.py

# Local режим (Ollama)
LLM_MODE=local python main.py
```

---

## Evaluator

После запуска в CLI:
```
> eval
```

Выводит:
- Fallback %
- Sources %
- Quotes %
- Средний latency

---

## 3 режима RAG

| Режим | RAG | Filter | Rewrite |
|-------|-----|--------|---------|
| RAG | ✅ | ❌ | ❌ |
| RAG+Filter | ✅ | ✅ | ❌ |
| RAG+Filter+Rewrite | ✅ | ✅ | ✅ |

---

## Команды CLI

| Команда | Описание |
|---------|---------|
| `rag_on/off` | Включить/выключить RAG |
| `filter_on/off` | Включить/выключить фильтрацию |
| `rewrite_on/off` | Включить/выключить перезапись |
| `eval` | Запустить оценку |
| `exit` | Выйти |

---

## Требования

- Python 3.10+
- OpenAI API ключ (.env)
- Ollama (запущен локально, для local режима)
- Модель `nomic-embed-text` для Ollama (embeddings)
- Модель `mistral` для Ollama (генерация, local режим)
