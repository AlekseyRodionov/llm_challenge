import json
from datetime import datetime
import os

LOG_DIR = "logs"


def log_llm(mode, model, latency, success,
            temperature=None, num_predict=None, max_tokens=None,
            config=None, prompt_len=None, error=None):
    os.makedirs(LOG_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "model": model,
        "latency": round(latency, 3),
        "success": success
    }

    if temperature is not None:
        entry["temperature"] = temperature
    if num_predict is not None:
        entry["num_predict"] = num_predict
    if max_tokens is not None:
        entry["max_tokens"] = max_tokens
    if config is not None:
        entry["config"] = config
    if prompt_len is not None:
        entry["prompt_len"] = prompt_len
    if error is not None:
        entry["error"] = error

    with open(f"{LOG_DIR}/llm_{mode}.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
