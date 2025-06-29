import pvporcupine
import pyaudio
import struct
import tkinter as tk
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

def gui():
    # Create the main window
    root = tk.Tk()
    root.title("Hello World App")

    # Create a label with the text "Hello, World!"
    label = tk.Label(root, text="Hello, World!", font=("Arial", 20))
    label.pack(padx=20, pady=20)

    # Start the Tkinter event loop
    root.mainloop()

# Initialize Porcupine
porcupine = pvporcupine.create(API_KEY,keywords=["jarvis"])  # other options: "alexa", "hey google", "picovoice", etc.

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
            gui()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()


