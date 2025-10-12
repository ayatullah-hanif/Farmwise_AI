# logger.py
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "interactions.log")

def log_interaction(message, response, language="en", intent="unknown"):
    """
    Log each interaction for analytics and personalization.
    """
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] LANG: {language} | INTENT: {intent}\n"
            f"User: {message}\n"
            f"AI: {response}\n\n"
        )
        f.write(log_entry)