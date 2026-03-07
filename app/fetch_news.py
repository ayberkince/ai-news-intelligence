import logging
import requests
from typing import List, Dict, Any
from app.config import NEWS_API_KEY

# Configure telemetry
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

NEWS_URL: str = "https://newsapi.org/v2/top-headlines"

def fetch_news() -> List[Dict[str, Any]]:
    """Fetches top US headlines from NewsAPI."""
    if not NEWS_API_KEY:
        logging.error("NEWS_API_KEY is missing. Check your .env file.")
        raise ValueError("Missing API Key")

    params: Dict[str, str] = {
        "country": "us",
        "apiKey": NEWS_API_KEY
    }

    logging.info(f"Fetching news from {NEWS_URL}...")
    response = requests.get(NEWS_URL, params=params)

    if response.status_code != 200:
        logging.error(f"API Error: {response.status_code} - {response.text}")
        raise Exception("Failed to fetch news")

    data: Dict[str, Any] = response.json()
    articles: List[Dict[str, Any]] = data.get("articles", [])
    
    logging.info(f"Successfully fetched {len(articles)} articles.")
    return articles