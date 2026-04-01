"""Retriever module for FAISS vector search."""
import os
import sys
import requests
import numpy as np
import faiss
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR = os.path.join(PROJECT_ROOT, "index")

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"


class Retriever:
    """Retriever for FAQ using FAISS + Ollama embeddings."""
    
    def __init__(self, index_path=None, metadata_path=None):
        self.index_path = index_path or os.path.join(INDEX_DIR, "index.faiss")
        self.metadata_path = metadata_path or os.path.join(INDEX_DIR, "metadata.json")
        
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"Index not found: {self.index_path}. Run project_indexer first.")
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata not found: {self.metadata_path}. Run project_indexer first.")
        
        self.index = faiss.read_index(self.index_path)
        
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
    
    def embed_query(self, query: str) -> np.ndarray:
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
                raise Exception(f"Ollama error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama. Is it running?")
    
    def retrieve(self, query: str, k: int = 3) -> list:
        query_embedding = self.embed_query(query)
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        
        return results


def create_retriever():
    """Factory function to create retriever."""
    return Retriever()
