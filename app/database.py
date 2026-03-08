import sqlite3
import logging
import os
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
DB_PATH: str = "data/news.db"

def get_connection() -> sqlite3.Connection:
    """Creates and returns a database connection."""
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    """Initializes the SQLite database and safely migrates the schema."""
    logger.info("Initializing database schema...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. The Real Articles Table (Restored)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT,
                    published_at TEXT,
                    url TEXT UNIQUE NOT NULL
                )
            ''')
            
            # 2. The Summaries Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_text TEXT NOT NULL,
                    source_filter TEXT,
                    article_limit INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_timestamp TEXT,
                    total_articles INTEGER,
                    displayed_articles INTEGER,
                    what_matters_now TEXT,
                    summary_text TEXT,
                    dominant_topics TEXT,
                    top_sources TEXT,
                    source_filter TEXT,
                    article_limit INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
            # 3. DAY 12 MIGRATION: Safely add the topics column if it doesn't exist
            try:
                cursor.execute("ALTER TABLE summaries ADD COLUMN topics TEXT")
                logger.info("Migration successful: Added 'topics' column to summaries.")
            except sqlite3.OperationalError:
                # Column already exists, safe to ignore
                pass
                
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def save_report(report: dict) -> None:
    """Persists a generated intelligence report to the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert lists of tuples into readable strings for SQLite storage
            dominant_topics_text = ", ".join([f"{t}:{c}" for t, c in report.get("top_topics", [])])
            top_sources_text = ", ".join([f"{s}:{c}" for s, c in report.get("top_sources", [])])

            cursor.execute("""
                INSERT INTO reports (
                    report_timestamp, total_articles, displayed_articles,
                    what_matters_now, summary_text, dominant_topics,
                    top_sources, source_filter, article_limit
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.get("report_timestamp"),
                report.get("total_articles"),
                report.get("displayed_articles"),
                report.get("what_matters_now"),
                report.get("summary_text"),
                dominant_topics_text,
                top_sources_text,
                report.get("source_filter"),
                report.get("article_limit")
            ))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to save report snapshot: {e}")


def insert_articles(articles: List[Dict[str, Any]]) -> int:
    """Inserts cleaned articles into the database and returns the count of new inserts."""
    logger.info(f"Attempting to insert {len(articles)} articles into the database...")
    inserted_count: int = 0
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for article in articles:
                try:
                    cursor.execute('''
                        INSERT INTO articles (title, source, published_at, url)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        article["title"],
                        article["source"],
                        article["published_at"],
                        article["url"]
                    ))
                    inserted_count += 1
                except sqlite3.IntegrityError:
                    continue
            conn.commit()
            
        logger.info(f"Successfully inserted {inserted_count} new articles.")
        return inserted_count
    except sqlite3.Error as e:
        logger.error(f"Failed to insert articles: {e}")
        return 0
    
def save_summary(summary_text: str, topics: str, source_filter: str, article_limit: int) -> None:
    """Persists an AI-generated summary and structured topics to the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO summaries (summary_text, topics, source_filter, article_limit)
                VALUES (?, ?, ?, ?)
            """, (summary_text, topics, source_filter, article_limit))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to save summary: {e}")