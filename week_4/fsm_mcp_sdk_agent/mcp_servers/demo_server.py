"""
Demo MCP Server - локальный сервер с инструментами для тестирования MCP.
Использует FastMCP SDK.
"""
import random
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo Server")


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


if __name__ == "__main__":
    mcp.run(transport="stdio")
