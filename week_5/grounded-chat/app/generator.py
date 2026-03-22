"""Generator module for LLM answer generation with Sources, Quotes, task state and history."""
import os
import sys
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm


MAX_CONTEXT_LENGTH = 2000


def build_context(chunks: list, max_len: int = MAX_CONTEXT_LENGTH) -> str:
    """
    Build context from retrieved chunks with length limit.
    
    Args:
        chunks: List of retrieved chunks
        max_len: Maximum context length in characters
        
    Returns:
        Combined context string
    """
    context = ""
    
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        if not text:
            continue
        
        source = chunk.get("source", "unknown")
        section = chunk.get("section", i + 1)
        chunk_id = chunk.get("chunk_id", i)
        chunk_text = f"[Source: {source} | Section: {section} | Chunk: {chunk_id}]\n{text}\n---\n"
        
        if len(context) + len(chunk_text) > max_len:
            break
        context += chunk_text
    
    return context.strip()


def build_history_section(history: list, max_len: int = 500) -> str:
    """
    Build history section from dialog history.
    
    Args:
        history: List of history entries
        max_len: Maximum length for history section
        
    Returns:
        Formatted history string
    """
    if not history:
        return "No previous messages."
    
    history_text = ""
    for entry in history:
        role = entry.get("role", "user")
        content = entry.get("content", "")
        
        if role == "user":
            history_text += f"User: {content}\n"
        else:
            history_text += f"Assistant: {content[:200]}...\n" if len(content) > 200 else f"Assistant: {content}\n"
    
    if len(history_text) > max_len:
        history_text = history_text[-max_len:]
    
    return history_text.strip()


def build_task_section(task_state: dict) -> str:
    """
    Build task section from task state.
    
    Args:
        task_state: Dictionary with goal, constraints, known_facts
        
    Returns:
        Formatted task string
    """
    lines = []
    
    goal = task_state.get("goal", "")
    if goal:
        lines.append(f"Goal: {goal}")
    else:
        lines.append("Goal: Not set")
    
    constraints = task_state.get("constraints", [])
    if constraints:
        lines.append("Constraints:")
        for c in constraints:
            lines.append(f"  - {c}")
    else:
        lines.append("Constraints: None")
    
    known_facts = task_state.get("known_facts", [])
    if known_facts:
        lines.append("Known facts:")
        for f in known_facts:
            lines.append(f"  - {f}")
    else:
        lines.append("Known facts: None")
    
    return "\n".join(lines)


def build_full_context(chunks: list, task_state: dict, history: list, max_len: int = MAX_CONTEXT_LENGTH) -> str:
    """
    Build full context including task state, history and chunks.
    
    Args:
        chunks: List of retrieved chunks
        task_state: Task state dictionary
        history: Dialog history list
        max_len: Maximum total context length
        
    Returns:
        Full context string
    """
    task_section = build_task_section(task_state)
    history_section = build_history_section(history)
    chunks_section = build_context(chunks, max_len=max_len)
    
    full_context = f"""TASK:
{task_section}

DIALOG HISTORY:
{history_section}

CONTEXT:
{chunks_section}"""
    
    return full_context.strip()


def parse_response(text: str) -> dict | None:
    """
    Parse LLM response with flexible regex + content validation.
    
    Args:
        text: Raw LLM response
        
    Returns:
        Dict with answer, sources, quotes or None if parsing fails
    """
    answer_match = re.search(r"Answer:\s*(.*?)\n+Sources:", text, re.DOTALL | re.IGNORECASE)
    sources_match = re.search(r"Sources:\s*(.*?)\n+Quotes:", text, re.DOTALL | re.IGNORECASE)
    quotes_match = re.search(r"Quotes:\s*(.*)", text, re.DOTALL | re.IGNORECASE)
    
    if not (answer_match and sources_match and quotes_match):
        return None
    
    answer = answer_match.group(1).strip()
    sources = sources_match.group(1).strip()
    quotes = quotes_match.group(1).strip()
    
    if not answer or len(answer) < 10:
        return None
    if not sources or len(sources) < 5:
        return None
    if not quotes or len(quotes) < 5:
        return None
    
    return {"answer": answer, "sources": sources, "quotes": quotes}


PROMPT_TEMPLATE = """You are a QA assistant that answers ONLY using the provided context.

CRITICAL: You MUST answer in RUSSIAN language. The user writes in Russian. Never answer in English.

Important:
- Use the provided TASK section to understand the user's goal
- Use the DIALOG HISTORY to maintain context
- Use the CONTEXT (chunks) to answer the question
- Do NOT use prior knowledge
- If the context is completely unrelated to the question, say: "I don't know"
- ALWAYS answer in RUSSIAN, even if the context is in English

Return EXACTLY in this format:

Answer:
<your answer>

Sources:
- <source | section | chunk_id>

Quotes:
1. "<exact quote from context>"
2. "<exact quote from context>"

{context}

Question:
{question}"""


def generate_answer_with_context(
    question: str, 
    chunks: list, 
    task_state: dict = None,
    history: list = None,
    llm_client=None
) -> dict:
    """
    Generate answer with RAG using task state, history and chunks.
    
    Args:
        question: User question
        chunks: Retrieved chunks from retriever
        task_state: Task state dictionary
        history: Dialog history list
        llm_client: LLM client (optional, uses default)
        
    Returns:
        Dict with answer, sources, quotes and metrics
    """
    if task_state is None:
        task_state = {"goal": "", "constraints": [], "known_facts": []}
    if history is None:
        history = []
    
    context = build_full_context(chunks, task_state, history)
    
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    
    raw_result = ask_llm(prompt=prompt)
    raw_text = raw_result.get("text", "")
    
    parsed = parse_response(raw_text)
    
    if parsed is None:
        result = {
            "text": "Не знаю. Уточните вопрос.",
            "mode": "with_rag",
            "chunks_used": len(chunks),
            "context_length": len(context),
            "input_tokens": raw_result.get("input_tokens", 0),
            "output_tokens": raw_result.get("output_tokens", 0),
            "total_tokens": raw_result.get("total_tokens", 0),
            "cost": raw_result.get("cost", 0),
            "raw_response": raw_text,
            "fallback": True
        }
    else:
        result = {
            "text": f"Answer:\n{parsed['answer']}\n\nSources:\n{parsed['sources']}\n\nQuotes:\n{parsed['quotes']}",
            "mode": "with_rag",
            "chunks_used": len(chunks),
            "context_length": len(context),
            "input_tokens": raw_result.get("input_tokens", 0),
            "output_tokens": raw_result.get("output_tokens", 0),
            "total_tokens": raw_result.get("total_tokens", 0),
            "cost": raw_result.get("cost", 0),
            "answer": parsed["answer"],
            "sources": parsed["sources"],
            "quotes": parsed["quotes"],
            "fallback": False
        }
    
    return result
