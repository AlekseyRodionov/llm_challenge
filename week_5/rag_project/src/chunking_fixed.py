"""Fixed size chunking module."""
from typing import List, Dict


CHUNK_SIZE = 500
OVERLAP = 50


def fixed_chunking(documents: List[Dict[str, str]], 
                   chunk_size: int = CHUNK_SIZE, 
                   overlap: int = OVERLAP) -> List[Dict[str, str]]:
    """
    Split documents into fixed-size chunks.
    
    Args:
        documents: List of documents with 'text' and 'source' keys
        chunk_size: Size of each chunk in characters
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of chunks, each containing:
        - chunk_id: unique identifier
        - text: chunk content
        - source: source filename
        - strategy: 'fixed'
    """
    chunks = []
    chunk_id = 0
    
    for doc in documents:
        text = doc["text"]
        source = doc["source"]
        
        # Split by chunk_size with overlap
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "chunk_id": f"fixed_{chunk_id}",
                "text": chunk_text,
                "source": source,
                "strategy": "fixed"
            })
            
            chunk_id += 1
            start += chunk_size - overlap
    
    return chunks
