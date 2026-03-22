"""Logger module for JSON Lines logging of RAG pipeline events."""
import json
import os
from datetime import datetime
from typing import Optional


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "rag_debug.log")


def ensure_log_dir():
    """Create logs directory if it doesn't exist."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def log_event(data: dict, path: Optional[str] = None) -> str:
    """
    Log event to JSON Lines file.
    
    Args:
        data: Dictionary with event data
        path: Optional path to log file
        
    Returns:
        Path to the log file
    """
    ensure_log_dir()
    
    target_path = path or LOG_FILE
    
    data["timestamp"] = datetime.utcnow().isoformat()
    
    with open(target_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    return target_path


def get_recent_logs(count: int = 10) -> list:
    """
    Get recent log entries.
    
    Args:
        count: Number of recent entries to return
        
    Returns:
        List of log entries
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines[-count:]:
        try:
            logs.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue
    
    return logs


def clear_logs():
    """Clear all logs."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
