import os
import json
import requests
import asyncio
import traceback
from fastapi import Request
from fastapi.responses import Response
from query import query_bot

VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")

def send_fb_message(recipient_id, message_text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://graph.facebook.com/v18.0/me/messages",
        params={"access_token": PAGE_ACCESS_TOKEN},
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        print("❌ FB Send Error:", response.status_code, response.text)
    else:
        print("✅ Sent:", message_text)

def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Verification failed", media_type="text/plain")

async def handle_message(request: Request):
    try:
        data = await request.json()
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                message_text = event["message"].get("text")
                print(f"📨 From {sender_id}: {message_text}")

                if message_text:
                    reply = await asyncio.to_thread(query_bot, message_text)
                    await asyncio.to_thread(send_fb_message, sender_id, reply)
    except Exception as e:
        print("❌ Exception in handle_message():", e)
        traceback.print_exc()
