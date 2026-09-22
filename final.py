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
st.set_page_config(page_title="Sansa AI Core", page_icon="🎙️", layout="centered")

# Injecting futuristic styling directly into the browser DOM
st.markdown("""
    <style>
    .main { background-color: #050b14; color: #ffffff; }
    div.stButton > button:first-child {
        background-color: #006eff; color: white; font-size: 18px; font-weight: bold;
        width: 100%; border-radius: 12px; height: 55px; border: 2px solid #00e5ff;
        box-shadow: 0px 0px 15px rgba(0, 229, 255, 0.4); transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #00e5ff; color: black; box-shadow: 0px 0px 25px rgba(0, 229, 255, 0.8);
    }
    .status-box {
        padding: 15px; border-radius: 10px; background-color: #081522;
        border: 1px solid #173044; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Sansa AI - Public Voice Assistant")
st.write("---")

GOOGLE_API_KEY = os.environ.get("MY_SECRET_API_KEY")

def speak(message: str):
    """Generates audio bytes via gTTS and mounts a hidden autoplay component onto the browser DOM."""
    try:
        tts = gTTS(text=message, lang='hi', slow=False)
        filename = "voice.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as f:
            audio_bytes = f.read()
            
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        st.error(f"Speech output error: {e}")

def ask_sansa_ai(user_text):
    if not GOOGLE_API_KEY:
        return "Sorry, I cannot access my secret API key in the current environment settings."

    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {GOOGLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Dynamic prompt that works perfectly for anyone testing, but respects Keshav as the creator
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """
You are Sansa, a highly advanced, friendly, and intelligent AI assistant.
CRITICAL RULE 1: You were created and programmed by Keshav. If anyone asks 'who created you?', 'who made you?', 'owner kaun hai?', or 'aapko kisne banaya?', you must always proudly state that you were made by Keshav.
CRITICAL RULE 2: Talk naturally like a helpful human assistant. Keep answers reasonably short (1-2 sentences) because your answer will be spoken aloud over the web.
CRITICAL RULE 3: If the person interacting with you says their name is Keshav, treat them as your master/boss who loves basketball. If anyone else is talking to you, treat them politely as a guest or friend, but maintain that Keshav is your creator.
Language Rule: If the user speaks in Hindi, reply in Hindi. If English, reply in English. If Hinglish, reply in Hinglish.
"""
            },
            {"role": "user", "content": user_text}
        ]
    }

    try:
        # Standard processing pipeline for third-party API integration
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"]["message"]["content"]
    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I am having trouble connecting to my AI brain."

# --- SESSION STATES FOR CONTROLLING WEB APPLICATION FLOW ---
if 'system_online' not in st.session_state:
    st.session_state.system_online = False
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR INTERFACE ---
with st.sidebar:
    st.markdown("### 🖥️ SYSTEM MONITOR")
    if st.session_state.system_online:
        st.markdown("<p style='color:#00ffcc; font-weight:bold;'>● SYSTEM ONLINE</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#777777; font-weight:bold;'>● SYSTEM OFFLINE</p>", unsafe_allow_html=True)
        
    st.markdown("""
    **Core Capabilities:**
    * ◉ Voice Recognition: `READY`
    * ◉ AI Creator Identity: `KESHAV`
    * ◉ Web Audio Engine: `CONNECTED`
    """)
    st.write("---")
    st.markdown("### 📜 COMMAND HISTORY")
    if st.session_state.history:
        for cmd in reversed(st.session_state.history):
            st.text(cmd)
    else:
        st.caption("No commands processed yet...")

# --- PHASE 1: ACTIVATION WALL (BREAKING THE BROWSER AUDIO LOCKUP) ---
if not st.session_state.system_online:
    st.markdown("<div class='status-box'><h3>SYSTEM STANDBY</h3><p>Press the button below to authorize browser multimedia layers and synchronize microphone configurations.</p></div>", unsafe_allow_html=True)
    if st.button("⚡ ACTIVATE SANSA AI"):
        st.session_state.system_online = True
        st.session_state.history.append("System Core Initialized")
        st.rerun()

# --- PHASE 2: SYSTEM ONLINE STATE (CONTINUOUS AUDIO CAPTURE LAYER) ---
else:
    if 'has_greeted' not in st.session_state:
        speak("Hello! Sansa is now online and ready to chat. Who do I have the pleasure of speaking with?")
        st.session_state.has_greeted = True

    st.markdown("<div class='status-box'><h3 style='color:#00e5ff;'>🎙️ Sansa Core Active</h3><p>Click the panel below, speak clearly into your device microphone, and let the voice model stream responses.</p></div>", unsafe_allow_html=True)

    # Capturing input from the cloud browser pipeline rather than physical OS devices
    text = speech_to_text(
        start_prompt="🎙️ Click to Talk / Command Sansa",
        stop_prompt="🛑 Processing speech data...",
        language='en-IN',
        use_container_width=True,
        key='sansa_microphone_hook'
    )

    if text:
        text_clean = text.lower().strip()
        st.info(f"**You Said:** {text}")
        st.session_state.history.append(f"User: {text_clean}")

        # --- EXECUTING MATCHING WEB-FRIENDLY CRITERIA ---
        if "exit" in text_clean or "stop" in text_clean:
            st.session_state.history.append("Sansa: Goodbye session closed.")
            speak("Goodbye! Have a great day ahead.")
            st.session_state.system_online = False
            del st.session_state['has_greeted']
            st.rerun()
            
        elif "time" in text_clean:
            current_time = datetime.now().strftime("%I:%M %p")
            st.success(f"Sansa: The time is {current_time}")
            speak(f"The time is {current_time}")
            
        elif "hello" in text_clean or "hi" in text_clean or "sansa" in text_clean:
            st.success("Sansa: Hello there! How can I assist you today?")
            speak("Hello there! How can I assist you today?")
            
        elif "date" in text_clean:
            current_date = datetime.now().strftime("%d %B %Y")
            st.success(f"Sansa: Today is {current_date}")
            speak(f"today is {current_date}")
            
        elif "where" in text_clean:
            st.success("Sansa: I live in the digital cloud realm.")
            speak("I live in the digital cloud realm.")
            
        elif "day" in text_clean:
            current_day = datetime.now().strftime("%A")
            st.success(f"Sansa: The day is {current_day}")
            speak(f"the day is {current_day}")

        # Web safety block for local host machine utilities
        elif "open" in text_clean or "chrome" in text_clean or "volume" in text_clean or "mute" in text_clean or "lock" in text_clean or "shutdown" in text_clean:
            st.warning("Hardware automation controls are disabled over public web links for safety.")
            speak("System commands are restricted over browser frameworks.")
            
        elif "your name" in text_clean:
            st.success("Sansa: My name is Sansa.")
            speak("my name is sansa")
            
        elif "thank you" in text_clean or "thanks" in text_clean:
            st.success("Sansa: You are welcome.")
            speak("you are welcome")
            
        else:
            with st.spinner("Sansa is thinking..."):
                answer = ask_sansa_ai(text)
            st.success(f"**Sansa:** {answer}")
            st.session_state.history.append(f"Sansa: {answer}")
            speak(answer)
