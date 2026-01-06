from google import genai
import os

# Using the same key used for tutoring
GEMINI_API_KEY = "AIzaSyAzlbCghujpX2mp9f6dstOH-Ha26RhWNwI"

class SpeechManager:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def transcribe_audio(self, audio_bytes):
        """Transcribes audio data using Google Gemini."""
        try:
            # Gemini can process audio bytes directly or via a temp file
            # For robustness with the SDK, we'll use the multimodal capability
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp", # Using flash for speed
                contents=[
                    "Transcribe this audio clip into plain text. Only return the transcription, nothing else.",
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ]
            )
            return response.text.strip()
        except Exception as e:
            print(f"STT Error: {e}")
            return None
