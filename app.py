from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# System Prompt pwojè Lito a
SYSTEM_PROMPT = """You are Lito, an AI-powered educational assistant designed specifically for Haitian students.
Your mission is to help students learn, understand concepts, solve problems, and improve their academic performance in a simple, friendly, and encouraging way.
Response Formatting Rules:
1. Use LaTeX ($...$) for all mathematical formulas.
2. Use Markdown formatting (# titles, **bold text**, *lists*) to structure responses.
3. Be clear, direct, and always explain step-by-step when solving problems."""

# Kle sekirite yo ki soti nan Render Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. VERIFIKASYON WEBHOOK (Pou Meta)
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == "Lito_Secret_2026":
            return challenge, 200
        return "Forbidden", 403

    # 2. RESEVWA AK REPONN MESAJ WHATSAPP
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            # Tcheke si se yon mesaj itilizatè a voye
            if data.get("entry") and data["entry"][0].get("changes") and data["entry"][0]["changes"][0].get("value") and data["entry"][0]["changes"][0]["value"].get("messages"):
                
                message_details = data["entry"][0]["changes"][0]["value"]["messages"][0]
                user_phone = message_details["from"]  # Nimewo moun ki ekri a
                
                # Tcheke si se yon mesaj tèks
                if message_details.get("type") == "text":
                    user_text = message_details["text"]["body"]
                    
                    # A) Voye mesaj la bay Gemini pou l bay repons lan
                    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
                    gemini_payload = {
                        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
                    }
                    gemini_resp = requests.post(gemini_url, json=gemini_payload).json()
                    
                    # Ekstrè tèks repons Gemini a
                    lito_reply = gemini_resp['candidates'][0]['content']['parts'][0]['text']
                    
                    # B) Voye repons Lito a tounen bay itilizatè a sou WhatsApp
                    whatsapp_url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
                    headers = {
                        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                        "Content-Type": "application/json"
                    }
                    whatsapp_payload = {
                        "messaging_product": "whatsapp",
                        "to": user_phone,
                        "type": "text",
                        "text": {"body": lito_reply}
                    }
                    
                    requests.post(whatsapp_url, json=whatsapp_payload, headers=headers)
                    
        except Exception as e:
            print(f"Erè nan pwosesis la: {e}")
            
        return "OK", 200

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
                    
