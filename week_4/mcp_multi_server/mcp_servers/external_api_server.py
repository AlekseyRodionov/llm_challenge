"""
External API MCP Server - получает советы по продуктивности с внешнего API.
Использует FastMCP SDK.
"""
import json

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("External API Server")


@mcp.tool()
def fetch_productivity_tips() -> list[str]:
    """Получить советы по продуктивности от внешнего API"""
    tips = []
    
    try:
        # Делаем 3 запроса к API
        for _ in range(3):
            response = httpx.get("https://api.adviceslip.com/advice", timeout=10)
            if response.status_code == 200:
                data = response.json()
                advice = data.get("slip", {}).get("advice", "")
                if advice:
                    tips.append(advice)
    except Exception as e:
        # Fallback советы если API недоступен
        tips = [
            "Регулярно делайте перерывы в работе",
            "Планируйте задачи заранее",
            "Отслеживайте прогресс ежедневно"
        ]
    
    return tips


if __name__ == "__main__":
    mcp.run(transport="stdio")
