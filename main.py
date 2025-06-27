# main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from rag_pipeline import get_answer
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import os

app = FastAPI()

# CORS for external apps (e.g., SendPulse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Facebook webhook verification
@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == os.getenv("FB_VERIFY_TOKEN"):
        return int(params.get("hub.challenge"))
    return {"status": "unauthorized"}

# Facebook webhook event handler
@app.post("/webhook")
async def handle_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(body, signature):
        return {"status": "invalid signature"}
    data = await request.json()
    print("FB Webhook received:", data)
    return {"status": "received"}

def verify_signature(payload: bytes, header_signature: str) -> bool:
    if not header_signature:
        return False
    secret = os.getenv("FB_APP_SECRET", "test_secret").encode()
    expected_signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_signature, header_signature)

# Smart AI chat endpoint for SendPulse
class Query(BaseModel):
    question: str

@app.post("/chat")
async def chat(query: Query):
    answer = get_answer(query.question)
    return {"answer": answer}