"""
Embedding Example 5: Word Relationships
========================================
Embeddings capture relationships between words.
Related words (king↔queen) score high.
Unrelated words (king↔banana) score low.

Run:
  source .env && python3 examples/embedding_5_word_relationships.py
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


# Word pairs to compare
pairs = [
    ("king", "queen"),
    ("dog", "puppy"),
    ("happy", "sad"),
    ("Python", "HTML"),
    ("yellow banana", "banana"),
]

# Get embeddings for all unique words
all_words = list({w for pair in pairs for w in pair})
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=all_words,
)
embs = {word: e.values for word, e in zip(all_words, result.embeddings)}

# Compare each pair
print("Word pair similarities:\n")
for a, b in pairs:
    score = cosine_similarity(embs[a], embs[b])
    bar = "█" * int(score * 20)
    print(f"  {a:>12} ↔ {b:<12}  {score:.4f}  {bar}")

print()
print("Related words score high, unrelated words score low.")
