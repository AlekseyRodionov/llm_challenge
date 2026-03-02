"""
Модуль для сжатия контекста через summarization.
Создает summary из старых сообщений и оставляет N последних.
"""
from app.llm_client import ask_llm, count_messages_tokens

SUMMARY_SYSTEM_PROMPT = """Ты - ассистент для создания кратких резюме диалогов.
Создай краткое резюме (2-3 предложения) предыдущего диалога.
Включи ключевые темы, вопросы пользователя и важные детали.
Не используй список - только связный текст."""


def create_summary(messages: list, model: str = None) -> str:
    """
    Создает summary из списка сообщений (без system).
    """
    if not messages:
        return ""
    
    user_messages = [m for m in messages if m.get("role") != "system"]
    
    if not user_messages:
        return ""
    
    conversation = ""
    for msg in user_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        conversation += f"{role}: {content}\n"
    
    summary_request = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Создай краткое резюме этого диалога:\n\n{conversation}"}
    ]
    
    result = ask_llm(
        prompt="Создай краткое резюме диалога",
        model=model,
        temperature=0.3,
        messages=summary_request
    )
    
    return result["text"]


def format_summary_message(summary: str) -> dict:
    """
    Форматирует summary в виде сообщения для контекста.
    """
    return {
        "role": "system",
        "content": f"[Краткое содержание предыдущего диалога]: {summary}"
    }


def compress_context(
    messages: list,
    keep_last: int = 5,
    compress_threshold: int = 10,
    model: str = None,
    existing_summary: str = None
) -> tuple[list, str]:
    """
    Сжимает контекст: оставляет N последних сообщений, остальное заменяет summary.
    
    Returns:
        Кортеж: (новый список сообщений, новое summary)
    """
    user_messages = [m for m in messages if m.get("role") != "system"]
    
    if len(user_messages) <= compress_threshold:
        return messages, existing_summary or ""
    
    older_messages = user_messages[:-keep_last]
    last_messages = user_messages[-keep_last:]
    
    if existing_summary:
        older_messages_for_summary = [{"role": "system", "content": f"[Предыдущее summary]: {existing_summary}"}] + older_messages
    else:
        older_messages_for_summary = older_messages
    
    new_summary = create_summary(older_messages_for_summary, model)
    
    new_messages = [
        {"role": "system", "content": "Ты полезный AI помощник."},
        format_summary_message(new_summary)
    ]
    new_messages.extend(last_messages)
    
    return new_messages, new_summary


def get_context_stats(messages: list, model: str) -> dict:
    """
    Возвращает статистику по контексту.
    """
    user_messages = [m for m in messages if m.get("role") != "system"]
    system_messages = [m for m in messages if m.get("role") == "system"]
    
    has_summary = any("[Краткое содержание" in m.get("content", "") for m in system_messages)
    
    return {
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "system_messages": len(system_messages),
        "total_tokens": count_messages_tokens(messages, model),
        "has_summary": has_summary
    }
