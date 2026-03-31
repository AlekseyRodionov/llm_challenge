"""
Модуль для сбора контекста из документации и кода проекта.
"""
import os
from typing import List

# Путь к корню проекта llm_challenge (на 3 уровня выше от code-review-agent)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

MAX_CONTEXT_LENGTH = 8000
MAX_CODE_FILES = 20


def load_project_docs(docs_path: str = None) -> List[dict]:
    """
    Загружает документацию проекта.
    
    Args:
        docs_path: Путь к папке с docs. По умолчанию - корень проекта.
        
    Returns:
        list: [{"source": "file.md", "text": "..."}]
    """
    if docs_path is None:
        docs_path = os.path.join(PROJECT_ROOT, "docs")
    
    if not os.path.exists(docs_path):
        # Пробуем корень проекта
        docs_path = PROJECT_ROOT
    
    docs = []
    
    # Ищем все .md файлы
    for root, dirs, files in os.walk(docs_path):
        # Исключаем системные папки
        dirs[:] = [d for d in dirs if d not in {".git", "venv", "__pycache__", "week_7"}]
        
        for filename in files:
            if not filename.endswith(".md"):
                continue
            
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                relpath = os.path.relpath(filepath, docs_path)
                docs.append({
                    "source": relpath,
                    "text": text
                })
            except Exception:
                pass
    
    return docs


def load_code_files(project_path: str = None, max_files: int = MAX_CODE_FILES) -> List[dict]:
    """
    Загружает .py файлы проекта.
    
    Args:
        project_path: Путь к проекту. По умолчанию - корень.
        max_files: Максимальное количество файлов.
        
    Returns:
        list: [{"source": "file.py", "text": "..."}]
    """
    if project_path is None:
        project_path = PROJECT_ROOT
    
    code_files = []
    
    for root, dirs, files in os.walk(project_path):
        # Исключаем системные папки
        dirs[:] = [d for d in dirs if d not in {".git", "venv", "__pycache__", "week_7", "docs"}]
        
        for filename in files:
            if not filename.endswith(".py"):
                continue
            
            # Пропускаем тесты и venv
            if filename.startswith("test_") or filename.endswith("_test.py"):
                continue
            if "venv" in root or "__pycache__" in root:
                continue
            
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                # Ограничиваем размер файла
                if len(text) > 5000:
                    text = text[:5000] + "\n... (truncated)"
                
                relpath = os.path.relpath(filepath, project_path)
                code_files.append({
                    "source": relpath,
                    "text": text
                })
            except Exception:
                pass
            
            if len(code_files) >= max_files:
                break
        
        if len(code_files) >= max_files:
            break
    
    return code_files


def build_context(parsed_diff: dict, docs: List[dict], code: List[dict], max_len: int = MAX_CONTEXT_LENGTH) -> str:
    """
    Собирает контекст из docs, code и изменённых файлов.
    
    Args:
        parsed_diff: Результат parse_diff()
        docs: Список документов
        code: Список .py файлов
        max_len: Максимальная длина контекста
        
    Returns:
        str: Собранный контекст
    """
    context_parts = []
    current_len = 0
    
    # Добавляем документацию проекта
    context_parts.append("[PROJECT DOCUMENTATION]")
    for doc in docs[:5]:  # Ограничим 5 документами
        text = doc.get("text", "")
        # Ограничиваем каждый документ
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        source = doc.get("source", "unknown")
        context_parts.append(f"\n--- {source} ---\n{text}")
        
        current_len += len(text) + 100
        if current_len > max_len:
            break
    
    # Добавляем код проекта
    if current_len < max_len - 1000:
        context_parts.append("\n\n[PROJECT CODE]")
        for f in code[:10]:  # Ограничим 10 файлами
            text = f.get("text", "")
            source = f.get("source", "unknown")
            context_parts.append(f"\n--- {source} ---\n{text}")
            
            current_len += len(text) + 100
            if current_len > max_len - 1000:
                break
    
    # Добавляем изменённые файлы
    if current_len < max_len - 500:
        context_parts.append("\n\n[CHANGED FILES]")
        for change in parsed_diff.get("changes", [])[:5]:
            file = change.get("file", "unknown")
            diff = change.get("diff", "")
            # Ограничиваем diff
            if len(diff) > 1500:
                diff = diff[:1500] + "\n... (truncated)"
            context_parts.append(f"\n--- {file} ---\n{diff}")
    
    return "\n".join(context_parts)
