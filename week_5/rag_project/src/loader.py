"""Loader module for reading documents from docs folder."""
import os
from typing import List, Dict


def load_documents(docs_path: str) -> List[Dict[str, str]]:
    """
    Read all .txt files from the docs folder.
    
    Args:
        docs_path: Path to the docs folder
        
    Returns:
        List of documents, each containing:
        - text: content of the file
        - source: filename
    """
    documents = []
    
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Directory not found: {docs_path}")
    
    for filename in os.listdir(docs_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            
            documents.append({
                "text": text,
                "source": filename
            })
    
    return documents
