import os

LLM_CONFIGS = {
    "fast": {
        "temperature": 0.1,
        "num_predict": 128,
        "num_ctx": 1024,
        "top_p": 0.9
    },
    "balanced": {
        "temperature": 0.1,
        "num_predict": 256,
        "num_ctx": 2048,
        "top_p": 0.9
    },
    "strict": {
        "temperature": 0.1,
        "num_predict": 320,
        "num_ctx": 4096,
        "top_p": 0.8
    }
}

DEFAULT_CONFIG = "balanced"
CURRENT_CONFIG = os.getenv("LLM_CONFIG", DEFAULT_CONFIG)


def get_llm_config():
    """Получить конфиг из ENV (читается при каждом вызове)."""
    return LLM_CONFIGS.get(CURRENT_CONFIG, LLM_CONFIGS[DEFAULT_CONFIG])
