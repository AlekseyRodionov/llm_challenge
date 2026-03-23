"""Точка входа."""
from app.cli import run_cli
from app.client import OllamaClient


def run_tests():
    """Запуск тестовых запросов."""
    client = OllamaClient()
    
    test_prompts = [
        "Привет",
        "Объясни что такое Python Fire",
        "Объясни как работает RAG"
    ]
    
    print("=" * 50)
    print("ТЕСТОВЫЕ ЗАПРОСЫ")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Тест {i} ---")
        print(f"Вопрос: {prompt}")
        
        response = client.generate(prompt)
        print(f"Ответ: {response}")
    
    print("\n" + "=" * 50)
    print("ТЕСТЫ ЗАВЕРШЕНЫ")
    print("=" * 50)
    print()


if __name__ == "__main__":
    run_tests()
    run_cli()
