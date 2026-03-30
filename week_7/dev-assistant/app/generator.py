"""Generator module for LLM answer generation."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm


MAX_CONTEXT_LENGTH = 10000


def build_full_context(branch: str, files: str, chunks: list, max_len: int = None) -> str:
    """Build full context with MCP data and document chunks."""
    if max_len is None:
        max_len = MAX_CONTEXT_LENGTH
    doc_context = build_context(chunks, max_len)
    
    return f"""[PROJECT CONTEXT]
Branch: {branch}

Files:
{files}

[DOCUMENT CONTEXT]
{doc_context}"""


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
        
        chunk_text = f"[{i+1}] {text}"
        
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
    prompt = f"Answer the question:\n\n{question}"
    
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
    
    prompt = f"""Use the context below to answer the question.

Context:
{context}

Question:
{question}

Answer:"""
    
    result = ask_llm(prompt=prompt)
    result["mode"] = "with_rag"
    result["chunks_used"] = len(chunks)
    result["context_length"] = len(context)
    
    return result


DEV_ASSISTANT_PROMPT = """Answer the question based on the context below.

Context:
{context}

Question:
{question}

Answer:"""


def generate_dev_answer(question: str, branch: str, files: str, chunks: list) -> dict:
    """Generate answer for Dev Assistant using MCP + RAG context."""
    context = build_full_context(branch, files, chunks)
    
    prompt = DEV_ASSISTANT_PROMPT.format(context=context, question=question)
    
    result = ask_llm(prompt=prompt)
    result["mode"] = "dev_assistant"
    result["chunks_used"] = len(chunks)
    
    sources = list(set(c.get("source", "unknown") for c in chunks))
    result["sources"] = sources if sources else ["НЕТ"]
    
    return result
