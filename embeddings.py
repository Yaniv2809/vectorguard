"""
VectorGuard — Embeddings Engine
מריץ locally, אפס עלות, אפס rate limits.
"""

from sentence_transformers import SentenceTransformer

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Singleton — טוען מודל פעם אחת לכל session."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed(text: str) -> list[float]:
    """ממיר טקסט בודד ל-vector."""
    model = _get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """ממיר רשימת טקסטים ל-vectors — יעיל מ-embed בלולאה."""
    model = _get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    מחשב קרבה בין שני vectors.
    משמש בבדיקות drift ו-embedding consistency.
    """
    import math

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
    norm_b = math.sqrt(sum(b ** 2 for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
