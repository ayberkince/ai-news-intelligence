import logging
from app.logger import setup_logger
from app.fetch_news import fetch_news
from app.clean_data import clean_articles
from app.database import init_db, insert_articles

def main() -> None:
    logger = setup_logger()
    logger.info("Starting AI News Intelligence ingestion pipeline...")
    
    try:
        # 1. Initialize State
        init_db()
        
        # 2. Extract
        raw_articles = fetch_news()
        
        # 3. Transform
        cleaned_articles = clean_articles(raw_articles)
        
        # 4. Load (SQL)
        insert_articles(cleaned_articles)
            
        logger.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()