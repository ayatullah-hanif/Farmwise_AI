import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from fastapi.staticfiles import StaticFiles
from utils.intent_response import get_intent_response
from utils.speech_to_text import convert_speech_to_text
from utils.text_to_speech import convert_text_to_speech
from utils.language_utils import detect_language
from utils.intent_classifier import classify_intent
from utils.data_model import get_personalized_response
from utils.memory_manager import remember_message, get_conversation_context
from utils.logger import log_interaction
import joblib
import pickle
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


app = FastAPI(
    title="FarmWise AI - Financial Assistant",
    description="Voice-enabled AI financial assistant for users.",
    version="2.2.0"
)

# --- Serve static audio directory ---
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_responses")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
app.mount("/audio_responses", StaticFiles(directory=AUDIO_DIR), name="audio_responses")


@app.get("/")
def home():
    return {"message": "Welcome to FarmWise AI 💰📊"}


# --- Language Mappings ---
LANGUAGE_MAP_FULL = {
    "en": "english",
    "yo": "yoruba",
    "ha": "hausa",
    "sw": "swahili",
    "twi": "twi"
}

ISO_MAP = {
    "english": "en",
    "yoruba": "yo",
    "hausa": "ha",
    "swahili": "sw",
    "twi": "ak"  # some systems use ak for Twi/Akan
}


def normalize_language(lang: Optional[str]) -> str:
    """Normalize any code (en, yo, etc.) to full language name (english, yoruba...)."""
    if not lang:
        return "english"
    lang = lang.lower().strip()
    return LANGUAGE_MAP_FULL.get(lang, lang) if len(lang) <= 3 else lang


# --- Multilingual financial tips & NLP-based detection ---
TIPS = {
    "savings": {
        "english": ["Try to save at least 10% of your income each month.",
                    "Keep an emergency fund for unexpected expenses."],
        "yoruba": ["Gbiyanju lati fi o kere ju 10% ti owo-wiwọle rẹ pamọ lododun.",
                    "Ṣe eto ajeseku pajawiri fun awọn inawo airotẹlẹ."],
        "hausa": ["Yi ƙoƙarin ajiye akalla 10% na kudin shiga kowane wata.",
                   "Samu asusun gaggawa don kashe kuɗi na ba zato ba tsammani."],
        "swahili": ["Jaribu kuweka angalau 10% ya mapato yako kila mwezi.",
                     "Hifadhi mfuko wa dharura kwa matumizi yasiyotegemewa."],
        "twi": ["Sɔ hwɛ sɛ wode w’akɔmɔde 10% si akyɛde biara mu.",
                 "Fa sika akyɛde bɔ ho ban wɔ nsɛm a ɛda hɔ no."]
    },
    "credit": {
        "english": ["Always repay loans on time to maintain a good credit record.",
                    "Check the interest rate before taking any loan."],
        "yoruba": ["Ma awọn awin pada ni akoko lati ni igbasilẹ kirẹditi to dara.",
                    "Ṣayẹwo oṣuwọn anfani ṣaaju gbigba awin kankan."],
        "hausa": ["Koyaushe biya bashi akan lokaci don kiyaye tarihin bashi mai kyau.",
                   "Duba ribar kudin ruwa kafin karɓar kowane bashi."],
        "swahili": ["Lipa mikopo kwa wakati ili kudumisha rekodi nzuri ya mikopo.",
                     "Angalia kiwango cha riba kabla ya kuchukua mkopo wowote."],
        "twi": ["Tua ka wɔ bere mu sɛnea ɛbɛyɛ a wo credit record bɛyɛ papa.",
                 "Hwɛ interest rate ansa na wopɛ sɛ wopaw no."]
    },
    "investment": {
        "english": ["Diversify your investments to reduce risk.",
                    "Start small and learn as you invest."],
        "yoruba": ["Ṣe oniruuru awọn idoko-owo rẹ lati dinku ewu.",
                    "Bẹrẹ kekere ki o kọ ẹkọ bi o ṣe n ṣe idoko-owo."],
        "hausa": ["Yi bambanta zuba jari don rage haɗari.",
                   "Fara da ƙanana ka koya yayin da kake saka jari."],
        "swahili": ["Tenga uwekezaji wako ili kupunguza hatari.",
                     "Anza kidogo na jifunze unapowekeza."],
        "twi": ["Bɔ w’adesua akyirikyiri mu de sɛe risk no.",
                 "Fi ase kakra na sua sɛnea wode sika gu so."]
    },
    "digital_finance": {
        "english": ["Use strong passwords for your mobile banking apps.",
                    "Always verify transactions before confirming."],
        "yoruba": ["Lo awọn ọrọigbaniwọle to lagbara fun awọn ohun elo banki alagbeka rẹ.",
                    "Ṣayẹwo gbogbo awọn iṣowo ṣaaju gbigba wọn."],
        "hausa": ["Yi amfani da kalmomin sirri masu ƙarfi don aikace-aikacen banki na wayar hannu.",
                   "Koyaushe tabbatar da ma'amaloli kafin tabbatarwa."],
        "swahili": ["Tumia nywila imara kwa programu zako za benki za simu.",
                     "Daima hakikisha miamala kabla ya kuthibitisha."],
        "twi": ["Fa password den wɔ mobile banking apps mu.",
                 "Hwɛ transactions no ansa na wopɛ sɛ wopaw no."]
    },
    "general": {
        "english": ["Keep learning about financial management.",
                    "Track your income and expenses regularly."],
        "yoruba": ["Tẹsiwaju lati kọ ẹkọ nipa iṣakoso owo.",
                    "Tẹle owo-wiwọle ati awọn inawo rẹ nigbagbogbo."],
        "hausa": ["Ci gaba da koyon sarrafa kudi.",
                   "Bi dididdiga kudin shiga da fita akai-akai."],
        "swahili": ["Endelea kujifunza kuhusu usimamizi wa fedha.",
                     "Fuatilia mapato na matumizi yako mara kwa mara."],
        "twi": ["Kɔ so sua financial management.",
                 "Di w’akɔmɔde ne nsesa ho adwene daa."]
    }
}

TOPIC_DESCRIPTIONS = {
    "savings": "saving money, emergency funds, saving accounts, saving tips",
    "credit": "loans, credit score, repayment, interest rates, borrowing",
    "investment": "investing money, stocks, bonds, diversify, portfolio",
    "digital_finance": "mobile banking, digital wallet, online transactions, fintech",
    "general": "financial literacy, budgeting, income and expenses, money management"
}

# Build topic model
vectorizer = TfidfVectorizer()
topic_matrix = vectorizer.fit_transform(TOPIC_DESCRIPTIONS.values())
TOPIC_KEYS = list(TOPIC_DESCRIPTIONS.keys())


def get_tip_nlp(user_input: str, lang: str) -> str:
    """Generate a multilingual financial tip based on message topic and detected language."""
    try:
        normalized_lang = normalize_language(lang)
        user_vec = vectorizer.transform([user_input])
        similarities = cosine_similarity(user_vec, topic_matrix)
        best_idx = similarities.argmax()
        best_topic = TOPIC_KEYS[best_idx]
        tips_for_topic = TIPS.get(best_topic, TIPS["general"])
        return random.choice(tips_for_topic.get(normalized_lang, tips_for_topic["english"]))
    except Exception as e:
        print(f"⚠️ get_tip_nlp error: {e}")
        return random.choice(TIPS["general"]["english"])


# --- Core Message Processor ---
async def process_message(user_text: str, user_id: str = "guest", lang_hint: Optional[str] = None):
    try:
        if lang_hint:
            response_lang = normalize_language(lang_hint)
            detected_language = response_lang
        else:
            detected_language = detect_language(user_text)
            response_lang = normalize_language(detected_language)

        intent = classify_intent(user_text)
        context = get_conversation_context(user_id)

        response_text = await get_intent_response(user_text, context=context, response_language=response_lang)
        personalized_hint = get_personalized_response(intent, user_text)
        full_response = f"{response_text}\n\n{personalized_hint}"

        remember_message(user_id, "user", user_text)
        remember_message(user_id, "assistant", full_response)

        try:
            audio_path = await convert_text_to_speech(full_response, lang=response_lang)
            audio_url = f"audio_responses/{os.path.basename(audio_path)}" if audio_path else None
        except Exception as tts_error:
            print(f"⚠️ TTS generation failed: {tts_error}")
            audio_url = None

        log_interaction(user_text, full_response, language=response_lang, intent=intent)
        tip = get_tip_nlp(user_text, lang=response_lang)

        return {
            "detected_language": detected_language,
            "intent": intent,
            "user_text": user_text,
            "ai_response": full_response,
            "tip": tip,
            "audio_url": audio_url
        }

    except Exception as e:
        print(f"❌ process_message error: {e}")
        return {"error": str(e)}


# --- Voice Chat Endpoint ---
@app.post("/voice_chat/")
async def full_voice_chat(
    file: Optional[UploadFile] = None,
    user_id: str = Form("guest"),
    text_override: Optional[str] = Form(None),
    lang: Optional[str] = Form(None)
):
    user_text = None

    if text_override:
        user_text = text_override
    elif file:
        transcription_lang = normalize_language(lang)
        iso_lang = ISO_MAP.get(transcription_lang, "en")
        try:
            user_text = await convert_speech_to_text(file, language=iso_lang)
            if not user_text or "Error transcribing" in user_text:
                print("⚠️ Retrying with auto-detect...")
                user_text = await convert_speech_to_text(file, language=None)
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            user_text = "Error transcribing speech"
    else:
        return JSONResponse(
            status_code=400,
            content={"detail": "No input provided. Provide text_override or file."}
        )

    result = await process_message(user_text, user_id=user_id, lang_hint=lang)
    return result


# --- Text-only Chat Endpoint ---
class ChatRequest(BaseModel):
    user_id: Optional[str] = "guest"
    text: str
    lang: Optional[str] = None


@app.post("/chat/")
async def chat_text(req: ChatRequest):
    if not req.text:
        return JSONResponse(status_code=400, content={"detail": "No text provided."})
    result = await process_message(req.text, user_id=req.user_id or "guest", lang_hint=req.lang)
    return result


# --- HDI CATEGORY PREDICTION MODEL INTEGRATION ---
model_path = os.path.join(os.path.dirname(__file__), "models", "hdi_classifier.pkl")

hdi_model = None
if os.path.exists(model_path):
    try:
        try:
            hdi_model = joblib.load(model_path)
        except Exception:
            with open(model_path, "rb") as f:
                hdi_model = pickle.load(f)
        print("✅ HDI model loaded successfully from:", model_path)
    except Exception as e:
        print(f"⚠️ Failed to load HDI model: {e}")
else:
    print(f"⚠️ HDI model not found at {model_path}. Please ensure the file exists in backend/models.")


EXPECTED_FEATURES = [
    "GNI_per_capita",
    "Expected_years_schooling_male",
    "Expected_years_schooling_female",
    "HDI_male",
    "HDI_female",
    "Estimated_GNI_male",
    "Estimated_GNI_female",
    "Adult_population"
]


class HDIInput(BaseModel):
    GNI_per_capita: float
    Expected_years_schooling_male: float
    Expected_years_schooling_female: float
    HDI_male: float
    HDI_female: float
    Estimated_GNI_male: float
    Estimated_GNI_female: float
    Adult_population: float


@app.post("/predict_hdi/")
async def predict_hdi(data: HDIInput):
    if hdi_model is None:
        return JSONResponse(status_code=500, content={"error": "HDI model not loaded."})
    try:
        input_df = pd.DataFrame([data.dict()])
        missing = [col for col in EXPECTED_FEATURES if col not in input_df.columns]
        if missing:
            return JSONResponse(
                status_code=400,
                content={"error": f"Missing required features: {missing}"}
            )
        prediction = hdi_model.predict(input_df)[0]
        proba = hdi_model.predict_proba(input_df).max()
        return {
            "prediction": prediction,
            "confidence": round(float(proba), 3),
            "features_used": EXPECTED_FEATURES
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})