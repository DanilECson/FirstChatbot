import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import datetime
import requests
import random
import re
import string
import sys
import os

# --- My existing API Keys ---
API_KEY = '0f115764e9ea514ff6ac530e71123520'
TIMEZONE_API_KEY = 'T6Y64PZ7PG3Z'
OPENROUTER_API_KEY = "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"

fallback_responses = [
    "Hmm, I'm still learning that part. Want to ask about the time or weather?",
    "That's a cool question. I'm not sure yet, but I can help with jokes or math!",
    "I don’t know that one yet. Maybe try asking me the time?",
    "Not sure how to reply, but I'm getting smarter every day!"
]

def extract_city(user_input):
    # Lowercase and remove punctuation
    cleaned = re.sub(f"[{re.escape(string.punctuation)}]", "", user_input.lower())

    # Look for 'in' and extract everything after
    if ' in ' in cleaned:
        city = cleaned.split(' in ')[1]
        city_words = city.split()

        # Try combining up to 3 words (for cities like "rio de janeiro")
        for i in range(3, 0, -1):
            possible_city = ' '.join(city_words[:i])
            if possible_city in city_timezone_map:
                return possible_city
        return city_words[0]  # fallback to first word if no match
    return None


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_city_timezone_map():
    city_tz = {}
    try:
        filepath = resource_path("cities1000.txt")
        with open(filepath, encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) < 18:
                    continue
                city_name = parts[1].lower()
                timezone = parts[17]
                if city_name not in city_tz:
                    city_tz[city_name] = timezone
    except FileNotFoundError:
        print("cities1000.txt not found")
    return city_tz

city_timezone_map = load_city_timezone_map()


# --- Core Bot Logic Functions ---
def tell_time(city):
    city = city.lower()
    timezone = city_timezone_map.get(city, None)
    if not timezone:
        return f"Sorry, I don't know the timezone for '{city}'."

    url = f"https://api.timezonedb.com/v2.1/get-time-zone?key={TIMEZONE_API_KEY}&format=json&by=zone&zone={timezone}"
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] != 'OK':
            return "Sorry, I couldn't get the time right now."
        time = data['formatted'].split(' ')[1]
        return f"The local time in {city.title()} is {time[:5]}."
    except:
        return "Something went wrong while fetching the time."

def tell_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            return f"Sorry, I couldn't find weather data for '{city}'."
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The weather in {city.title()} is {description}. It's currently {temperature}°C."
    except:
        return "Sorry, I couldn't fetch weather data right now."

def tell_joke():
    jokes = [
        "Why don’t scientists trust atoms? Because they make up everything!",
        "Why did the math book look sad? Because it had too many problems.",
        "Why was the computer cold? It left its Windows open.",
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "What do you call a pony with a cough? A little horse.",
        "What did one hat say to the other? You wait here.I’ll go on a head.",
        "What do you call a magic dog? A labracadabrador.",
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "What do you call fake spaghetti? An impasta!",
        "Why don’t eggs tell jokes? They’d crack each other up.",
        "Why can’t your nose be 12 inches long? Because then it would be a foot!",
        "What do you call cheese that isn’t yours? Nacho cheese.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why did the bicycle fall over? Because it was two-tired.",
        "What did one wall say to the other wall? 'I'll meet you at the corner.'",
        "Why can’t you give Elsa a balloon? Because she will let it go!",
        "What do you get when you cross a snowman and a vampire? Frostbite.",
        "Why do bees have sticky hair? Because they use honeycombs!",
        "What do you call a pile of cats? A meowtain.",
        "How does a penguin build its house? Igloos it together.",
        "What do you call a dog magician? A labracadabrador.",
        "How do you make holy water? You boil the hell out of it.",
        "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
        "What do you call a can opener that doesn’t work? A can’t opener.",
        "Why did the coffee file a police report? It got mugged.",
        "Why did the orange stop? It ran out of juice.",
        "What did the grape do when it got stepped on? Nothing, it just let out a little wine.",
        "Why do cows wear bells? Because their horns don’t work.",
        "What’s brown and sticky? A stick.",
        "What do you call a fish with no eyes? Fsh.",
        "Why did the cookie go to the hospital? Because it felt crummy.",
        "Why was the math teacher late? She took the rhombus.",
        "Why don’t oysters share their pearls? Because they’re shellfish.",
        "What kind of shoes do ninjas wear? Sneakers.",
        "How does the moon cut his hair? Eclipse it.",
        "Did you hear about the claustrophobic astronaut? He just needed a little space.",
        "Why did the tomato blush? Because it saw the salad dressing.",
        "How does a scientist freshen their breath? With experi-mints!",
        "Why was the calendar so popular? It had a lot of dates.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why don’t some couples go to the gym? Because some relationships don’t work out.",
        "Did you hear about the guy who invented Lifesavers? He made a mint!",
        "I used to play piano by ear, but now I use my hands."
    ]
    return random.choice(jokes)


def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://yourappname.com",  # just identify your app
        "Content-Type": "application/json"
    }

    body = {
        "model": "mistralai/mistral-7b-instruct",  # change to any supported model
        "messages": [
            {"role": "system", "content": "You are a friendly AI assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print("Error from OpenRouter:", e)
        return random.choice(fallback_responses)

def get_bot_reply(text):
    text = text.lower()

    if 'time' in text:
        city = extract_city(text) or 'colombo'
        return tell_time(city)

    elif 'weather' in text:
        city = extract_city(text) or 'colombo'
        return tell_weather(city)

    elif 'joke' in text:
        return tell_joke()

    elif "what is your name" in text or "what's your name" in text or "Do you have a name" in text:
        return "I don't have a name right now but you can call me Bot"

    elif 'who made you' in text or 'who created you' in text or 'who programmed you' in text or 'made' in text or 'programmed' in text or 'created' in text:
        return "I was made by Danil Christopherson and powered by Mistral AI"

    elif any(q in text for q in ['bye', 'goodbye', 'see you']):
        return "Goodbye! Come back soon."

    else:
        return ask_openrouter(text)


# --- Kivy GUI Layout ---
class ChatBotLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Create scrollable chat log
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.chat_log_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=10, spacing=5)
        self.chat_log_box.bind(minimum_height=self.chat_log_box.setter('height'))
        self.scroll.add_widget(self.chat_log_box)

        # Create input field and send button
        self.input_box = TextInput(hint_text="Type your message...", multiline=False, size_hint_y=0.075)
        self.send_button = Button(text="Send", size_hint_y=0.075)
        self.send_button.bind(on_press=self.process_input)

        # Add everything to layout
        self.add_widget(self.scroll)
        self.add_widget(self.input_box)
        self.add_widget(self.send_button)

        # Greet the user
        self.add_message("Hi! Ask me anything", from_bot=True)

    def add_message(self, message, from_bot=False):
        prefix = "Bot: " if from_bot else "You: "
        label = Label(
            text=prefix + message,
            size_hint_y=None,
            halign='left',
            valign='top',
            text_size=(self.width - 30, None),
        )
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + 20))
        self.chat_log_box.add_widget(label)

        # Auto-scroll to bottom
        self.scroll.scroll_y = 0


    def process_input(self, instance):
        user_text = self.input_box.text.strip()
        if user_text == "":
            return

        self.add_message(user_text, from_bot=False)
        reply = get_bot_reply(user_text)
        self.add_message(reply, from_bot=True)
        self.input_box.text = ""


class ChatBotApp(App):
    def build(self):
        self.title = "Bot - Your AI Assistant"
        return ChatBotLayout()

if __name__ == '__main__':
    ChatBotApp().run()
