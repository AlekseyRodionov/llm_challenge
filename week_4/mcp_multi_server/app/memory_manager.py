"""
Модуль управления памятью агента.
Реализует трёхслойную модель памяти с использованием SQLite.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

DB_PATH = Path(__file__).parent.parent / "memory" / "memory.db"

PRESET_PROFILES = [
    ("junior", "Подробные пошаговые объяснения. Простой язык."),
    ("senior", "Кратко. Без базовых объяснений. Фокус на практике."),
    ("manager", "Концептуально. С точки зрения бизнеса. Минимум кода."),
]


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            state TEXT NOT NULL,
            task_text TEXT NOT NULL,
            plan TEXT,
            current_step INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_invariants (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            rule TEXT NOT NULL,
            keywords TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()
    init_profiles()


def init_profiles():
    """Инициализирует профили, если таблица пуста."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        for name, description in PRESET_PROFILES:
            cursor.execute(
                "INSERT INTO profiles (name, description) VALUES (?, ?)",
                (name, description)
            )
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            ("active_profile", "junior")
        )
        conn.commit()
    
    conn.close()


def get_all_profiles() -> List[Dict]:
    """Получает все профили."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM profiles")
    results = [{"id": row[0], "name": row[1], "description": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_profile_by_name(name: str) -> Optional[Dict]:
    """Получает профиль по имени (без учёта регистра)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description FROM profiles WHERE LOWER(name) = LOWER(?)",
        (name,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "description": row[2]}
    return None


def get_active_profile() -> dict:
    """Получает активный профиль."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM settings WHERE key = 'active_profile'")
    row = cursor.fetchone()
    
    if not row:
        profile_name = "junior"
    else:
        profile_name = row[0]
    
    cursor.execute(
        "SELECT id, name, description FROM profiles WHERE LOWER(name) = LOWER(?)",
        (profile_name,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {"id": row[0], "name": row[1], "description": row[2]}
    
    return {"id": 1, "name": "junior", "description": "Подробные пошаговые объяснения. Простой язык."}


def set_active_profile(name: str) -> bool:
    """Устанавливает активный профиль по имени."""
    profile = get_profile_by_name(name)
    if not profile:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("active_profile", profile["name"])
    )
    conn.commit()
    conn.close()
    return True


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
    return memory_id or 0


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
    return memory_id or 0


def get_long_term_memory() -> List[Dict]:
    """Получает все записи из долговременной памяти."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, created_at FROM long_term_memory ORDER BY created_at")
    results = [{"id": row[0], "content": row[1], "created_at": row[2]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_working_memory() -> List[Dict]:
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
