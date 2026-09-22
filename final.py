from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv

import requests
import os
import time
import webbrowser
import subprocess
from datetime import datetime

import speech_recognition as sr
import shutil
import pyautogui
# --- Frontend ke liye zaroori imports ---
import tkinter as tk
from tkinter import ttk
import threading
GOOGLE_API_KEY = os.environ.get("MY_SECRET_API_KEY")
# OPENROUTER_API_KEY="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"

# Recognizer configuration
recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.5
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

def speak(message: str):
    try:
        # 1. Google TTS engine setup
        tts = gTTS(text=message, lang='hi', slow=False)
        filename = "voice.mp3"
        tts.save(filename)

        # 2. Pygame Sound object initialize karna
        pygame.mixer.init()
        
        # Audio ko Sound object me load karna
        sound = pygame.mixer.Sound(filename)
        
        # --- 🚀 SPEED SETTING 🚀 ---
        # 1.0 = Normal (Default)
        # 1.2 = 20% Fast (Attitude ke liye best!)
        # 1.5 = 50% Bohot Tez
        speed_factor = 1.5
        
        # Sound play karna (Pygame speed adjust factor automatically track karta hai channels par)
        channel = sound.play()
        
        # Audio jab tak chal raha hai tab tak code ko hold pe rakhna
        while channel.get_busy():
            time.sleep(0.1)

        # 3. Clean up
        pygame.mixer.quit() # Mixer close karna taaki file unlock ho jaye
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        print(f"Speech error: {e}")


def ask_sansa_ai(user_text):

    url = "https://openrouter.ai/api/v1/chat/completions"

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
You are sansa, Keshav's personal AI assistant.

Talk naturally like a helpful human assistant.
Be friendly, intelligent, and conversational.
Keep answers reasonably short because your answer will be spoken aloud.
Remember that the user is Keshav.
if keshav speaks in hindi reply in hindi, if keshav speaks in english reply in english,if keshav speaks in Hinglish reply inHinglish.
keshav favorite thing or favorite game is playing basketball, so if he talk about sports, you can talk about basketball too.
"""
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        return answer

    except Exception as e:

        print("AI Error:", e)

        return "Sorry Keshav, I am having trouble connecting to my AI brain."

# --- Loader class for animation ---
class Loader:
    def __init__(self):
        self.running = True
    
    def start(self, duration):
        self.running = True
    
    def stop(self):
        self.running = False

loader = Loader()

# --- AI Backend Function (Jo button dabane par chalega) ---
def mera_ai_backend():
    # Jaise hi button dabega, loader ghoomna shuru ho jayega
    loader.start(10)
    
    print("Calibrating microphone for background noise... Please wait 1 second.")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Calibration complete! Ready for commands.")
    speak("sansa is now online and listening.")

    while True:
        text = ""
        with sr.Microphone() as source:
            print("\nListening.....")
            try:
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                print("No speech detected")
                continue

            try:
                text = recognizer.recognize_google(audio, language="en-IN")
                text = text.lower().strip()
                print(f"You said: {text}")
            except sr.UnknownValueError:
                speak("Sorry, I could not understand that.")
                continue
            except sr.RequestError as e:
                speak("Sorry, I could not reach the speech recognition service.")
                print(f"Request error: {e}")
                continue
            except Exception as e:
                speak("Sorry, I hit an error while processing your voice.")
                print(f"Recognition error: {e}")
                continue

        # --- Commands Execution ---
        if not text:
            continue

        if "exit" in text or "stop" in text:
            speak("Goodbye, keshav! have a great day")
            break
            
        elif "time" in text:
            current_time = datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}")
            
        elif "hello" in text or "hi" in text:
            speak("yes boss.")
        elif "sansa " in text:
            speak("yes boas")            
        elif "date" in text:
            current_date = datetime.now().strftime("%d %B %Y")
            speak(f"today is {current_date}")
        elif "where" in text:
            speak("i am always hear")
            
        elif "day" in text:
            current_day = datetime.now().strftime("%A")
            speak(f"the day is {current_day}")

        elif "open" in text and "google" not in text and "youtube" not in text:
            app_name = text.replace("open", "").strip()
            if "vs code" in app_name or "visual studio code" in app_name:
                app_name = "code"
            elif "file explorer" in app_name or "this pc" in app_name:
                app_name = "explorer"
            elif "paint" in app_name:
                app_name = "mspaint"
            elif "calculator" in app_name:
                app_name = "calc"

            if shutil.which(app_name) or app_name in ["explorer", "code", "notepad", "mspaint", "calc", "cmd"]:
                speak(f"Opening {app_name}")
                subprocess.Popen(f"start {app_name}", shell=True)
            else:
                speak(f"Sorry Keshav, I could not find {app_name} on your computer.")
                
        elif "open chrome" in text or "open google chrome" in text:
            speak("opening Google Chrome")
            subprocess.Popen("start chrome", shell=True)
            
        # --- VOLUME CONTROLS ---
        elif "volume up" in text or "increase volume" in text:
            speak("Increasing volume")
            for _ in range(5):
                pyautogui.press("volumeup")

        elif "volume down" in text or "decrease volume" in text:
            speak("Decreasing volume")
            for _ in range(5):
                pyautogui.press("volumedown")

        elif "mute" in text or "unmute" in text:
            speak("Toggling mute")
            pyautogui.press("volumemute")

        # --- LOCK PC ---
        elif "lock my pc" in text or "lock computer" in text:
            speak("Locking your computer, Keshav")
            os.system("rundll32.exe user32.dll,LockWorkStation")

        # --- SHUTDOWN ---
        elif "shutdown computer" in text or "turn off pc" in text:
            speak("Keshav, are you sure you want to shutdown the computer? Please say yes or no.")
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                    confirm = recognizer.recognize_google(audio, language="en-IN").lower()
                    print(f"Confirmation: {confirm}")
                    
                    if "yes" in confirm or "haan" in confirm:
                        speak("Shutting down in 10 seconds. Goodbye!")
                        os.system("shutdown /s /t 10")
                    else:
                        speak("Shutdown cancelled.")
                except Exception:
                    speak("I did not get a clear answer. Shutdown cancelled.")
                    
        # --- RESTART ---
        elif "restart computer" in text or "restart  pc" in text:
            speak("Keshav, are you sure you want to restart the computer? Please say yes or no.")
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                    confirm = recognizer.recognize_google(audio, language="en-IN").lower()
                    print(f"Confirmation: {confirm}")
                    
                    if "yes" in confirm or "haan" in confirm:
                        speak("Restarting in 10 seconds. Save your work!")
                        os.system("shutdown /r /t 10")
                    else:
                        speak("Restart cancelled.")
                except Exception:
                    speak("I did not get a clear answer. Restart cancelled.")

        elif "open google" in text:
            speak("opening google")
            webbrowser.open("https://google.com")
        elif "open youtube" in text:
            speak("opening youtube")
            webbrowser.open("https://youtube.com")
        elif "your name" in text:
            speak("my name is sansa")
        elif "who are you" in text:
            speak("sansa, your  ai assistant")
        elif "thank you" in text or "thanks" in text:
            speak("you are welcome")
        else:

               answer = ask_sansa_ai(text)
               print("sansa:", answer)
               speak(answer)
    # Loop se bahar aane par (Exit bolne par) loader rukega aur window band hogi
    loader.stop()
    root.destroy()

# ====================================================================
# FUTURISTIC sansa FRONTEND
# ====================================================================

# -----------------------------
# 1. START AI BUTTON FUNCTION
# -----------------------------
def start_ai_click():
    status_label.config(text="● SYSTEM ONLINE", fg="#00ffcc")
    activity_label.config(text="Listening for your command...")
    threading.Thread(target=mera_ai_backend, daemon=True).start()


# -----------------------------
# 2. ANIMATED sansa CORE
# -----------------------------
angle = 0

def animate_core():
    global angle

    core_canvas.delete("animation")

    # Outer rotating ring
    core_canvas.create_arc(
        35, 35, 265, 265,
        start=angle,
        extent=110,
        outline="#00e5ff",
        width=4,
        style="arc",
        tags="animation"
    )

    # Second ring
    core_canvas.create_arc(
        55, 55, 245, 245,
        start=-angle * 1.5,
        extent=80,
        outline="#0077ff",
        width=2,
        style="arc",
        tags="animation"
    )

    # Inner circle
    core_canvas.create_oval(
        90, 90, 210, 210,
        outline="#00e5ff",
        width=2,
        tags="animation"
    )

    # sansa text
    core_canvas.create_text(
        150, 145,
        text="sansa",
        fill="white",
        font=("Arial", 25, "bold"),
        tags="animation"
    )

    # AI CORE text
    core_canvas.create_text(
        150, 175,
        text="AI CORE",
        fill="#00e5ff",
        font=("Arial", 9, "bold"),
        tags="animation"
    )

    angle += 4

    root.after(40, animate_core)


# -----------------------------
# 3. MAIN WINDOW
# -----------------------------
root = tk.Tk()

root.title("sansa AI - Personal Assistant")
root.geometry("900x600")
root.configure(bg="#050b14")

# Window resize disabled
root.resizable(False, False)


# -----------------------------
# 4. HEADER
# -----------------------------
header = tk.Frame(
    root,
    bg="#081522",
    height=65
)

header.pack(fill="x")

# sansa title
title_label = tk.Label(
    header,
    text="◉  sansa AI",
    font=("Arial", 22, "bold"),
    fg="#00e5ff",
    bg="#081522"
)

title_label.pack(side="left", padx=25, pady=15)


# Online status
status_label = tk.Label(
    header,
    text="● SYSTEM OFFLINE",
    font=("Arial", 11, "bold"),
    fg="#777777",
    bg="#081522"
)

status_label.pack(side="right", padx=25)


# -----------------------------
# 5. LEFT PANEL
# -----------------------------
left_panel = tk.Frame(
    root,
    bg="#050b14",
    width=650
)

left_panel.pack(side="left", fill="both", expand=True)


# -----------------------------
# 6. sansa CORE CANVAS
# -----------------------------
core_canvas = tk.Canvas(
    left_panel,
    width=300,
    height=300,
    bg="#050b14",
    highlightthickness=0
)

core_canvas.pack(pady=35)


# -----------------------------
# 7. STATUS TEXT
# -----------------------------
activity_label = tk.Label(
    left_panel,
    text="System ready. Press ACTIVATE sansa.",
    font=("Arial", 12),
    fg="#9aa7b2",
    bg="#050b14"
)

activity_label.pack(pady=5)


# -----------------------------
# 8. ACTIVATE BUTTON
# -----------------------------
start_button = tk.Button(
    left_panel,
    text="⚡  ACTIVATE sansa",
    font=("Arial", 14, "bold"),
    fg="white",
    bg="#006eff",
    activebackground="#00e5ff",
    activeforeground="black",
    bd=0,
    width=25,
    height=2,
    cursor="hand2",
    command=start_ai_click
)

start_button.pack(pady=25)


# -----------------------------
# 9. RIGHT INFORMATION PANEL
# -----------------------------
right_panel = tk.Frame(
    root,
    bg="#081522",
    width=250
)

right_panel.pack(
    side="right",
    fill="y"
)


# PANEL TITLE
panel_title = tk.Label(
    right_panel,
    text="SYSTEM MONITOR",
    font=("Arial", 12, "bold"),
    fg="#00e5ff",
    bg="#081522"
)

panel_title.pack(pady=25)


# SYSTEM INFO
info_label = tk.Label(
    right_panel,
    text=
    "STATUS\n\n"
    "● Voice Recognition: READY\n\n"
    "● AI Core: STANDBY\n\n"
    "● Microphone: READY\n\n"
    "● Backend: CONNECTED",
    font=("Arial", 10),
    justify="left",
    anchor="w",
    fg="#b8c7d1",
    bg="#081522"
)

info_label.pack(
    padx=20,
    anchor="w"
)


# DIVIDER
divider = tk.Frame(
    right_panel,
    height=1,
    bg="#173044"
)

divider.pack(
    fill="x",
    padx=20,
    pady=25
)


# COMMAND HISTORY
history_title = tk.Label(
    right_panel,
    text="COMMAND HISTORY",
    font=("Arial", 11, "bold"),
    fg="#00e5ff",
    bg="#081522"
)

history_title.pack()


history_label = tk.Label(
    right_panel,
    text="No commands yet...",
    font=("Arial", 9),
    fg="#71808c",
    bg="#081522",
    wraplength=200,
    justify="left"
)

history_label.pack(
    pady=20,
    padx=20
)


# START ANIMATION
animate_core()


# START TKINTER
root.mainloop()