# text_to_speech.py
import os
import uuid
import asyncio
import edge_tts
from langdetect import detect

AUDIO_DIR = "audio_responses"
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE_MAP = {
    "english": "en-US-AriaNeural",
    "en": "en-US-AriaNeural",
    "yoruba": "yo-NG-AbeoNeural",
    "yo": "yo-NG-AbeoNeural",
    "hausa": "ha-NG-LamiNeural",
    "ha": "ha-NG-LamiNeural",
    "swahili": "sw-KE-ZuriNeural",
    "sw": "sw-KE-ZuriNeural",
    "twi": "ak-GH-AmaNeural",
    "ak": "ak-GH-AmaNeural",
}

DEFAULT_VOICE = "en-US-AriaNeural"


async def convert_text_to_speech(text: str, lang: str = "auto") -> str:
    """
    Convert text into speech using Edge-TTS (supports African languages).
    - Respects selected language if provided.
    - Auto-detects only if lang='auto' or missing.
    """
    try:
        # Determine language
        if not lang or lang.lower() == "auto":
            try:
                detected = detect(text)
                print(f"🌍 Auto-detected language: {detected}")
                lang = detected
            except Exception:
                lang = "en"
        else:
            print(f"🎯 User-selected language: {lang}")

        # Choose appropriate voice
        voice = VOICE_MAP.get(lang.lower(), DEFAULT_VOICE)

        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Perform speech synthesis
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(filepath)

        return filepath.replace("\\", "/")

    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return None


def convert_text_to_speech_sync(text: str, lang: str = "auto") -> str:
    """Synchronous wrapper for compatibility."""
    return asyncio.run(convert_text_to_speech(text, lang))