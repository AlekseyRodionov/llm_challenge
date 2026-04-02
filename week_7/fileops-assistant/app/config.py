import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

MAX_FILES = 20
IGNORED_DIRS = {"__pycache__", ".git", "venv", ".venv", "node_modules"}
ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}
