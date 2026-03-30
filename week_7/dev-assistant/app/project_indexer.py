"""Project documentation indexer for Dev Assistant."""
import os
import sys
import json
import requests
import numpy as np
import faiss

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_PATH = os.path.join(PROJECT_ROOT, "..", "..")  # корень llm_challenge
INDEX_PATH = os.path.join(PROJECT_ROOT, "project_index", "index.faiss")
META_PATH = os.path.join(PROJECT_ROOT, "project_index", "metadata.json")

IGNORE_DIRS = {".git", "venv", "__pycache__", ".pytest_cache", "week_7"}

# Только документация (без .py)
EXTENSIONS = (".md", ".txt")

# Исключить большие датасеты
IGNORE_FILES = {"fire_dataset.txt", "mkdocs_dataset.txt", "test_results.txt", "monitoring_summary.txt"}

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"

CHUNK_SIZE = 500
OVERLAP = 50
MAX_TEXT_LENGTH = 4000


def find_docs():
    """Find all .md, .txt and .py files recursively from root."""
    documents = []
    
    if not os.path.exists(DOCS_PATH):
        raise ValueError(f"Root folder not found: {DOCS_PATH}")
    
    for root, dirs, files in os.walk(DOCS_PATH):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in files:
            if not filename.endswith(EXTENSIONS):
                continue
            if filename in IGNORE_FILES:
                continue
            
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                    relpath = os.path.relpath(filepath, DOCS_PATH)
                    documents.append({
                        "source": relpath,
                        "text": text
                    })
                except Exception as e:
                    print(f"  Warning: Could not read {filepath}: {e}")
    
    if not documents:
        raise ValueError("No documents found. Add .md, .txt or .py files.")
    
    return documents


def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP):
    """Split text into chunks with overlap."""
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "source": source
        })
        
        start += chunk_size - overlap
        chunk_id += 1
    
    return chunks


def generate_embedding(text: str) -> np.ndarray:
    """Generate embedding via Ollama API."""
    text = text[:MAX_TEXT_LENGTH]
    
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": text},
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.status_code}")
    
    data = response.json()
    return np.array(data.get("embedding", []), dtype='float32')


def create_index(embeddings: list) -> faiss.Index:
    """Create FAISS index from embeddings."""
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index


def main():
    """Run indexing pipeline."""
    print("=" * 50)
    print("Project Documentation Indexer")
    print("=" * 50)
    
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    
    print(f"\n[1/4] Loading documents from {DOCS_PATH}...")
    documents = find_docs()
    print(f"  Found {len(documents)} documents")
    for doc in documents:
        print(f"    - {doc['source']}: {len(doc['text'])} chars")
    
    print(f"\n[2/4] Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_text(doc["text"], doc["source"])
        all_chunks.extend(chunks)
    print(f"  Created {len(all_chunks)} chunks")
    
    print(f"\n[3/4] Generating embeddings...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        print(f"  Embedding {i+1}/{len(all_chunks)}...", end="\r")
        emb = generate_embedding(chunk["text"])
        embeddings.append(emb)
        chunk["embedding"] = emb.tolist()
    print(f"\n  Generated {len(embeddings)} embeddings")
    
    print(f"\n[4/4] Building FAISS index...")
    index = create_index(embeddings)
    
    faiss.write_index(index, INDEX_PATH)
    
    metadata = [{"id": c["id"], "text": c["text"], "source": c["source"]} for c in all_chunks]
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n  Saved: {INDEX_PATH}")
    print(f"  Saved: {META_PATH}")
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
