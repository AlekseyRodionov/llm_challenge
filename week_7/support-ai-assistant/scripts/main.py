#!/usr/bin/env python3
"""Support AI Assistant - main script."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.support_agent import answer
from app.user_context import get_user, get_user_ticket


def show_context(user_id):
    """Показать контекст текущего пользователя."""
    user = get_user(user_id)
    ticket = get_user_ticket(user_id)
    
    status_emoji = "🔴" if user and user.get("status") == "blocked" else "🟢"
    status_text = user.get("status", "unknown") if user else "unknown"
    name = user.get("name", "Unknown") if user else "Unknown"
    
    print(f"{status_emoji} Пользователь: {name} ({status_text})")
    if ticket:
        print(f"📋 Тикет: {ticket.get('issue', 'N/A')}, {ticket.get('attempts', 0)} попыток")
    else:
        print("📋 Тикет: нет")


def demo_mode():
    """Демо режим - 10 тестовых сценариев со связанным диалогом."""
    print("=" * 60)
    print("Support AI Assistant - Demo Mode (10 вопросов)")
    print("=" * 60)
    print()
    
    tests = [
        # Блок 1: user_id=1 (заблокированный)
        {"user_id": 1, "question": "Почему не работает авторизация?", "desc": "Первый вопрос"},
        {"user_id": 1, "question": "Как исправить?", "desc": "Продолжение"},
        
        # Блок 2: user_id=2 (активный)
        {"user_id": 2, "question": "Как сбросить пароль?", "desc": "Смена пользователя"},
        {"user_id": 2, "question": "Что делать если письмо не приходит?", "desc": "Продолжение"},
        
        # Блок 3: user_id=1 (снова заблокированный)
        {"user_id": 1, "question": "Почему аккаунт заблокирован?", "desc": "Возврат к заблокированному"},
        {"user_id": 1, "question": "Это надолго?", "desc": "Продолжение"},
        
        # Блок 4: user_id=3 (активный с тикетом)
        {"user_id": 3, "question": "Что с моим аккаунтом?", "desc": "Новый пользователь"},
        {"user_id": 3, "question": "Как восстановить доступ?", "desc": "Продолжение"},
        
        # Блок 5: user_id=2 (финал)
        {"user_id": 2, "question": "Безопасно ли хранить данные?", "desc": "Смена пользователя"},
        {"user_id": 2, "question": "Спасибо!", "desc": "Завершение"},
    ]
    
    for i, test in enumerate(tests, 1):
        user = get_user(test["user_id"])
        status_emoji = "🔴" if user and user.get("status") == "blocked" else "🟢"
        
        print(f"[{i}/10] user_id={test['user_id']} {status_emoji}")
        print(f"Вопрос: {test['question']}")
        
        result = answer(test["user_id"], test["question"])
        print(f"Ответ: {result}")
        print()


def cli_mode():
    """Ручной режим - задаём вопросы."""
    print("=" * 50)
    print("Support AI Assistant")
    print("=" * 50)
    print("Доступные команды:")
    print("  /user <id> - сменить пользователя (1, 2, 3)")
    print("  /info      - показать контекст пользователя")
    print("  /help      - показать примеры вопросов")
    print("  exit       - выход")
    print("=" * 50)
    
    user_id = input("user_id: ")
    
    # Обработка команды /user в начале (может быть /user 1 или /user1)
    user_id_stripped = user_id.strip()
    if user_id_stripped.startswith("/user") and len(user_id_stripped) > 5:
        # /user 1 или /user1
        parts = user_id_stripped.split()
        if len(parts) >= 2:
            new_id = parts[1]
        else:
            new_id = user_id_stripped[5:]  # /user1 без пробела
        
        if new_id.isdigit():
            user_id = int(new_id)
            print(f"Сменили пользователя: user_id={user_id}")
        else:
            print("Неверный user_id")
            return
    elif user_id.isdigit():
        user_id = int(user_id)
    else:
        print("Неверный user_id")
        return
    
    questions = [
        "Почему не работает авторизация?",
        "Как сбросить пароль?",
        "Почему аккаунт заблокирован?",
        "Что делать при ошибке входа?",
        "Как изменить пароль?",
        "Безопасно ли хранить мои данные?",
    ]
    
    while True:
        print()
        show_context(user_id)
        question = input("Вопрос (exit для выхода): ")
        if question.lower() in ["exit", "quit"]:
            break
        
        # Команда смены пользователя (/user 1 или /user1)
        if question.strip().startswith("/user"):
            q = question.strip()
            parts = q.split()
            if len(parts) >= 2:
                new_id = parts[1]
            else:
                new_id = q[5:]  # /user1 без пробела
            
            if new_id.isdigit():
                user_id = int(new_id)
                print(f"Сменили пользователя: user_id={user_id}")
            else:
                print("Неверный user_id")
            continue
        
        # Команда показа контекста
        if question.strip() == "/info":
            show_context(user_id)
            continue
        
        # Команда помощи
        if question.strip() == "/help":
            print("\nПримеры вопросов:")
            for q in questions:
                print(f"  - {q}")
            continue
        
        if not question.strip():
            continue
        
        result = answer(user_id, question)
        print(f"\nОтвет: {result}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        cli_mode()


if __name__ == "__main__":
    main()
