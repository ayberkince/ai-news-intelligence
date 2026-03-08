import google.generativeai as genai
from app.config import GEMINI_API_KEY
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-2.5-flash")

def summarize_articles(articles):
    if not articles:
        return {"summary": "No news available.", "topics": []}

    headlines = "\n".join([f"- {title} ({source})" for title, source, _ in articles])

    prompt = f"""
    You are a financial news aggregator. Analyze these headlines and return a JSON object.
    
    JSON Structure:
    {{
      "summary": "A 2-3 sentence overview of these events.",
      "topics": ["Topic1", "Topic2", "Topic3"]
    }}

    Headlines:
    {headlines}
    """

    # NEW: Safety Settings to prevent the 'System Error' on sensitive news
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"},
            safety_settings=safety_settings
        )
        
        # Clean up the response text
        raw_text = response.text.strip()
        parsed = json.loads(raw_text)
        
        return {
            "summary": parsed.get("summary", "Summary generation successful."),
            "topics": parsed.get("topics", ["Market Update"])
        }
        
    except Exception as e:
        logger.error(f"AI Generation Failed: {e}")
        # If it still fails, let's see why
        return {
            "summary": f"**System Error:** {str(e)}",
            "topics": ["System Error"]
        }