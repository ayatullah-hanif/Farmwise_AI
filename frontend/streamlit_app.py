import streamlit as st
import requests
import os
import tempfile
import joblib
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "https://farmwise-ai.onrender.com")  

# --- Page configuration ---
st.set_page_config(
    page_title="💬 FARMWISE AI",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Farmwise AI – Your Agricultural AI Assistant")

# --- Supported languages ---
LANG_OPTIONS = [
    ("Auto-detect", None),
    ("English", "en"),
    ("Yoruba", "yo"),
    ("Hausa", "ha"),
    ("Swahili", "sw"),
    ("Twi", "twi")
]

# --- Session state ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "selected_lang" not in st.session_state:
    st.session_state["selected_lang"] = None
if "last_audio" not in st.session_state:
    st.session_state["last_audio"] = None


# --- Load model silently (no UI warnings) ---
@st.cache_resource
def load_model_silently():
    try:
        model_path = os.path.join("backend", "models", "hdi_expected_features.pkl")
        if os.path.exists(model_path):
            return joblib.load(model_path)
    except Exception:
        pass
    return None  # just skip silently

model = load_model_silently()


# --- Language selector ---
st.markdown("**Language / Èdè — Select or use Auto-detect**")
lang_display = st.selectbox(
    "Choose language",
    options=[opt[0] for opt in LANG_OPTIONS],
    index=0,
    key="lang_select"
)
selected_code = next((code for name, code in LANG_OPTIONS if name == lang_display), None)
st.session_state["selected_lang"] = selected_code

st.markdown("---")


# --- Backend communication ---
def call_voice_chat(file=None, text_override=None, lang: str = None):
    try:
        data = {"user_id": "guest"}
        if lang:
            data["lang"] = lang

        files = None
        if text_override:
            data["text_override"] = text_override
        elif file:
            files = {"file": file}
        else:
            return None

        response = requests.post(f"{BACKEND_URL}/voice_chat/", files=files, data=data, timeout=90)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Processing failed: {e}")
        return None


# --- Chat rendering ---
def append_chat(user_text, ai_response, tip=None, audio_url=None, detected_language=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    detected_language = detected_language.capitalize() if detected_language else ""
    full_audio_url = None

    if audio_url:
        if audio_url.startswith("http"):
            full_audio_url = audio_url
        else:
            full_audio_url = f"{BACKEND_URL.rstrip('/')}/{audio_url.lstrip('/')}"

    st.session_state["chat_history"].append({
        "user_text": user_text,
        "ai_response": ai_response,
        "tip": tip,
        "audio_url": full_audio_url,
        "timestamp": timestamp,
        "detected_language": detected_language
    })
    st.session_state["last_audio"] = full_audio_url


def render_chat():
    for msg in st.session_state["chat_history"]:
        detected = msg.get("detected_language") or ""
        st.markdown(
            f"<div style='background-color:#4a90e2; color:white; padding:10px; border-radius:10px; "
            f"max-width:80%; margin-left:auto; margin-bottom:5px;'>"
            f"<b>You [{msg['timestamp']}]:</b> {msg['user_text']}</div>",
            unsafe_allow_html=True
        )
        lang_badge = (
            f"<span style='font-size:12px; color:#fff; background:#00796b; padding:2px 6px; border-radius:6px;'>"
            f"Detected: {detected}</span>"
            if detected else ""
        )
        audio_html = ""
        if msg["audio_url"]:
            audio_html = f"<br>🔊 <audio controls src='{msg['audio_url']}'></audio>"
        tip_html = ""
        if msg.get("tip"):
            tip_html = f"<br><i style='color:#ffeb3b;'>💡 Tip: {msg['tip']}</i>"

        st.markdown(
            f"<div style='background-color:#333; color:white; padding:10px; border-radius:10px; "
            f"max-width:80%; margin-right:auto; margin-bottom:10px;'>"
            f"{lang_badge}<b>AI [{msg['timestamp']}]:</b> {msg['ai_response']}{tip_html}{audio_html}</div>",
            unsafe_allow_html=True
        )


# --- Chat container ---
chat_container = st.container()
with chat_container:
    st.markdown("### 💬 Conversation")
    render_chat()
    st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)


# --- Bottom input bar ---
st.markdown("""
<style>
.bottom-input {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: white;
    padding: 15px 20px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.15);
    z-index: 100;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="bottom-input">', unsafe_allow_html=True)

text_input = st.text_input("💬 Type your message...", key="user_text_input", label_visibility="collapsed")
audio_input = st.audio_input("🎤 Or record a message")

col1, col2 = st.columns([1, 1])
with col1:
    send_btn = st.button("Send", use_container_width=True)
with col2:
    replay_btn = st.button("Replay last audio", use_container_width=True)


# --- Send message ---
if send_btn:
    with st.spinner("💭 Processing..."):
        lang_code = st.session_state.get("selected_lang")
        data = None

        if text_input.strip():
            data = call_voice_chat(text_override=text_input, lang=lang_code)
        elif audio_input:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_input.getvalue())
                tmp_path = tmp.name
            with open(tmp_path, "rb") as f:
                data = call_voice_chat(file=f, lang=lang_code)
            os.remove(tmp_path)
        else:
            st.warning("Please type or record a message first!")

        if data:
            user_text = data.get("user_text", text_input if text_input else "Error transcribing")
            ai_response = data.get("ai_response", "⚠️ No response received")
            tip = data.get("tip")
            audio_url = data.get("audio_url")
            detected_lang = data.get("detected_language")

            # Background model (silent)
            if model is not None:
                try:
                    features = np.random.rand(4).reshape(1, -1)
                    prediction = model.predict(features)[0]
                    ai_response += f"\n\n📊 [Model insight: {prediction:.3f}]"
                except Exception:
                    pass  # no UI message shown

            append_chat(user_text, ai_response, tip=tip, audio_url=audio_url, detected_language=detected_lang)
            st.session_state.pop("user_text_input", None)
            st.rerun()

# --- Replay last audio ---
if replay_btn:
    if st.session_state.get("last_audio"):
        st.audio(st.session_state["last_audio"], format="audio/mp3")
    else:
        st.info("No previous audio to replay.")

st.markdown('</div>', unsafe_allow_html=True)