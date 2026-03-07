import logging
from app.logger import setup_logger
from app.fetch_news import fetch_news
from app.clean_data import clean_articles, save_articles

def main() -> None:
    # Initialize observability first
    logger = setup_logger()
    logger.info("Starting AI News Intelligence ingestion pipeline...")
    
    try:
        raw_articles = fetch_news()
        cleaned_articles = clean_articles(raw_articles)
        save_articles(cleaned_articles)
            
        logger.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()