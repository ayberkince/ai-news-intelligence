import sqlite3
import logging
from typing import List, Tuple
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

def get_all_sources() -> List[str]:
    """Returns a list of all unique news sources in the database."""
    logger.info("Querying all unique sources...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT source FROM articles WHERE source IS NOT NULL ORDER BY source")
            rows: List[str] = [row[0] for row in cursor.fetchall()]
        return rows
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return []

def get_latest_articles(limit: int = 5, source_filter: str = "All") -> List[Tuple[str, str, str]]:
    """Returns the newest articles, optionally filtered by source."""
    logger.info(f"Querying the {limit} latest articles (Filter: {source_filter})...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if source_filter and source_filter != "All":
                cursor.execute("""
                    SELECT title, source, published_at
                    FROM articles
                    WHERE source = ?
                    ORDER BY published_at DESC
                    LIMIT ?
                """, (source_filter, limit))
            else:
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