import json
import os
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

def clean_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validates, deduplicates, and formats raw article data."""
    cleaned: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set() # O(1) lookup time for deduplication

    for article in articles:
        title: str | None = article.get("title")
        source: str | None = article.get("source", {}).get("name")
        published_at: str | None = article.get("publishedAt")
        url: str | None = article.get("url")

        # 1. Validation: Skip incomplete records
        if not title or not source or not url:
            continue

        # 2. Deduplication: Skip repeated URLs
        if url in seen_urls:
            continue

        seen_urls.add(url)

        cleaned.append({
            "title": title.strip(),
            "source": source.strip(),
            "published_at": published_at,
            "url": url.strip()
        })

    logger.info(f"Filtered {len(articles)} raw articles down to {len(cleaned)} valid articles.")
    return cleaned

def save_articles(articles: List[Dict[str, Any]], path: str = "data/news.json") -> None:
    """Saves structured article data securely to a JSON file."""
    # Defensive engineering: ensure the exact directory path exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved {len(articles)} articles to {path}.")
    except IOError as e:
        logger.error(f"Failed to save articles to {path}: {e}")
        raise