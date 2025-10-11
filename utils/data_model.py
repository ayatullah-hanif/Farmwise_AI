# data_model.py
def get_personalized_response(intent: str, message: str) -> str:
    """
    Adds personalized or data-driven hints depending on intent.
    """
    if intent == "loan_inquiry":
        return "💡 Tip: You can check local cooperative societies for lower-interest agricultural loans."
    elif intent == "crop_advice":
        return "🌱 Hint: Choose drought-resistant crops during the dry season for better yield."
    elif intent == "weather_update":
        return "☀️ Reminder: Always plan irrigation based on the 7-day weather forecast."
    elif intent == "market_info":
        return "💰 Suggestion: Compare market prices in nearby towns to get the best deal."
    else:
        return "✅ Tip: Keep good farm records — they can help you qualify for grants and insurance later."