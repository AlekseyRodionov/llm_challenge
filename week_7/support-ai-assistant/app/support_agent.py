"""Support Agent - главный модуль для ответов на вопросы пользователей."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from retriever import Retriever
from generator import generate_support_answer
from user_context import get_user, get_user_ticket


def answer(user_id: int, question: str) -> str:
    """Главная функция - дать ответ на вопрос пользователя.
    
    Args:
        user_id: ID пользователя
        question: Вопрос пользователя
    
    Returns:
        Ответ ассистента
    """
    user = get_user(user_id)
    ticket = get_user_ticket(user_id)
    
    retriever = Retriever()
    chunks = retriever.retrieve(question, k=3)
    
    result = generate_support_answer(question, user, ticket, chunks)
    return result["text"]
