import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY: str | None = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")