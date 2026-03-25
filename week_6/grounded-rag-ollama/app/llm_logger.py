import json
from datetime import datetime
import os

LOG_DIR = "logs"


def log_llm(mode, model, latency, success, error=None):
    os.makedirs(LOG_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "model": model,
        "latency": round(latency, 3),
        "success": success
    }

    if error:
        entry["error"] = error

    with open(f"{LOG_DIR}/llm_{mode}.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
