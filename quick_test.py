import requests
import json
import time

print("Testing Ollama with minimal parameters...")
start = time.time()

payload = {
    "model": "llama3.2:1b",
    "prompt": "Hi",
    "stream": False,
    "options": {
        "num_predict": 50  # Limit to just 50 tokens
    }
}

try:
    response = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=120)
    elapsed = time.time() - start
    result = response.json()
    
    print(f"✓ Response received in {elapsed:.2f} seconds")
    print(f"Response: {result.get('response', 'EMPTY')}")
    print(f"Done: {result.get('done', False)}")
    
    if not result.get('response'):
        print("\n⚠️ WARNING: Model returned empty response!")
        print("Full response JSON:")
        print(json.dumps(result, indent=2))
        
except requests.exceptions.Timeout:
    print(f"✗ Request timed out after {time.time() - start:.2f} seconds")
except Exception as e:
    print(f"✗ Error: {e}")
