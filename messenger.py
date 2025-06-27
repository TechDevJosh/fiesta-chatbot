import os
import requests
from dotenv import load_dotenv
from query import query_bot

load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")

FB_URL = "https://graph.facebook.com/v18.0/me/messages"

def send_fb_message(recipient_id, message_text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}"
    }
    response = requests.post(FB_URL, params={"access_token": PAGE_ACCESS_TOKEN}, headers=headers, json=payload)
    if response.status_code != 200:
        print("❌ FB Send Error:", response.status_code, response.text)

async def handle_message(data):
    if "entry" in data:
        for entry in data["entry"]:
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")
                    if message_text:
                        print(f"📨 From {sender_id}: {message_text}")
                        reply = query_bot(message_text)
                        send_fb_message(sender_id, reply)
