import re
import time
import requests
from threading import Lock
from typing import TypedDict

from app.config import OLLAMA_URL, MODEL, OPTIONS, REQUEST_TIMEOUT


class GenerateResult(TypedDict):
    text: str
    latency: float


_system_prompt = """Answer in one short sentence.
Do not add explanations or extra phrases.

Question:
{prompt}

Answer:"""

_lock = Lock()


def clean_response(text: str) -> str:
    bad_prefixes = [
        "Sure,",
        "Sure!",
        "Sure. ",
        "As a helpful AI assistant,",
        "As an AI assistant,",
        "Here's a",
        "Here's",
        "A short and simple answer",
        "Answered by:",
        "The answer is:",
    ]

    for p in bad_prefixes:
        if text.startswith(p):
            text = text.replace(p, "", 1).strip()

    return text


def trim_to_sentence(text: str) -> str:
    sentences = re.split(r'[.!?]', text)
    result = sentences[0].strip()
    if result:
        return result + "."
    return text


def is_truncated(text: str) -> bool:
    if text.endswith(("is", "was", "were", "has", "have", "can", "could", "will", "would")):
        return True
    if len(text.split()) < 3:
        return True
    return False


def generate(prompt: str) -> GenerateResult:
    full_prompt = _system_prompt.format(prompt=prompt)

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": OPTIONS,
    }

    start_time = time.time()

    with _lock:
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            elapsed = time.time() - start_time

            text = data.get("response", "").strip()
            text = clean_response(text)
            text = trim_to_sentence(text)

            return GenerateResult(
                text=text,
                latency=round(elapsed, 2),
            )
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return GenerateResult(
                text="Сервис временно недоступен (LLM не отвечает)",
                latency=round(elapsed, 2),
            )
        except requests.exceptions.RequestException:
            elapsed = time.time() - start_time
            return GenerateResult(
                text="Сервис временно недоступен (LLM не отвечает)",
                latency=round(elapsed, 2),
            )


def generate_with_retry(prompt: str) -> GenerateResult:
    for attempt in range(3):
        result = generate(prompt)
        text = result["text"]

        if text and not is_truncated(text):
            return result

    return GenerateResult(
        text="I don't know",
        latency=0,
    )
