import logging
from app.logger import setup_logger
from app.fetch_news import fetch_news
from app.clean_data import clean_articles
from app.database import init_db, insert_articles
from app.queries import count_articles, get_latest_articles, get_top_sources

def main() -> None:
    logger = setup_logger()
    logger.info("Starting AI News Intelligence ingestion pipeline...")
    
    try:
        # --- WRITE PATH (Ingestion) ---
        init_db()
        raw_articles = fetch_news()
        cleaned_articles = clean_articles(raw_articles)
        insert_articles(cleaned_articles)
        
        # --- READ PATH (Analytics) ---
        print("\n" + "="*50)
        print("📊 AI NEWS INTELLIGENCE REPORT")
        print("="*50)
        
        total = count_articles()
        print(f"\nTotal Stored Articles: {total}\n")
        
        print("🔥 Latest Headlines:")
        for title, source, published_at in get_latest_articles(5):
            print(f"  - [{source}] {title}")
            
        print("\n📈 Top Sources:")
        for source, count in get_top_sources(3):
            print(f"  - {source}: {count} articles")
            
        print("\n" + "="*50 + "\n")
            
        logger.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()