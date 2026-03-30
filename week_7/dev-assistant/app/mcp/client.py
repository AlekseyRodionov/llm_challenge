"""
MCP Client - подключение к MCP серверу через stdio.
"""
import json
import os
import subprocess
from typing import Any, Dict, Optional

# Корень проекта llm_challenge
# app/mcp/client.py -> app/mcp -> app -> dev-assistant -> week_7 -> llm_challenge
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".."))


class MCPClient:
    """Клиент для подключения к MCP серверу через stdio."""
    
    def __init__(self, server_script: str = "app/mcp/server.py"):
        self.server_script = server_script
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
    
    def connect(self) -> bool:
        """Подключение к MCP серверу."""
        try:
            self.process = subprocess.Popen(
                ["python", self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            initialize_result = self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "dev-assistant",
                    "version": "1.0.0"
                }
            })
            return initialize_result is not None
        except Exception:
            self.process = None
            return False
    
    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """Отправить JSON-RPC запрос."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None
        
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or {}
        }
        
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            if not response_line:
                return None
            
            response = json.loads(response_line)
            
            if "error" in response:
                print(f"MCP Error: {response['error']}", file=__import__('sys').stderr)
                return None
            
            return response.get("result")
        except Exception as e:
            print(f"MCP request error: {e}", file=__import__('sys').stderr)
            return None
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[str]:
        """Вызвать инструмент на MCP сервере."""
        result = self._send_request(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments or {}
            }
        )
        return result
    
    def get_tools(self) -> Optional[list]:
        """Получить список доступных инструментов."""
        return self._send_request("tools/list")
    
    def disconnect(self):
        """Отключиться от MCP сервера."""
        if self.process:
            self.process.terminate()
            self.process = None


_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> Optional[MCPClient]:
    """Получить глобальный экземпляр MCP клиента."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        if not _mcp_client.connect():
            print("Warning: MCP connection failed, using fallback", file=__import__('sys').stderr)
            _mcp_client = None
    return _mcp_client


def mcp_git_branch() -> str:
    """Получить ветку через MCP."""
    client = get_mcp_client()
    if client:
        result = client.call_tool("git_branch", {"project_path": PROJECT_ROOT})
        if result:
            return result
    return "unknown"


def mcp_project_files(max_files: int = 350) -> str:
    """Получить список файлов через MCP."""
    client = get_mcp_client()
    if client:
        result = client.call_tool("project_files", {"max_files": max_files, "project_path": PROJECT_ROOT})
        if result:
            return result
    return ""
