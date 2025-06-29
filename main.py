import pvporcupine
import pyaudio
import struct
import tkinter as tk
from dotenv import load_dotenv
import os
import speech_recognition as sr
import threading
import queue

# Load environment
load_dotenv()
API_KEY = os.getenv("API_KEY")

recognizer = sr.Recognizer()
event_queue = queue.Queue()

# GUI running flag
gui_running = False

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
            audio = recognizer.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            text_box.insert(tk.END, "No speech detected.\n")
            return

    try:
        text = recognizer.recognize_google(audio)
        text_box.insert(tk.END, f"\nYou said: {text}\n")
        if "exit" in text.lower():
            root.quit()
    except sr.UnknownValueError:
        text_box.insert(tk.END, "\nCould not understand audio\n")
    except sr.RequestError as e:
        text_box.insert(tk.END, f"\nError: {e}\n")

# Porcupine detection in background
def hotword_loop():
    porcupine = pvporcupine.create(access_key=API_KEY, keywords=["jarvis"])
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
