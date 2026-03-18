"""
Embedding Example 2: Cosine Similarity
=======================================
How do you measure if two texts are similar?
Compare their embeddings using cosine similarity.
  1.0 = identical meaning
  0.0 = completely unrelated

Run:
  source .env && python3 examples/embedding_2_cosine_similarity.py
"""

import os
import math
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def cosine_similarity(a, b):
    """Dot product divided by magnitudes."""
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    return dot / (mag_a * mag_b)


# Three sentences: two similar, one different
sentences = [
    "The weather is cloudy today",       # [0]
    "Python is my favorite language",      # [1]
    "The weather is sunny today",          # [2]
]

# Get embeddings
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=sentences,
)
embs = [e.values for e in result.embeddings]

# Compare
print("Comparing sentences:")
for i, s in enumerate(sentences):
    print(f"  [{i}] {s}")
print()

print(f"[0] vs [1] (both about Python):  {cosine_similarity(embs[0], embs[1]):.4f}")
print(f"[0] vs [2] (Python vs weather):  {cosine_similarity(embs[0], embs[2]):.4f}")
print(f"[1] vs [2] (Python vs weather):  {cosine_similarity(embs[1], embs[2]):.4f}")
print()
print("Similar meanings → high score. Different meanings → low score.")
