"""Generator module for LLM answer generation."""
import os
import sys

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
        chunk_text = f"[Source: {source} | Section: {section}]\n{text}\n---"
        
        if len(context) + len(chunk_text) + 1 > max_len:
            break
            
        context += chunk_text + "\n"
    
    return context.strip()


def generate_answer(question: str, llm_client=None) -> dict:
    """
    Generate answer without RAG (direct LLM query).
    
    Args:
        question: User question
        llm_client: LLM client (optional, uses default)
        
    Returns:
        Dict with answer and metrics
    """
    prompt = f"Ответьте на вопрос:\n\n{question}"
    
    result = ask_llm(prompt=prompt)
    result["mode"] = "without_rag"
    
    return result


def generate_answer_with_context(question: str, chunks: list, llm_client=None) -> dict:
    """
    Generate answer with RAG (using retrieved chunks as context).
    
    Args:
        question: User question
        chunks: Retrieved chunks from retriever
        llm_client: LLM client (optional, uses default)
        
    Returns:
        Dict with answer and metrics
    """
    context = build_context(chunks)
    
    prompt = f"""Используйте контекст ниже для ответа на вопрос.

Контекст:
{context}

Вопрос:
{question}

Ответ:"""
    
    result = ask_llm(prompt=prompt)
    result["mode"] = "with_rag"
    result["chunks_used"] = len(chunks)
    result["context_length"] = len(context)
    
    return result
