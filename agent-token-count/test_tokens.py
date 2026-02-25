"""
Тестовый скрипт для проверки лимита токенов.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.chdir("/Users/aleks_ey/Documents/dev/python/llm_challenge/agent-token-count")

from dotenv import load_dotenv
load_dotenv()

from app.llm_client import get_history_tokens, get_request_tokens, check_token_limit, count_tokens

def test_fill_simulation():
    model = "openai/gpt-4o-mini"
    
    messages = [
        {"role": "system", "content": "Ты полезный AI помощник."}
    ]
    
    print("=" * 60)
    print("ТЕСТ: Симуляция заполнения токенов")
    print("=" * 60)
    
    from app.llm_client import count_tokens
    dummy_text = "Lorem ipsum dolor sit amet consectetur adipiscing elit. " * 4500
    
    tokens_per_fill = count_tokens(dummy_text, model) * 2
    
    for i in range(5):
        messages.append({"role": "user", "content": dummy_text})
        messages.append({"role": "assistant", "content": "Dummy response for simulation. " * 800})
        
        history_tokens = get_history_tokens(messages, model)
        request_tokens = 10
        limit = check_token_limit(history_tokens, request_tokens, model)
        
        print(f"\nШаг {i+1} (fill #{i+1}):")
        print(f"  Сообщений: {len(messages)}")
        print(f"  Токенов в fill: ~{tokens_per_fill}")
        print(f"  Всего токенов истории: {history_tokens}")
        print(f"  Лимит: {limit['total']} / {limit['max']} ({limit['percent']}%)")
        
        if limit['overflow']:
            print(f"\n  ⚠️ ПРЕВЫШЕН ЛИМИТ!")
            print(f"  Ошибка будет при отправке запроса!")
            break
    
    print("\n" + "=" * 60)
    print("Проверка: отправляем минимальный запрос")
    print("=" * 60)
    
    request_tokens = get_request_tokens("привет", model)
    limit = check_token_limit(history_tokens, request_tokens, model)
    
    print(f"  История: {history_tokens}")
    print(f"  Запрос: {request_tokens}")
    print(f"  Всего: {limit['total']}")
    print(f"  Лимит: {limit['total']} / {limit['max']} ({limit['percent']}%)")
    
    if limit['overflow']:
        print(f"\n  ⚠️ ОШИБКА: Превышен лимит!")
    else:
        print(f"\n  ✅ Запрос может быть отправлен")

if __name__ == "__main__":
    test_fill_simulation()
