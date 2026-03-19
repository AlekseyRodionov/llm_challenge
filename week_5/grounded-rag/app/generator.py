"""Generator module for LLM answer generation with Sources and Quotes."""
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
    Format includes chunk_id for source tracking.
    
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
        chunk_text = f"[Chunk {chunk_id} | Source: {source} | Section: {section}]\n{text}\n---\n"
        
        if len(context) + len(chunk_text) > max_len:
            break
        context += chunk_text
    
    return context.strip()


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


PROMPT_TEMPLATE = """You are a QA assistant working with retrieved documentation.

Rules:
- Use the provided context to answer the question.
- Do NOT use prior knowledge.
- If the context is completely unrelated, say: "I don't know".

Return EXACTLY in this format. Do not add anything else.

Answer:
<your answer>

Sources:
- <source | section | chunk_id>

Quotes:
1. "<exact quote from context>"
2. "<exact quote from context>"

Context:
{context}

Question:
{question}"""


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
    Returns structured response with Answer, Sources, and Quotes.
    
    Args:
        question: User question
        chunks: Retrieved chunks from retriever
        llm_client: LLM client (optional, uses default)
        
    Returns:
        Dict with answer, sources, quotes and metrics
    """
    context = build_context(chunks)
    
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
