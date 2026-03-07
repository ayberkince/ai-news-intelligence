import logging
import os

def setup_logger() -> logging.Logger:
    """Configures application-wide logging to a file and terminal."""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ],
        force=True  # <--- THIS IS THE MAGIC FIX
    )
    
    return logging.getLogger(__name__)