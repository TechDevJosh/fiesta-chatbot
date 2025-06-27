# main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv
from messenger import handle_message

# Load .env variables
load_dotenv()
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN")

# Initialize FastAPI app
app = FastAPI()

# Webhook verification (GET request)
@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)
    return PlainTextResponse("Verification failed", status_code=403)

# Incoming messages (POST request)
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    await handle_message(data)
    return JSONResponse(content={"status": "ok"})

# Health check root
@app.get("/")
def root():
    return {"status": "Bot is alive"}
