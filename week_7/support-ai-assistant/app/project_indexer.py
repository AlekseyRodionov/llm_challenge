"""Project indexer - создание FAISS индекса из FAQ документов."""
import os
import sys
import json
import requests
import numpy as np
import faiss

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "app"))

from config import DOCS_DIR, INDEX_DIR, OLLAMA_URL, OLLAMA_MODEL, CHUNK_SIZE, OVERLAP, MAX_EMBED_LENGTH


def embed_text(text: str) -> np.ndarray:
    """Получить embedding через Ollama API."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": text[:MAX_EMBED_LENGTH]},
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.status_code} - {response.text}")
    
    embedding = np.array(response.json()["embedding"], dtype='float32')
    return embedding.reshape(1, -1)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list:
    """Разбить текст на чанки с фиксированным размером."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_index():
    """Создать FAISS индекс из docs/."""
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                chunks = chunk_text(text)
                for chunk in chunks:
                    if chunk.strip():
                        docs.append({"text": chunk, "source": filename})
    
    if not docs:
        raise ValueError("No documents found in docs/. Add .md files to docs/ folder.")
    
    print(f"Loaded {len(docs)} document chunks")
    
    embeddings = []
    for i, doc in enumerate(docs):
        print(f"Creating embedding {i+1}/{len(docs)}...")
        emb = embed_text(doc["text"])
        embeddings.append(emb[0])
    
    embeddings = np.array(embeddings).astype('float32')
    dimension = embeddings.shape[1]
    print(f"Embedding dimension: {dimension}")
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    faiss.write_index(index, os.path.join(INDEX_DIR, "index.faiss"))
    
    with open(os.path.join(INDEX_DIR, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    print(f"FAISS index saved to {INDEX_DIR}")
    print(f"Total chunks: {len(docs)}")


if __name__ == "__main__":
    print("Building FAQ index...")
    build_index()
