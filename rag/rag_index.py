import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from rag.rag_builder import build_documents_from_db

RAG_CACHE = {}
INDEX_PATH = "rag/rag_store/faiss.index"
DOC_PATH = "rag/rag_store/docs.npy"

model = SentenceTransformer("all-MiniLM-L6-v2")

def build_and_save_index():
    documents = build_documents_from_db()
    embeddings = model.encode(documents)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    os.makedirs("rag/rag_store", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    np.save(DOC_PATH, documents)

    return index, documents


def load_index():
    if os.path.exists(INDEX_PATH) and os.path.exists(DOC_PATH):
        index = faiss.read_index(INDEX_PATH)
        documents = np.load(DOC_PATH, allow_pickle=True).tolist()
        return index, documents
    else:
        return build_and_save_index()


faiss_index, documents = load_index()


def search_rag(query, top_k=3):
    query_embedding = model.encode([query])
    _, indices = faiss_index.search(query_embedding, top_k)
    return [documents[i] for i in indices[0]]

def cached_rag_search(query):
    if query in RAG_CACHE:
        return RAG_CACHE[query]

    docs = search_rag(query)
    RAG_CACHE[query] = docs
    return docs
