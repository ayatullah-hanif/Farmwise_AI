# intent_response.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def get_intent_response(message: str, context=None, response_language: str = "en") -> str:
    """
    Generates AI response based on user message and conversation context using Groq model.
    Handles financial questions, farming queries, and casual conversation.
    Always returns a safe string even if the API response is malformed.
    """

    try:
        # Normalize language code
        response_language = (response_language or "en").lower()

        # 🔹 Prepare conversation context with casual conversation capability
        system_prompt = (
            "You are FarmWise AI — a friendly, approachable, and knowledgeable assistant for farmers. "
            "You can handle both professional financial/farming questions and casual conversation. "
            "When users ask about farming, finance, savings, digital payments, or cooperative models, "
            "give clear, simple, and helpful guidance. "
            "When users chat casually (greetings, jokes, or general conversation), respond warmly and naturally, "
            "like a human friend, while keeping a slight educational/farming tone if possible. "
            # language directive:
            f"Reply in the user's language. If a language is specified, reply in {response_language}. "
            # style directive:
            "Use a warm, female voice/tone, normal pace, and keep responses concise and easy to understand for low-literacy users."
        )

        context_messages = [{"role": "system", "content": system_prompt}]

        # 🔹 Add previous conversation context if available
        if context:
            for msg in context:
                context_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # 🔹 Add the new user message
        context_messages.append({"role": "user", "content": message})

        # 🔹 Send to Groq model
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=context_messages,
            temperature=0.6,
            max_tokens=500
        )

        # 🔹 Safely extract response
        choices = getattr(chat_completion, "choices", [])
        if not choices or not hasattr(choices[0], "message") or not hasattr(choices[0].message, "content"):
            raise ValueError("No valid content returned from Groq model")

        response_text = choices[0].message.content
        if not response_text or not response_text.strip():
            raise ValueError("Empty response from Groq model")

        return response_text.strip()

    except Exception as e:
        # Fallback safe response
        return (
            "⚠️ An error occurred while generating a response.\n\n"
            "💡 Tip: You can check local cooperative societies for lower-interest agricultural loans, "
            "or just say hi to chat casually with FarmWise AI!"
        )
