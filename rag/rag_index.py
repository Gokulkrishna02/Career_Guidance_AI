import faiss
import numpy as np
import os
import sys

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
try:
    from rag.rag_builder import build_documents_from_db
except ImportError:
    from rag_builder import build_documents_from_db

RAG_CACHE = {}
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(_BASE, "rag", "rag_store", "faiss.index")
DOC_PATH   = os.path.join(_BASE, "rag", "rag_store", "docs.npy")

# Load model once at module import time
model = SentenceTransformer("all-MiniLM-L6-v2")


def build_and_save_index():
    """Build FAISS index from all documents (static + DB) and persist to disk."""
    documents = build_documents_from_db()

    if not documents:
        documents = [
            "Career Guidance AI is ready. Ask me about careers, colleges, skills, and entrance exams.",
            "Students should explore their interests early and develop both technical and communication skills.",
        ]

    embeddings = model.encode(documents, show_progress_bar=False)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    np.save(DOC_PATH, np.array(documents, dtype=object))

    # Clear search cache since index changed
    RAG_CACHE.clear()

    return index, documents


def load_index():
    """Load FAISS index from disk, or rebuild if it doesn't exist."""
    if os.path.exists(INDEX_PATH) and os.path.exists(DOC_PATH):
        try:
            index = faiss.read_index(INDEX_PATH)
            documents = np.load(DOC_PATH, allow_pickle=True).tolist()
            if len(documents) > 5:  # looks healthy
                return index, documents
        except Exception:
            pass
    return build_and_save_index()


# Load at module import
faiss_index, documents = load_index()


def search_rag(query: str, top_k: int = 4) -> list[str]:
    """Search FAISS index for the most relevant documents."""
    query_embedding = model.encode([query])
    top_k = min(top_k, len(documents))
    distances, indices = faiss_index.search(np.array(query_embedding, dtype=np.float32), top_k)
    return [documents[i] for i in indices[0] if i < len(documents)]


def cached_rag_search(query: str, top_k: int = 4) -> list[str]:
    """Cached wrapper around search_rag."""
    cache_key = f"{query}|{top_k}"
    if cache_key in RAG_CACHE:
        return RAG_CACHE[cache_key]
    docs = search_rag(query, top_k)
    RAG_CACHE[cache_key] = docs
    return docs
