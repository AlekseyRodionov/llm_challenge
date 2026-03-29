import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify

from app.config import API_KEY, FLASK_PORT
from app.limiter import limiter
from app.ollama_client import generate_with_retry as generate

app = Flask(__name__)

LOG_DIR = "/opt/llm-service/logs"
LOG_FILE = os.path.join(LOG_DIR, "chat.log")


def log_request(ip: str, prompt: str, response: str, latency: float):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | IP: {ip} | Q: {prompt} | A: {response} | {latency}s\n"

    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    ip = request.remote_addr or "unknown"
    if not limiter.is_allowed(ip):
        wait_time = limiter.time_until_allowed(ip)
        return jsonify({
            "error": "Too Many Requests",
            "retry_after": round(wait_time, 1) if wait_time else 1,
        }), 429

    data = request.get_json()
    if not data:
        return jsonify({"error": "Empty request"}), 400

    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Пустой запрос"}), 400

    if len(message) > 500:
        return jsonify({"error": "Слишком длинный запрос"}), 400

    result = generate(message)

    log_request(ip, message, result["text"], result["latency"])

    return jsonify({
        "response": result["text"],
        "latency": result["latency"],
    })


if __name__ == "__main__":
    print(f"Starting server on port {FLASK_PORT}...")
    print(f"API Key: {API_KEY[:8]}...")
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)
