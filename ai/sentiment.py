"""Optional, offline-safe sentiment detection."""

from __future__ import annotations

import threading

_lock = threading.Lock()
_sentiment_analyzer = None
_load_attempted = False


def get_sentiment_analyzer():
    """Load a locally cached transformer model once, without downloading it."""
    global _load_attempted, _sentiment_analyzer
    with _lock:
        if _load_attempted:
            return _sentiment_analyzer
        _load_attempted = True
        try:
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
                pipeline,
            )

            model_name = "distilbert-base-uncased-finetuned-sst-2-english"
            tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name, local_files_only=True
            )
            _sentiment_analyzer = pipeline(
                "sentiment-analysis", model=model, tokenizer=tokenizer
            )
        except Exception as error:
            print(f"Sentiment model unavailable; using neutral fallback: {error}")
        return _sentiment_analyzer


def detect_sentiment(text: str) -> str:
    if not text:
        return "NEUTRAL"

    analyzer = get_sentiment_analyzer()
    if analyzer is None:
        return "NEUTRAL"

    result = analyzer(text[:512])[0]
    if result["score"] < 0.6:
        return "NEUTRAL"
    return result["label"].upper()
