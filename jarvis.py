import os
import speech_recognition as sr
import webbrowser
import pyttsx3
import requests
from openai import OpenAI
from gtts import gTTS
import pygame

engine = pyttsx3.init()

# Embedded music library (previously in musicLibrary.py)
music = {
    "believer": "https://www.youtube.com/watch?v=7wtfhZwyrcc",
    "shape of you": "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "numb": "https://www.youtube.com/watch?v=kXYiU_JCYtU",
    "drivers license": "https://www.youtube.com/watch?v=ZmDBbnmKpqQ",
    
    "pal pal dil ke paas" : "https://www.youtube.com/watch?v=Vabo2KVaEwA&list=RDVabo2KVaEwA&start_radio=1&pp=ygUTcGFsIHBhbCBkaWwga2UgcGFhc6AHAQ%3D%3D",
    "sweater weather": "https://www.youtube.com/watch?v=GCdwKhTtNNw&list=RDGCdwKhTtNNw&start_radio=1&pp=ygUPc3dlYXRlciB3ZWF0aGVyoAcB0gcJCSkKAYcqIYzv",
    "kya hua tera wada" :"https://www.youtube.com/watch?v=fyZ-sOHj-Vg&list=RDfyZ-sOHj-Vg&start_radio=1&pp=ygURa3lhIGh1YSB0ZXJhIHdhZGGgBwE%3D",
    "khamoshiyan":"https://www.youtube.com/watch?v=Mv3SZDP7QUo&list=RDMv3SZDP7QUo&start_radio=1&pp=ygUQa2hhbW9zaGl5YW4gc29uZ6AHAQ%3D%3D",
    "saiyaara":"https://www.youtube.com/watch?v=UEG_F6tWj8c&list=RDUEG_F6tWj8c&start_radio=1",
}

def find_song(name: str):
    if not name:
        return None
    key = name.lower().strip()
    if key in music:
        return music[key]
    norm = key.replace(" ", "")
    for k, v in music.items():
        if k.lower().replace(" ", "") == norm:
            return v
    for k, v in music.items():
        if key in k.lower():
            return v
    return None

def list_songs():
    return sorted(music.keys())

# Use environment variables; fall back to empty strings
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if not NEWS_API_KEY:
    print("Warning: NEWS_API_KEY not set. News feature will be disabled.")

if not OPENAI_API_KEY or OPENAI_API_KEY.lower().startswith("your_"):
    print("Warning: OPENAI_API_KEY not set or uses a placeholder. AI features are disabled.")
    OPENAI_ENABLED = False
else:
    OPENAI_ENABLED = True

def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    try:
        tts = gTTS(text)
        tmp = "temp_jarvis_tts.mp3"
        tts.save(tmp)
        pygame.mixer.init()
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass
        pygame.mixer.quit()
        os.remove(tmp)
    except Exception:
        try:
            speak_old(text)
        except Exception as e:
            print(f"Speak error: {e}")

def aiProcess(command):
    if not OPENAI_ENABLED:
        print("AI disabled: OPENAI_API_KEY not configured.")
        return "AI is not available. Please set the OPENAI_API_KEY environment variable."
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise virtual assistant named Jarvis."},
                {"role": "user", "content": command}
            ],
            max_tokens=300,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "I encountered an error processing your request."

def processCommand(c):
    text = c.lower()
    if "open google" in text:
        webbrowser.open("https://google.com")
        return
    if "open facebook" in text:
        webbrowser.open("https://facebook.com")
        return
    if "open youtube" in text:
        webbrowser.open("https://youtube.com")
        return
    if "open linkedin" in text:
        webbrowser.open("https://linkedin.com")
        return
    if text.startswith("play"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            speak("Please specify a song name. Available songs are: " + ", ".join(list_songs()))
            return
        song_name = parts[1].strip()
        url = find_song(song_name)
        if url:
            webbrowser.open(url)
        else:
            speak(f"Song '{song_name}' not found. Available songs: " + ", ".join(list_songs()))
        return
    if "news" in text:
        if not NEWS_API_KEY:
            speak("News API key is not configured.")
            return
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}", timeout=8)
            r.raise_for_status()
            data = r.json()
            articles = data.get("articles", [])[:5]
            for article in articles:
                speak(article.get("title", "No title"))
        except Exception as e:
            print(f"News error: {e}")
            speak("Unable to fetch news right now.")
        return

    output = aiProcess(c)
    speak(output)

if __name__ == "__main__":
    speak("Initializing Jarvis.")
    while True:
        r = sr.Recognizer()
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8

        print("recognizing...")
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.8)
                print("Listening for wake word...")
                try:
                    audio = r.listen(source, timeout=6, phrase_time_limit=4)
                except sr.WaitTimeoutError:
                    print("Listening timed out while waiting for phrase to start.")
                    continue

            try:
                word = r.recognize_google(audio)
            except sr.UnknownValueError:
                print("Could not understand audio (wake word).")
                continue
            except sr.RequestError as e:
                print(f"Error with speech recognition service; {e}")
                continue

            if word.strip().lower() == "jarvis":
                speak("Yes?")
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    print("Jarvis Active...")
                    try:
                        audio = r.listen(source, timeout=8, phrase_time_limit=8)
                    except sr.WaitTimeoutError:
                        print("Listening timed out while waiting for command.")
                        continue

                try:
                    command = r.recognize_google(audio)
                    print(f"Command: {command}")
                    processCommand(command)
                except sr.UnknownValueError:
                    print("Could not understand command. Please speak clearly.")
                except sr.RequestError as e:
                    print(f"Error with speech recognition service; {e}")

        except sr.RequestError as e:
            print(f"Error with speech recognition service; {e}")
        except Exception as e:
            print(f"Error; {e}")
