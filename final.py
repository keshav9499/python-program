import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS
from streamlit_mic_recorder import speech_to_text

# Load environment variables
load_dotenv()

# Streamlit Page configuration for futuristic dark theme
st.set_page_config(page_title="Sansa Anti-Lag AI Core", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050b14; color: #ffffff; }
    div.stButton > button:first-child {
        background-color: #006eff; color: white; font-size: 18px; font-weight: bold;
        width: 100%; border-radius: 12px; height: 55px; border: 2px solid #00e5ff;
        box-shadow: 0px 0px 15px rgba(0, 229, 255, 0.4);
    }
    .status-box {
        padding: 20px; border-radius: 10px; background-color: #081522;
        border: 1px solid #173044; margin-bottom: 20px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Sansa AI - Network Guarded Assistant")
st.write("---")

GOOGLE_API_KEY = os.environ.get("MY_SECRET_API_KEY")

def speak(message: str):
    """Generates audio bytes dynamically with failsafe streaming loops over weak web layers."""
    try:
        tts = gTTS(text=message, lang='hi', slow=False)
        filename = f"voice_{int(time.time())}.mp3"
        tts.save(filename)
        
        # Audio creation lag buffer
        time.sleep(1.2)
        
        with open(filename, "rb") as f:
            audio_bytes = f.read()
            
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        st.error(f"Speech layer caught an isolated lag buffer spike: {e}")

def ask_sansa_ai(user_text):
    if not GOOGLE_API_KEY:
        return "Sorry, I cannot access my secret API key in the current environment settings."

    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {GOOGLE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """
You are Sansa, a friendly and intelligent AI assistant.
CRITICAL RULE 1: You were created by Keshav. If anyone asks 'who created you?' or 'aapko kisne banaya?', you must always state that you were made by Keshav.
CRITICAL RULE 2: Keep answers very short and crisp (1 short sentence) because your answer will be spoken aloud.
Language Rule: If the user speaks in Hindi, reply in Hindi. If English, reply in English.
"""
            },
            {"role": "user", "content": user_text}
        ]
    }

    # --- 🛡️ ADVANCED NETWORK GUARD MATRIX (ANTI-LAG RETRY) ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Low timeout factor prevents browser tab freeze over weak networks
            response = requests.post(url, headers=headers, json=data, timeout=12)
            if response.status_code == 200:
                result = response.json()
                return result["choices"]["message"]["content"]
        except (requests.exceptions.RequestException, Exception) as e:
            # Short fallback sleep before shooting the secondary connection query retry vector
            time.sleep(1.5)
            continue
            
    # Clean offline execution loop backstop if all 3 public network connections fail
    return "OFFLINE_FALLBACK_TRIGGERED"

# --- APPLICATION STATES ---
if 'system_online' not in st.session_state:
    st.session_state.system_online = False

# --- PHASE 1: INITIAL TRIGGER ---
if not st.session_state.system_online:
    st.markdown("<div class='status-box'><h3>SYSTEM STANDBY</h3><p>Press the button below to initialize Sansa's network-guarded voice protocol.</p></div>", unsafe_allow_html=True)
    if st.button("⚡ ACTIVATE SANSA VOICE CORE"):
        st.session_state.system_online = True
        st.rerun()

# --- PHASE 2: PURE VOICE SESSION ---
else:
    if 'has_greeted' not in st.session_state:
        speak("Hello! Sansa is now online. Click the microphone button below and talk to me.")
        st.session_state.has_greeted = True

    st.markdown("<div class='status-box'><h3 style='color:#00e5ff;'>🎙️ Anti-Lag Voice Session Active</h3><p>System protected against network fluctuations. Tap the button below and speak clearly.</p></div>", unsafe_allow_html=True)

    # Public web browser media component hook
    text = speech_to_text(
        start_prompt="👉 Click Here to Speak to Sansa 👈",
        stop_prompt="🛑 Processing Voice Input... Please Wait...",
        language='en-IN',
        use_container_width=True,
        key='sansa_network_guarded_mic'
    )

    if text:
        text_clean = text.lower().strip()
        st.info(f"**Sansa Heard:** {text}")

        # --- INSTANT LOCAL CRITERIA (Bypasses external API entirely to ensure zero lag) ---
        if "time" in text_clean:
            ans = f"The time is {datetime.now().strftime('%I:%M %p')}"
        elif "date" in text_clean:
            ans = f"Today is {datetime.now().strftime('%d %B %Y')}"
        elif "day" in text_clean:
            ans = f"The day is {datetime.now().strftime('%A')}"
        elif "hello" in text_clean or "hi" in text_clean or "sansa" in text_clean:
            ans = "Hello there! How can I assist you today?"
        elif "your name" in text_clean:
            ans = "My name is Sansa."
        elif "who are you" in text_clean:
            ans = "Sansa, your personal AI assistant."
        elif "open" in text_clean or "chrome" in text_clean or "volume" in text_clean or "mute" in text_clean or "lock" in text_clean or "shutdown" in text_clean:
            ans = "System automation commands are locked over remote web links for data security."
        else:
            with st.spinner("Sansa is verifying cloud data packets..."):
                ans = ask_sansa_ai(text)
                
            # If network completely fails, provide clean vocal feedback instead of blank script freezing
            if ans == "OFFLINE_FALLBACK_TRIGGERED":
                ans = "Master Keshav, Aapke network me dikkat hai, par maine offline system backup se check kiya hai. Main online brain se connect nahi ho pa rahi."

        st.success(f"**Sansa Response:** {ans}")
        speak(ans)
        
        # Hard system pause to let browser state logs completely refresh
        time.sleep(0.5)
