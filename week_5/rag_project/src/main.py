"""Main pipeline for RAG document indexing."""
import os
import sys
from tqdm import tqdm

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loader import load_documents
from chunking_fixed import fixed_chunking
from chunking_structure import structure_chunking
from embedder import generate_embeddings
from index_store import create_faiss_index, save_index, save_metadata


def main():
    """Run the complete indexing pipeline."""
    # Paths
    docs_path = os.path.join(os.path.dirname(__file__), "..", "docs")
    index_path = os.path.join(os.path.dirname(__file__), "..", "index")
    
    # Ensure index directory exists
    os.makedirs(index_path, exist_ok=True)
    
    print("=" * 50)
    print("RAG Document Indexing Pipeline")
    print("=" * 50)
    
    # Step 1: Load documents
    print("\n[1/8] Loading documents...")
    documents = load_documents(docs_path)
    print(f"  Documents loaded: {len(documents)}")
    for doc in documents:
        print(f"    - {doc['source']}: {len(doc['text'])} chars")
    
    # Step 2: Fixed chunking
    print("\n[2/8] Running fixed chunking...")
    fixed_chunks = fixed_chunking(documents)
    print(f"  Fixed chunks created: {len(fixed_chunks)}")
    
    # Step 3: Structure chunking
    print("\n[3/8] Running structure chunking...")
    structure_chunks = structure_chunking(documents)
    print(f"  Structure chunks created: {len(structure_chunks)}")
    
    # Step 4: Generate embeddings for fixed chunks
    print("\n[4/8] Generating embeddings for fixed chunks...")
    try:
        fixed_chunks_with_emb = generate_embeddings(fixed_chunks)
    except Exception as e:
        print(f"  Error: {e}")
        print("  Skipping embedding generation.")
        return
    
    # Filter chunks with valid embeddings (must have non-empty list)
    fixed_valid = [c for c in fixed_chunks_with_emb if c.get("embedding") and len(c.get("embedding", [])) > 0]
    print(f"  Valid embeddings: {len(fixed_valid)}")
    
    # Step 5: Generate embeddings for structure chunks
    print("\n[5/8] Generating embeddings for structure chunks...")
    try:
        structure_chunks_with_emb = generate_embeddings(structure_chunks)
    except Exception as e:
        print(f"  Error: {e}")
        print("  Skipping embedding generation.")
        return
    
    structure_valid = [c for c in structure_chunks_with_emb if c.get("embedding") and len(c.get("embedding", [])) > 0]
    print(f"  Valid embeddings: {len(structure_valid)}")
    
    # Step 6: Build FAISS index for fixed
    print("\n[6/8] Building FAISS index for fixed...")
    if fixed_valid:
        embeddings_fixed = [c["embedding"] for c in fixed_valid]
        index_fixed = create_faiss_index(embeddings_fixed)
        save_index(index_fixed, os.path.join(index_path, "faiss_fixed.index"))
        save_metadata(fixed_valid, os.path.join(index_path, "metadata_fixed.json"))
        print(f"  Saved: faiss_fixed.index, metadata_fixed.json")
    
    # Step 7: Build FAISS index for structure
    print("\n[7/8] Building FAISS index for structure...")
    if structure_valid:
        embeddings_structure = [c["embedding"] for c in structure_valid]
        index_structure = create_faiss_index(embeddings_structure)
        save_index(index_structure, os.path.join(index_path, "faiss_structure.index"))
        save_metadata(structure_valid, os.path.join(index_path, "metadata_structure.json"))
        print(f"  Saved: faiss_structure.index, metadata_structure.json")
    
    # Step 8: Comparison
    print("\n[8/8] Comparison:")
    print("-" * 40)
    
    # Fixed strategy stats
    if fixed_valid:
        avg_len_fixed = sum(len(c["text"]) for c in fixed_valid) / len(fixed_valid)
        print(f"Strategy: fixed")
        print(f"  Chunks: {len(fixed_valid)}")
        print(f"  Average length: {avg_len_fixed:.1f} chars")
    
    # Structure strategy stats
    if structure_valid:
        avg_len_structure = sum(len(c["text"]) for c in structure_valid) / len(structure_valid)
        print(f"\nStrategy: structure")
        print(f"  Chunks: {len(structure_valid)}")
        print(f"  Average length: {avg_len_structure:.1f} chars")
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)


if __name__ == "__main__":
    main()
