# Конфигурация Code Review Agent

# Лимиты для контекста
MAX_CONTEXT_LENGTH = 8000  # Максимум символов в контексте
MAX_CODE_FILES = 20        # Максимум .py файлов для контекста
MAX_DOCS = 5               # Максимум документов
MAX_DIFF_LENGTH = 5000    # Максимум символов в diff

# Пути
PROJECT_ROOT = None  # Определяется динамически в rag_context.py

# LLM настройки
DEFAULT_MODEL = "openai/gpt-4o-mini"
TEMPERATURE = 0.3
MAX_TOKENS = 2000
