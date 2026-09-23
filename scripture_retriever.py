"""scripture_retriever.py – Fast query and retrieval engine over brain.json.

Provides indexed access to the 31,152 scripture verses in brain.json, allowing
the AI brain to fetch exact original verses (Hebrew & Greek) alongside moral citations.
"""

from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from app.brain.moral_ontology import ScriptureCitation, find_matching_scripts, MoralScript

DATA_DIR = Path(__file__).parent / "data"
BRAIN_JSON = DATA_DIR / "brain.json"


class VerseRecord(TypedDict):
    book: str
    chapter: int
    verse: int
    language: str
    text: str


class RetrievedEvidence(TypedDict):
    script_id: str
    script_title: str
    rule_statement: str
    rationale: str
    canonical_reference: str
    book: str
    chapter: int
    verse_range: str
    language: str
    original_text: str
    summary_text: str


class ScriptureRetriever:
    """In-memory indexed retriever for the scripture brain."""

    def __init__(self, brain_path: Path | None = None) -> None:
        self.brain_path = brain_path or BRAIN_JSON
        self._verses: list[VerseRecord] = []
        self._index: dict[tuple[str, int, int], VerseRecord] = {}
        self._loaded: bool = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if not self.brain_path.exists():
            return
        with open(self.brain_path, "r", encoding="utf-8") as f:
            self._verses = json.load(f)
        for v in self._verses:
            key = (v["book"], v["chapter"], v["verse"])
            self._index[key] = v
        self._loaded = True

    @property
    def total_verses(self) -> int:
        self._ensure_loaded()
        return len(self._verses)

    def get_verse(self, book_file: str, chapter: int, verse: int) -> VerseRecord | None:
        """Fetch an exact verse by its book filename, chapter, and verse number."""
        self._ensure_loaded()
        return self._index.get((book_file, chapter, verse))

    def get_verses_range(
        self, book_file: str, chapter: int, verse_start: int, verse_end: int
    ) -> list[VerseRecord]:
        """Fetch a contiguous range of verses."""
        self._ensure_loaded()
        results: list[VerseRecord] = []
        for v_num in range(verse_start, verse_end + 1):
            record = self._index.get((book_file, chapter, v_num))
            if record:
                results.append(record)
        return results

    def retrieve_moral_evidence(self, query: str, limit: int = 4) -> list[RetrievedEvidence]:
        """Find moral scripts matching the query and retrieve their supporting scripture verses from brain.json."""
        self._ensure_loaded()
        matching_scripts = find_matching_scripts(query)
        evidence_list: list[RetrievedEvidence] = []

        for script in matching_scripts:
            for citation in script.citations:
                records = self.get_verses_range(
                    citation.book_file,
                    citation.chapter,
                    citation.verse_start,
                    citation.verse_end,
                )
                if records:
                    original_texts = " ".join(r["text"] for r in records)
                    language = records[0]["language"]
                else:
                    original_texts = ""
                    language = "hebrew" if "hebwlc" in citation.book_file else "greek"

                v_range = (
                    f"{citation.verse_start}"
                    if citation.verse_start == citation.verse_end
                    else f"{citation.verse_start}-{citation.verse_end}"
                )
                ref_str = f"{citation.canonical_book} {citation.chapter}:{v_range}"

                evidence_list.append(
                    {
                        "script_id": script.id,
                        "script_title": script.title,
                        "rule_statement": script.rule_statement,
                        "rationale": script.rationale,
                        "canonical_reference": ref_str,
                        "book": citation.book_file,
                        "chapter": citation.chapter,
                        "verse_range": v_range,
                        "language": language,
                        "original_text": original_texts,
                        "summary_text": citation.summary_text,
                    }
                )
                if len(evidence_list) >= limit:
                    return evidence_list

        return evidence_list


@lru_cache(maxsize=1)
def get_scripture_retriever() -> ScriptureRetriever:
    """Singleton accessor for the cached scripture retriever."""
    retriever = ScriptureRetriever()
    return retriever

