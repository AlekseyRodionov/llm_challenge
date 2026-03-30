import os

IGNORE_DIRS = {".git", "venv", "__pycache__", ".pytest_cache", "week_7", "memory"}
IGNORE_EXT = {".pyc", ".index", ".json", ".db"}
IGNORE_FILES = {"fire_dataset.txt", "mkdocs_dataset.txt", "monitoring_summary.txt", "test_tokens.py"}


def get_project_files(project_path: str = "../..", max_files: int = 350) -> str:
    """Get list of project files (excluding venv, .git, datasets, etc.)."""
    files = []
    
    for root, dirs, filenames in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if filename.startswith("."):
                continue
            if filename.endswith(tuple(IGNORE_EXT)):
                continue
            if filename in IGNORE_FILES:
                continue
            
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, project_path)
            files.append(relpath)
    
    files = sorted(files)[:max_files]
    return "\n".join(files)
