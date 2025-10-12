# language_utils.py
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # for consistent results

def detect_language(text: str) -> str:
    """
    Detects the language of a given text. Returns ISO-like code or 'unknown'.
    """
    try:
        lang = detect(text)
        return lang
    except Exception:
        return "unknown"
