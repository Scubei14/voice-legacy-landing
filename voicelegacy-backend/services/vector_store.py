from __future__ import annotations
from typing import List, Dict, Any
from config import settings
from services.embeddings import embed_texts

_mem = []
_client = None; _collection = None; _index = None

def _init_chroma():
    global _client, _collection
    try:
        import chromadb, os
        os.makedirs(settings.CHROMA_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        _collection = _client.get_or_create_collection("memories", metadata={"hnsw:space":"cosine"})
    except Exception:
        _client = None; _collection=None

def _init_pinecone():
    global _index
    try:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        name = settings.PINECONE_INDEX
        if name not in [i["name"] for i in pc.list_indexes()]:
            pc.create_index(name=name, dimension=384, metric="cosine", spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION))
        _index = pc.Index(name)
    except Exception:
        _index = None

def _add_mem(doc_id, text, user_id, persona_id, embedding):
    if embedding is None: embedding = embed_texts([text])[0]
    _mem.append({"id":doc_id,"text":text,"user_id":user_id,"persona_id":persona_id,"embedding":embedding})

def add(doc_id: str, text: str, user_id: int, persona_id: int | None, embedding: List[float] | None = None):
    backend = settings.VECTOR_BACKEND
    if backend == "pinecone":
        if _index is None: _init_pinecone()
        if not _index: return _add_mem(doc_id, text, user_id, persona_id, embedding)
        if embedding is None: embedding = embed_texts([text])[0]
        _index.upsert(vectors=[{"id": doc_id, "values": embedding, "metadata":{"user_id":user_id, "persona_id": persona_id or -1, "text": text}}])
    elif backend == "chroma":
        if _collection is None: _init_chroma()
        if not _collection: return _add_mem(doc_id, text, user_id, persona_id, embedding)
        _collection.add(ids=[doc_id], documents=[text], metadatas=[{"user_id":user_id, "persona_id": persona_id or -1}])
    else:
        _add_mem(doc_id, text, user_id, persona_id, embedding)

def query(query_text: str, user_id: int, persona_id: int | None = None, top_k: int = 5) -> List[Dict[str,Any]]:
    backend = settings.VECTOR_BACKEND
    if backend == "pinecone" and _index:
        vec = embed_texts([query_text])[0]
        filters = {"user_id":{"$eq": user_id}}
        if persona_id is not None: filters["persona_id"] = {"$eq": persona_id}
        res = _index.query(vector=vec, top_k=top_k, include_metadata=True, filter=filters)
        return [{"text": m["metadata"].get("text",""), "metadata": m["metadata"], "score": float(m.get("score",0.0))} for m in res.get("matches",[])]
    if backend == "chroma" and _collection:
        where = {"user_id": user_id} if persona_id is None else {"user_id": user_id, "persona_id": persona_id}
        r = _collection.query(query_texts=[query_text], n_results=top_k, where=where)
        docs=r.get("documents",[[]])[0]; metas=r.get("metadatas",[[]])[0]; dists=r.get("distances",[[]])[0]
        return [{"text": d, "metadata": m, "score": float(s)} for d,m,s in zip(docs, metas, dists)]
    import numpy as np
    qv = embed_texts([query_text])[0]
    scored=[]
    for m in _mem:
        if m["user_id"] != user_id: continue
        if persona_id is not None and m["persona_id"] != persona_id: continue
        v = np.array(m["embedding"]); q = np.array(qv)
        score = float((v@q)/((np.linalg.norm(v) or 1.0)*(np.linalg.norm(q) or 1.0)))
        scored.append((score,m))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [{"text": m["text"], "metadata":{"user_id":m["user_id"], "persona_id": m["persona_id"]}, "score": s} for s,m in scored[:top_k]]
