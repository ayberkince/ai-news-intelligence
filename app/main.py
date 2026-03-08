import logging
from app.pipeline import run_ingestion_pipeline

def main() -> None:
    print("Starting manual pipeline execution...")
    try:
        result = run_ingestion_pipeline()
        print(f"✅ Success! Fetched: {result['raw_count']} | Cleaned: {result['cleaned_count']} | Newly Inserted: {result['inserted_count']}")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")

if __name__ == "__main__":
    main()