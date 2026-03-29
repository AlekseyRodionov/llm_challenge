import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("MODEL", "tinyllama")

RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "1"))
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))

OPTIONS = {
    "temperature": 0.2,
    "num_predict": 60,
    "top_p": 0.8,
}

MAX_INPUT_LENGTH = 500
REQUEST_TIMEOUT = 60
