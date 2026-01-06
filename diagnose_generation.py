"""
Diagnostic script for quiz generation issues
"""
import requests
import json
import sys

# Configuration
OLLAMA_BASE_URL = "http://127.0.0.1:11434/api"
MODEL = "llama3.2:1b" 
CONCEPT = "Generative AI"

def query_ollama(prompt, model=MODEL, stream=True, json_format=False):
    payload = {
        "model": model, 
        "prompt": prompt, 
        "stream": stream,
        "options": {
            "num_predict": 2048,
            "num_ctx": 4096,
            "temperature": 0.7
        }
    }
    if json_format:
        payload["format"] = "json"

    print(f"Sending request... (Stream={stream}, JSON={json_format})")
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/generate", json=payload, stream=stream, timeout=(5, 300))
        response.raise_for_status()
        
        full_text = ""
        for line in response.iter_lines():
            if line:
                decoded = json.loads(line.decode('utf-8'))
                chunk = decoded.get("response", "")
                sys.stdout.write(chunk)
                sys.stdout.flush()
                full_text += chunk
        return full_text
    except Exception as e:
        print(f"\nError: {e}")
        return ""

prompt = (
    f"Generate a 5-question multiple choice quiz about '{CONCEPT}'.\n"
    "Format each question EXACTLY like this (Text format, NO JSON):\n\n"
    "Q1. [Question Text]?\n"
    "A) [Option 1]\n"
    "B) [Option 2]\n"
    "C) [Option 3]\n"
    "D) [Option 4]\n"
    "Answer: [Full Option Text]\n\n"
    "Do not write introductions. Start directly with Q1."
)

print("-" * 50)
print("TESTING QUIZ GENERATION (Text Mode)")
print("-" * 50)
output = query_ollama(prompt)
print("\n" + "-" * 50)
print("\nCOMPLETE OUTPUT RECEIVED.")
print(f"Length: {len(output)} characters")
