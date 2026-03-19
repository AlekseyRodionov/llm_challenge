"""Query rewriter module - improves questions for better retrieval."""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm


REWRITE_PROMPT = """You are helping improve search queries for a technical documentation RAG system.

Given a user question, rewrite it to be more specific and search-friendly for retrieving relevant documentation chunks.

IMPORTANT: The documentation is in English, but the user may ask in Russian or English.

Your task:
1. If the question is in Russian, add English technical terms in parentheses
2. If the question is in English, keep it as is but add necessary context
3. Focus on adding domain-specific terminology

Examples:
- Russian: "Что такое Fire?" → "What is Fire (Python CLI library for command-line interfaces)?"
- Russian: "Как установить MkDocs?" → "How to install MkDocs (Python static site generator for documentation)?"
- English: "How to use Fire?" → "How to use Fire (Google Python CLI library)?"

Question:
{question}

Rewritten question:"""


def rewrite_query(question: str, llm_client=None) -> str:
    """
    Rewrite question to be more specific for retrieval.
    
    Args:
        question: Original question
        llm_client: LLM client (optional)
        
    Returns:
        Rewritten question string
    """
    prompt = REWRITE_PROMPT.format(question=question)
    
    result = ask_llm(prompt=prompt)
    
    return result.get("text", question).strip()
