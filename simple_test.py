"""
Simple test of Ollama basic functionality
"""
import requests

url = "http://127.0.0.1:11434/api/generate"
data = {
    "model": "llama3.2:1b",
    "prompt": "Say hello",
    "stream": False
}

print("Testing Ollama...")
try:
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    print(f"Response: {result.get('response', 'No response')}")
    print("✓ Test passed!")
except Exception as e:
    print(f"✗ Error: {e}")
