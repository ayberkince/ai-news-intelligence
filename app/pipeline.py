import logging
from typing import Dict
from app.logger import setup_logger
from app.fetch_news import fetch_news
from app.clean_data import clean_articles
from app.database import init_db, insert_articles

def run_ingestion_pipeline() -> Dict[str, int]:
    """Executes the full ETL pipeline and returns execution metrics."""
    logger = setup_logger()
    logger.info("Pipeline execution triggered via Orchestrator.")
    
    # 1. Initialize State
    init_db()
    
    # 2. Extract & Transform
    raw_articles = fetch_news()
    cleaned_articles = clean_articles(raw_articles)
    
    # 3. Load
    inserted_count = insert_articles(cleaned_articles)
    
    return {
        "raw_count": len(raw_articles),
        "cleaned_count": len(cleaned_articles),
        "inserted_count": inserted_count
    }