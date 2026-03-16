"""Structure-based chunking module."""
import re
from typing import List, Dict


def structure_chunking(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Split documents by structure: double newlines and markdown headers.
    
    Args:
        documents: List of documents with 'text' and 'source' keys
        
    Returns:
        List of chunks, each containing:
        - chunk_id: unique identifier
        - text: chunk content
        - source: source filename
        - strategy: 'structure'
        - section: header name if present
    """
    chunks = []
    chunk_id = 0
    
    for doc in documents:
        text = doc["text"]
        source = doc["source"]
        
        # Split by double newlines first
        paragraphs = text.split("\n\n")
        
        current_section = None
        current_chunk_parts = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if paragraph starts with markdown header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', para)
            
            if header_match:
                # Save previous chunk if exists
                if current_chunk_parts:
                    chunk_text = "\n\n".join(current_chunk_parts)
                    chunks.append({
                        "chunk_id": f"structure_{chunk_id}",
                        "text": chunk_text,
                        "source": source,
                        "strategy": "structure",
                        "section": current_section
                    })
                    chunk_id += 1
                    current_chunk_parts = []
                
                # New section
                current_section = header_match.group(2).strip()
                # Remove header from text
                remaining = para.split('\n', 1)
                if len(remaining) > 1:
                    current_chunk_parts.append(remaining[1].strip())
                else:
                    current_chunk_parts.append("")
            else:
                current_chunk_parts.append(para)
        
        # Save last chunk
        if current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts)
            chunks.append({
                "chunk_id": f"structure_{chunk_id}",
                "text": chunk_text,
                "source": source,
                "strategy": "structure",
                "section": current_section
            })
            chunk_id += 1
    
    return chunks
