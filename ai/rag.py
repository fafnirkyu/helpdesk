"""Small, offline-safe retrieval helper for the helpdesk classifier.

The embedding model is optional. Importing the API must not download models or
block startup; when a locally cached model is unavailable, the classifier still
receives a deterministic set of example tickets.
"""

from __future__ import annotations

from functools import lru_cache

KNOWLEDGE_BASE = [
    {"instruction": "I can't log into my account", "response": "ACCOUNT"},
    {"instruction": "My order hasn't arrived yet", "response": "ORDER"},
    {"instruction": "I was charged twice", "response": "BILLING"},
    {"instruction": "The app keeps crashing", "response": "TECHNICAL"},
    {"instruction": "I want to cancel my subscription", "response": "SUBSCRIPTION"},
    {"instruction": "Promo code invalid", "response": "BILLING"},
    {"instruction": "Website very slow", "response": "TECHNICAL"},
    {"instruction": "I forgot my password", "response": "ACCOUNT"},
]


@lru_cache(maxsize=1)
def _get_embedding_model():
    """Return a cached local embedding model, or ``None`` when unavailable."""
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", local_files_only=True
        )
    except Exception as error:
        print(f"Embedding model unavailable; using example fallback: {error}")
        return None


def _fallback_examples(message: str, top_k: int) -> list[dict[str, str]]:
    terms = set(message.lower().split())
    ranked = sorted(
        KNOWLEDGE_BASE,
        key=lambda example: len(terms & set(example["instruction"].lower().split())),
        reverse=True,
    )
    return ranked[:top_k]


@lru_cache(maxsize=1)
def _knowledge_embeddings():
    model = _get_embedding_model()
    if model is None:
        return None
    return model.encode(
        [example["instruction"] for example in KNOWLEDGE_BASE],
        normalize_embeddings=True,
    )


def retrieve_examples(message: str, top_k: int = 3) -> list[dict[str, str]]:
    """Return relevant example tickets without making any network request."""
    if top_k <= 0:
        return []

    model = _get_embedding_model()
    embeddings = _knowledge_embeddings()
    if model is None or embeddings is None:
        return _fallback_examples(message, top_k)

    query_embedding = model.encode(message, normalize_embeddings=True)
    scores = embeddings @ query_embedding
    indices = scores.argsort()[::-1][:top_k]
    return [KNOWLEDGE_BASE[index] for index in indices]
