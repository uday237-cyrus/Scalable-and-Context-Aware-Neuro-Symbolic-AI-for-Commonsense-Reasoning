"""build_brain.py - Scripture-aware brain builder for the NeuroSymbolic AI.

Run this script ONCE (or whenever you add / update .usfm files) to parse the
Hebrew and Greek scripture texts and compile them into a persistent brain
knowledge store (brain.json) that the running FastAPI app can load instantly.

Location
--------
    backend/
    ├── build_brain.py          <- THIS FILE
    └── app/
        └── brain/
            └── data/
                ├── hebwlc_usfm/   <- Hebrew OT .usfm files go here
                ├── grcsbl_usfm/   <- Greek NT .usfm files go here
                └── brain.json     <- generated output (all parsed verses)

Usage
-----
    # From the backend/ directory (with the venv active):
    python build_brain.py

    # Rebuild only one collection:
    python build_brain.py --collection hebrew
    python build_brain.py --collection greek

    # Rebuild and run a quick phrase search across all verses:
    python build_brain.py --search "love your neighbour"

    # Suppress per-file progress lines:
    python build_brain.py --quiet
"""

from __future__ import annotations

import argparse
import os
import re
import json
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------

# This file lives at backend/build_brain.py -> backend/ is its parent.
BACKEND_DIR = Path(__file__).parent.resolve()

# Canonical folder pairs: (relative-path-from-backend, language-label)
FOLDERS: list[tuple[str, str]] = [
    ("app/brain/data/hebwlc_usfm", "hebrew"),
    ("app/brain/data/grcsbl_usfm", "greek"),
]

# Output file written alongside the USFM data directories
OUTPUT_FILE = BACKEND_DIR / "app" / "brain" / "data" / "brain.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_banner(title: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n  {title}\n{bar}")


def _collection_stats(brain: list[dict], language: str) -> dict:
    """Return verse count and unique book list for one language."""
    subset = [v for v in brain if v["language"] == language]
    books = sorted({v["book"] for v in subset})
    return {"verse_count": len(subset), "book_count": len(books), "books": books}


# ---------------------------------------------------------------------------
# Core parse engine
# ---------------------------------------------------------------------------

def _parse_usfm_file(filepath: str, filename: str, language: str) -> list[dict]:
    """Parse a single .usfm file and return a list of verse dicts.

    Each dict matches the schema:
        {
            "book":     str,   # filename of the source .usfm file
            "chapter":  int,
            "verse":    int,
            "language": str,   # "hebrew" | "greek"
            "text":     str    # raw verse text with USFM inline markers stripped
        }
    """
    verses: list[dict] = []
    chapter = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Chapter marker
            if line.startswith("\\c "):
                try:
                    chapter = int(line.split()[1])
                except (IndexError, ValueError):
                    pass  # malformed marker - keep current chapter

            # Verse marker
            elif line.startswith("\\v "):
                match = re.match(r'\\v\s+(\d+)\s+(.*)', line)
                if match:
                    verse_num = int(match.group(1))
                    text = match.group(2)
                    verses.append({
                        "book": filename,
                        "chapter": chapter,
                        "verse": verse_num,
                        "language": language,
                        "text": text,
                    })

    return verses


# ---------------------------------------------------------------------------
# Main build routine
# ---------------------------------------------------------------------------

def build(
    targets: list[str] | None = None,
    *,
    verbose: bool = True,
) -> list[dict]:
    """Parse all requested USFM collections and write brain.json."""
    active_labels = set(targets) if targets else {lang for _, lang in FOLDERS}
    brain: list[dict] = []
    start = time.perf_counter()

    _print_banner("NeuroSymbolic AI - Brain Builder")
    print(f"  Started  : {datetime.now(timezone.utc).isoformat()}")
    print(f"  Targets  : {', '.join(sorted(active_labels))}")
    print(f"  Output   : {OUTPUT_FILE}\n")

    # Walk every configured folder
    for rel_folder, language in FOLDERS:

        if language not in active_labels:
            continue

        folder = os.path.join(BACKEND_DIR, rel_folder)

        # Guard: folder must exist
        if not os.path.exists(folder):
            print(f"  [WARN] Folder not found: {folder}")
            print("         Create it and drop your .usfm files inside, then re-run.\n")
            continue

        usfm_files = sorted(f for f in os.listdir(folder) if f.endswith(".usfm"))

        if not usfm_files:
            print(f"  [WARN] No .usfm files found in: {folder}\n")
            continue

        print(f"[{language.upper()}] {len(usfm_files)} file(s) found - parsing ...")

        for filename in usfm_files:
            filepath = os.path.join(folder, filename)
            verses = _parse_usfm_file(filepath, filename, language)
            brain.extend(verses)

            if verbose:
                print(f"  Reading {filename:<48}  ->  {len(verses):>6} verses")

        lang_stats = _collection_stats(brain, language)
        print(
            f"\n  [{language.upper()} total] "
            f"{lang_stats['verse_count']} verses across "
            f"{lang_stats['book_count']} book(s)\n"
        )

    # Write brain.json
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(brain, f, ensure_ascii=False, indent=2)

    # Final summary
    elapsed = time.perf_counter() - start
    _print_banner("Build Complete")
    print(f"  Verses saved : {len(brain)}")
    print(f"  Elapsed      : {elapsed:.2f}s")
    print(f"\n  brain.json -> {OUTPUT_FILE}\n")

    print("SUCCESS")
    print(f"Verses: {len(brain)}")
    print(f"Saved:  {OUTPUT_FILE}")

    return brain


# ---------------------------------------------------------------------------
# Optional: quick full-text search demo
# ---------------------------------------------------------------------------

def demo_search(brain: list[dict], query: str) -> None:
    """Print the first 10 verses containing query across all languages."""
    q = query.lower()
    hits = [v for v in brain if q in v["text"].lower()]

    _print_banner(f'Search: "{query}"')
    if not hits:
        print("  No matches found.\n")
        return

    print(f"  {len(hits)} match(es). Showing first 10:\n")
    for v in hits[:10]:
        lang = v["language"].upper()[:6]
        ref = f'{v["book"]} {v["chapter"]}:{v["verse"]}'
        snippet = textwrap.shorten(v["text"], width=80, placeholder=" ...")
        print(f"  [{lang:6}]  {ref:<35}  {snippet}")
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the NeuroSymbolic AI brain (brain.json) from USFM scripture files.\n\n"
            "Place your .usfm files in:\n"
            "  backend/app/brain/data/hebwlc_usfm/   (Hebrew OT)\n"
            "  backend/app/brain/data/grcsbl_usfm/   (Greek NT)\n"
            "then run this script from the backend/ directory."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--collection",
        choices=["hebrew", "greek", "both"],
        default="both",
        help="Which USFM collection(s) to build (default: both).",
    )
    parser.add_argument(
        "--search",
        metavar="QUERY",
        default=None,
        help="After building, run a quick full-text search and print matching verses.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-file progress output.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    targets = ["hebrew", "greek"] if args.collection == "both" else [args.collection]
    brain = build(targets, verbose=not args.quiet)
    if args.search:
        demo_search(brain, args.search)
