from __future__ import annotations

from functools import lru_cache

from app.config import get_settings


# ---------------------------------------------------------------------------
# Pipeline loader
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_pipeline():
    """Load the heavyweight model only when explicitly enabled.

    Fixes
    -----
    - BUG-2: ``get_settings()`` is now called lazily *inside* this function
      instead of at module-import time. This prevents crashes when the module
      is imported in environments without a .env file (e.g. unit tests).
    - BUG-5: Reading settings inside the function body means the cached
      pipeline is always consistent with the settings that were active when
      the first call was made, rather than a stale module-level snapshot.
    """
    settings = get_settings()
    if not settings.enable_transformers:
        return None
    try:
        from transformers import pipeline  # type: ignore[import-untyped]

        return pipeline("zero-shot-classification", model=settings.hf_model_name)
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Heuristic scorer (transparent fallback when Transformers is disabled)
# ---------------------------------------------------------------------------

def _heuristic_scores(query: str, answers: list[str]) -> dict[str, float]:
    """Return a normalised confidence dict using simple keyword heuristics.

    Fixes
    -----
    - BUG-1: The empty-answers guard is now the *first* statement so it
      short-circuits before building the scores dict. Previously the dict was
      built first (always empty for an empty list, which happened to be falsy),
      making the guard work only by accident and obscuring the intent.
    - BUG-3: Initial scores are set to ``1 / len(answers)`` (equal prior)
      instead of the hardcoded magic value ``0.34``. With 0.34 and two answers
      the unnormalised sum is 0.68; with three it is 1.02 – neither is a
      principled prior. Equal initialisation ensures every answer starts from
      the same neutral baseline regardless of how many candidates are provided.
    """
    # BUG-1 fix: guard first, before any allocation
    if not answers:
        return {"unclear": 0.5}

    lower_query = query.lower()

    # BUG-3 fix: equal prior scaled to number of answers
    equal_prior = 1.0 / len(answers)
    scores: dict[str, float] = {answer: equal_prior for answer in answers}

    positive = {"yes", "true", "likely"}
    negative = {"no", "false", "unlikely"}
    has_negation = any(
        word in lower_query.split()
        for word in {"not", "never", "cannot", "can't"}
    )

    for answer in answers:
        label = answer.lower()
        if label in positive:
            scores[answer] += 0.16 if not has_negation else -0.08
        elif label in negative:
            scores[answer] += 0.16 if has_negation else -0.08
        elif label == "unclear":
            scores[answer] += 0.08

    # Normalise so all scores sum to 1.0 (floor each at 0.01 to avoid zeros)
    total = sum(max(v, 0.01) for v in scores.values())
    return {k: round(max(v, 0.01) / total, 3) for k, v in scores.items()}


# ---------------------------------------------------------------------------
# Public reasoning interface
# ---------------------------------------------------------------------------

def reason_about(query: str, candidate_answers: list[str]) -> dict:
    """Classify a query against caller-provided options.

    Uses the HuggingFace zero-shot pipeline when ``ENABLE_TRANSFORMERS=true``
    in the environment, otherwise falls back to the transparent heuristic
    scorer so the confidence number is never a hidden black-box result.

    Fixes
    -----
    - BUG-4: ``zip(..., strict=True)`` is only available in Python ≥ 3.10.
      Replaced with an explicit ``assert`` that the two sequences have equal
      length before zipping, which is compatible with Python 3.9+ and raises
      a clear error if the model ever returns mismatched label/score lists.
    - BUG-6: ``max(scores, key=scores.get)`` passes ``dict.get`` as the key
      function, which has return type ``Optional[float]`` and is rejected by
      mypy / Pylance. Replaced with an explicit lambda that always returns a
      ``float`` (safe because every value in *scores* is a float at this point).
    - BUG-2 (secondary): ``settings`` is now retrieved lazily via
      ``get_settings()`` rather than using a module-level global, keeping this
      function consistent with ``_get_pipeline()``.
    """
    settings = get_settings()
    answers = candidate_answers or ["yes", "no", "unclear"]
    model = _get_pipeline()

    if model:
        result = model(query, candidate_labels=answers, multi_label=False)
        labels: list[str] = result["labels"]
        raw_scores: list[float] = result["scores"]

        # BUG-4 fix: explicit length guard instead of zip(strict=True)
        if len(labels) != len(raw_scores):
            raise ValueError(
                f"Model returned {len(labels)} labels but {len(raw_scores)} scores; "
                "cannot build a reliable scores dict."
            )
        scores = {label: round(score, 3) for label, score in zip(labels, raw_scores)}
        return {
            "best_answer": labels[0],
            "scores": scores,
            "engine": settings.hf_model_name,
        }

    # Heuristic fallback
    scores = _heuristic_scores(query, answers)

    # BUG-6 fix: lambda guarantees float return type for the key function
    best_answer = max(scores, key=lambda k: scores[k])

    return {
        "best_answer": best_answer,
        "scores": scores,
        "engine": "lightweight confidence fallback",
    }
