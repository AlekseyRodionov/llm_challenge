"""Ollama API client."""
import requests


class OllamaClient:
    """Simple client for Ollama API."""
    
    def __init__(self, model: str = "mistral"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"
    
    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        print("[DEBUG] Отправка запроса в Ollama...")
        
        response = requests.post(self.url, json=payload)
        
        if response.status_code != 200:
            print(f"[ERROR] Ollama вернул статус {response.status_code}")
            return ""
        
        print("[DEBUG] Ответ получен")
        
        data = response.json()
        return data.get("response", "")
