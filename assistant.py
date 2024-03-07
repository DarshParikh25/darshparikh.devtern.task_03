import speech_recognition as sr
import pyttsx3
import datetime
import pytz
import requests
import PyDictionary as PyDictionary
import threading
import webbrowser
import openai
import os
from google.cloud import translate_v2 as translate
import re

# Initialize the Google Cloud Translation client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "our-keyword-411607-f0b3444c77b7.json"
translate_client = translate.Client()

# Initialize the speech recognition engine
recognizer = sr.Recognizer()

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Please try again.")
        return ""
    except sr.RequestError:
        print("Sorry, there was an error with the speech recognition service.")
        return ""

def speak(text):
    engine.say(text)
    engine.runAndWait()

def set_reminder(reminder_time, reminder_task):
    now = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    reminder_time = datetime.datetime.strptime(reminder_time, '%I:%M %p').replace(year=now.year, month=now.month, day=now.day)
    delta_time = reminder_time - now
    seconds = delta_time.total_seconds()
    if seconds < 0:
        reminder_time += datetime.timedelta(days=1)
        seconds = (reminder_time - now).total_seconds()
    print("Reminder set for:", reminder_time)
    engine.say(f"Reminder set. I'll remind you to {reminder_task} at {reminder_time.strftime('%I:%M %p')}.")
    engine.runAndWait()

def get_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Chennai",
        "appid": "6c48ba85b939326060ff63112a8243c1",
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    weather_description = data['weather'][0]['description']
    temperature = data['main']['temp']
    speak(f"Today's weather is {weather_description} with a temperature of {temperature} degrees Celsius.")

def get_news():
    url = "https://newsapi.org/s/google-news-api"
    params = {
        "country": "us",
        "apiKey": "ca10bdfba39848d8a9bc17ad78b61959"
    }
    response = requests.get(url, params=params)
    data = response.json()
    headlines = [article['title'] for article in data['articles']]
    speak("Here are the latest news headlines:")
    for headline in headlines:
        speak(headline)

def define_word(word):
    dictionary = PyDictionary()
    meanings = dictionary.meaning(word)
    if meanings:
        for part_of_speech, meaning_list in meanings.items():
            for meaning in meaning_list:
                speak(f"{word} ({part_of_speech}): {meaning}")
    else:
        speak(f"Sorry, I couldn't find the meaning of {word}.")

def set_alarm(alarm_time):
    def run_alarm():
        now = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        alarm_time_obj = datetime.datetime.strptime(alarm_time, '%I:%M %p').replace(year=now.year, month=now.month, day=now.day)
        delta_time = alarm_time_obj - now
        seconds = delta_time.total_seconds()
        if seconds < 0:
            alarm_time_obj += datetime.timedelta(days=1)
            seconds = (alarm_time_obj - now).total_seconds()
        print("Alarm set for:", alarm_time_obj)
        speak(f"Alarm set for {alarm_time}.")
        # Wait until the alarm time
        alarm_thread = threading.Timer(seconds, notify_alarm())
        alarm_thread.start()

    def notify_alarm():
        print("Alarm!")
        speak("Alarm!")

    run_alarm()

def convert_units(quantity, unit_from, unit_to):
    url = "https://api.unitconvert.io/"
    params = {
        "q": f"{quantity} {unit_from} to {unit_to}"
    }
    response = requests.get(url, params=params)
    data = response.json()
    conversion_result = data['result']
    speak(f"The conversion result is {conversion_result}.")

def provide_directions(destination, current_location=None):
    if current_location:
        url = f"https://www.google.com/maps/dir/{current_location}/{destination}"
    else:
        url = f"https://www.google.com/maps/dir//{destination}"

    speak(f"Opening directions to {destination} in your web browser.")
    engine.runAndWait()
    webbrowser.open(url)

def answer_question(question):
    response = openai.Completion.create(
        engine="davinci",
        prompt=question,
        max_tokens=50
    )
    answer = response.choices[0].text.strip()
    speak(answer)

def translate_phrase(phrase, target_language):
    detection = translate_client.detect_language(phrase)
    translation = translate_client.translate(phrase, target_language=target_language)
    speak(f"In {detection['language']}, '{phrase}' translates to '{translation['translatedText']}' in {target_language}.")

def calculate(expression):
    try:
        result = eval(expression)
        speak(f"The result of {expression} is {result}.")
    except Exception as e:
        speak("Sorry, I couldn't evaluate that expression. Please try again.")

def main():
    speak("Hello! I'm your Python Voice Assistant. How can I help you today?")
    command = listen()

    if "hello" in command:
        speak("Hello! How can I assist you?")
    
    elif "set reminder" in command:
        speak("Sure, please specify the time and task for the reminder.")
        reminder_time = listen()
        reminder_task = listen()
        set_reminder(reminder_time, reminder_task)

    elif "today's weather" in command:
        get_weather()

    elif "today's news" in command:
        get_news()

    elif "define a word" in command:
        speak("Sure, please specify the word you want to define.")
        word = listen()
        define_word(word)

    elif "set alarm" in command:
        speak("Sure, please specify the time for the alarm.")
        alarm_time = listen()
        set_alarm(alarm_time)

    elif "convert units" in command:
        speak("Sure, please specify the quantity, unit from, and unit to for the conversion.")
        conversion_input = listen()
        quantity, unit_from, unit_to = conversion_input.split(" ")
        convert_units(quantity, unit_from, unit_to)

    elif "provide directions" in command:
        speak("Sure, please specify the destination.")
        destination = listen()
        speak("Would you like to specify your current location? If yes, please say it, otherwise, I'll assume your current location.")
        current_location = listen()
        provide_directions(destination, current_location)

    elif "answer a question" in command:
        speak("Sure, please ask your question.")
        question = listen()
        answer_question(question)

    elif "translate a phrase" in command:
        speak("Sure, please specify the phrase you want to translate.")
        phrase = listen()
        speak("Great! Now, please specify the target language.")
        target_language = listen()
        translate_phrase(phrase, target_language)

    elif "calculate" in command:
        speak("Sure, please specify the arithmetic expression.")
        expression = listen()
        # Remove any non-numeric characters except for arithmetic operators
        expression = re.sub(r'[^0-9+\-*/\s.]', '', expression)
        calculate(expression)

if __name__ == "__main__":
    main()