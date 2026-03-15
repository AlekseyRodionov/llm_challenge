"""
MCP Client - подключение к локальному MCP серверу через stdio.
Упрощённая реализация с subprocess и JSON-RPC.
"""
import json
import os
import subprocess
from typing import Any, Dict, List, Optional


class MCPClient:
    """Клиент для подключения к MCP серверу через stdio."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self._request_id = 0
    
    def connect(self, server_script: str) -> bool:
        """Подключение к MCP серверу через stdio."""
        self._request_id = 0
        
        try:
            cwd = os.getcwd()
            server_path = os.path.join(cwd, server_script)
            
            # Запускаем сервер как подпроцесс
            self.process = subprocess.Popen(
                ["python", server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=cwd
            )
            
            # Отправляем initialize запрос
            result = self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp_multi_server",
                    "version": "1.0.0"
                }
            })
            
            return result is not None
        except Exception as e:
            print(f"MCP connection error: {e}")
            self.process = None
            return False
    
    def connect_to_demo_server(self) -> bool:
        """Подключение к demo_server"""
        return self.connect("mcp_servers/demo_server.py")
    
    def connect_to_external_server(self) -> bool:
        """Подключение к external_api_server"""
        return self.connect("mcp_servers/external_api_server.py")
    
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
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def list_tools(self) -> List[str]:
        """Получить список доступных инструментов."""
        result = self._send_request("tools/list", {})
        if result and "tools" in result:
            return [tool["name"] for tool in result["tools"]]
        return []
    
    def call_tool(self, name: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Вызвать инструмент."""
        if args is None:
            args = {}
        
        result = self._send_request("tools/call", {
            "name": name,
            "arguments": args
        })
        
        if result and "content" in result:
            content = result["content"]
            if isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict):
                        texts.append(item.get("text", str(item)))
                    else:
                        texts.append(str(item))
                
                # Пробуем распарсить JSON
                if len(texts) == 1:
                    try:
                        import json
                        parsed = json.loads(texts[0])
                        return parsed
                    except (json.JSONDecodeError, TypeError):
                        return texts[0]
                return texts
            return str(content)
        return None
    
    def close(self):
        """Закрыть соединение."""
        if self.process:
            self.process.terminate()
            self.process = None
