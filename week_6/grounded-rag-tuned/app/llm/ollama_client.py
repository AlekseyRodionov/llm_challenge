import time
import requests
import logging
import os

from app.config import get_llm_config, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class OllamaClient:
    DEFAULT_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "mistral"
    TIMEOUT = 30

    def __init__(self, model=None, url=None):
        self.model = model or self.DEFAULT_MODEL
        self.url = url or self.DEFAULT_URL

    def generate(self, prompt: str) -> dict:
        config = get_llm_config()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config["temperature"],
                "num_predict": config["num_predict"],
                "top_p": config["top_p"],
                "num_ctx": config.get("num_ctx", 2048)
            }
        }

        start = time.time()
        config_name = os.getenv("LLM_CONFIG", DEFAULT_CONFIG)

        try:
            r = requests.post(self.url, json=payload, timeout=self.TIMEOUT)
            latency = time.time() - start

            if r.status_code != 200:
                logger.error(f"Ollama error: {r.status_code}")
                from app.llm_logger import log_llm
                log_llm(
                    mode="local",
                    model=self.model,
                    config=config_name,
                    temperature=config["temperature"],
                    num_predict=config["num_predict"],
                    latency=latency,
                    prompt_len=len(prompt),
                    success=False,
                    error=f"HTTP {r.status_code}"
                )
                return {"text": "I don't know", "latency": latency, "model": self.model, "success": False}

            data = r.json()
            text = data.get("response", "")

            from app.llm_logger import log_llm
            log_llm(
                mode="local",
                model=self.model,
                config=config_name,
                temperature=config["temperature"],
                num_predict=config["num_predict"],
                latency=latency,
                prompt_len=len(prompt),
                success=True
            )

            return {
                "text": text,
                "latency": latency,
                "model": self.model,
                "success": True
            }

        except Exception as e:
            latency = time.time() - start
            logger.error(f"Ollama exception: {e}")
            from app.llm_logger import log_llm
            log_llm(
                mode="local",
                model=self.model,
                config=config_name,
                temperature=config["temperature"],
                num_predict=config["num_predict"],
                latency=latency,
                prompt_len=len(prompt),
                success=False,
                error=str(e)
            )
            return {"text": "I don't know", "latency": latency, "model": self.model, "success": False}
