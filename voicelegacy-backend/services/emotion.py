from typing import Dict, List
import warnings

_pipe_cache = None

def _pipe():
    try:
        from transformers import pipeline
        return pipeline('text-classification', model='joeddav/distilbert-base-uncased-go-emotions-student', return_all_scores=True)
    except Exception as e:
        warnings.warn(f"Emotion model failed to load: {e}")
        return None

def ensure():
    global _pipe_cache
    if _pipe_cache is None: _pipe_cache = _pipe()
    return _pipe_cache

def top_emotions(text: str, k: int = 5) -> List[Dict]:
    if not text or not text.strip(): return [{'label': 'neutral', 'score': 0.5}]
    p = ensure()
    if not p: return [{'label': 'neutral', 'score': 0.5}]
    try:
        scores = p(text[:512])[0]; scores.sort(key=lambda x: x['score'], reverse=True); return scores[:k]
    except Exception:
        return [{'label': 'neutral', 'score': 0.5}]
