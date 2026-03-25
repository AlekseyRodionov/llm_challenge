import time
import requests
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    DEFAULT_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "mistral"
    TIMEOUT = 30

    def __init__(self, model=None, url=None):
        self.model = model or self.DEFAULT_MODEL
        self.url = url or self.DEFAULT_URL

    def generate(self, prompt: str) -> dict:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.5
            }
        }

        start = time.time()

        try:
            r = requests.post(self.url, json=payload, timeout=self.TIMEOUT)
            latency = time.time() - start

            if r.status_code != 200:
                logger.error(f"Ollama error: {r.status_code}")
                return {"text": "I don't know", "latency": latency, "model": self.model, "success": False}

            data = r.json()
            text = data.get("response", "")

            logger.debug(f"[OLLAMA RAW RESPONSE]\n{text}")

            return {
                "text": text,
                "latency": latency,
                "model": self.model,
                "success": True
            }

        except Exception as e:
            latency = time.time() - start
            logger.error(f"Ollama exception: {e}")
            return {"text": "I don't know", "latency": latency, "model": self.model, "success": False}
