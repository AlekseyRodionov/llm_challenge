"""RAG Agent - extends simp-agent with RAG capabilities."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm
from retriever import create_retriever
from generator import generate_answer, generate_answer_with_context


class Agent:
    """
    LLM agent with optional RAG support.
    
    Supports two modes:
    - Without RAG: direct LLM query
    - With RAG: retrieve relevant chunks + LLM query
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7, rag_enabled: bool = False):
        """
        Initialize agent.
        
        Args:
            model: LLM model name
            temperature: Temperature parameter (0-2)
            rag_enabled: Enable RAG mode
        """
        self.model = model
        self.temperature = temperature
        self.rag_enabled = rag_enabled
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
    
    def ask(self, question: str) -> dict:
        """
        Ask question to agent.
        
        Args:
            question: User question
            
        Returns:
            Dict with answer and metrics
        """
        if not self.rag_enabled:
            result = generate_answer(question)
        else:
            if not self.retriever:
                raise Exception("RAG is enabled but retriever is not initialized. Run indexing first.")
            
            chunks = self.retriever.retrieve(question, k=3)
            result = generate_answer_with_context(question, chunks)
            
            result["retrieved_chunks"] = chunks
        
        self.messages.append({"role": "user", "content": question})
        self.messages.append({"role": "assistant", "content": result["text"]})
        
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
            "retriever_loaded": self.retriever is not None,
            "model": self.model,
            "temperature": self.temperature
        }
