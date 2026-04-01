"""User context module - MCP для получения данных пользователей и тикетов."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_user(user_id: int) -> dict:
    """Получить данные пользователя по ID."""
    with open(os.path.join(DATA_DIR, "users.json"), 'r', encoding='utf-8') as f:
        users = json.load(f)
    return next((u for u in users if u["id"] == user_id), None)


def get_user_ticket(user_id: int) -> dict:
    """Получить тикет пользователя."""
    with open(os.path.join(DATA_DIR, "tickets.json"), 'r', encoding='utf-8') as f:
        tickets = json.load(f)
    return next((t for t in tickets if t["user_id"] == user_id), None)
