from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# System Prompt ou a: Mwen mete premye pati a pou ou, ou ka ranpli rès la pita
SYSTEM_PROMPT = """You are Lito, an AI-powered educational assistant designed specifically for Haitian students.
Your mission is to help students learn, understand concepts, solve problems, and improve their academic performance in a simple, friendly, and encouraging way.
Response Formatting Rules:
1. Use LaTeX ($...$) for all mathematical formulas.
2. Use Markdown formatting (# titles, **bold text**, *lists*) to structure responses.
3. Be clear, direct, and always explain step-by-step when solving problems."""

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 

# --- 1. WOUT POU META WHATSAPP (Sa ki t ap bloke w la) ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # Meta ap voye yon GET request pou l verifye koneksyon an
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        # Token sa dwe idantik ak sa w mete nan bwat Meta a
        if mode == "subscribe" and token == "Lito_Secret_2026":
            return challenge, 200
        return "Forbidden", 403

    # Lè yon moun ekri w sou WhatsApp, Meta ap voye mesaj la isit la
    if request.method == 'POST':
        # Nou pral travay sou pati sa a pita pou voye mesaj la bay Gemini
        return "OK", 200


# --- 2. WOUT POU APLIKASYON ANDROID OU A (Kòd ou te genyen an) ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_text = data.get("text")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
    }
    
    response = requests.post(url, json=payload)
    return jsonify(response.json())

if __name__ == '__main__':
    # Sa ede l mache san pwoblèm sou Render
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    
