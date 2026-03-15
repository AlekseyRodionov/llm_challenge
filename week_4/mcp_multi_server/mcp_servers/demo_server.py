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


# === Pipeline MCP Tools ===

@mcp.tool()
def fetch_recent_reports() -> list[dict]:
    """Получить последние отчёты из БД"""
    with open(LOG_FILE, "a") as f:
        f.write("[Pipeline] Fetching reports from DB\n")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT created_at, issues_count FROM scheduled_reports ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    reports = [{"time": row[0], "issues": row[1]} for row in rows]
    with open(LOG_FILE, "a") as f:
        f.write(f"[Pipeline] fetched {len(reports)} reports\n")
    return reports


@mcp.tool()
def analyze_reports(reports) -> dict:
    """Анализировать отчёты"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[Pipeline] Analyzing reports, input type: {type(reports)}\n")
    
    # Если reports - строка (ошибка), возвращаем пустой результат
    if isinstance(reports, str):
        return {"total_reports": 0, "average_issues": 0, "max_issues": 0}
    
    if not reports:
        return {"total_reports": 0, "average_issues": 0, "max_issues": 0}
    
    # Пробуем обработать как список
    try:
        reports_list = reports if isinstance(reports, list) else [reports]
        
        # Парсим JSON-строки если нужно
        parsed_reports = []
        for r in reports_list:
            if isinstance(r, str):
                try:
                    import json
                    parsed_reports.append(json.loads(r))
                except:
                    parsed_reports.append({"issues": 0})
            else:
                parsed_reports.append(r)
        
        total = len(parsed_reports)
        issues_list = []
        for r in parsed_reports:
            if isinstance(r, dict):
                issues_list.append(r.get("issues", 0))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                issues_list.append(r[1])
            else:
                issues_list.append(0)
        
        avg = sum(issues_list) / total if total > 0 else 0
        max_issues = max(issues_list) if issues_list else 0
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"[Pipeline] Error analyzing: {e}\n")
        return {"total_reports": 0, "average_issues": 0, "max_issues": 0}
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[Pipeline] avg={avg:.1f} max={max_issues}\n")
    return {"total_reports": total, "average_issues": avg, "max_issues": max_issues}


@mcp.tool()
def generate_summary(analysis, tips=None) -> str:
    """Сформировать summary с использованием LLM"""
    with open(LOG_FILE, "a") as f:
        f.write(f"[Pipeline] Generating summary, analysis type: {type(analysis)}, tips type: {type(tips)}\n")
    
    # Проверяем, что analysis - словарь
    if not isinstance(analysis, dict):
        with open(LOG_FILE, "a") as f:
            f.write(f"[Pipeline] ERROR: analysis is not dict, it's {type(analysis)}: {analysis}\n")
        return f"Error: analysis is {type(analysis)}, expected dict"
    
    # Пробуем использовать LLM
    try:
        import os
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from app.llm_client import ask_llm
        
        tips_list = tips if isinstance(tips, list) else []
        tips_text_en = ", ".join(tips_list)
        
        # Переводим советы на русский
        tips_russian = tips_text_en
        if tips_list:
            translation_prompt = f"""Переведи на русский язык советы ниже. 
Выведи ТОЛЬКО перевод, БЕЗ лишнего текста, БЕЗ фразы "Вот перевод":

{tips_text_en}"""
            translated = ask_llm(translation_prompt, max_tokens=200)
            tips_russian = f"=== Советы (adviceslip.com) ===\n{translated.get('text', tips_text_en)}"
        
        # Формируем основной промт
        prompt = f"""Дай краткий анализ на русском языке по данным мониторинга:
- Отчётов: {analysis.get('total_reports', 0)}
- Среднее: {analysis.get('average_issues', 0):.1f}
- Пик: {analysis.get('max_issues', 0)}

Дай:
1. Краткую оценку (1 предложение)
2. 2-3 рекомендации списком
3. Оценку: подходят ли советы к контексту мониторинга (да/нет и почему)
"""
        llm_result = ask_llm(prompt, max_tokens=500)
        llm_text = llm_result.get("text", "")
        
        # Формируем полный ответ
        result = f"""=== Данные мониторинга ===
Отчётов: {analysis.get('total_reports', 0)}
Среднее: {analysis.get('average_issues', 0):.1f}
Пик: {analysis.get('max_issues', 0)}

{tips_russian}

=== Анализ ===
{llm_text}
"""
        
        with open(LOG_FILE, "a") as f:
            f.write("[Pipeline] Generated with LLM\n")
        
        return result
    except Exception as e:
        # Fallback на простой шаблон
        tips_list = tips if isinstance(tips, list) else []
        tips_text = "\n".join(f"{i}. {t}" for i, t in enumerate(tips_list, 1))
        summary = f"""=== Данные мониторинга ===
Отчётов: {analysis.get('total_reports', 0)}
Среднее: {analysis.get('average_issues', 0):.1f}
Пик: {analysis.get('max_issues', 0)}

=== Советы ===
{tips_text}

(LLM недоступен)
"""
        with open(LOG_FILE, "a") as f:
            f.write(f"[Pipeline] LLM error, using template: {e}\n")
        return summary


@mcp.tool()
def save_summary(summary: str) -> str:
    """Сохранить summary в файл"""
    with open(LOG_FILE, "a") as f:
        f.write("[Pipeline] Saving summary\n")
    summary_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory/monitoring_summary.txt")
    with open(summary_path, "w") as f:
        f.write(summary)
    with open(LOG_FILE, "a") as f:
        f.write("[Pipeline] saved to memory/monitoring_summary.txt\n")
    return summary_path


@mcp.tool()
def run_monitoring_pipeline() -> str:
    """Автоматический запуск мониторинг pipeline"""
    with open(LOG_FILE, "a") as f:
        f.write("[Pipeline] === Starting monitoring pipeline ===\n")
    
    # Шаг 1: получить данные
    reports = fetch_recent_reports()
    
    # Шаг 2: анализировать
    analysis = analyze_reports(reports)
    
    # Шаг 3: сформировать summary
    summary = generate_summary(analysis)
    
    # Шаг 4: сохранить
    path = save_summary(summary)
    
    with open(LOG_FILE, "a") as f:
        f.write("[Pipeline] === Pipeline completed ===\n")
    return f"Pipeline completed. Summary saved to: {path}"


if __name__ == "__main__":
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] MCP Server started\n")
    
    init_db()
    mcp.run(transport="stdio")
