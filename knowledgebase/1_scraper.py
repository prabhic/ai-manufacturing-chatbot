#!/usr/bin/env python3
"""
Prusa Knowledge Base Scraper — Educational Version
====================================================
Scrapes help.prusa3d.com articles and saves them as plain text files.
These text files become your "corpus" for embedding & RAG exercises.

THE 3-STEP FLOW:
  1. DISCOVER — Find article URLs on the product page
  2. SCRAPE   — Download each article, extract clean text
  3. SAVE     — Write one .txt file per article into corpus/

Usage:
    cd knowledgebase
    python scraper.py                        # Scrape MK4S (default)
    python scraper.py --product core-one     # Scrape a different product
    python scraper.py --max-articles 10      # Limit for quick testing

Output:
    corpus/
    ├── mk4s__first-layer-calibration.txt
    ├── mk4s__hotend-clog.txt
    └── ...
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Install dependencies first:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)


# ── Configuration ───────────────────────────────────────────────────────

BASE_URL = "https://help.prusa3d.com"

# Be polite: identify yourself and wait between requests
HEADERS = {"User-Agent": "Educational-Scraper/1.0 (student project)"}
DELAY_SECONDS = 1.5  # pause between HTTP requests

# Products we can scrape (slug → page path)
PRODUCTS = {
    "mk4s":     "/product/mk4s",
    "mk4":      "/product/mk4",
    "core-one": "/product/core-one",
    "xl":       "/product/xl",
    "mini-2":   "/product/mini-2",
}


# ── Step 1: DISCOVER article URLs ──────────────────────────────────────

def discover_articles(product_slug, max_articles=50):
    """
    Visit the product page and find all article links.

    HOW IT WORKS:
    - Fetch the product page HTML
    - Find every <a> tag whose href contains "/article/"
    - Return a list of full URLs (no duplicates)
    """
    product_path = PRODUCTS.get(product_slug)
    if not product_path:
        print(f"Unknown product: {product_slug}")
        print(f"Available: {', '.join(PRODUCTS.keys())}")
        sys.exit(1)

    url = BASE_URL + product_path
    print(f"\n1. DISCOVERING articles at: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Collect unique article URLs
    seen = set()
    articles = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/article/" in href:
            full_url = urljoin(BASE_URL, href)
            if full_url not in seen:
                seen.add(full_url)
                title_hint = a_tag.get_text(strip=True)
                articles.append({"url": full_url, "title_hint": title_hint})

    articles = articles[:max_articles]
    print(f"   Found {len(articles)} articles")
    return articles


# ── Step 2: SCRAPE one article ─────────────────────────────────────────

def scrape_article(url):
    """
    Download a single article and extract clean text.

    HOW IT WORKS:
    - Fetch the page HTML
    - Find the <h1> title
    - Find the main content area (article, main, or largest div)
    - Strip HTML tags → keep only readable text
    - Return a dict with title, url, and clean text

    WHY CLEAN TEXT?
    Embeddings work on text, not HTML. We need to remove all the
    <div>, <span>, <script> noise and keep just the words.
    """
    time.sleep(DELAY_SECONDS)  # Be polite to the server

    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        print(f"   SKIP (HTTP {resp.status_code}): {url}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "Untitled"

    # Find main content area
    content = (
        soup.find("div", class_="article-content")
        or soup.find("article")
        or soup.find("main")
    )
    if not content:
        # Fallback: pick the div with the most text
        divs = soup.find_all("div")
        if divs:
            content = max(divs, key=lambda d: len(d.get_text()))

    if not content:
        return None

    # Convert HTML → clean text (one line per paragraph/heading)
    clean_text = html_to_text(content)

    if len(clean_text.split()) < 20:
        return None  # Skip nearly-empty pages

    return {"title": title, "url": url, "text": clean_text}


def html_to_text(element):
    """
    Convert an HTML element to clean readable text.

    Keeps:
      - Headings as "## Heading"
      - Paragraphs as plain text
      - List items as "- item"
    Removes:
      - All HTML tags, scripts, styles
    """
    # Remove script and style elements
    for tag in element.find_all(["script", "style"]):
        tag.decompose()

    lines = []
    for child in element.descendants:
        if child.name == "h1":
            lines.append(f"\n# {child.get_text(strip=True)}\n")
        elif child.name in ("h2", "h3", "h4"):
            prefix = "#" * int(child.name[1])
            lines.append(f"\n{prefix} {child.get_text(strip=True)}\n")
        elif child.name == "p":
            text = child.get_text(strip=True)
            if text:
                lines.append(text)
        elif child.name == "li":
            lines.append(f"- {child.get_text(strip=True)}")

    # Deduplicate consecutive identical lines
    result = []
    for line in lines:
        if not result or line != result[-1]:
            result.append(line)

    return "\n".join(result)


# ── Step 3: SAVE to corpus ─────────────────────────────────────────────

def save_to_corpus(article, product_slug, output_dir):
    """
    Save one article as a .txt file.

    File format:
        Title: <title>
        URL: <source url>
        Product: <product>
        ---
        <article text>

    WHY THIS FORMAT?
    When we later embed these documents, the title and metadata
    at the top help the embedding capture what the article is about.
    """
    # Create a safe filename from the URL
    article_id = article["url"].split("/")[-1].split("?")[0]
    article_id = re.sub(r"[^a-zA-Z0-9_-]", "_", article_id)
    filename = f"{product_slug}__{article_id}.txt"

    filepath = output_dir / filename
    content = (
        f"Title: {article['title']}\n"
        f"URL: {article['url']}\n"
        f"Product: {product_slug}\n"
        f"---\n\n"
        f"{article['text']}\n"
    )
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ── Main ────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape Prusa KB articles into text files for embeddings"
    )
    parser.add_argument(
        "--product", "-p", default="mk4s",
        help="Product to scrape (default: mk4s)",
    )
    parser.add_argument(
        "--max-articles", "-m", type=int, default=50,
        help="Max articles to scrape (default: 50)",
    )
    parser.add_argument(
        "--output", "-o", default="./corpus",
        help="Output directory (default: ./corpus)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Discover
    articles = discover_articles(args.product, args.max_articles)

    # Step 2 & 3: Scrape each article and save
    print(f"\n2. SCRAPING articles (with {DELAY_SECONDS}s delay between requests)...")
    saved = []
    for i, art_info in enumerate(articles):
        url = art_info["url"]
        hint = art_info.get("title_hint", "")[:60]
        print(f"   [{i+1}/{len(articles)}] {hint or url}")

        article = scrape_article(url)
        if article:
            path = save_to_corpus(article, args.product, output_dir)
            saved.append(article)
            word_count = len(article["text"].split())
            print(f"           ✓ Saved ({word_count} words)")
        else:
            print(f"           ✗ Skipped (empty or failed)")

    # Summary
    print(f"\n3. DONE!")
    print(f"   Articles saved : {len(saved)}")
    print(f"   Output folder  : {output_dir.absolute()}")
    print(f"   Total words    : {sum(len(a['text'].split()) for a in saved)}")
    print(f"\n   Next step: use these .txt files to create embeddings!")
    print(f"   See examples/embedding_3_semantic_search.py for how.")

    # Save a simple index
    index = [{"title": a["title"], "url": a["url"]} for a in saved]
    index_path = output_dir / "_index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"   Index saved to : {index_path.name}")


if __name__ == "__main__":
    main()
