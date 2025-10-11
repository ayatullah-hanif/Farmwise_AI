# 🌾 Farmwise AI Assistant

**Farmwise AI Assistant** is an intelligent, multilingual voice-and-text-based assistant designed to enhance **financial inclusion** for farmers and rural users.  
It provides insightful responses, practical tips, and localized support through an integrated **FastAPI backend** and **Streamlit frontend**.

---

## 🚀 Features

- 🎙️ **Voice & Text Chat** — Talk or type naturally in your preferred language.
- 🌍 **Multilingual Support** — English, Yoruba, Hausa, Swahili, and Twi.
- 🧠 **AI-Powered Understanding** — Smart intent detection and language-based NLP tips.
- 🗣️ **Speech Synthesis** — Converts responses back to audio using Text-to-Speech (TTS).
- 🔄 **Seamless Integration** — FastAPI backend handles processing; Streamlit frontend manages user interaction.
- 💡 **Dynamic Tips** — Provides financial and inclusion-related suggestions tailored to user queries and detected language.

---

## 🧩 Project Structure

📦 farmwise-ai-assistant
├── main.py # FastAPI backend (core logic, endpoints)
├── intent_response.py # NLP + Intent classification
├── speech_to_text.py # Speech recognition module
├── text_to_speech.py # Text-to-speech module
├── streamlit_app.py # Streamlit frontend UI
├── models/
│ └── hdi_predictor.pkl # Saved ML model
├── requirements.txt # Dependencies
└── README.md # Project documentation


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/farmwise-ai-assistant.git
cd farmwise-ai-assistant


python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Mac/Linux


pip install -r requirements.txt

uvicorn main:app --reload

streamlit run streamlit_app.py

🧠 Core Functionality
Module	Description
main.py	Hosts FastAPI routes for text & voice chat, processes language detection, returns AI responses and tips.
intent_response.py	Handles NLP-based intent recognition and dynamic tip generation.
speech_to_text.py	Converts voice input to text using speech recognition.
text_to_speech.py	Converts AI responses to voice for playback in the UI.
streamlit_app.py	Builds the user interface for interaction and displays chat bubbles + audio playback.

💬 Supported Languages

🇬🇧 English

🇳🇬 Yoruba

🇳🇬 Hausa

🇰🇪 Swahili

🇬🇭 Twi

🌐 Deployment Options

🧾 Streamlit Cloud (Recommended for frontend demo)

⚡ Hugging Face Spaces (Both FastAPI + Streamlit support)

☁️ Render / Railway / Vercel (For backend-only deployment)

🧩 Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	FastAPI
Speech Recognition	SpeechRecognition + pydub
Text-to-Speech	gTTS
Machine Learning	scikit-learn
NLP	TF-IDF + Cosine Similarity
Data Storage	Joblib / Pickle model serialization

👩🏽‍💻 Author
Ayatullah Hanif
🎓 Mechanical Engineering @ Federal University of Technology, Minna
💡 Passionate about Data Analytics, Machine Learning, and AI Engineering

📧 [hanifayatullah2@gmail.com]
🌐 GitHub Profile

⭐ Contribute
Contributions, suggestions, and issues are welcome!
If you’d like to collaborate:

Fork the repository

Create a new branch

Make your changes

Submit a Pull Request 🚀

🪪 License

This project is licensed under the MIT License — see the LICENSE
 file for details.

“Empowering rural communities through AI-driven inclusion.” 🌍
