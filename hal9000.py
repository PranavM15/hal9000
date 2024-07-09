import os
import subprocess
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import smtplib
import pywhatkit as kit
import time
import requests
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

emails = {
    "Mark": "mcuban@gmail.com",
    "Elon": "emusk@gmail.com",
    "Sheryl": "ssandberg@gmail.com",
    "Sundar": "spichai@gmail.com",
    "Tim": "tcook@gmail.com",
    "Satya": "snadella@gmail.com",
    "Susan": "swojcicki@gmail.com",
    "Reed": "rhastings@gmail.com",
    "Gini": "grometty@gmail.com",
    "Jeff": "jbezos@gmail.com",
    "Marissa": "mmayer@gmail.com"
}

def say(audio, rate=1.15):
    subprocess.call(['say', '-r', str(int(180 * rate)), audio])

def greet():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        say("Good morning!")
    elif hour >= 12 and hour < 18:
        say("Good afternoon!")
    else:
        say("Good evening!")

    say("My name is Hal 9000! What can I do for you?")

def readCommand():
    r = sr.Recognizer()
    mic = sr.Microphone()

    r.energy_threshold = 400 
    r.dynamic_energy_threshold = True
    r.dynamic_energy_adjustment_damping = 0.1
    r.dynamic_energy_ratio = 2.0 
    r.pause_threshold = 0.6
    r.operation_timeout = 5
    r.phrase_threshold = 0.3
    r.non_speaking_duration = 0.3

    with mic as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
    try:
        print("Recognizing...")
        transcript = r.recognize_google(audio)
        print(transcript)
    except Exception as e:
        print("Say that again please...")
        return "None"
    return transcript

def open_application(app_name):
    d = '/Applications'
    apps = list(map(lambda x: x.split('.app')[0].lower(), os.listdir(d)))
    
    for app in apps:
        if app_name in app:
            app_path = os.path.join(d, app + '.app')
            os.system(f'open "{app_path}"')
            return True
    return False

def open_website(site_name):
    site_name = site_name.replace(" ", "")
    if not site_name.startswith("http"):
        site_name = "http://" + site_name + ".com"
    webbrowser.open(site_name)
    return True

def search_youtube(query):
    search_url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(search_url)

def play_youtube_video(query):
    kit.playonyt(query)
    say(f"Playing {query} on YouTube")

def send_email(to_address, subject, body):
    from_address = "your-email@gmail.com"
    password = "your-password"
    
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_address, password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        say("Email sent successfully")
    except Exception as e:
        say("Failed to send email")
        print(e)

def tell_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    say(f"The current time is {current_time}")

def logout():
    say("Logging out.")
    os.system("osascript -e 'tell application \"System Events\" to log out'")

def tell_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    joke = response.json()
    say(joke["setup"])
    say(joke["punchline"])

def create_google_item(item):
    urls = {
        'document': 'https://docs.new',
        'sheet': 'https://sheets.new',
        'slide': 'https://slides.new',
        'meet': 'https://meet.new',
        'form': 'https://forms.new',
        'site': 'https://sites.new'
    }
    if item in urls:
        webbrowser.open(urls[item])
        say(f"Creating a new Google {item}")
    else:
        say(f"Sorry, I can't create a {item}")

def set_timer(duration):
    say(f"Setting a timer for {duration} seconds.")
    time.sleep(duration)
    say("Time's up!")

def take_note():
    say("What would you like to note down?")
    note = readCommand()
    with open("notes.txt", "a") as file:
        file.write(note + "\n")
    say("Note taken.")

def calculate(expression):
    try:
        result = eval(expression)
        say(f"The result is {result}")
    except Exception as e:
        say("I couldn't calculate that.")

def summarize_wikipedia(topic):
    try:
        summary = wikipedia.summary(topic, sentences=3)
        say(summary)
    except Exception as e:
        say("I couldn't find any information on that topic.")

def generate_openai_response(prompt):
    from config import apikey

    try:
        client = OpenAI(
            api_key=os.environ[apikey],  
        )

        response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=1,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        ) 
        message = response.choices[0].text.strip()
        say(message)
    except Exception as e:
        say("Sorry, I couldn't generate a response.")
        print(e)
        return None

if __name__ == "__main__":
    greet()
    while True:
        transcript = readCommand().lower()

        if 'stop' in transcript:
            say("Goodbye!")
            break
        
        if 'open' in transcript:
            target = transcript.replace('open', '').strip()
            if open_application(target):
                say(f"Opening the {target} application!")
            else:
                open_website(target)
                say(f"Opening {target}.com!")

        elif 'wikipedia' in transcript:
            say("Searching Wikipedia...")
            transcript = transcript.replace("wikipedia", "")
            results = wikipedia.summary(transcript, sentences = 3)
            print(results)
            say("According to Wikipedia, " + results)

        elif 'search youtube for' in transcript:
            query = transcript.replace('search youtube for', '').strip()
            search_youtube(query)
            say(f"Searching YouTube for {query}")
        
        elif 'send an email to' in transcript:
            name = transcript.split('send an email to ')[1].split(' subject ')[0].strip().title()
            if name in emails:
                try:
                    to_address = emails[name]
                    subject = transcript.split('subject ')[1].split(' body ')[0].strip()
                    body = transcript.split('body ')[1].strip()
                    send_email(to_address, subject, body)
                except IndexError:
                    say("Please provide the email subject and body in the correct format")
            else:
                say(f"Email address for {name} not found")

        elif 'play' in transcript:
            track_name = transcript.replace('play', '').strip()
            play_youtube_video(track_name)

        elif "the time" in transcript:
            tell_time()
        
        elif 'log out' in transcript:
            logout()

        elif 'joke' in transcript or 'funny' in transcript or 'laugh' in transcript:
            tell_joke()

        elif 'create a new' in transcript:
            item = transcript.replace('create a new', '').strip()
            create_google_item(item)

        elif 'set a timer for' in transcript:
            try:
                duration = int(transcript.split('set a timer for')[1].strip().split()[0])
                set_timer(duration)
            except (IndexError, ValueError):
                say("Please specify the duration in seconds correctly.")

        elif 'note' in transcript:
            take_note()
        
        elif 'calculate' in transcript:
            expression = transcript.replace('calculate', '').strip()
            calculate(expression)
        
        elif 'summarise' in transcript or 'summary' in transcript:
            topic = transcript.replace('summarize', '').strip()
            summarize_wikipedia(topic)

        elif 'ai' in transcript:
            generate_openai_response(transcript)
