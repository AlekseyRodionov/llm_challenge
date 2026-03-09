"""
MCP Client - подключение к локальному MCP серверу через stdio (без SDK).
"""
import json
import subprocess
from typing import Any, Dict, Optional


class MCPClient:
    """Клиент для подключения к MCP серверу через stdio."""
    
    def __init__(self, server_script: str = "mcp_servers/demo_server.py"):
        self.server_script = server_script
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
    
    def connect(self) -> bool:
        """Подключение к MCP серверу через stdio."""
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
                    "name": "fsm_mcp_agent",
                    "version": "1.0.0"
                }
            })
            return initialize_result is not None
        except Exception:
            self.process = None
            return False
    
    def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Отправить JSON-RPC запрос."""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return None
        
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params
        }
        
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            response = self.process.stdout.readline()
            if response:
                result = json.loads(response)
                if "result" in result:
                    return result["result"]
            return None
        except Exception:
            return None
    
    def list_tools(self) -> list[str]:
        """Получить список доступных инструментов."""
        result = self._send_request("tools/list", {})
        if result and "tools" in result:
            return [tool["name"] for tool in result["tools"]]
        return []
    
    def call_tool(self, name: str, args: dict[str, Any]) -> Any:
        """Вызвать инструмент."""
        result = self._send_request("tools/call", {
            "name": name,
            "arguments": args
        })
        if result and "content" in result:
            return result["content"]
        return None
    
    def close(self):
        """Закрыть соединение."""
        if self.process:
            self.process.terminate()
            self.process = None
