"""Analyzer module - code analysis functions."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from file_tools import list_files, read_file, search_in_files
from llm_tasks import analyze_api_usage
from config import WORKSPACE_DIR, MAX_FILES


def detect_usage_type(line_content: str, api_name: str) -> str:
    """Определить тип использования API.
    
    Returns:
        Тип: DEF, CALL, IMPORT, USE
    """
    line = line_content.strip()
    
    # Импорт
    if 'import' in line and api_name in line:
        return "IMPORT"
    
    # Определение функции
    if f'def {api_name}' in line or f'def {api_name.lower()}' in line:
        return "DEF"
    
    # Вызов функции (с скобками)
    if f'{api_name}(' in line:
        return "CALL"
    
    # Просто использование
    if api_name in line:
        return "USE"
    
    return "USE"


def format_results(results: dict, api_name: str = "") -> str:
    """Форматировать результаты поиска для чтения.
    
    Args:
        results: Словарь {file: [(line_num, code), ...]}
        api_name: Имя API для определения типа
    
    Returns:
        Форматированный текст с типами использования
    """
    lines = []
    
    for file_path, matches in results.items():
        file_name = os.path.basename(file_path)
        lines.append(f"\n📄 {file_name}")
        
        for line_num, code in matches:
            usage_type = detect_usage_type(code, api_name or "")
            lines.append(f"   ├─ [{usage_type}] {line_num}: {code}")
    
    return "\n".join(lines)


def find_api_usage(api_name: str, root_dir: str = None) -> str:
    """Найти использование API.
    
    Returns:
        Текстовый отчёт с местами использования
    """
    root_dir = root_dir or WORKSPACE_DIR
    files = list_files(root_dir)
    
    results = search_in_files(api_name, files)
    
    if not results:
        return f"""📊 SUMMARY
───────────────────────────────────────
Файлов найдено: 0
Всего обращений: 0

📍 РЕЗУЛЬТАТ
───────────────────────────────────────
Ничего не найдено

🧠 AI АНАЛИЗ
───────────────────────────────────────
API "{api_name}" не используется в проекте."""
    
    # SUMMARY
    total_matches = sum(len(m) for m in results.values())
    main_file = max(results.keys(), key=lambda f: len(results[f]))
    main_file_name = os.path.basename(main_file)
    
    summary = f"""📊 SUMMARY
───────────────────────────────────────
Файлов найдено: {len(results)}
Всего обращений: {total_matches}
Основной файл: {main_file_name}"""
    
    formatted = format_results(results, api_name)
    analysis = analyze_api_usage(api_name, results)
    
    return f"""{summary}

📍 РЕЗУЛЬТАТ
───────────────────────────────────────
{formatted}

🧠 AI АНАЛИЗ
───────────────────────────────────────
{analysis}"""


def analyze_project_structure(root_dir: str = None) -> str:
    """Анализ структуры проекта.
    
    Returns:
        Текстовый обзор структуры
    """
    root_dir = root_dir or WORKSPACE_DIR
    files = list_files(root_dir)
    
    if not files:
        return "Файлы не найдены."
    
    report = ["📂 Структура проекта:\n"]
    
    file_infos = []
    for f in files:
        rel_path = os.path.relpath(f, root_dir)
        size = os.path.getsize(f)
        try:
            lines = len(read_file(f).splitlines())
        except:
            lines = 0
        file_infos.append({
            "path": rel_path,
            "size": size,
            "lines": lines
        })
    
    for info in file_infos:
        report.append(f"  📄 {info['path']} ({info['lines']} строк)")
    
    total_lines = sum(f['lines'] for f in file_infos)
    report.append(f"\n📊 Всего: {len(files)} файлов, {total_lines} строк")
    
    return '\n'.join(report)


def collect_code_context(root_dir: str = None, max_chars: int = 6000) -> str:
    """Собрать содержимое файлов для контекста.
    
    Returns:
        Объединённое содержимое файлов
    """
    root_dir = root_dir or WORKSPACE_DIR
    files = list_files(root_dir)
    
    context = []
    total_chars = 0
    
    for file_path in files:
        if total_chars >= max_chars:
            break
        
        try:
            content = read_file(file_path)
            rel_path = os.path.relpath(file_path, root_dir)
            
            context.append(f"\n{'='*40}\n")
            context.append(f"📄 {rel_path}\n")
            context.append(f"{'='*40}\n")
            context.append(content)
            
            total_chars += len(content)
        except:
            continue
    
    return '\n'.join(context)


def get_file_summary(file_path: str) -> str:
    """Краткое описание файла."""
    if not os.path.exists(file_path):
        return "Файл не найден"
    
    content = read_file(file_path)
    lines = content.splitlines()
    
    summary = f"📄 {os.path.basename(file_path)}\n"
    summary += f"   Строк: {len(lines)}\n"
    summary += f"   Символов: {len(content)}\n"
    
    functions = [l for l in lines if l.strip().startswith('def ')]
    classes = [l for l in lines if l.strip().startswith('class ')]
    
    if functions:
        summary += f"   Функций: {len(functions)}\n"
    if classes:
        summary += f"   Классов: {len(classes)}\n"
    
    return summary
