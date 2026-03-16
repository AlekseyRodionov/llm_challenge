"""Index storage module using FAISS."""
import json
import numpy as np
import faiss
import os
from typing import List, Dict


def create_faiss_index(embeddings: List[List[float]]) -> faiss.Index:
    """
    Create FAISS index from embeddings.
    
    Args:
        embeddings: List of embedding vectors
        
    Returns:
        FAISS index
    """
    # Convert to numpy array
    vectors = np.array(embeddings).astype('float32')
    
    # Get dimension
    dimension = vectors.shape[1]
    
    # Create L2 (Euclidean) index
    index = faiss.IndexFlatL2(dimension)
    
    # Add vectors
    index.add(vectors)
    
    return index


def save_index(index: faiss.Index, index_path: str) -> None:
    """
    Save FAISS index to file.
    
    Args:
        index: FAISS index
        index_path: Path to save index
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    faiss.write_index(index, index_path)


def save_metadata(chunks: List[Dict[str, str]], metadata_path: str) -> None:
    """
    Save metadata for chunks to JSON.
    
    Args:
        chunks: List of chunks with metadata
        metadata_path: Path to save metadata
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    # Prepare metadata (without embeddings)
    metadata = []
    for chunk in chunks:
        meta = {
            "chunk_id": chunk.get("chunk_id"),
            "text": chunk.get("text"),
            "source": chunk.get("source"),
            "strategy": chunk.get("strategy"),
            "section": chunk.get("section", "")
        }
        metadata.append(meta)
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def load_index(index_path: str) -> faiss.Index:
    """
    Load FAISS index from file.
    
    Args:
        index_path: Path to index file
        
    Returns:
        FAISS index
    """
    return faiss.read_index(index_path)


def load_metadata(metadata_path: str) -> List[Dict[str, str]]:
    """
    Load metadata from JSON.
    
    Args:
        metadata_path: Path to metadata file
        
    Returns:
        List of metadata entries
    """
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)
