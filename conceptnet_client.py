from __future__ import annotations

from urllib.parse import quote

import requests

CONCEPTNET_API = "https://api.conceptnet.io/c/en/"


def fetch_conceptnet_facts(term: str, limit: int = 10) -> list[dict[str, str]]:
    """Fetch a bounded, English ConceptNet neighbourhood for an explicit seed action."""
    cleaned = " ".join(term.split())
    if not cleaned:
        return []
    response = requests.get(f"{CONCEPTNET_API}{quote(cleaned.lower())}", params={"limit": min(limit, 50)}, timeout=10)
    response.raise_for_status()
    facts: list[dict[str, str]] = []
    for edge in response.json().get("edges", [])[:limit]:
        start = edge.get("start", {}).get("label")
        end = edge.get("end", {}).get("label")
        relation = edge.get("rel", {}).get("label")
        if start and end and relation:
            facts.append({"start": start, "relation": relation, "end": end})
    return facts

