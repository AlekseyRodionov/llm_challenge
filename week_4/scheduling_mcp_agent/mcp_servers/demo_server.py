"""
Demo MCP Server - локальный сервер с инструментами для тестирования MCP.
Использует FastMCP SDK.
Поддержка scheduling - периодический сбор отчетов.
"""
import json
import os
import random
import sqlite3
import threading
import time
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo Server")

# Константа пути к базе данных
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory/memory.db")

# Переменные scheduler
scheduler_active = False
scheduler_thread = None
scheduler_interval = 20
last_collection_time = None
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scheduler.log")


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            issues_count INTEGER,
            issues TEXT
        )
    ''')
    conn.commit()
    conn.close()


def scheduler_loop():
    """Фоновый цикл scheduler"""
    global scheduler_active, last_collection_time
    
    # Логируем старт потока
    with open(LOG_FILE, "a") as f:
        f.write("[Scheduler] Thread started\n")
    
    while True:
        if scheduler_active:
            timestamp = datetime.now().isoformat()
            
            # Логируем начало сбора
            with open(LOG_FILE, "a") as f:
                f.write(f"[{timestamp}] Collecting report...\n")
            
            issues = get_mock_issues()
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO scheduled_reports (created_at, issues_count, issues) VALUES (?, ?, ?)",
                (timestamp, len(issues), json.dumps(issues))
            )
            conn.commit()
            conn.close()
            
            last_collection_time = timestamp
            
            # Логируем сохранение
            with open(LOG_FILE, "a") as f:
                f.write(f"[{timestamp}] Saved report ({len(issues)} issues)\n")
        
        time.sleep(scheduler_interval)


@mcp.tool()
def current_time() -> str:
    """Возвращает текущее время в формате YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool()
def get_mock_issues() -> list[str]:
    """Возвращает список демо-задач для проекта"""
    return ["Issue 1 in default", "Issue 2 in default"]


@mcp.tool()
def mock_random_tip() -> str:
    """Возвращает случайный учебный совет"""
    tips = [
        "Не забывай сохранять промежуточные результаты!",
        "Используй версионирование кода для отслеживания изменений.",
        "Пиши понятные комментарии к сложным участкам кода.",
        "Тестируй код после каждого изменения.",
        "Документируй свой API для удобства использования.",
    ]
    return random.choice(tips)


@mcp.tool()
def schedule_report(interval_seconds: int = 20) -> str:
    """Запускает периодический сбор отчетов"""
    global scheduler_active, scheduler_interval, scheduler_thread
    
    if scheduler_active:
        return "Scheduler already running"
    
    scheduler_interval = interval_seconds
    scheduler_active = True
    
    # Логируем запуск
    with open(LOG_FILE, "a") as f:
        f.write(f"[Scheduler] Activated with interval={interval_seconds}s\n")
    
    # Запускаем поток
    scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
    scheduler_thread.start()
    
    return f"Report scheduled every {interval_seconds} seconds"


@mcp.tool()
def stop_reports() -> str:
    """Останавливает периодический сбор отчетов"""
    global scheduler_active
    
    # Логируем остановку
    with open(LOG_FILE, "a") as f:
        f.write("[Scheduler] Stopped\n")
    
    scheduler_active = False
    return "Report collection stopped"


@mcp.tool()
def get_reports_summary() -> str:
    """Возвращает агрегированную статистику"""
    global last_collection_time
    
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] get_reports_summary called\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MAX(created_at) FROM scheduled_reports")
    count, last = cursor.fetchone()
    conn.close()
    
    if count is None or count == 0:
        return "No reports collected yet"
    
    # Читаем последние записи из лога
    log_info = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
            if lines:
                log_info = "\n".join(lines[-3:])  # Последние 3 записи
    
    result = f"Reports collected: {count}\nLast report: {last}"
    if scheduler_active and last_collection_time:
        result += f"\n[Scheduler active]"
    elif scheduler_active:
        result += f"\n[Scheduler starting...]"
    else:
        result += f"\n[Scheduler stopped]"
    
    if log_info:
        result += f"\n\nRecent log:\n{log_info}"
    
    return result


@mcp.tool()
def get_last_reports() -> str:
    """Возвращает последние 5 отчетов"""
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] get_last_reports called\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT created_at, issues_count FROM scheduled_reports ORDER BY id DESC LIMIT 5"
    )
    reports = cursor.fetchall()
    conn.close()
    
    if not reports:
        return "No reports yet"
    
    result = "Last 5 reports:\n"
    for created_at, issues_count in reports:
        result += f"- {created_at}: {issues_count} issues\n"
    return result.strip()


if __name__ == "__main__":
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] MCP Server started\n")
    
    init_db()
    mcp.run(transport="stdio")
