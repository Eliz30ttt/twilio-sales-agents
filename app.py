from flask import Flask, request
import requests
import os
from twilio.twiml.voice_response import VoiceResponse

app = Flask(name)

# Load Hugging Face API token from environment
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

def query_hf(prompt):
    payload = {"inputs": prompt}
    response = requests.post(MODEL_URL, headers=headers, json=payload)
    return response.json()

# Test route
@app.route("/")
def home():
    return "AI Sales Agent is running!"

# Twilio entry point
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    gather = resp.gather(
        input="speech",
        action="/process",
        method="POST",
        speechTimeout="auto"
    )

    gather.say("Hi, this is an AI sales assistant. What are you looking for today?")

    return str(resp)

# Process speech
@app.route("/process", methods=["POST"])
def process():
    user_input = request.form.get("SpeechResult", "")

    prompt = f"""
You are a professional phone sales agent.

Rules:
- Keep responses short (1-2 sentences)
- Ask one question at a time
- Qualify the lead (budget, needs, intent)
- Sound natural and conversational

Customer said:
{user_input}

Respond:
"""

    try:
        hf_response = query_hf(prompt)
        ai_text = hf_response[0]["generated_text"]
    except:
        ai_text = "Sorry, I didn’t catch that. Can you repeat?"

    resp = VoiceResponse()
    resp.say(ai_text)

    resp.gather(
        input="speech",
        action="/process",
        method="POST"
    )

    return str(resp)

if name == "main":
    app.run(host="0.0.0.0", port=10000)
