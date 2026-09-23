from __future__ import annotations

from collections import defaultdict
from threading import Lock


class ContextEngine:
    """Bounded in-memory context. Persisted messages remain available through the history API."""

    def __init__(self, max_turns: int = 5) -> None:
        self.max_turns = max_turns
        self._sessions: dict[str, list[dict]] = defaultdict(list)
        self._lock = Lock()

    def update_context(self, session_id: str, query: str, concepts: list[str], entities: list[dict]) -> None:
        with self._lock:
            turns = self._sessions[session_id]
            turns.append({"query": query, "concepts": concepts, "entities": entities})
            self._sessions[session_id] = turns[-self.max_turns :]

    def enrich_concepts(self, session_id: str, concepts: list[str]) -> list[str]:
        with self._lock:
            previous = [concept for turn in self._sessions.get(session_id, [])[:-1] for concept in turn["concepts"]]
        return list(dict.fromkeys([*concepts, *previous]))[:12]

    def get_context_summary(self, session_id: str) -> str:
        with self._lock:
            turns = self._sessions.get(session_id, [])
            return " | ".join(turn["query"] for turn in turns[-self.max_turns :])

