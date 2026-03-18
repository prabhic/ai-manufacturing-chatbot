"""
Embedding Example 3: Semantic Search
=====================================
Search by MEANING, not keywords.
"How do AI systems learn?" finds "Machine learning models learn
patterns from data" — even though they share almost no words.

Run:
  source .env && python3 examples/embedding_3_semantic_search.py
"""

import os
import math
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b)


# Our tiny "database" of documents
documents = [
    "Python is a programming language known for readability",
    "Machine learning models learn patterns from data",
    "The Eiffel Tower is in Paris, France",
    "Neural networks are inspired by the human brain",
    "Photosynthesis converts sunlight into energy in plants",
]

# Pre-compute document embeddings
doc_result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=documents,
)
doc_embs = [e.values for e in doc_result.embeddings]

# Show embeddings for each document
print("Document embeddings (first 5 & last 5 numbers):")
print("-" * 60)
for i, (doc, emb) in enumerate(zip(documents, doc_embs)):
    first5 = [round(v, 4) for v in emb[:5]]
    last5  = [round(v, 4) for v in emb[-5:]]
    print(f"  [{i}] \"{doc}\"")
    print(f"      First 5: {first5}")
    print(f"      Last  5: {last5}")
    print()

# Search!
query = "How do AI systems learn?"
query_emb = client.models.embed_content(
    model="gemini-embedding-001",
    contents=query,
).embeddings[0].values

# Show query embedding
print("Query embedding (first 5 & last 5 numbers):")
print("-" * 60)
print(f"  \"{query}\"")
print(f"      First 5: {[round(v, 4) for v in query_emb[:5]]}")
print(f"      Last  5: {[round(v, 4) for v in query_emb[-5:]]}")
print()

# Rank by similarity
ranked = sorted(
    [(cosine_similarity(query_emb, d), doc) for d, doc in zip(doc_embs, documents)],
    reverse=True,
)

print(f'Query: "{query}"\n')
print("Results (best match first):")
for score, doc in ranked:
    print(f"  {score:.4f}  {doc}")
