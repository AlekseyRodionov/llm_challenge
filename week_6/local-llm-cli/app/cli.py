"""CLI интерфейс."""
from app.client import OllamaClient


def run_cli():
    """Запуск интерактивного CLI."""
    client = OllamaClient()
    
    print("Local LLM CLI (введите 'exit' для выхода)")
    print()
    
    while True:
        user_input = input("Вы: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ("exit", "quit", "выход"):
            print("До свидания!")
            break
        
        response = client.generate(user_input)
        print(f"LLM: {response}")
        print()
