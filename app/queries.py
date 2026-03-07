import sqlite3
import logging
from typing import List, Tuple, Any
from app.database import get_connection

logger = logging.getLogger(__name__)

def count_articles() -> int:
    """Returns the total number of articles stored in the database."""
    logger.info("Querying total article count...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            result: int = cursor.fetchone()[0]
        return result
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return 0

def get_latest_articles(limit: int = 5) -> List[Tuple[str, str, str]]:
    """Returns the newest articles based on publish date."""
    logger.info(f"Querying the {limit} latest articles...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, source, published_at
                FROM articles
                ORDER BY published_at DESC
                LIMIT ?
            """, (limit,))
            rows: List[Tuple[str, str, str]] = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return []

def get_top_sources(limit: int = 5) -> List[Tuple[str, int]]:
    """Returns the most frequent news sources in the database."""
    logger.info(f"Querying the top {limit} news sources...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, COUNT(*) as article_count
                FROM articles
                GROUP BY source
                ORDER BY article_count DESC
                LIMIT ?
            """, (limit,))
            rows: List[Tuple[str, int]] = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return []