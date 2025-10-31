from __future__ import annotations
from typing import List
import numpy as np
from config import settings

_model = None

def _load_model():
    global _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDINGS_MODEL)
    except Exception:
        _model = None

def _load():
    if _model is None: _load_model()
    return _model

def _fallback_embed(texts: List[str]) -> List[List[float]]:
    dim = 384; out = []
    for t in texts:
        vec = np.zeros(dim, dtype=np.float32); seed = 2166136261
        for i,ch in enumerate(t.encode('utf-8')):
            seed = (seed ^ ch) * 16777619 & 0xffffffff
            vec[i % dim] += (seed % 1000) / 1000.0
        n = np.linalg.norm(vec) or 1.0
        out.append((vec/n).tolist())
    return out

def embed_texts(texts: List[str]) -> List[List[float]]:
    m = _load()
    if m:
        try:
            v = m.encode(texts, show_progress_bar=False, normalize_embeddings=True)
            return v.tolist()
        except Exception:
            pass
    return _fallback_embed(texts)
