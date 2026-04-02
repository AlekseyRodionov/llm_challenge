"""File Agent - главный модуль координации."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from file_tools import list_files, read_file, write_file, generate_diff
from analyzer import find_api_usage, analyze_project_structure, collect_code_context
from llm_tasks import generate_with_context, generate_readme, suggest_improvements
from config import WORKSPACE_DIR, OUTPUTS_DIR


def run_task(task: str) -> dict:
    """Главная функция - выполнить задачу.
    
    Args:
        task: Задача пользователя (например "найди get_user")
    
    Returns:
        dict с результатом
    """
    task_lower = task.lower()
    result = {"task": task, "output": "", "files_created": []}
    
    if "найди" in task_lower or "search" in task_lower or "find" in task_lower:
        api_name = extract_api_name(task)
        output = find_api_usage(api_name, WORKSPACE_DIR)
        result["output"] = output
        
        report_path = os.path.join(OUTPUTS_DIR, "api_usage_report.txt")
        write_file(report_path, output)
        result["files_created"].append(report_path)
    
    elif "readme" in task_lower or "документация" in task_lower or "генерируй" in task_lower:
        context = collect_code_context(WORKSPACE_DIR, max_chars=5000)
        readme_content = generate_readme(context)
        result["output"] = readme_content
        
        readme_path = os.path.join(OUTPUTS_DIR, "generated_readme.md")
        write_file(readme_path, readme_content)
        result["files_created"].append(readme_path)
    
    elif "улучши" in task_lower or "improve" in task_lower or "suggest" in task_lower:
        context = collect_code_context(WORKSPACE_DIR, max_chars=4000)
        improvements = suggest_improvements(context)
        
        result["output"] = improvements["text"]
        
        diff_path = os.path.join(OUTPUTS_DIR, "improvements.txt")
        write_file(diff_path, improvements["text"])
        result["files_created"].append(diff_path)
    
    elif "структура" in task_lower or "structure" in task_lower:
        output = analyze_project_structure(WORKSPACE_DIR)
        result["output"] = output
    
    else:
        context = collect_code_context(WORKSPACE_DIR)
        response = generate_with_context(task, context)
        result["output"] = response["text"]
    
    return result


def extract_api_name(task: str) -> str:
    """Извлечь имя API из задачи."""
    words = task.lower().split()
    
    # Ищем явное имя функции (например get_user)
    for word in words:
        if word in ["get_user", "getuser", "get", "find", "search"]:
            # Следующее слово может быть именем
            idx = words.index(word)
            if idx + 1 < len(words):
                candidate = words[idx + 1]
                if not candidate in ["где", "все", "места", "использования", "функцию"]:
                    return candidate
    
    # Если не нашли - ищем после "функцию" или "api"
    for i, word in enumerate(words):
        if word in ["функцию", "api", "метод"]:
            if i + 1 < len(words):
                return words[i + 1]
    
    # Default
    return "get_user"


def list_files_task() -> str:
    """Список файлов проекта."""
    files = list_files(WORKSPACE_DIR)
    
    output = "📂 Файлы проекта:\n"
    for f in files:
        rel_path = os.path.relpath(f, WORKSPACE_DIR)
        output += f"  - {rel_path}\n"
    
    return output
