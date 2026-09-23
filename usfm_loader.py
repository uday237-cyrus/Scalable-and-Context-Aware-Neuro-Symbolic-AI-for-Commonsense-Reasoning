"""usfm_loader.py – Parses USFM scripture files into plain-text passages.

USFM (Unified Standard Format Markers) is the standard format for digital
Bible texts. This loader strips the markers and returns clean verse text that
the brain can ingest as moral-knowledge input.

Supported collections
---------------------
- hebwlc_usfm/  : Hebrew Westminster Leningrad Codex (Old Testament)
- grcsbl_usfm/  : Greek SBL text (New Testament)

Usage
-----
    from app.brain.usfm_loader import USFMLoader

    loader = USFMLoader()

    # Load a single book file
    verses = loader.load_file("02-GENhebwlc.usfm", collection="hebrew")

    # Load every verse from the full Hebrew collection
    all_ot = loader.load_collection("hebrew")

    # Load every verse from the full Greek collection
    all_nt = loader.load_collection("greek")

    # Quick search across both collections
    results = loader.search("love your neighbour")
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Generator

from app.brain import GREEK_DIR, HEBREW_DIR

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

# Matches any USFM marker:  \id, \v, \c, \p, \mt, etc. (with optional number)
_MARKER_RE = re.compile(r"\\[a-zA-Z]+\d*\s*")

# Matches a verse marker and captures the verse number: \v 3
_VERSE_RE = re.compile(r"\\v\s+(\d+)\s*")

# Matches a chapter marker and captures the chapter number: \c 1
_CHAPTER_RE = re.compile(r"\\c\s+(\d+)")

# Matches the book-id line: \id GEN – Genesis
_ID_RE = re.compile(r"\\id\s+(\S+)")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class Verse:
    """A single scripture verse with location metadata."""

    __slots__ = ("collection", "book", "chapter", "verse", "text")

    def __init__(
        self,
        collection: str,
        book: str,
        chapter: int,
        verse: int,
        text: str,
    ) -> None:
        self.collection = collection  # "hebrew" | "greek"
        self.book = book              # e.g. "GEN", "MAT"
        self.chapter = chapter
        self.verse = verse
        self.text = text.strip()

    @property
    def reference(self) -> str:
        """Human-readable reference, e.g. 'GEN 1:1'."""
        return f"{self.book} {self.chapter}:{self.verse}"

    def __repr__(self) -> str:
        return f"<Verse {self.reference} [{self.collection}]>"

    def to_dict(self) -> dict:
        return {
            "collection": self.collection,
            "book": self.book,
            "chapter": self.chapter,
            "verse": self.verse,
            "reference": self.reference,
            "text": self.text,
        }


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class USFMLoader:
    """Loads and queries USFM files from the brain data directory."""

    _COLLECTIONS: dict[str, Path] = {
        "hebrew": HEBREW_DIR,
        "greek": GREEK_DIR,
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_file(self, filename: str, collection: str = "hebrew") -> list[Verse]:
        """Parse a single .usfm file and return all its verses.

        Parameters
        ----------
        filename:
            The file name only (e.g. ``"02-GENhebwlc.usfm"``).
        collection:
            Either ``"hebrew"`` or ``"greek"``.

        Returns
        -------
        list[Verse]
            All verses found in the file, in canonical order.
        """
        directory = self._resolve_collection(collection)
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(
                f"USFM file not found: {path}\n"
                f"Place the file inside: {directory}"
            )
        return list(self._parse(path, collection))

    def load_collection(self, collection: str = "hebrew") -> list[Verse]:
        """Load every .usfm file in a collection directory.

        Files are processed in filesystem order (which follows the numeric
        prefix of the canonical book order).

        Parameters
        ----------
        collection:
            Either ``"hebrew"`` or ``"greek"``.
        """
        directory = self._resolve_collection(collection)
        usfm_files = sorted(directory.glob("*.usfm"))
        if not usfm_files:
            return []
        verses: list[Verse] = []
        for path in usfm_files:
            verses.extend(self._parse(path, collection))
        return verses

    def list_files(self, collection: str = "hebrew") -> list[str]:
        """Return the filenames present in a collection directory."""
        directory = self._resolve_collection(collection)
        return sorted(p.name for p in directory.glob("*.usfm"))

    def search(
        self,
        query: str,
        collections: list[str] | None = None,
        case_sensitive: bool = False,
    ) -> list[Verse]:
        """Full-text search across one or more collections.

        Parameters
        ----------
        query:
            The text to look for inside verse text.
        collections:
            Which collections to search. Defaults to both ``["hebrew", "greek"]``.
        case_sensitive:
            Whether the match is case-sensitive.

        Returns
        -------
        list[Verse]
            All verses whose text contains *query*.
        """
        targets = collections or list(self._COLLECTIONS)
        q = query if case_sensitive else query.lower()
        results: list[Verse] = []
        for coll in targets:
            for verse in self.load_collection(coll):
                haystack = verse.text if case_sensitive else verse.text.lower()
                if q in haystack:
                    results.append(verse)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_collection(self, collection: str) -> Path:
        directory = self._COLLECTIONS.get(collection)
        if directory is None:
            raise ValueError(
                f"Unknown collection '{collection}'. "
                f"Choose one of: {list(self._COLLECTIONS)}"
            )
        return directory

    @staticmethod
    def _parse(path: Path, collection: str) -> Generator[Verse, None, None]:
        """Parse a single USFM file and yield Verse objects."""
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        # Detect book code from \id line
        book = path.stem.split("-")[-1].replace("hebwlc", "").replace("grcsbl", "").upper()
        for line in lines:
            id_match = _ID_RE.match(line)
            if id_match:
                book = id_match.group(1).upper()
                break

        chapter = 0
        verse_num = 0
        verse_text_parts: list[str] = []

        def _flush() -> Verse | None:
            if verse_num > 0 and verse_text_parts:
                raw = " ".join(verse_text_parts)
                clean = _MARKER_RE.sub(" ", raw).strip()
                if clean:
                    return Verse(collection, book, chapter, verse_num, clean)
            return None

        for line in lines:
            chap_match = _CHAPTER_RE.search(line)
            if chap_match:
                flushed = _flush()
                if flushed:
                    yield flushed
                chapter = int(chap_match.group(1))
                verse_num = 0
                verse_text_parts = []
                continue

            verse_match = _VERSE_RE.search(line)
            if verse_match:
                flushed = _flush()
                if flushed:
                    yield flushed
                verse_num = int(verse_match.group(1))
                # Capture any text that follows the marker on the same line
                after_marker = line[verse_match.end():]
                verse_text_parts = [after_marker] if after_marker.strip() else []
                continue

            # Continuation line inside a verse
            if verse_num > 0:
                verse_text_parts.append(line)

        # Flush the final verse
        flushed = _flush()
        if flushed:
            yield flushed

