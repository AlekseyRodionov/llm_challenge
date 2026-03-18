"""RAG Agent - extends simp-agent with RAG capabilities, filtering and query rewrite."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm
from retriever import create_retriever, INITIAL_TOP_K, MAX_DISTANCE, FINAL_TOP_K, filter_chunks
from generator import generate_answer, generate_answer_with_context
from query_rewriter import rewrite_query


class Agent:
    """
    LLM agent with optional RAG, filtering and query rewrite support.
    
    Supports modes:
    - Without RAG: direct LLM query
    - With RAG: retrieval + optional filter + optional rewrite
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7, 
                 rag_enabled: bool = True, use_filter: bool = False, use_rewrite: bool = False):
        """
        Initialize agent.
        
        Args:
            model: LLM model name
            temperature: Temperature parameter (0-2)
            rag_enabled: Enable RAG mode
            use_filter: Enable distance filtering
            use_rewrite: Enable query rewrite
        """
        self.model = model
        self.temperature = temperature
        self.rag_enabled = rag_enabled
        self.use_filter = use_filter
        self.use_rewrite = use_rewrite
        self.messages = []
        self._add_system_prompt()
        
        self.retriever = None
        if self.rag_enabled:
            self._init_retriever()
    
    def _add_system_prompt(self):
        """Add system prompt to message history."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник."
        })
    
    def _init_retriever(self):
        """Initialize retriever for RAG."""
        try:
            self.retriever = create_retriever()
        except Exception as e:
            print(f"Warning: Could not initialize retriever: {e}")
            self.retriever = None
    
    def enable_rag(self):
        """Enable RAG mode."""
        self.rag_enabled = True
        if not self.retriever:
            self._init_retriever()
    
    def disable_rag(self):
        """Disable RAG mode."""
        self.rag_enabled = False
    
    def enable_filter(self):
        """Enable distance filtering."""
        self.use_filter = True
    
    def disable_filter(self):
        """Disable distance filtering."""
        self.use_filter = False
    
    def enable_rewrite(self):
        """Enable query rewrite."""
        self.use_rewrite = True
    
    def disable_rewrite(self):
        """Disable query rewrite."""
        self.use_rewrite = False
    
    def ask(self, question: str) -> dict:
        """
        Ask question to agent.
        
        Args:
            question: User question
            
        Returns:
            Dict with answer and metrics
        """
        original_question = question
        
        if not self.rag_enabled:
            result = generate_answer(question)
            result["retrieved_chunks"] = []
            return result
        
        if not self.retriever:
            raise Exception("RAG is enabled but retriever is not initialized. Run indexing first.")
        
        query = question
        if self.use_rewrite:
            rewritten = rewrite_query(question)
            # print(f"\033[90m[rewrite] {rewritten}\033[0m")
            query = rewritten
        
        chunks = self.retriever.retrieve(query, k=INITIAL_TOP_K)
        # distances = [c.get("score", -1) for c in chunks]
        # print(f"\033[90m[retrieval] found: {len(chunks)}, distances: {[f'{d:.3f}' for d in distances]}\033[0m")
        
        if self.use_filter:
            filtered = filter_chunks(chunks, max_distance=MAX_DISTANCE, top_k=FINAL_TOP_K)
            # filtered_distances = [c.get("score", -1) for c in filtered]
            # print(f"\033[90m[filter] threshold={MAX_DISTANCE}, before={len(chunks)}, after={len(filtered)}, kept={[f'{d:.3f}' for d in filtered_distances]}\033[0m")
            chunks = filtered
        else:
            chunks = chunks[:FINAL_TOP_K]
        
        result = generate_answer_with_context(original_question, chunks)
        result["retrieved_chunks"] = chunks
        
        return result
    
    def reset_history(self):
        """Clear message history, keep system prompt."""
        self.messages = []
        self._add_system_prompt()
    
    def get_history(self) -> list:
        """Get copy of message history."""
        return self.messages.copy()
    
    def get_status(self) -> dict:
        """Get agent status."""
        return {
            "rag_enabled": self.rag_enabled,
            "use_filter": self.use_filter,
            "use_rewrite": self.use_rewrite,
            "retriever_loaded": self.retriever is not None,
            "model": self.model,
            "temperature": self.temperature
        }
