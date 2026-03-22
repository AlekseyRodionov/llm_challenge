"""Chat Agent with RAG, memory, task state and logging."""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from llm_client import ask_llm
from retriever import create_retriever, INITIAL_TOP_K, MAX_DISTANCE, FINAL_TOP_K, filter_chunks
from generator import generate_answer_with_context
from query_rewriter import rewrite_query
from logger import log_event


HISTORY_LIMIT = 5
MAX_KNOWN_FACTS = 3
PREPOSITIONS = ["на ", "с ", "для ", "в ", "к "]
MIN_WORD_LEN = 3


class Agent:
    """
    Chat agent with RAG, task state memory, dialog history and logging.
    
    Pipeline:
    User Input → Update Task State → Query Rewrite → Retrieval → Filter → 
    Context Builder (task_state + history + chunks) → LLM → Parse → Output + Logs
    """
    
    def __init__(self, model: str = None, temperature: float = 0.7,
                 rag_enabled: bool = True, use_filter: bool = False, use_rewrite: bool = False,
                 debug_mode: bool = False):
        """
        Initialize agent.
        
        Args:
            model: LLM model name
            temperature: Temperature parameter (0-2)
            rag_enabled: Enable RAG mode
            use_filter: Enable distance filtering
            use_rewrite: Enable query rewrite
            debug_mode: Enable debug console output
        """
        self.model = model
        self.temperature = temperature
        self.rag_enabled = rag_enabled
        self.use_filter = use_filter
        self.use_rewrite = use_rewrite
        self.debug_mode = debug_mode
        
        self.messages = []
        self._add_system_prompt()
        
        self.history = []
        self.task_state = {
            "goal": "",
            "constraints": [],
            "known_facts": []
        }
        
        self.retriever = None
        if self.rag_enabled:
            self._init_retriever()
    
    def _add_system_prompt(self):
        """Add system prompt to message history."""
        self.messages.append({
            "role": "system",
            "content": "Ты полезный AI помощник. Отвечай ТОЛЬКО на русском языке."
        })
    
    def _init_retriever(self):
        """Initialize retriever for RAG."""
        try:
            self.retriever = create_retriever()
        except Exception as e:
            print(f"Warning: Could not initialize retriever: {e}")
            self.retriever = None
    
    def update_task_state(self, question: str):
        """
        Update task state based on question (rule-based).
        
        Rules:
        - "хочу" in question → goal (with reset)
        - PREPOSITIONS in question → constraints
        - len(question.split()) < 6 → known_facts (capped to MAX_KNOWN_FACTS)
        """
        q_lower = question.lower()
        
        if "хочу" in q_lower:
            self.task_state["goal"] = question
            self.task_state["constraints"] = []
            self.task_state["known_facts"] = []
        
        for prep in PREPOSITIONS:
            if prep in q_lower and len(question.split()) > 2:
                words = question.split()
                relevant_words = [w for w in words if len(w) >= MIN_WORD_LEN]
                if relevant_words and question not in self.task_state["constraints"]:
                    self.task_state["constraints"].append(question)
                break
        
        if len(question.split()) < 6:
            if question not in self.task_state["known_facts"]:
                self.task_state["known_facts"].append(question)
            
            if len(self.task_state["known_facts"]) > MAX_KNOWN_FACTS:
                self.task_state["known_facts"] = self.task_state["known_facts"][-MAX_KNOWN_FACTS:]
    
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
    
    def toggle_debug(self):
        """Toggle debug mode."""
        self.debug_mode = not self.debug_mode
        return self.debug_mode
    
    def reset(self):
        """Reset history and task state."""
        self.history = []
        self.task_state = {
            "goal": "",
            "constraints": [],
            "known_facts": []
        }
        self.messages = []
        self._add_system_prompt()
    
    def ask(self, question: str) -> dict:
        """
        Ask question to agent with full pipeline.
        
        Args:
            question: User question
            
        Returns:
            Dict with answer, sources, quotes and metrics
        """
        original_question = question
        
        log_data = {
            "question": question,
            "rewritten_query": None,
            "rewrite_context_used": False,
            "task_state": self.task_state.copy(),
            "retrieval": {
                "top_k": INITIAL_TOP_K,
                "distances": [],
                "chunks_found": 0
            },
            "filter": {
                "before": 0,
                "after": 0,
                "fallback_used": False
            },
            "context": {
                "history_used": 0,
                "context_chars": 0
            },
            "generation": {
                "raw_response": None,
                "parsed": None
            },
            "result": {
                "fallback": False,
                "has_sources": False,
                "has_quotes": False
            }
        }
        
        self.update_task_state(question)
        log_data["task_state"] = self.task_state.copy()
        
        if not self.rag_enabled:
            result = generate_answer_with_context(question, [])
            result["retrieved_chunks"] = []
            result["mode"] = "without_rag"
            return result
        
        if not self.retriever:
            raise Exception("RAG is enabled but retriever is not initialized.")
        
        query = question
        if self.use_rewrite:
            rewritten, context_used = rewrite_query(question, task_state=self.task_state)
            query = rewritten
            log_data["rewritten_query"] = rewritten
            log_data["rewrite_context_used"] = context_used
            if self.debug_mode:
                ctx_marker = "[CTX]" if context_used else ""
                print(f"[DEBUG] {ctx_marker} Rewritten: {rewritten}")
        
        chunks = self.retriever.retrieve(query, k=INITIAL_TOP_K)
        log_data["retrieval"]["distances"] = [c["score"] for c in chunks]
        log_data["retrieval"]["chunks_found"] = len(chunks)
        
        if self.debug_mode:
            print(f"[DEBUG] Retrieved {len(chunks)} chunks, distances: {[f'{d:.1f}' for d in log_data['retrieval']['distances'][:5]]}")
        
        log_data["filter"]["before"] = len(chunks)
        
        if self.use_filter:
            filtered, final_top_k, best_distance = filter_chunks(chunks, max_distance=MAX_DISTANCE, top_k=FINAL_TOP_K)
            chunks = filtered
        else:
            chunks = chunks[:FINAL_TOP_K]
            final_top_k = FINAL_TOP_K
            best_distance = chunks[0]["score"] if chunks else float("inf")
        
        log_data["filter"]["after"] = len(chunks)
        log_data["final_top_k_used"] = final_top_k
        log_data["best_distance"] = round(best_distance, 2)
        
        if best_distance < 220:
            log_data["retrieval_quality"] = "high"
        elif best_distance < 260:
            log_data["retrieval_quality"] = "medium"
        else:
            log_data["retrieval_quality"] = "low"
        
        if not chunks and self.use_filter:
            log_data["filter"]["fallback_used"] = True
            chunks = chunks[:FINAL_TOP_K] if chunks else []
        
        result = generate_answer_with_context(
            original_question, 
            chunks,
            task_state=self.task_state,
            history=self.history[-HISTORY_LIMIT:]
        )
        
        log_data["context"]["history_used"] = min(len(self.history), HISTORY_LIMIT)
        log_data["context"]["context_chars"] = result.get("context_length", 0)
        
        log_data["generation"]["raw_response"] = result.get("raw_response", "")[:500]
        log_data["generation"]["parsed"] = "answer" in result
        
        log_data["result"]["fallback"] = result.get("fallback", False)
        log_data["result"]["has_sources"] = "sources" in result
        log_data["result"]["has_quotes"] = "quotes" in result
        
        result["retrieved_chunks"] = chunks
        
        if "text" in result:
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": result["text"]})
        
        if self.debug_mode:
            print(f"[DEBUG] Result: fallback={result.get('fallback')}, sources={log_data['result']['has_sources']}")
        
        log_event(log_data)
        
        return result
    
    def get_history(self) -> list:
        """Get copy of history."""
        return self.history.copy()
    
    def get_task_state(self) -> dict:
        """Get copy of task state."""
        return self.task_state.copy()
    
    def get_status(self) -> dict:
        """Get agent status."""
        return {
            "rag_enabled": self.rag_enabled,
            "use_filter": self.use_filter,
            "use_rewrite": self.use_rewrite,
            "retriever_loaded": self.retriever is not None,
            "model": self.model,
            "temperature": self.temperature,
            "debug_mode": self.debug_mode,
            "history_size": len(self.history),
            "task_state": self.task_state
        }
