# intent_classifier.py
def classify_intent(text: str) -> str:
    """
    Simple rule-based intent classifier (can later be replaced with ML).
    """
    text_lower = text.lower()

    if any(word in text_lower for word in ["loan", "credit", "money"]):
        return "loan_inquiry"
    elif any(word in text_lower for word in ["crop", "plant", "farming", "seed"]):
        return "crop_advice"
    elif any(word in text_lower for word in ["weather", "rain", "sun", "temperature"]):
        return "weather_update"
    elif any(word in text_lower for word in ["market", "price", "sell", "buy"]):
        return "market_info"
    else:
        return "general"