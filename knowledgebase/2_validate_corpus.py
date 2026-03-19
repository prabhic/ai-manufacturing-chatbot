#!/usr/bin/env python3
"""
Corpus Validator — Check your scraped files
=============================================
Run this AFTER scraping to see what you got.

Usage:
    python validate_corpus.py
    python validate_corpus.py ./corpus
"""

import sys
from pathlib import Path


def validate(corpus_dir="./corpus"):
    corpus = Path(corpus_dir)

    if not corpus.exists():
        print(f"Corpus not found at: {corpus.absolute()}")
        print(f"Run the scraper first: python scraper.py")
        sys.exit(1)

    # Count .txt files
    txt_files = list(corpus.glob("*.txt"))
    total_words = 0
    shortest = ("", float("inf"))
    longest = ("", 0)

    print(f"\nCorpus: {corpus.absolute()}")
    print(f"{'='*50}")

    for f in sorted(txt_files):
        if f.name.startswith("_"):
            continue  # skip _index.json etc.
        text = f.read_text(encoding="utf-8")
        words = len(text.split())
        total_words += words
        if words < shortest[1]:
            shortest = (f.name, words)
        if words > longest[1]:
            longest = (f.name, words)

    article_count = len([f for f in txt_files if not f.name.startswith("_")])

    print(f"  Articles : {article_count}")
    print(f"  Total words : {total_words:,}")

    if article_count > 0:
        print(f"  Avg words/article : {total_words // article_count}")
        print(f"  Shortest : {shortest[0]} ({shortest[1]} words)")
        print(f"  Longest  : {longest[0]} ({longest[1]} words)")

    # Check index
    index = corpus / "_index.json"
    if index.exists():
        print(f"  Index    : ✓ _index.json")
    else:
        print(f"  Index    : ✗ missing")

    print(f"\n  Files:")
    for f in sorted(txt_files)[:15]:
        if not f.name.startswith("_"):
            words = len(f.read_text(encoding="utf-8").split())
            print(f"    {f.name} ({words} words)")
    if article_count > 15:
        print(f"    ... and {article_count - 15} more")

    print()
    if article_count >= 5:
        print("  ✓ Corpus looks good! Ready for embedding exercises.")
    else:
        print("  ✗ Too few articles. Try increasing --max-articles.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "./corpus"
    validate(path)
