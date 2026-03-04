"""
Task Manager для FSM Task Mode.
Управление задачами в SQLite.
"""
import json
import re
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict

from app.memory_manager import DB_PATH


def create_task(task_text: str) -> int:
    """Создаёт новую задачу. Возвращает id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (state, task_text, plan, current_step) VALUES (?, ?, ?, ?)",
        ("IDLE", task_text, "", 0)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def get_task() -> Optional[Dict]:
    """Получает активную задачу. Возвращает dict или None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, state, task_text, plan, current_step FROM tasks WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "state": row[1],
            "task_text": row[2],
            "plan": row[3],
            "current_step": row[4]
        }
    return None


def update_task(state: str, plan: str = None, current_step: int = None):
    """Обновляет задачу."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if plan is not None and current_step is not None:
        cursor.execute(
            "UPDATE tasks SET state = ?, plan = ?, current_step = ? WHERE id = 1",
            (state, plan, current_step)
        )
    elif plan is not None:
        cursor.execute(
            "UPDATE tasks SET state = ?, plan = ? WHERE id = 1",
            (state, plan)
        )
    elif current_step is not None:
        cursor.execute(
            "UPDATE tasks SET state = ?, current_step = ? WHERE id = 1",
            (state, current_step)
        )
    else:
        cursor.execute(
            "UPDATE tasks SET state = ? WHERE id = 1",
            (state,)
        )
    
    conn.commit()
    conn.close()


def delete_task():
    """Удаляет задачу."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = 1")
    conn.commit()
    conn.close()


def parse_plan(text: str) -> List[str]:
    """Парсит план из текста LLM. Ищет строки вида: 1. ... """
    lines = text.strip().split("\n")
    plan = []
    for line in lines:
        match = re.match(r'^\d+\.\s*(.+)$', line.strip())
        if match:
            plan.append(match.group(1).strip())
    return plan


def get_current_step_text(plan_json: str, current_step: int) -> str:
    """Получает текст текущего шага."""
    try:
        plan = json.loads(plan_json)
        if 0 <= current_step < len(plan):
            return plan[current_step]
    except:
        pass
    return ""
