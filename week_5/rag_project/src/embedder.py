"""Embedder module for generating embeddings via Ollama API."""
import requests
from typing import List, Dict


OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"
MAX_TEXT_LENGTH = 4000  # Limit text length to avoid context overflow


def generate_embeddings(chunks: List[Dict[str, str]], 
                       model: str = MODEL_NAME) -> List[Dict[str, str]]:
    """
    Generate embeddings for chunks using Ollama API.
    
    Args:
        chunks: List of chunks with 'text' key
        model: Ollama model name for embeddings
        
    Returns:
        List of chunks with added 'embedding' key
    """
    chunks_with_embeddings = []
    
    for chunk in chunks:
        # Truncate text to avoid context overflow
        text = chunk["text"][:MAX_TEXT_LENGTH]
        
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": text
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data.get("embedding", [])
                chunk["embedding"] = embedding
            else:
                chunk["embedding"] = None
                print(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            chunk["embedding"] = None
            print("Error: Cannot connect to Ollama. Is it running?")
            raise
        except Exception as e:
            chunk["embedding"] = None
            print(f"Error generating embedding: {e}")
        
        chunks_with_embeddings.append(chunk)
    
    return chunks_with_embeddings
