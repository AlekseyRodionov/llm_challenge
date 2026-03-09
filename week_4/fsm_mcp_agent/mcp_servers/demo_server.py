"""
Demo MCP Server - локальный сервер с инструментами для тестирования MCP.
Реализовано без SDK через JSON-RPC over stdio.
"""
import json
import sys
from datetime import datetime


class MCPServer:
    """Простой MCP сервер."""
    
    def __init__(self):
        self.tools = {
            "current_time": {
                "name": "current_time",
                "description": "Возвращает текущее время",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "add_numbers": {
                "name": "add_numbers",
                "description": "Складывает два числа",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "integer", "description": "Первое число"},
                        "b": {"type": "integer", "description": "Второе число"}
                    },
                    "required": ["a", "b"]
                }
            },
            "echo": {
                "name": "echo",
                "description": "Возвращает тот же текст",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Текст для возврата"}
                    },
                    "required": ["text"]
                }
            }
        }
        self.protocol_version = "2024-11-05"
        self.capabilities = {}
    
    def handle_request(self, request: dict) -> dict:
        """Обработать запрос."""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return self._handle_initialize(request, request_id)
        elif method == "tools/list":
            return self._handle_list_tools(request_id)
        elif method == "tools/call":
            return self._handle_call_tool(request, request_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def _handle_initialize(self, request: dict, request_id: int) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.protocol_version,
                "capabilities": self.capabilities,
                "serverInfo": {
                    "name": "Demo MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_list_tools(self, request_id: int) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    def _handle_call_tool(self, request: dict, request_id: int) -> dict:
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "current_time":
            content = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif tool_name == "add_numbers":
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            content = str(a + b)
        elif tool_name == "echo":
            content = arguments.get("text", "")
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        }
    
    def run(self):
        """Запустить сервер."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response:
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception:
                continue


if __name__ == "__main__":
    server = MCPServer()
    server.run()
