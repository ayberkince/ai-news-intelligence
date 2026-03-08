import logging
from app.logger import setup_logger
from app.fetch_news import fetch_news
from app.clean_data import clean_articles
from app.database import init_db, insert_articles
from app.queries import get_latest_articles
from app.ai_summary import summarize_articles

def main() -> None:
    logger = setup_logger()
    logger.info("Starting AI News Intelligence pipeline...")
    
    try:
        # 1. State Initialization
        init_db()
        
        # 2. Extract, Transform, Load (ETL)
        raw_articles = fetch_news()
        cleaned_articles = clean_articles(raw_articles)
        insert_articles(cleaned_articles)
        
        # 3. Query State
        latest_articles = get_latest_articles(limit=10)
        
        # 4. Artificial Intelligence Synthesis
        summary = summarize_articles(latest_articles)
        
        # 5. Output
        print("\n" + "="*50)
        print("🧠 AI NEWS INTELLIGENCE SUMMARY")
        print("="*50 + "\n")
        print(summary.strip())
        print("\n" + "="*50 + "\n")
            
        logger.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()