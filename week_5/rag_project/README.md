# RAG Document Indexing Pipeline

Учебный проект по реализации pipeline индексации документов для RAG.

## Структура проекта

```
rag_project/
├── docs/                    # Исходные документы
│   ├── fire_dataset.txt
│   └── mkdocs_dataset.txt
├── src/                    # Исходный код
│   ├── loader.py
│   ├── chunking_fixed.py
│   ├── chunking_structure.py
│   ├── embedder.py
│   ├── index_store.py
│   └── main.py
├── index/                  # Созданные индексы
└── requirements.txt
```

## Требования

- Python 3.10+
- Ollama

## Установка зависимостей

```bash
cd rag_project
pip install -r requirements.txt
```

## Установка Ollama

### macOS

```bash
brew install ollama
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Скачивание модели embeddings

```bash
ollama pull nomic-embed-text
```

## Запуск Ollama

```bash
ollama serve
```

## Запуск проекта

```bash
cd rag_project
python src/main.py
```

## Результат

После запуска в папке `index/` будут созданы:

- `faiss_fixed.index` - FAISS индекс для fixed chunking
- `metadata_fixed.json` - метаданные для fixed chunking
- `faiss_structure.index` - FAISS индекс для structure chunking
- `metadata_structure.json` - метаданные для structure chunking

## Стратегии чанкинга

### Fixed Chunking

- Разбиение по фиксированному размеру (500 символов)
- Перекрытие между чанками: 50 символов

### Structure Chunking

- Разбиение по двойным переносам строк
- Новый чанк при обнаружении markdown заголовка (#)
- Сохраняется имя секции в метаданных
