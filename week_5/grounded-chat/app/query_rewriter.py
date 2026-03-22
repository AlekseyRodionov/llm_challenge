"""Query rewriter module - improves questions for better retrieval with smart context."""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm


SHORT_QUERY_THRESHOLD = 5


REWRITE_PROMPT_SIMPLE = """You are helping improve search queries for a technical documentation RAG system.

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


REWRITE_PROMPT_WITH_CONTEXT = """You are helping improve search queries for a technical documentation RAG system.

Given a user question AND the conversation context, rewrite the question to be more specific for retrieval.

IMPORTANT:
- The documentation is in English
- User questions are in Russian or English
- Use the Goal and Constraints to understand the context

TASK CONTEXT:
Goal: {goal}
Constraints: {constraints}

Your task:
1. Combine the short question with the goal and constraints
2. Add English technical terms from the documentation
3. Make the rewritten query specific and search-friendly

Examples:
- Q: "Как настроить?" + Goal: "Хочу задеплоить MkDocs" + Constraints: ["На GitHub Pages"]
  → "How to configure MkDocs deployment to GitHub Pages?"

- Q: "Как запускать?" + Goal: "Хочу CLI" + Constraints: ["На Python"]
  → "How to run Python CLI applications?"

Question:
{question}

Rewritten question:"""


def rewrite_query(question: str, llm_client=None, task_state: dict = None) -> tuple:
    """
    Rewrite question to be more specific for retrieval.
    
    Uses smart context-aware rewriting for short questions.
    
    Args:
        question: Original question
        llm_client: LLM client (optional)
        task_state: Task state with goal, constraints (optional)
        
    Returns:
        Tuple of (rewritten_question, context_used)
    """
    word_count = len(question.split())
    use_context = (
        task_state is not None and 
        word_count < SHORT_QUERY_THRESHOLD and 
        (task_state.get("goal") or task_state.get("constraints"))
    )
    
    if use_context:
        goal = task_state.get("goal", "")
        constraints = task_state.get("constraints", [])
        constraints_str = ", ".join(constraints) if constraints else "None"
        
        prompt = REWRITE_PROMPT_WITH_CONTEXT.format(
            goal=goal or "None",
            constraints=constraints_str,
            question=question
        )
        context_used = True
    else:
        prompt = REWRITE_PROMPT_SIMPLE.format(question=question)
        context_used = False
    
    result = ask_llm(prompt=prompt)
    rewritten = result.get("text", question).strip()
    
    return rewritten, context_used
