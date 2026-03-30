import subprocess
import json


def get_git_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "unknown"
    except Exception:
        return "unknown"


def get_github_commits(limit: int = 10) -> str:
    """Get recent commits from GitHub API."""
    try:
        result = subprocess.run(
            ["curl", "-s", "https://api.github.com/repos/AlekseyRodionov/llm_challenge/commits?per_page=" + str(limit)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return "Не удалось получить коммиты"
        
        commits = json.loads(result.stdout)
        
        if not commits:
            return "Нет коммитов"
        
        lines = []
        for c in commits:
            sha = c.get("sha", "?")[:7]
            date = c.get("commit", {}).get("author", {}).get("date", "")[:10]
            msg = c.get("commit", {}).get("message", "").split("\n")[0][:60]
            lines.append(f"- {date} {sha} — {msg}")
        
        return "\n".join(lines)
    
    except Exception as e:
        return f"Ошибка: {str(e)[:50]}"
