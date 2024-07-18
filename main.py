import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import time
import threading
import sys
import os
import dotenv

dotenv.load_dotenv()


r = sr.Recognizer()
source = sr.Microphone()
listener_thread = None


client = OpenAI(
  organization=os.getenv('OPENAI_ORGANIZATION_ID'),
  project=os.getenv('OPENAI_PROJ_ID'),
  api_key=os.getenv('OPENAI_API_KEY')
)


def Speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 175)
    engine.say(text)
    engine.runAndWait()


def callback(recognizer, audio):
    try:
        speech_as_text = recognizer.recognize_google(audio)
        print(speech_as_text)
        if "bot" in speech_as_text or "hey bot" in speech_as_text:
            Speak("How can I help you?")
            recognize_main()
    except sr.UnknownValueError:
        Speak("Oops! Didn't catch that")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition Service; {e}")


def recognize_main():
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    data = ""
    try:
        data = r.recognize_google(audio)
        data = data.lower()
        print("You said: " + data)
        
        if "bye" in data:
            Speak("Goodbye!")
            sys.exit()
            
        else:
            gpt_response(data)
            time.sleep(1)
            
    except sr.UnknownValueError:
        Speak("The bot did not understand your request")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition Service; {e}")


def gpt_response(data):
    response = client.chat.completions.create(
        model="gpt-3.5",
        messages=[
            {"role": "system", "content": "You are a voice assistant that gives short and concise answers to my questions."},
            {"role": "user", "content": data}
        ]
    )
    message_content = response.choices[0].message.content
    Speak(message_content)


def start_keyword_listener():
    global listener_thread
    if listener_thread and listener_thread.is_alive():
        listener_thread.join()
    print("Waiting for a keyword... say 'bot' or 'hey bot'")
    listener_thread = threading.Thread(target=r.listen_in_background, args=(source, callback))
    listener_thread.start()


if __name__ == "__main__":
    start_keyword_listener()
    while True:
        time.sleep(1)