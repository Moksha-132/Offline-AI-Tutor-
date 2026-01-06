import pyttsx3
import threading

# Global engine instance to avoid initialization issues
# pyttsx3 generally runs an event loop. In Streamlit, this can be tricky.
# We will use a separate thread or simple one-off calls if possible.
# Note that pyttsx3's runAndWait blocking behavior is what we want for "synchronous" feel in a separate thread.

class TTSManager:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150) # default speed
        except Exception as e:
            print(f"TTS Init Error: {e}")
            self.engine = None

    def speak(self, text, rate=150):
        if not self.engine:
            return
        
        try:
            # We must recreate or re-configure in the thread if running in a loop, 
            # but for simple offline apps, re-init inside function often avoids "loop already started" errors in Streamlit re-runs.
            engine = pyttsx3.init() 
            engine.setProperty('rate', rate)
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # Engine loop might be busy
            pass

    def save_to_file(self, text, filename, rate=150):
        if not self.engine:
            return False
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.save_to_file(text, filename)
            engine.runAndWait()
            return True
        except Exception:
            return False

def speak_text_thread(text, rate=150):
    """Runs TTS in a separate thread so UI doesn't freeze completely."""
    tts = TTSManager()
    thread = threading.Thread(target=tts.speak, args=(text, rate))
    thread.start()
