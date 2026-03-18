"""Retriever module for FAISS vector search with filtering."""
import os
import sys
import requests
import numpy as np
import faiss


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR = os.path.join(PROJECT_ROOT, "index")

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"

INITIAL_TOP_K = 5
FINAL_TOP_K = 2
MAX_DISTANCE = 300.0


class Retriever:
    """Retriever for FAISS vector search using Ollama embeddings."""
    
    def __init__(self, index_path=None, metadata_path=None):
        """
        Initialize retriever with FAISS index and metadata.
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSON file
        """
        self.index_path = index_path or os.path.join(INDEX_DIR, "faiss_fixed.index")
        self.metadata_path = metadata_path or os.path.join(INDEX_DIR, "metadata_fixed.json")
        
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Index not found: {self.index_path}. Run indexing first.")
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata not found: {self.metadata_path}. Run indexing first.")
        
        self.index = faiss.read_index(self.index_path)
        
        import json
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for query using Ollama API.
        
        Args:
            query: User query string
            
        Returns:
            Query embedding as numpy array
        """
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": query},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = np.array(data.get("embedding", []), dtype='float32')
                return embedding.reshape(1, -1)
            else:
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Is it running?")
    
    def retrieve(self, query: str, k: int = INITIAL_TOP_K) -> list:
        """
        Retrieve top-k relevant chunks for query with distance scores.
        
        Args:
            query: User query
            k: Number of chunks to retrieve (default: INITIAL_TOP_K=5)
            
        Returns:
            List of relevant chunks with metadata and distance score
        """
        query_embedding = self.embed_query(query)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.metadata):
                chunk = self.metadata[idx].copy()
                chunk["score"] = float(distances[0][i])
                results.append(chunk)
        
        return results


def filter_chunks(chunks: list, max_distance: float = MAX_DISTANCE, top_k: int = FINAL_TOP_K) -> list:
    """
    Filter chunks by distance threshold and return top-k.
    
    Args:
        chunks: List of chunks with score (distance)
        max_distance: Maximum distance threshold (smaller = better)
        top_k: Number of chunks to return
        
    Returns:
        Filtered and sorted list of chunks
    """
    if not chunks:
        return []
    
    filtered = [c for c in chunks if c.get("score", float("inf")) <= max_distance]
    
    if not filtered:
        return chunks[:top_k]
    
    sorted_chunks = sorted(filtered, key=lambda x: x.get("score", float("inf")))
    
    return sorted_chunks[:top_k]


def create_retriever():
    """Factory function to create retriever."""
    return Retriever()
