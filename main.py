import speech_recognition as sr
import os
import webbrowser
import requests
import openai
import datetime
import pyttsx3  # For text-to-speech
import json  # For storing and retrieving knowledge
from config import apikey

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Chat history and knowledge base
chatStr = ""
knowledge_base = {}
tasks = []

# Load knowledge base from file (if exists)
if os.path.exists("knowledge_base.json"):
    with open("knowledge_base.json", "r") as kb_file:
        knowledge_base = json.load(kb_file)

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    """Captures microphone input from the user."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that. Please say it again.")
            return ""
        except sr.RequestError as e:
            speak("There was a problem with the speech recognition service.")
            print(f"Error: {e}")
            return ""

def save_knowledge():
    """Save the current knowledge base to a file."""
    with open("knowledge_base.json", "w") as kb_file:
        json.dump(knowledge_base, kb_file, indent=4)

def search_web(query):
    """Search for the query using ChatGPT."""
    try:
        openai.api_key = apikey
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        reply = response["choices"][0]["message"]["content"]
        speak(reply)
        print(reply)
        return reply
    except openai.error.OpenAIError as e:
        speak("There was an error while communicating with OpenAI.")
        print(f"Error: {e}")
        return "Error occurred."

def get_weather(location):
    """Fetch current weather for a location using OpenWeatherMap API."""
    api_key = "3bbca5c6b6ec60b6af2c3016ea8e8c7f"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            speak(f"The weather in {location} is {weather} with a temperature of {temp} degrees Celsius.")
            print(f"Weather in {location}: {weather}, {temp}°C")
        else:
            speak("Sorry, I couldn't fetch the weather details. Please check the location.")
    except Exception as e:
        speak("An error occurred while fetching the weather.")
        print(f"Error: {e}")

def manage_tasks(action, task=None):
    """Manage daily tasks."""
    global tasks
    if action == "add":
        tasks.append(task)
        speak("Task added.")
    elif action == "show":
        if tasks:
            speak("Here are your tasks.")
            for i, task in enumerate(tasks, 1):
                speak(f"{i}. {task}")
        else:
            speak("You have no tasks.")
    elif action == "clear":
        tasks = []
        speak("All tasks cleared.")

def help_menu():
    """Display the help menu with available commands."""
    commands = [
        "open [site name] - Opens websites like Google, YouTube.",
        "what is the time - Tells the current time.",
        "add task - Adds a task to your list.",
        "show tasks - Shows your task list.",
        "clear tasks - Clears all tasks.",
        "weather [location] - Gets the weather for a location.",
        "reset chat - Resets chat history.",
        "turn off - Shuts down Jarvis."
    ]
    speak("Here are some commands you can use:")
    for cmd in commands:
        print(cmd)
        speak(cmd)

def learn_from_interaction(query):
    """Automatically learns new information during interaction."""
    global knowledge_base
    speak("I couldn't find the answer to that. Let me try to help.")
    result = search_web(query)  # Use your existing `search_web` function for this.
    if result and result != "Error occurred.":
        speak("Does this answer your question?")
        print("Listening for your confirmation or correction...")
        answer = takeCommand().lower()
        if "yes" in answer:
            knowledge_base[query] = result
            save_knowledge()
            speak("Got it! I've saved this information.")
        elif "no" in answer:
            speak("What should the correct answer be?")
            correct_answer = takeCommand().lower()
            if correct_answer:
                knowledge_base[query] = correct_answer
                save_knowledge()
                speak("Thank you! I've updated my knowledge.")
        else:
            speak("Alright, I won't save this information for now.")
    else:
        speak("Sorry, I couldn't find an answer. Please try again later.")

if __name__ == '__main__':
    print("Welcome to Jarvis A.I")
    speak("Jarvis A.I is now activated.")
    while True:
        query = takeCommand().lower()

        if "turn off" in query:
            speak("Goodbye! Have a nice day.")
            break

        elif "reset chat" in query:
            chatStr = ""
            speak("Chat history reset.")

        elif "weather" in query:
            location = query.replace("weather", "").strip()
            get_weather(location)

        elif "add task" in query:
            speak("What task would you like to add?")
            task = takeCommand().lower()
            manage_tasks("add", task)

        elif "show tasks" in query:
            manage_tasks("show")

        elif "clear tasks" in query:
            manage_tasks("clear")

        elif "help" in query:
            help_menu()

        else:
            if query in knowledge_base:
                speak(knowledge_base[query])
            else:
                learn_from_interaction(query)
