import speech_recognition as sr
from pyttsx3 import init

recognizer = sr.Recognizer()
engine = init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def processCommand(command):
    print(f"Processing command: {command}")
    # Add your command processing logic here

if __name__ == "__main__":
    speak("Initializing Jarvis")

    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

            word = recognizer.recognize_google(audio)
            print("Heard:", word)

            if word.lower() == "jarvis":
                speak("Yes")

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("Jarvis Active...")
                    audio = recognizer.listen(source, timeout=5)

                command = recognizer.recognize_google(audio)
                print("Command:", command)
                processCommand(command)

        except sr.WaitTimeoutError:
            continue

        except sr.UnknownValueError:
            continue

        except Exception as e:
            print("Error:", e)

