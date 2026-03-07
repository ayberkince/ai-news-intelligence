import json
import logging
from typing import List, Dict, Any

def clean_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extracts and formats required fields from raw NewsAPI data."""
    logging.info(f"Cleaning {len(articles)} raw articles...")
    cleaned: List[Dict[str, Any]] = []

    for article in articles:
        # We use .get() to avoid KeyError if the API changes its response shape
        cleaned.append({
            "title": article.get("title", "No Title"),
            "source": article.get("source", {}).get("name", "Unknown Source"),
            "published_at": article.get("publishedAt", "Unknown Date"),
            "url": article.get("url", "")
        })

    logging.info(f"Successfully cleaned {len(cleaned)} articles.")
    return cleaned

def save_articles(articles: List[Dict[str, Any]], path: str = "data/news.json") -> None:
    """Saves structured article data to a JSON file."""
    logging.info(f"Saving structured data to {path}...")
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2)
        logging.info("Data saved successfully.")
    except IOError as e:
        logging.error(f"Failed to save articles to {path}: {e}")
        raise