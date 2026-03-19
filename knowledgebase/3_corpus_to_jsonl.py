#!/usr/bin/env python3
"""
Step 2: Convert Corpus → JSONL (for embeddings)
=================================================
Reads .txt files from the corpus and produces a .jsonl file
where each line is one "chunk" ready to be embedded.

WHY JSONL?
- One JSON object per line = easy to inspect, debug, count
- You can see exactly what will go into the vector DB
- Standard format that many tools understand

WHY CHUNK?
- Embedding models have a token limit (~2048 tokens)
- Smaller chunks = more precise search results
- Each chunk should be about one topic/paragraph

THE PIPELINE:
  .txt files  →  corpus_to_jsonl.py  →  corpus_chunks.jsonl  →  vector DB

Usage:
    cd knowledgebase
    python corpus_to_jsonl.py                          # defaults
    python corpus_to_jsonl.py --chunk-size 300          # smaller chunks
    python corpus_to_jsonl.py --corpus ./corpus --output chunks.jsonl

Output format (one JSON per line):
    {"id": "mk4s__warping_2011__0", "text": "When printing large...", "metadata": {"title": "Warping", "url": "...", "product": "mk4s", "chunk_index": 0}}
"""

import json
import sys
from pathlib import Path


# ── Step 1: Read a .txt file and extract metadata + body ────────────────

def parse_corpus_file(filepath):
    """
    Parse a corpus .txt file into metadata + body text.

    Our .txt files have this format:
        Title: Warping
        URL: https://...
        Product: mk4s
        ---
        <body text>
    """
    content = filepath.read_text(encoding="utf-8")

    # Split header from body at the "---" separator
    if "---" in content:
        header, body = content.split("---", 1)
    else:
        header, body = "", content

    # Parse header fields
    metadata = {}
    for line in header.strip().split("\n"):
        if ": " in line:
            key, value = line.split(": ", 1)
            metadata[key.lower()] = value.strip()

    return metadata, body.strip()


# ── Step 2: Split text into chunks ──────────────────────────────────────

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks of roughly `chunk_size` words.

    WHY OVERLAP?
    If a sentence spans two chunks, the overlap ensures both chunks
    contain the full context. Without overlap, you might cut a
    sentence in half and lose meaning.

    Example with chunk_size=5, overlap=2:
      "A B C D E F G H I J"
      Chunk 0: "A B C D E"
      Chunk 1: "D E F G H"     ← "D E" overlaps with chunk 0
      Chunk 2: "G H I J"       ← "G H" overlaps with chunk 1
    """
    words = text.split()

    if len(words) <= chunk_size:
        return [text]  # Small enough, no need to split

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # Move forward with overlap

    return chunks


# ── Step 3: Convert all corpus files to JSONL ───────────────────────────

def corpus_to_jsonl(corpus_dir, output_file, chunk_size=500, overlap=50):
    """
    Read all .txt files, chunk them, and write one JSONL file.

    Each line in the output is:
    {
        "id": "mk4s__warping_2011__0",    ← unique ID (filename + chunk index)
        "text": "When printing large...",   ← the text to embed
        "metadata": {
            "title": "Warping",
            "url": "https://...",
            "product": "mk4s",
            "chunk_index": 0,
            "source_file": "mk4s__warping_2011.txt"
        }
    }
    """
    corpus = Path(corpus_dir)
    txt_files = sorted(corpus.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {corpus.absolute()}")
        sys.exit(1)

    total_chunks = 0

    with open(output_file, "w", encoding="utf-8") as out:
        for filepath in txt_files:
            metadata, body = parse_corpus_file(filepath)

            if not body:
                print(f"  SKIP (empty): {filepath.name}")
                continue

            # Chunk the body text
            chunks = chunk_text(body, chunk_size=chunk_size, overlap=overlap)
            file_id = filepath.stem  # filename without .txt

            for i, chunk in enumerate(chunks):
                record = {
                    "id": f"{file_id}__{i}",
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "source_file": filepath.name,
                    },
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

            print(f"  {filepath.name} → {len(chunks)} chunk(s)")

    print(f"\nDone! Wrote {total_chunks} chunks to {output_file}")
    return total_chunks


# ── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert corpus .txt files to JSONL chunks for embeddings"
    )
    parser.add_argument(
        "--corpus", "-c", default="./corpus",
        help="Corpus directory (default: ./corpus)",
    )
    parser.add_argument(
        "--output", "-o", default="./corpus_chunks.jsonl",
        help="Output JSONL file (default: ./corpus_chunks.jsonl)",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=500,
        help="Words per chunk (default: 500)",
    )
    parser.add_argument(
        "--overlap", type=int, default=50,
        help="Overlap words between chunks (default: 50)",
    )
    args = parser.parse_args()

    print(f"Converting corpus to JSONL...")
    print(f"  Corpus dir  : {args.corpus}")
    print(f"  Chunk size  : {args.chunk_size} words")
    print(f"  Overlap     : {args.overlap} words")
    print(f"  Output      : {args.output}")
    print()

    total = corpus_to_jsonl(
        args.corpus, args.output,
        chunk_size=args.chunk_size, overlap=args.overlap,
    )

    # Show a sample record
    print(f"\nSample record (first line of {args.output}):")
    print("-" * 50)
    with open(args.output, encoding="utf-8") as f:
        first = json.loads(f.readline())
        print(f"  id:    {first['id']}")
        print(f"  text:  {first['text'][:100]}...")
        print(f"  meta:  {first['metadata']}")


if __name__ == "__main__":
    main()
