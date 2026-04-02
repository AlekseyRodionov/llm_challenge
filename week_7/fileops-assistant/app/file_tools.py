"""File tools - core module for file operations."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from config import WORKSPACE_DIR, OUTPUTS_DIR, MAX_FILES, IGNORED_DIRS, ALLOWED_EXTENSIONS


def list_files(root_dir: str = None) -> list:
    """Рекурсивно вернуть список файлов."""
    root_dir = root_dir or WORKSPACE_DIR
    
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1]
            if ext in ALLOWED_EXTENSIONS:
                full_path = os.path.join(dirpath, filename)
                files.append(full_path)
                
                if len(files) >= MAX_FILES:
                    return files
    
    return files


def read_file(path: str) -> str:
    """Прочитать файл."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def search_in_files(pattern: str, files: list = None) -> dict:
    """Найти строки где встречается pattern.
    
    Returns:
        {file_path: [(line_number, line_content), ...]}
    """
    files = files or list_files()
    results = {}
    
    for file_path in files:
        matches = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern in line:
                        matches.append((line_num, line.rstrip()))
        except (UnicodeDecodeError, IOError):
            continue
        
        if matches:
            results[file_path] = matches
    
    return results


def write_file(path: str, content: str) -> str:
    """Сохранить файл."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return path


def generate_diff(old_content: str, new_content: str, old_path: str = "original.py", new_path: str = "modified.py") -> str:
    """Сгенерировать unified diff."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff_lines = []
    diff_lines.append(f"--- {old_path}\n")
    diff_lines.append(f"+++ {new_path}\n")
    
    import difflib
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=old_path, tofile=new_path, lineterm='')
    
    for line in diff:
        diff_lines.append(line + '\n')
    
    return ''.join(diff_lines)


def get_file_info(path: str) -> dict:
    """Получить информацию о файле."""
    stat = os.stat(path)
    return {
        "path": path,
        "name": os.path.basename(path),
        "size": stat.st_size,
        "lines": len(read_file(path).splitlines()),
    }
