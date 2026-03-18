"""
Embedding Example 1: What is an Embedding?
===========================================
An embedding converts text into a list of numbers (a vector).
Similar texts get similar numbers. That's the core idea!

Run:
  source .env && python3 examples/embedding_1_what_is_embedding.py
"""

import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Convert a sentence into a vector of numbers
text = "The cat sat on the mat"
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
)
vector = result.embeddings[0].values

print(f'Text: "{text}"')
print(f"Vector has {len(vector)} dimensions")
print(f"First 5 numbers: {[round(v, 4) for v in vector[:5]]}")
print(f"Last  5 numbers: {[round(v, 4) for v in vector[-5:]]}")
print()
print("That's it! An embedding is just a list of numbers")
print("that captures the MEANING of your text.")
