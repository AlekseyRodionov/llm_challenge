"""
Модуль для сохранения истории сообщений в SQLite.
"""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


class MessageStorage:
    """
    Хранилище сообщений на базе SQLite.
    Сохраняет историю диалога между сессиями.
    """

    def __init__(self, db_path: str = None):
        """
        Инициализация хранилища.
        
        Args:
            db_path: Путь к файлу БД (по умолчанию memory/conversation.db)
        """
        if db_path is None:
            base_dir = Path(__file__).parent.parent
            db_path = base_dir / "memory" / "conversation.db"
        
        self.db_path = str(db_path)
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        """Создает директорию для БД если её нет."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _init_db(self):
        """Инициализирует таблицу в БД."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT DEFAULT 'default'
            )
        """)
        conn.commit()
        conn.close()

    def save_message(self, role: str, content: str, session_id: str = "default"):
        """
        Сохраняет одно сообщение в БД.
        
        Args:
            role: Роль (system, user, assistant)
            content: Текст сообщения
            session_id: ID сессии
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO messages (role, content, timestamp, session_id) VALUES (?, ?, ?, ?)",
            (role, content, timestamp, session_id)
        )
        conn.commit()
        conn.close()

    def save_messages(self, messages: list, session_id: str = "default"):
        """
        Сохраняет список сообщений в БД.
        
        Args:
            messages: Список сообщений [{role, content}, ...]
            session_id: ID сессии
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        for msg in messages:
            cursor.execute(
                "INSERT INTO messages (role, content, timestamp, session_id) VALUES (?, ?, ?, ?)",
                (msg.get("role"), msg.get("content"), timestamp, session_id)
            )
        
        conn.commit()
        conn.close()

    def load_messages(self, session_id: str = "default") -> list:
        """
        Загружает все сообщения из БД.
        
        Args:
            session_id: ID сессии
            
        Returns:
            Список сообщений [{role, content}, ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [{"role": row[0], "content": row[1]} for row in rows]

    def has_history(self, session_id: str = "default") -> bool:
        """
        Проверяет есть ли сохраненная история.
        
        Args:
            session_id: ID сессии
            
        Returns:
            True если есть сообщения
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ?",
            (session_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0

    def clear_history(self, session_id: str = "default"):
        """
        Очищает историю сообщений.
        
        Args:
            session_id: ID сессии
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def get_message_count(self, session_id: str = "default") -> int:
        """
        Возвращает количество сохраненных сообщений.
        
        Args:
            session_id: ID сессии
            
        Returns:
            Количество сообщений
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE session_id = ?",
            (session_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
