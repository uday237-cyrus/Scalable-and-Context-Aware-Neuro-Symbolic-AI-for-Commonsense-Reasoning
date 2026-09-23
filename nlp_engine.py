from __future__ import annotations

import re
from functools import lru_cache

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from", "how",
    "i", "in", "is", "it", "me", "of", "on", "or", "the", "this", "that", "to", "was", "what",
    "when", "where", "which", "who", "why", "will", "with", "would", "you", "your",
}


@lru_cache(maxsize=1)
def _load_spacy_model():
    """Load the optional model once; the assistant remains usable without it."""
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except (ImportError, OSError):
        return None


def _fallback_analysis(text: str) -> dict:
    words = [word.lower() for word in _WORD_RE.findall(text)]
    concepts = list(dict.fromkeys(word for word in words if word not in _STOPWORDS))[:12]
    proper_nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
    return {
        "entities": [{"text": item, "label": "PROPER_NOUN"} for item in proper_nouns],
        "key_concepts": concepts,
        "tokens": words,
        "engine": "rule-based fallback",
    }


def analyze_query(text: str) -> dict:
    """Extract named entities and candidate graph concepts from a user query."""
    model = _load_spacy_model()
    if model is None:
        return _fallback_analysis(text)

    document = model(text)
    concepts = [token.lemma_.lower() for token in document if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop]
    return {
        "entities": [{"text": entity.text, "label": entity.label_} for entity in document.ents],
        "key_concepts": list(dict.fromkeys(concepts))[:12],
        "tokens": [token.text for token in document],
        "engine": "spaCy en_core_web_sm",
    }

