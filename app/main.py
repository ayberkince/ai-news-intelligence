import logging
from app.fetch_news import fetch_news

def main() -> None:
    logging.info("Starting AI News Intelligence ingestion pipeline...")
    
    try:
        articles = fetch_news()
        
        print("\n--- Latest Headlines ---\n")
        
        for article in articles[:5]:
            title: str = article.get("title", "No Title")
            source: str = article.get("source", {}).get("name", "Unknown Source")
            print(f"- {title} ({source})")
            
        logging.info("Pipeline execution completed successfully.")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()