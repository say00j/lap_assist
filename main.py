import pvporcupine
import pyaudio
import struct
import tkinter as tk
from dotenv import load_dotenv
import os
import speech_recognition as sr
import threading
import queue
import webbrowser
import pygame
import pyautogui
import google.generativeai as genai
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index for different voice
    engine.say(text)
    engine.runAndWait()




# Load environment
load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")
API_KEY = os.getenv("API_KEY")

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("notif_sound.wav")

recognizer = sr.Recognizer()
event_queue = queue.Queue()

# GUI running flag
gui_running = False

#gemini
def givePrompt(api_key,prompt):

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-002")  # Or 'gemini-pro-vision'
        response = model.generate_content(prompt)
        if response and response.text: # Check for a valid response
            return response.text
        else:
            return "API key may be valid, but something went wrong."

    except Exception as e:
        return f"API key is invalid or an error occurred: {e}"

# GUI Setup
def gui():
    global root, text_box

    root = tk.Tk()
    root.title("Lap Assist")
    root.geometry("500x500")

    text_box = tk.Text(root, height=25, width=60)
    text_box.pack(pady=10)

    root.after(100, process_events)
    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())
    root.mainloop()

# Process events safely in the main thread
def process_events():
    try:
        while True:
            event = event_queue.get_nowait()
            if event == "jarvis":
                try:
                    engine.stop()
                    pygame.mixer.music.play()
                finally:
                    text_box.insert(tk.END, "Hotword 'Jarvis' detected!\n")
                    threading.Thread(target=recognize_speech, daemon=True).start()
    except queue.Empty:
        pass
    root.after(100, process_events)

# Speech recognition thread
def recognize_speech():
    global gui_running
    with sr.Microphone() as source:
        text_box.insert(tk.END, "Listening...\n")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
        except sr.WaitTimeoutError:
            text_box.insert(tk.END, "No speech detected.\n")
            return

    try:
        text = recognizer.recognize_google(audio)
        print("text = " + text)
        gemini_tuned_text = givePrompt(API_KEY,f""" prompt='{text}' follow these rules for prompt,
                                       1.if prompt is something like 'iron man wor' fix and return 'iron man working' no need to explain just return the prompt,
                                       2.if prompt is starting with question words, return the answer in plain text,
                                       3.Dont cut down the prompt
                                       4.dont bold the text using **
                                       """)
        text_box.insert(tk.END, f"\nYou said: {text}\n")
        text_box.insert(tk.END, f"\njarvis: {gemini_tuned_text}\n")
        speak(gemini_tuned_text)

        if "shutdown" in gemini_tuned_text.lower():
            root.quit()
        elif "open youtube" in gemini_tuned_text.lower():
            query = gemini_tuned_text.lower()[gemini_tuned_text.lower().find("youtube") + len("youtube") + 1:]
            print("query=" + query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        elif "open google" in gemini_tuned_text.lower():
            query = gemini_tuned_text.lower()[gemini_tuned_text.lower().find("google") + len("google") + 1:]
            print("query=" + query)
            webbrowser.open(f"https://www.google.com/search?q={query}")
        elif "scroll up" in gemini_tuned_text.lower():
            pyautogui.scroll(500) 
        elif "scroll down" in gemini_tuned_text.lower():
            pyautogui.scroll(-500) 



    except sr.UnknownValueError:
        text_box.insert(tk.END, "\nCould not understand audio\n")
    except sr.RequestError as e:
        text_box.insert(tk.END, f"\nError: {e}\n")

# Porcupine detection in background
def hotword_loop():
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["jarvis"])
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                event_queue.put("jarvis")
    except Exception as e:
        print("Error in hotword loop:", e)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

# Start hotword detection in background
threading.Thread(target=hotword_loop, daemon=True).start()

# Start GUI in main thread
gui()
