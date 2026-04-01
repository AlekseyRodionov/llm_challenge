"""Generator module for LLM answer generation with user context."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm

MAX_CONTEXT_LENGTH = 5000


def build_context(chunks: list, max_len: int = MAX_CONTEXT_LENGTH) -> str:
    context = ""
    
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        if not text:
            continue
        
        chunk_text = f"[{i+1}] {text}"
        
        if len(context) + len(chunk_text) + 1 > max_len:
            break
            
        context += chunk_text + "\n"
    
    return context.strip()


def generate_support_answer(question: str, user: dict, ticket: dict, chunks: list) -> dict:
    """Генерация ответа с учётом контекста пользователя."""
    
    user_context = ""
    if user:
        user_context = f"""[ПОЛЬЗОВАТЕЛЬ]
Имя: {user.get('name', 'Unknown')}
Email: {user.get('email', 'Unknown')}
Статус: {user.get('status', 'Unknown')}
"""
    
    ticket_context = ""
    if ticket:
        ticket_context = f"""[ТИКЕТ]
Проблема: {ticket.get('issue', 'Unknown')}
Попыток входа: {ticket.get('attempts', 0)}
Статус тикета: {ticket.get('status', 'Unknown')}
"""
    
    doc_context = build_context(chunks)
    
    prompt = f"""Ты — AI ассистент поддержки пользователей.

Используй предоставленную документацию как основу.
Учитывай данные пользователя и тикета.
Если в документации нет точного ответа - используй свои знания о системе.

{user_context}
{ticket_context}

[ДОКУМЕНТАЦИЯ]
{doc_context}

Вопрос:
{question}

Ответ (1-2 предложения):"""
    
    result = ask_llm(prompt=prompt)
    result["chunks_used"] = len(chunks)
    
    return result
