"""
Script to check available Gemini models
"""
import os
import google.generativeai as genai

# Configure API
api_key = os.getenv('GEMINI_API_KEY', 'your-api-key-here')
genai.configure(api_key=api_key)

print("Available Gemini Models:")
print("-" * 50)

try:
    for model in genai.list_models():
        print(f"Model: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print("-" * 50)
except Exception as e:
    print(f"Error: {e}")
