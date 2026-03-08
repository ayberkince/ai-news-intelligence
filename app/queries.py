import sqlite3
import logging
from typing import List, Tuple
from app.database import get_connection
from typing import List, Tuple, Optional, Any



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
    
from typing import List, Tuple, Optional # Make sure Optional is imported at the top!

def get_latest_summary() -> Optional[Tuple[str, str, str, int, str]]:
    """Retrieves the most recently saved AI summary and topics."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Notice we added 'topics' to the SELECT statement
            cursor.execute("""
                SELECT summary_text, topics, source_filter, article_limit, created_at
                FROM summaries
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        logger.error(f"Database query failed: {e}")
        return None

def get_summary_history(limit: int = 20) -> List[Tuple[int, str, str, str, int, str]]:
    """Retrieves a list of historical AI summaries and topics."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Notice we added 'topics' to the SELECT statement
            cursor.execute("""
                SELECT id, summary_text, topics, source_filter, article_limit, created_at
                FROM summaries
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch summary history: {e}")
        return []
    
def get_summary_topics(limit: int = 50) -> List[Tuple[str, str]]:
    """Retrieves stored topics from recent summaries for trend analysis."""
    logger.info(f"Querying topics from the last {limit} summaries...")
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT topics, created_at
                FROM summaries
                WHERE topics IS NOT NULL AND topics != ''
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch topic history: {e}")
        return []