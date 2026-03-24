"""Flask web interface for Local LLM CLI."""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request
from app.client import OllamaClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route("/")
def index():
    logger.debug("GET / - отображение формы")
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt", "").strip()
    
    if not prompt:
        logger.debug("POST /ask - пустой промпт")
        return render_template("index.html", error="Введите вопрос")
    
    logger.debug(f"POST /ask - запрос: {prompt[:50]}...")
    
    client = OllamaClient()
    
    try:
        response = client.generate(prompt)
        if not response:
            logger.debug("POST /ask - пустой ответ от модели")
            return render_template("index.html", error="Ошибка при обращении к модели")
        logger.debug("POST /ask - ответ получен")
        return render_template("index.html", response=response)
    except Exception as e:
        logger.debug(f"POST /ask - исключение: {e}")
        return render_template("index.html", error="Ошибка при обращении к модели")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
