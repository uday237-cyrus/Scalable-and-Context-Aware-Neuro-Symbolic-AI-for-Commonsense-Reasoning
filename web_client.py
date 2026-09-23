"""web_client.py – Live web search via DuckDuckGo (no API key required).

Returns plain-text snippets for the top 3-5 results so the conversational
brain can ground real-world factual answers in live information.
"""

from __future__ import annotations

import logging
from typing import TypedDict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class WebSnippet(TypedDict):
    title: str
    snippet: str
    url: str


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class WebSearchClient:
    """Thin wrapper around DuckDuckGo text search.

    Usage::

        client = WebSearchClient()
        snippets = client.search("current weather Mumbai")
        for s in snippets:
            print(s["snippet"], s["url"])
    """

    _MAX_RESULTS = 5

    def is_available(self) -> bool:
        """Return True if the duckduckgo_search library is importable."""
        try:
            import duckduckgo_search  # noqa: F401
            return True
        except ImportError:
            return False

    def search(self, query: str, max_results: int | None = None) -> list[WebSnippet]:
        """Search DuckDuckGo and return up to *max_results* text snippets.

        Args:
            query: The search query string.
            max_results: Override the default cap (default: 5).

        Returns:
            A list of :class:`WebSnippet` dicts.  Empty list on any error.
        """
        if not self.is_available():
            logger.warning("duckduckgo_search not installed — web search unavailable.")
            return []

        cap = max_results or self._MAX_RESULTS
        snippets: list[WebSnippet] = []

        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=cap)
                for r in results or []:
                    body = r.get("body") or r.get("snippet") or ""
                    title = r.get("title") or ""
                    url = r.get("href") or r.get("url") or ""
                    if body or title:
                        snippets.append(
                            WebSnippet(
                                title=title.strip(),
                                snippet=body.strip(),
                                url=url.strip(),
                            )
                        )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Web search failed for query %r: %s", query, exc)

        return snippets[:cap]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_client: WebSearchClient | None = None


def get_web_client() -> WebSearchClient:
    global _client
    if _client is None:
        _client = WebSearchClient()
    return _client

