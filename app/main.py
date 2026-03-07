import logging
from app.fetch_news import fetch_news
from app.clean_data import clean_articles, save_articles

def main() -> None:
    logging.info("Starting AI News Intelligence ingestion pipeline...")
    
    try:
        # Step 1: Ingest
        raw_articles = fetch_news()
        
        # Step 2: Clean & Structure
        cleaned_articles = clean_articles(raw_articles)
        
        # Step 3: Persist State (Staging)
        save_articles(cleaned_articles)
            
        logging.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()