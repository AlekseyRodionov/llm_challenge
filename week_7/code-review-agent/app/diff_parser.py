"""
Модуль для парсинга git diff.
"""


def parse_diff(diff_text: str) -> dict:
    """
    Парсит git diff и возвращает структурированные данные.
    
    Args:
        diff_text: Текст git diff
        
    Returns:
        dict: {
            "files": ["file1.py", "file2.py"],
            "changes": [
                {"file": "file1.py", "diff": "..."}
            ]
        }
    """
    if not diff_text or not diff_text.strip():
        return {"files": [], "changes": []}
    
    changes = []
    files = []
    
    # Разбиваем по "diff --git"
    parts = diff_text.split("diff --git")
    
    for part in parts[1:]:  # Пропускаем первый пустой элемент
        part = "diff --git" + part
        
        lines = part.split("\n")
        
        # Имя файла обычно в первой строке после "diff --git"
        filename = None
        for line in lines:
            if line.startswith("--- a/") or line.startswith("+++ b/"):
                # Извлекаем имя файла
                path = line.replace("--- a/", "").replace("+++ b/", "").strip()
                if path.startswith("a/"):
                    path = path[2:]
                if path.startswith("b/"):
                    path = path[2:]
                filename = path
                break
        
        if filename and filename not in files:
            files.append(filename)
            
            changes.append({
                "file": filename,
                "diff": part
            })
    
    return {
        "files": files,
        "changes": changes
    }


def get_changed_files(diff_text: str) -> list:
    """
    Возвращает список изменённых файлов.
    
    Args:
        diff_text: Текст git diff
        
    Returns:
        list: Список имён файлов
    """
    parsed = parse_diff(diff_text)
    return parsed.get("files", [])


def get_file_diff(diff_text: str, filename: str) -> str:
    """
    Возвращает diff для конкретного файла.
    
    Args:
        diff_text: Текст git diff
        filename: Имя файла
        
    Returns:
        str: Diff для файла или пустая строка
    """
    parsed = parse_diff(diff_text)
    for change in parsed.get("changes", []):
        if change.get("file") == filename:
            return change.get("diff", "")
    return ""
