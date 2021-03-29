import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
import tkinter as tk

API_KEY  = "tLqLAxukkTYi"
PROJECT_TOKEN = "tKcz_WO1uxY4"
RUN_TOKEN = "tyb-HMqgLD5t"

class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        }
        self.data = self.get_data()

    def get_data(self):
        response = requests.get(f"https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data", params = self.params)
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        total = self.data["total"]
        for content in total:
            if content["name"] == "Coronavirus Cases:":
                return content["value"]

        return "0"

    def get_total_deaths(self):
        total = self.data["total"]
        for content in total:
            if content["name"] == "Deaths:":
                return content["value"]

        return "0"   

    def get_total_recovered(self):
        total = self.data["total"]
        for content in total:
            if content["name"] == "Recovered:":
                return content["value"]
        
        return "0"

    def get_country_data(self, country):
        data = self.data["country"]

        for content in data:
            if content["name"].lower() == country.lower():
                return content

        return "0"   

    def get_list_of_countries(self):
        countries = []
        for country in self.data["country"]:
            countries.append(country["name"].lower())

        return countries  

    def update_data(self):
        requests.post(f"https://www.parsehub.com/api/v2/projects/{self.project_token}/run", params=self.params)

        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new_data
                    print("Data updated")
                    break
                time.sleep(5)


        t = threading.Thread(target=poll)
        t.start()

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            e = str(e)
            #print("Exception:",e)
    return said.lower()

root = tk.Tk()
root.title("Covid-19 Voice Assistant")
answer_text = tk.StringVar()

data = Data(API_KEY, PROJECT_TOKEN)

TOTAL_PATTERNS = {
                re.compile("[\w\s]+ total cases [\w\s]"):data.get_total_cases,
                re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
                re.compile("[\w\s]+ total cases"):data.get_total_cases,
                
                re.compile("[\w\s]+ total deaths [\w\s]"):data.get_total_deaths,
                re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
                re.compile("[\w\s]+ total deaths"):data.get_total_deaths,

                re.compile("[\w\s]+ total recovered [\w\s]"):data.get_total_recovered,
                re.compile("[\w\s]+ total [\w\s]+ recovered"):data.get_total_recovered,
                re.compile("[\w\s]+ total recovered"):data.get_total_recovered,
                    
                }

COUNTRY_PATTERNS = {
                re.compile("[\w\s]+ new deaths [\w\s]+"): lambda country: data.get_country_data(country)["new_deaths"],
                re.compile("new deaths [\w\s]+"): lambda country: data.get_country_data(country)["new_deaths"],
                re.compile("[\w\s]+ new cases [\w\s]+"): lambda country: data.get_country_data(country)["new_cases"],
                re.compile("new cases [\w\s]+"): lambda country: data.get_country_data(country)["new_cases"],
                re.compile("[\w\s]+ active cases [\w\s]+"): lambda country: data.get_country_data(country)["active_cases"],
                re.compile("active cases [\w\s]+"): lambda country: data.get_country_data(country)["active_cases"],
                re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)["total_cases"],
                re.compile("cases [\w\s]+"): lambda country: data.get_country_data(country)["total_cases"],
                re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)["total_deaths"],
                re.compile("deaths [\w\s]+"): lambda country: data.get_country_data(country)["total_deaths"],
                }
UPDATE_COMMAND = "update"

def question():
    country_list = data.get_list_of_countries()

    s = answer_text.get()
    print("Listening...")
    text = ""
    speak("I'm listening")
    while text == "":
        text = get_audio()
    print(text)
    result = None

    for pattern, func in COUNTRY_PATTERNS.items():
        if pattern.match(text) and result == None:
            words = set(text.split(" "))
            for country in country_list:
                if country in words:
                    result = func(country)
                    if(result == "" or result == " "):
                        result = "Sorry, but this data it's not published yet"
                    break
        

    for pattern, func in TOTAL_PATTERNS.items():
        if pattern.match(text):
            result = func()
            break
    
    if text == UPDATE_COMMAND:
        result = "Data is being updated. This may take a moment!"
        data.update_data()

    if result:
        print(result)
        s += result + "\n"
        speak(result)
    elif text!="":
        s += "Sorry, I don't understand. Can you call it again?" + "\n"
        speak("Sorry, I don't understand. Can you call it again?")
    answer_text.set(s)

                    
HEIGHT = 620
WIDTH = 1000

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

background_image = tk.PhotoImage(file="covid.png")
background_label = tk.Label(root, image=background_image)
background_label.place(relwidth=1, relheight=1)

frame = tk.Frame(root, bg="#80c1ff", bd=5)
frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.1, anchor="n")

entry = tk.Label(frame, font=40, text="I'm listening!")
entry.place(relwidth=0.65, relheight=1)


lower_frame = tk.Frame(root, bg="#80c1ff", bd=10)
lower_frame.place(relx=0.5, rely=0.20, relwidth=0.75, relheight=0.3, anchor="n")

label_hints = tk.Label(lower_frame, text =  "Hints:\n"
                                            "Say: 'Update', if you want fresh data!\n"
                                            "Here are some questions you can ask from me:\n"
                                            "How many total cases in the world?\n"
                                            "How many new cases in Romania?\n"
                                            "How many active cases in France?\n"
                                            "How many new deaths in China?\n"
                                            "How many total recovered in the world?",
                                             font=("Courier", 13), anchor="nw", justify="left",bd=4)
label_hints.place(relwidth=1, relheight=1)


lower_frame2 = tk.Frame(root, bg="#80c1ff", bd=10)
lower_frame2.place(relx=0.5, rely=0.5, relwidth=0.75, relheight= 0.4, anchor="n")

answer = tk.Text(lower_frame2, font=("Courier", 13), bd=4)
#answer.insert(tk.END,answer_text)
answer.place(relwidth=1, relheight=1)
answer.pack()
answer_text.trace("w", lambda a,b,c: answer.insert(tk.END,answer_text.get()))
answer.config(state="disabled")

button_image = tk.PhotoImage(file="microphone.png")
button = tk.Button(frame, image=button_image, command = question)
button.place(relx=0.7, relheight=1, relwidth=0.3)


root.mainloop()




