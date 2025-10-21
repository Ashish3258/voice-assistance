import speech_recognition as sr
import webbrowser
import pyttsx3
import wikipedia
import datetime
import os
import requests
import random
from googletrans import Translator
import json
import pyjokes
import wolframalpha
import yfinance as yf
import schedule
import time
from cryptography.fernet import Fernet

# ------------------- CONFIG -------------------
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()

WEATHER_API_KEY = "your_openweathermap_api_key"
NEWS_API_KEY = "your_newsapi_key"
MUSIC_FOLDER = "C:/Users/YourName/Music"
NOTES_FILE = "notes.txt"
WOLFRAM_APP_ID = "your_wolframalpha_appid"
CRICAPI_KEY = "your_cricapi_key"
ENCRYPTION_KEY = Fernet.generate_key()  # Save securely
fernet = Fernet(ENCRYPTION_KEY)

# ------------------- SPEAK -------------------
def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# ------------------- WEATHER -------------------
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            return "Sorry, I could not get weather information."
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is {weather} with a temperature of {temp}°C"
    except:
        return "Sorry, I could not fetch weather data right now."

# ------------------- NEWS -------------------
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        articles = response.json().get("articles", [])
        headlines = [a["title"] for a in articles[:5]]
        if headlines:
            for i, headline in enumerate(headlines, 1):
                speak(f"News {i}: {headline}")
        else:
            speak("Sorry, I couldn't fetch the news.")
    except:
        speak("Sorry, I could not fetch news right now.")

# ------------------- COVID INFO -------------------
def get_covid(country="India"):
    try:
        url = f"https://disease.sh/v3/covid-19/countries/{country}"
        response = requests.get(url)
        data = response.json()
        cases = data["cases"]
        deaths = data["deaths"]
        recovered = data["recovered"]
        return f"COVID status in {country}: {cases} total cases, {deaths} deaths, and {recovered} recovered."
    except:
        return "Sorry, I could not fetch COVID information."

# ------------------- NOTES -------------------
def take_note(note):
    try:
        with open(NOTES_FILE, "a") as f:
            f.write(note + "\n")
        speak("Note saved successfully.")
    except:
        speak("Sorry, I could not save the note.")

def read_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r") as f:
                notes = f.readlines()
            if notes:
                speak("Here are your notes:")
                for note in notes:
                    speak(note.strip())
            else:
                speak("You don't have any notes yet.")
        else:
            speak("No notes found.")
    except:
        speak("Sorry, I could not read notes right now.")

# ------------------- SECURE NOTES -------------------
def save_secure_note(note):
    try:
        encrypted = fernet.encrypt(note.encode())
        with open("secure_notes.txt", "ab") as f:
            f.write(encrypted + b"\n")
        speak("Secure note saved.")
    except:
        speak("Error saving secure note.")

def read_secure_notes():
    try:
        with open("secure_notes.txt", "rb") as f:
            lines = f.readlines()
        if lines:
            for line in lines:
                decrypted = fernet.decrypt(line).decode()
                speak(decrypted)
        else:
            speak("No secure notes found.")
    except:
        speak("Error reading secure notes.")

# ------------------- MATH -------------------
def solve_math(command):
    try:
        expression = command.replace("solve", "").replace("what is", "").strip()
        result = eval(expression)
        speak(f"The result is {result}")
    except:
        speak("Sorry, I could not solve that.")

def solve_advanced_math(query):
    try:
        client = wolframalpha.Client(WOLFRAM_APP_ID)
        res = client.query(query)
        answer = next(res.results).text
        speak(f"The answer is {answer}")
    except:
        speak("Sorry, I could not solve that.")

# ------------------- MUSIC -------------------
def play_music():
    try:
        songs = [song for song in os.listdir(MUSIC_FOLDER) if song.endswith((".mp3", ".wav"))]
        if songs:
            song = random.choice(songs)
            speak(f"Playing {song}")
            os.startfile(os.path.join(MUSIC_FOLDER, song))
        else:
            speak("No music files found in your music folder.")
    except:
        speak("Sorry, I couldn't open your music folder.")

# ------------------- TRANSLATE -------------------
def translate_text(command):
    try:
        if "translate" in command:
            words = command.split("to")
            if len(words) >= 2:
                text_to_translate = words[0].replace("translate", "").strip()
                target_lang = words[1].strip()
                lang_map = {
                    "hindi": "hi", "english": "en", "french": "fr",
                    "spanish": "es", "german": "de", "chinese": "zh-cn",
                    "japanese": "ja", "korean": "ko", "arabic": "ar"
                }
                if target_lang in lang_map:
                    translated = translator.translate(text_to_translate, dest=lang_map[target_lang])
                    result = f"{text_to_translate} in {target_lang} is {translated.text}"
                    speak(result)
                else:
                    speak("Sorry, I don't know that language yet.")
            else:
                speak("Please say translate followed by text and target language.")
    except Exception as e:
        speak("Sorry, I could not translate right now.")
        print("Error in translation:", e)

# ------------------- FUN FACTS -------------------
def tell_random_fact():
    try:
        response = requests.get("http://numbersapi.com/random/trivia")
        fact = response.text
        speak(f"Did you know? {fact}")
    except:
        speak("Sorry, I couldn't fetch a fact.")

# ------------------- STOCK -------------------
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.info['regularMarketPrice']
        speak(f"The current price of {ticker} is {price} dollars")
    except:
        speak("Sorry, I could not fetch the stock price.")

# ------------------- CRICKET -------------------
def get_cricket_score(match_id):
    try:
        url = f"https://cricapi.com/api/cricketScore?apikey={CRICAPI_KEY}&unique_id={match_id}"
        response = requests.get(url).json()
        if 'score' in response:
            speak(f"Score: {response['score']}")
        else:
            speak("Sorry, couldn't fetch score.")
    except:
        speak("Error fetching cricket score.")

# ------------------- ALARMS -------------------
def set_reminder(time_str, message):
    def job():
        speak(f"Reminder: {message}")
    schedule.every().day.at(time_str).do(job)
    speak(f"Reminder set for {time_str}")

# ------------------- COMMAND PROCESSOR -------------------
def processCommand(c):
    c = c.lower()

    if "exit" in c or "quit" in c or "stop" in c:
        speak("Goodbye sir. Shutting down.")
        exit()

    # Websites
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "whatsapp": "http://web.whatsapp.com/",
        "linkedin": "https://in.linkedin.com/",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "netflix": "https://www.netflix.com",
        "amazon prime": "https://www.primevideo.com",
        "prime video": "https://www.primevideo.com",
        "hotstar": "https://www.hotstar.com",
        "spotify": "https://open.spotify.com"
    }
    for key in sites:
        if f"open {key}" in c:
            speak(f"Opening {key}")
            webbrowser.open(sites[key])
            return

    # Wikipedia
    if "wikipedia" in c:
        query = c.replace("search wikipedia for", "").replace("wikipedia", "").strip()
        if query:
            speak(f"Searching Wikipedia for {query}")
            try:
                summary = wikipedia.summary(query, sentences=2)
                speak(summary)
            except:
                speak("Sorry, I could not find information on Wikipedia.")
        return

    # Google search
    if "search for" in c:
        query = c.replace("search for", "").strip()
        speak(f"Searching Google for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return

    # Weather
    if "weather" in c:
        words = c.split()
        if "in" in words:
            city = words[words.index("in") + 1]
            speak(get_weather(city))
        else:
            speak("Please tell me the city. For example: What is the weather in Delhi?")
        return

    # Music
    if "play music" in c or "play song" in c:
        play_music()
        return

    # Translate
    if "translate" in c:
        translate_text(c)
        return

    # Time & Date
    if "time" in c:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return
    if "date" in c:
        today = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {today}")
        return

    # Jokes
    if "joke" in c or "tell me a joke" in c:
        joke = pyjokes.get_joke()
        speak(joke)
        return

    # News
    if "news" in c:
        speak("Here are the top headlines:")
        get_news()
        return

    # COVID
    if "covid" in c:
        country = "India"
        words = c.split()
        if "in" in words:
            country = words[words.index("in") + 1]
        speak(get_covid(country))
        return

    # Notes
    if "note" in c:
        if "take a note" in c:
            note = c.replace("take a note", "").strip()
            take_note(note)
        elif "read my notes" in c:
            read_notes()
        elif "save secure note" in c:
            note = c.replace("save secure note", "").strip()
            save_secure_note(note)
        elif "read secure notes" in c:
            read_secure_notes()
        return

    # Math
    if "solve" in c or "what is" in c:
        solve_math(c)
        return
    if "calculate" in c or "advanced math" in c:
        solve_advanced_math(c)
        return

    # Fun facts
    if "fun fact" in c or "tell me something interesting" in c:
        tell_random_fact()
        return

    # Stocks
    if "stock price" in c:
        ticker = c.split()[-1].upper()
        get_stock_price(ticker)
        return

    # Cricket
    if "cricket score" in c:
        match_id = c.split()[-1]
        get_cricket_score(match_id)
        return

    # Reminders
    if "set reminder" in c:
        try:
            parts = c.split(" at ")
            message = parts[0].replace("set reminder", "").strip()
            time_str = parts[1].strip()
            set_reminder(time_str, message)
        except:
            speak("Please say reminder in format: set reminder <message> at <HH:MM>")
        return

    speak("Sorry sir, I don't know that command yet.")

# ------------------- MAIN -------------------
if __name__ == "__main__":
    speak("Hello sir, I am Jarvis, your personal assistant. How can I help you?")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio)
            print("You said:", command)

            if "hello jarvis" in command.lower():
                speak("Hello sir, how can I help you?")
            else:
                processCommand(command)
        except sr.UnknownValueError:
            print("Jarvis could not understand audio")
        except sr.RequestError as e:
            print("Jarvis error; {0}".format(e))