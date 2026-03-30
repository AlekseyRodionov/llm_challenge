"""
MCP Server - JSON-RPC 2.0 через stdio для Dev Assistant.
"""
import json
import subprocess
import os
import sys


class MCPServer:
    def __init__(self):
        self.tools = {
            "git_branch": self.get_git_branch,
            "project_files": self.get_project_files,
            "initialize": self.initialize,
        }
        self.protocol_version = "2024-11-05"
        self.capabilities = {}
    
    def initialize(self, **kwargs) -> dict:
        """MCP initialize - возвращает capabilities."""
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "dev-assistant-mcp",
                "version": "1.0.0"
            }
        }
    
    def get_git_branch(self, **kwargs) -> str:
        """Получить текущую ветку git."""
        try:
            project_path = kwargs.get("project_path")
            if project_path:
                cwd = project_path
            else:
                cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=cwd
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def get_project_files(self, **kwargs) -> str:
        """Получить список файлов проекта."""
        max_files = kwargs.get("max_files", 100)
        project_path = kwargs.get("project_path")
        
        if project_path:
            abs_project_path = project_path
        else:
            abs_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        
        IGNORE_DIRS = {".git", "venv", "__pycache__", ".pytest_cache", "week_7", "memory"}
        IGNORE_EXT = {".pyc", ".index", ".json", ".db"}
        IGNORE_FILES = {"fire_dataset.txt", "mkdocs_dataset.txt", "monitoring_summary.txt", "test_tokens.py"}
        
        abs_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), project_path))
        files = []
        
        for root, dirs, filenames in os.walk(abs_project_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                if filename.endswith(tuple(IGNORE_EXT)):
                    continue
                if filename in IGNORE_FILES:
                    continue
                relpath = os.path.relpath(os.path.join(root, filename), abs_project_path)
                files.append(relpath)
        
        files = sorted(files)[:max_files]
        return "\n".join(files)
    
    def handle_request(self, request: dict) -> dict:
        """Обработать JSON-RPC запрос."""
        method = request.get("method")
        request_id = request.get("id")
        
        # Handle tools/call
        if method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            tool_args = request.get("params", {}).get("arguments", {})
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**tool_args)
                    return {"jsonrpc": "2.0", "id": request_id, "result": result}
                except Exception as e:
                    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(e)}}
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}}
        
        # Handle tools/list
        if method == "tools/list":
            tools = []
            for name in self.tools.keys():
                if name not in ["initialize"]:
                    tools.append({"name": name})
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
        
        if method not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
        
        try:
            params = request.get("params", {})
            result = self.tools[method](**params)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Запустить MCP server."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception:
                continue


if __name__ == "__main__":
    server = MCPServer()
    server.run()
