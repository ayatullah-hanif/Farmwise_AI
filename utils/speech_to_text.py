import os
from groq import Groq
import tempfile
from fastapi import UploadFile

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def convert_speech_to_text(file: UploadFile, language: str = None):
    """
    Convert uploaded audio to text using Groq's Whisper model.
    Handles fallback and auto-detect gracefully.
    """
    temp_path = None
    try:
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(await file.read())
            temp_path = temp_audio.name

        # Open file for transcription
        with open(temp_path, "rb") as audio_file:
            params = {"model": "whisper-large-v3", "file": audio_file}
            if language:
                params["language"] = language

            transcript = client.audio.transcriptions.create(**params)

        # Return text output
        return getattr(transcript, "text", str(transcript))

    except Exception as e:
        print(f"❌ Speech-to-text error: {e}")
        return "Error transcribing speech"

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass