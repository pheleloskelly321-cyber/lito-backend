from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# System Prompt la rete fiks isit la
SYSTEM_PROMPT = """You are Lito, an AI-powered educational assistant... (kole tout system prompt ou a isit la)"""

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") # N ap mete kle a nan Render, pa nan kòd la!

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_text = data.get("text")
    
    # Lojik pou voye bay Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
    }
    
    response = requests.post(url, json=payload)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run()
  
