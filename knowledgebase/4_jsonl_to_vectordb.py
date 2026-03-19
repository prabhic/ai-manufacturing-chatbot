#!/usr/bin/env python3
"""
Step 3: Load JSONL → Embed → Store in Vector DB
=================================================
Reads the .jsonl file, generates embeddings with Gemini,
and stores everything in ChromaDB (a simple local vector DB).

Then you can SEARCH the knowledge base by meaning!

THE FULL PIPELINE:
  scraper.py → corpus_to_jsonl.py → jsonl_to_vectordb.py → SEARCH!

Usage:
    cd knowledgebase
    source ../.env
    python jsonl_to_vectordb.py                           # defaults
    python jsonl_to_vectordb.py --query "nozzle clogged"  # search immediately

Prerequisites:
    pip install google-genai chromadb
"""

import json
import math
import os
import sys
from pathlib import Path

try:
    import chromadb
    from google import genai
except ImportError:
    print("Install dependencies:")
    print("  pip install google-genai chromadb")
    sys.exit(1)


# ── Config ──────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "gemini-embedding-001"
COLLECTION_NAME = "prusa_kb"
BATCH_SIZE = 20  # Embed this many chunks per API call


# ── Step 1: Load chunks from JSONL ─────────────────────────────────────

def load_jsonl(filepath):
    """
    Read the JSONL file. Each line is one chunk.
    Returns list of dicts with 'id', 'text', 'metadata'.
    """
    chunks = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


# ── Step 2: Embed + Store in ChromaDB ──────────────────────────────────

def build_vectordb(chunks, db_path="./vectordb"):
    """
    Embed all chunks with Gemini and store in ChromaDB.

    ChromaDB stores:
      - id:        unique chunk ID
      - document:  the text (for display in search results)
      - embedding: the vector (for similarity search)
      - metadata:  title, url, product (for filtering)
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY environment variable")
        print("  source ../.env")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Create ChromaDB (stores data in ./vectordb/ folder)
    chroma = chromadb.PersistentClient(path=db_path)

    # Delete old collection if it exists, so we start fresh
    try:
        chroma.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = chroma.create_collection(name=COLLECTION_NAME)

    print(f"\nEmbedding {len(chunks)} chunks (batch size={BATCH_SIZE})...")

    # Process in batches (API has limits on how many texts per call)
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]

        texts = [c["text"] for c in batch]
        ids = [c["id"] for c in batch]
        metadatas = []
        for c in batch:
            # ChromaDB metadata must be flat (no nested dicts/lists)
            meta = {
                "title": c["metadata"].get("title", ""),
                "url": c["metadata"].get("url", ""),
                "product": c["metadata"].get("product", ""),
                "source_file": c["metadata"].get("source_file", ""),
                "chunk_index": c["metadata"].get("chunk_index", 0),
            }
            metadatas.append(meta)

        # Call Gemini to get embeddings
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
        )
        embeddings = [e.values for e in result.embeddings]

        # Store in ChromaDB
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        done = min(i + BATCH_SIZE, len(chunks))
        print(f"  [{done}/{len(chunks)}] embedded and stored")

    print(f"\nVector DB saved to: {db_path}/")
    print(f"Collection '{COLLECTION_NAME}' has {collection.count()} chunks")
    return collection


# ── Step 3: Search! ────────────────────────────────────────────────────

def search(query, db_path="./vectordb", n_results=3):
    """
    Search the vector DB by meaning.

    HOW IT WORKS:
    1. Embed the query text using the same Gemini model
    2. ChromaDB finds the closest vectors (most similar chunks)
    3. Return the matching text + metadata
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Embed the query
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
    )
    query_embedding = result.embeddings[0].values

    # Open existing DB and search
    chroma = chromadb.PersistentClient(path=db_path)
    collection = chroma.get_collection(name=COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    # Display results
    print(f'\nQuery: "{query}"')
    print(f"Top {n_results} results:")
    print("-" * 50)

    for i in range(len(results["ids"][0])):
        doc = results["documents"][0][i]
        meta = results["metadatas"][0][i]
        dist = results["distances"][0][i]
        print(f"\n  [{i+1}] {meta.get('title', 'Unknown')} (distance: {dist:.4f})")
        print(f"      Source: {meta.get('source_file', '')}")
        # Show first 200 chars of the chunk
        preview = doc[:200].replace("\n", " ")
        print(f"      Text: {preview}...")


# ── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Embed JSONL chunks and store in ChromaDB vector database"
    )
    parser.add_argument(
        "--input", "-i", default="./corpus_chunks.jsonl",
        help="Input JSONL file (default: ./corpus_chunks.jsonl)",
    )
    parser.add_argument(
        "--db", "-d", default="./vectordb",
        help="Vector DB path (default: ./vectordb)",
    )
    parser.add_argument(
        "--query", "-q", default=None,
        help="Search query (optional — if set, skips building and just searches)",
    )
    args = parser.parse_args()

    if args.query:
        # Just search an existing DB
        search(args.query, db_path=args.db)
    else:
        # Build the DB from JSONL
        jsonl_path = Path(args.input)
        if not jsonl_path.exists():
            print(f"JSONL file not found: {jsonl_path}")
            print(f"Run corpus_to_jsonl.py first!")
            sys.exit(1)

        chunks = load_jsonl(jsonl_path)
        print(f"Loaded {len(chunks)} chunks from {jsonl_path}")

        collection = build_vectordb(chunks, db_path=args.db)

        # Demo search
        print("\n" + "=" * 50)
        print("Let's test with a search!")
        print("=" * 50)
        search("How do I fix warping?", db_path=args.db)

        print(f"\nTo search again:")
        print(f'  python jsonl_to_vectordb.py --query "your question here"')


if __name__ == "__main__":
    main()
