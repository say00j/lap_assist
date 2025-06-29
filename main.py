import pvporcupine
import pyaudio
import struct
import tkinter as tk
from dotenv import load_dotenv
import os
import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
load_dotenv()
API_KEY = os.getenv("API_KEY")

# GUI global reference
label = None

def recognize_speech():
    global label
    with sr.Microphone() as source:
        label.configure(text="Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        label.configure(text="You said: " + text)
    except sr.UnknownValueError:
        label.configure(text="Could not understand audio")
    except sr.RequestError as e:
        label.configure(text="Could not request results: " + str(e))

def gui():
    global label
    root = tk.Tk()
    root.title("Lap Assist")

    label = tk.Label(root, text="", font=("Arial", 20))
    label.pack(padx=20, pady=20)

    # Start speech recognition in a new thread
    threading.Thread(target=recognize_speech, daemon=True).start()

    root.mainloop()

# Initialize Porcupine
porcupine = pvporcupine.create(access_key=API_KEY, keywords=["jarvis"])

# Set up microphone
pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("Listening for 'Jarvis'...")

try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Hotword 'Jarvis' detected!")
            gui()  # Open GUI when hotword detected
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
