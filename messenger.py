# messenger.py
import os
import requests
from dotenv import load_dotenv
from query import query_bot

load_dotenv()
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

def send_message(recipient_id: str, message_text: str):
    # Handle local curl testing mode if sender_id is clearly fake
    if recipient_id.startswith("test_"):
        print(f"🧪 [TEST MODE] Simulated send to: {recipient_id}")
        print(f"📤 Message content: {message_text}")
        return

    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={FB_PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    print(f"📤 Sending to FB ID: {recipient_id}")
    print(f"✅ FB Response: {response.status_code} - {response.text}")

async def handle_message(payload: dict):
    print(f"📥 Raw payload received: {payload}")

    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            if "message" in event and "text" in event["message"]:
                message_text = event["message"]["text"]
                print(f"📩 Message from {sender_id}: {message_text}")

                # Use scripted greeting or fallback to RAG
                if message_text.lower().startswith("hi") or "inquire" in message_text.lower():
                    reply = "Hi po! Welcome to Fiesta Communities. How can we assist you today?"
                else:
                    reply = query_bot(message_text)

                send_message(sender_id, reply)
