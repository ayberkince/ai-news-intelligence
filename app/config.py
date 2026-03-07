import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

# Type hint to explicitly state this should be a string (or None)
NEWS_API_KEY: str | None = os.getenv("NEWS_API_KEY")