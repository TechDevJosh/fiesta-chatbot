# messenger.py
import os
import json
import requests
from query import query_bot

FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

def send_message(recipient_id, message_text):
    """Send message to Facebook Messenger."""
    print(f"📤 Sending to {recipient_id}: {message_text}")  # Log out for debug
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    response = requests.post(url, params=params, headers=headers, json=payload)
    print("✅ FB Response:", response.status_code, response.text)

def get_greeting_reply(message_text):
    """Quick rule-based response."""
    if message_text.lower() in ["hi", "hello", "helo", "helloo", "hwllo"]:
        return "Hello po! I'm [Agent Name] from Fiesta Communities Prime Residences. How can I help you po?"
    else:
        return query_bot(message_text)

async def handle_message(data):
    """Handle incoming FB Messenger webhook POST"""
    print("📥 Raw payload received:", json.dumps(data, indent=2))
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]
            if "message" in event:
                message_text = event["message"].get("text")
                if message_text:
                    print(f"📩 Message from {sender_id}: {message_text}")
                    reply = get_greeting_reply(message_text)
                    send_message(sender_id, reply)
