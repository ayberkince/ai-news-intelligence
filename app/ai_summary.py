import logging
from google import genai
from typing import List, Tuple
from app.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Defensive engineering: Fail fast if the key is missing
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY is missing. Check your .env file.")
    raise ValueError("Missing Gemini API Key")

# Initialize the modern GenAI client
client = genai.Client(api_key=GEMINI_API_KEY)

def summarize_articles(articles: List[Tuple[str, str, str]]) -> str:
    """Sends article headlines to Gemini and returns an AI-generated summary."""
    if not articles:
        logger.warning("No articles provided to summarize.")
        return "No news available to summarize."

    logger.info(f"Sending {len(articles)} articles to Gemini for summarization...")
    
    # Transform the structured data into a text prompt
    headlines: str = "\n".join([f"- {title} (Source: {source})" for title, source, _ in articles])
    
    prompt: str = f"""
    You are a professional financial and global news analyst.
    Summarize the key themes and events in these news headlines.
    
    Headlines:
    {headlines}
    
    Write a short, concise paragraph summarizing the main trends. Do not use bullet points.
    """
    
    try:
        # Modern SDK syntax using the latest flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        logger.info("Successfully received AI summary from Gemini.")
        return response.text
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return "Error generating AI summary."