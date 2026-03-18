"""
Embedding Example 4: Document Clustering
==========================================
Group documents by topic using embeddings.
We pick topic labels ("Food", "Sports", "Space") and assign
each document to the closest topic.

Run:
  source .env && python3 examples/embedding_4_clustering.py
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


documents = [
    "Pizza is a popular Italian dish",
    "Basketball was invented in 1891",
    "Mars is the fourth planet from the Sun",
    "Sushi is Japanese food made with rice",
    "Tennis is played on a court with a net",
    "The Milky Way has billions of stars",
]

topics = ["Food", "Sports", "Space"]

# Embed documents and topics
doc_embs = [e.values for e in client.models.embed_content(
    model="gemini-embedding-001", contents=documents
).embeddings]

topic_embs = [e.values for e in client.models.embed_content(
    model="gemini-embedding-001", contents=topics
).embeddings]

# Assign each document to the closest topic
print("Document → Topic assignment:\n")
for doc, doc_emb in zip(documents, doc_embs):
    scores = [(cosine_similarity(doc_emb, t), label) for t, label in zip(topic_embs, topics)]
    best_score, best_topic = max(scores)
    print(f"  [{best_topic:>6}] {doc}  ({best_score:.4f})")
