"""
Модуль управления памятью агента.
Реализует трёхслойную модель памяти с использованием SQLite.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "memory" / "memory.db"


def init_db():
    """Инициализирует базу данных SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS working_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_long_term_memory(content: str) -> int:
    """Добавляет запись в долговременную память."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO long_term_memory (content, created_at) VALUES (?, ?)",
        (content, datetime.now().isoformat())
    )
    conn.commit()
    memory_id = cursor.lastrowid
    conn.close()
    return memory_id


def add_working_memory(content: str) -> int:
    """Добавляет запись в рабочую память."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO working_memory (content, created_at) VALUES (?, ?)",
        (content, datetime.now().isoformat())
    )
    conn.commit()
    memory_id = cursor.lastrowid
    conn.close()
    return memory_id


def get_long_term_memory() -> list:
    """Получает все записи из долговременной памяти."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM long_term_memory ORDER BY created_at")
    results = [{"id": row[0], "content": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_working_memory() -> list:
    """Получает все записи из рабочей памяти."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM working_memory ORDER BY created_at")
    results = [{"id": row[0], "content": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results


def clear_working_memory():
    """Очищает рабочую память."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM working_memory")
    conn.commit()
    conn.close()


def clear_all_memory():
    """Очищает всю память из БД."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM long_term_memory")
    cursor.execute("DELETE FROM working_memory")
    conn.commit()
    conn.close()
