import os
import time
import requests
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS

# Load environment variables
load_dotenv()

# Streamlit Page configuration for futuristic dark theme
st.set_page_config(page_title="Sansa AI Core", page_icon="🎙️", layout="centered")

# Injecting futuristic styling directly into the browser DOM
st.markdown("""
    <style>
    .main { background-color: #050b14; color: #ffffff; }
    .status-box {
        padding: 15px; border-radius: 10px; background-color: #081522;
        border: 1px solid #173044; margin-bottom: 20px;
    }
    .chat-bubble-user {
        background-color: #006eff; padding: 10px 15px; border-radius: 15px 15px 0px 15px;
        margin: 10px 0; width: fit-content; max-width: 80%; float: right; clear: both; color: white;
    }
    .chat-bubble-sansa {
        background-color: #173044; padding: 10px 15px; border-radius: 15px 15px 15px 0px;
        margin: 10px 0; width: fit-content; max-width: 80%; float: left; clear: both; color: #00e5ff;
        border: 1px solid #00e5ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Sansa AI - Real-time Voice & Text Assistant")
st.write("---")

GOOGLE_API_KEY = os.environ.get("MY_SECRET_API_KEY")

def speak(message: str):
    """Generates audio bytes via gTTS and mounts an autoplay component onto the browser DOM securely."""
    try:
        tts = gTTS(text=message, lang='hi', slow=False)
        filename = f"voice_{int(time.time())}.mp3"
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
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"]["message"]["content"]
    except Exception as e:
        return "Sorry, I am having trouble connecting to my AI brain."

# --- SESSION STATES FOR CONTROLLING CHAT FLOW ---
if 'system_online' not in st.session_state:
    st.session_state.system_online = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- PHASE 1: ACTIVATION WALL ---
if not st.session_state.system_online:
    st.markdown("<div class='status-box'><h3>SYSTEM STANDBY</h3><p>Press the button below to authorize browser multimedia layers and wake up Sansa.</p></div>", unsafe_allow_html=True)
    if st.button("⚡ ACTIVATE SANSA AI"):
        st.session_state.system_online = True
        st.rerun()

# --- PHASE 2: ACTIVE SYSTEM INTERFACE ---
else:
    if 'has_greeted' not in st.session_state:
        speak("Hello! Sansa is now online. Type or use mic typing to chat with me.")
        st.session_state.has_greeted = True

    st.markdown("<div class='status-box'><h3 style='color:#00e5ff;'>🎙️ Sansa Chat Core Active</h3><p>Type your message below. (You can also click the microphone icon on your keyboard to speak into the text box!)</p></div>", unsafe_allow_html=True)

    # Display Chat History beautifully
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"<div class='chat-bubble-user'>{message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-sansa'>{message}</div>", unsafe_allow_html=True)

    st.write(" ") # Spacing

    # Safe Form Input to kill any refresh/processing lag loop completely
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Message Sansa...", placeholder="Type here or use voice dictation...")
        submit_button = st.form_submit_button(label="Send 🚀")

    if submit_button and user_input:
        text_clean = user_input.lower().strip()
        st.session_state.chat_history.append(("user", user_input))

        # --- EXECUTING MATCHING LOGIC ---
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
            ans = "System commands and hardware controls are restricted over browser frameworks for safety."
        else:
            with st.spinner("Sansa is processing..."):
                ans = ask_sansa_ai(user_input)

        st.session_state.chat_history.append(("sansa", ans))
        st.rerun()

    # Trigger audio for the latest Sansa reply to achieve stable audio delivery
    if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "sansa":
        latest_reply = st.session_state.chat_history[-1][1]
        speak(latest_reply)
