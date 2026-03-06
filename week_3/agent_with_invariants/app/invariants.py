"""
Модуль системных инвариантов агента.
Хранение в SQLite, три уровня защиты.
"""
import json
import sqlite3
from pathlib import Path

from app.llm_client import ask_llm

DB_PATH = Path(__file__).parent.parent / "memory" / "memory.db"

DEFAULT_INVARIANTS = [
    {
        "id": "ARCH_001",
        "type": "architecture",
        "rule": "Архитектура агента должна использовать FSM workflow",
        "keywords": ["убрать fsm", "отказаться от fsm", "без fsm", "избавиться от fsm", "без конечного автомата", "упростить архитектуру", "remove fsm", "replace fsm", "without fsm", "переделать без fsm", "отказаться от конечного автомата", "убрать конечный автомат", "без использования fsm", "без использования конечного автомата", "не использовать fsm", "не использовать конечный автомат", "альтернатива fsm"]
    },
    {
        "id": "STACK_001",
        "type": "tech_stack",
        "rule": "Проект должен оставаться Python CLI приложением",
        "keywords": ["web ui", "веб интерфейс", "веб-интерфейс", "javascript", "node.js", "react", "vue", "angular", "frontend", "браузер", "django", "flask", "web приложение", "веб-приложение", "html", "css"]
    },
    {
        "id": "STACK_002",
        "type": "database",
        "rule": "Проект должен использовать SQLite в качестве базы данных",
        "keywords": ["postgresql", "postgres", "mysql", "mariadb", "mongodb", "redis", "nosql", "dynamodb", "firebase", "другая база", "другую базу", "заменить sqlite", "подключить postgresql", "подключить mysql", "использовать mongodb"]
    },
    {
        "id": "BUS_001",
        "type": "business_rule",
        "rule": "Задачи должны следовать FSM workflow: планирование → подтверждение → выполнение",
        "keywords": ["skip planning", "без планирования", "пропустить планирование", "без approval", "без подтверждения", "direct execution", "прямое выполнение", "пропустить этап", "сразу выполнить", "без согласования", "пропустить шаг"]
    }
]


def init_invariants_db():
    """Инициализация таблицы и загрузка дефолтных инвариантов."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Удаляем старые дефолтные инварианты и загружаем новые
    cursor.execute("DELETE FROM system_invariants WHERE id IN ('ARCH_001', 'STACK_001', 'STACK_002', 'BUS_001')")
    
    for inv in DEFAULT_INVARIANTS:
        cursor.execute(
            "INSERT OR REPLACE INTO system_invariants (id, type, rule, keywords, is_active) VALUES (?, ?, ?, ?, ?)",
            (inv["id"], inv["type"], inv["rule"], json.dumps(inv["keywords"]), 1)
        )
    conn.commit()
    
    conn.close()


def get_invariants_from_db() -> list:
    """Получить активные инварианты из БД."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, rule, keywords FROM system_invariants WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    
    invariants = []
    for row in rows:
        keywords = json.loads(row[3]) if row[3] else []
        invariants.append({
            "id": row[0],
            "type": row[1],
            "rule": row[2],
            "keywords": keywords
        })
    return invariants


def get_all_invariants_from_db() -> list:
    """Получить все инварианты из БД (для show_invariants)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, rule, keywords, is_active FROM system_invariants ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    invariants = []
    for row in rows:
        keywords = json.loads(row[3]) if row[3] else []
        invariants.append({
            "id": row[0],
            "type": row[1],
            "rule": row[2],
            "keywords": keywords,
            "is_active": bool(row[4])
        })
    return invariants


def add_invariant_to_db(inv_type: str, rule: str, keywords: list) -> str:
    """
    Добавить инвариант в БД.
    Генерирует ID автоматически.
    Возвращает ID добавленного инварианта.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(CAST(SUBSTR(id, 5) AS INTEGER)) FROM system_invariants WHERE id LIKE 'INV_%'")
    max_num = cursor.fetchone()[0] or 0
    new_id = f"INV_{max_num + 1:03d}"
    
    cursor.execute(
        "INSERT INTO system_invariants (id, type, rule, keywords, is_active) VALUES (?, ?, ?, ?, ?)",
        (new_id, inv_type, rule, json.dumps(keywords), 1)
    )
    conn.commit()
    conn.close()
    
    return new_id


def remove_invariant_from_db(inv_id: str) -> bool:
    """Удалить инвариант из БД. Возвращает True если удален."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM system_invariants WHERE id = ?", (inv_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def toggle_invariant_in_db(inv_id: str, active: bool) -> bool:
    """Включить/выключить инвариант. Возвращает True если изменен."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE system_invariants SET is_active = ? WHERE id = ?", (1 if active else 0, inv_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def generate_keywords_with_llm(rule: str) -> list:
    """
    Генерирует keywords на основе правила через LLM.
    
    Args:
        rule: Текст правила
        
    Returns:
        Список ключевых слов/фраз
    """
    prompt = f"""Проанализируй правило и предложи 8-12 ключевых слов или фраз на РУССКОМ и АНГЛИЙСКОМ языках,
которые могут указывать на нарушение этого правила.
Верни ТОЛЬКО JSON массив слов/фраз (без пояснений).

Правило: {rule}

Пример формата: ["keyword1", "keyword2", "фраза 1", "фраза 2"]"""

    messages = [
        {"role": "system", "content": "Ты - генератор ключевых слов для системы инвариантов."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        result = ask_llm(
            prompt="",
            model="openai/gpt-4o-mini",
            temperature=0.3,
            messages=messages
        )
        
        keywords_text = result["text"].strip()
        
        try:
            keywords = json.loads(keywords_text)
            if isinstance(keywords, list):
                return [k.strip().lower() for k in keywords if k.strip()]
        except json.JSONDecodeError:
            import re
            match = re.search(r'\[[\s\S]*\]', keywords_text)
            if match:
                keywords = json.loads(match.group())
                return [k.strip().lower() for k in keywords if k.strip()]
        
        return []
    except Exception as e:
        print(f"Error generating keywords: {e}")
        return []


def get_next_invariant_id() -> str:
    """Получить следующий ID для инварианта."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(CAST(SUBSTR(id, 5) AS INTEGER)) FROM system_invariants WHERE id LIKE 'INV_%'")
    max_num = cursor.fetchone()[0] or 0
    conn.close()
    return f"INV_{max_num + 1:03d}"


def check_invariants(text: str) -> list:
    """
    Проверяет текст на нарушение инвариантов.
    
    Args:
        text: Текст ответа LLM для проверки
        
    Returns:
        Список ID нарушенных инвариантов
    """
    invariants = get_invariants_from_db()
    text_lower = text.lower()
    violations = []
    
    for inv in invariants:
        inv_id = inv["id"]
        keywords = inv.get("keywords", [])
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                if inv_id not in violations:
                    violations.append(inv_id)
                break
    
    return violations


def explain_violation(violations: list) -> str:
    """
    Формирует сообщение о нарушении инвариантов.
    
    Args:
        violations: Список ID нарушенных инвариантов
        
    Returns:
        Сообщение об ошибке для пользователя
    """
    invariants = get_invariants_from_db()
    messages = []
    
    for vid in violations:
        for inv in invariants:
            if inv["id"] == vid:
                messages.append(f"{vid} — {inv['rule']}")
                break
    
    result = "❌ Предложенное решение нарушает системные инварианты проекта.\n\n"
    result += "Нарушенные правила:\n"
    for msg in messages:
        result += f"* {msg}\n"
    result += "\nПредложите решение, которое соответствует этим ограничениям."
    
    return result


def get_invariants_list() -> list:
    """Возвращает список активных инвариантов (алиас для совместимости)."""
    return get_invariants_from_db()
