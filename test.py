import pyttsx3

engine = pyttsx3.init()

# List all available voices
voices = engine.getProperty('voices')

# Print voice info (optional)
for index, voice in enumerate(voices):
    print(f"{index}: {voice.name} ({voice.gender if hasattr(voice, 'gender') else 'unknown'})")

# Set to female voice (often index 1 on Windows)
engine.setProperty('voice', voices[1].id)

# Say something
engine.say("Hello, I am a female voice speaking to you.")
engine.runAndWait()
