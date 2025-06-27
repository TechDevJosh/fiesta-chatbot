from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from dotenv import load_dotenv
import os
from messenger import handle_message, VERIFY_TOKEN

load_dotenv()
app = FastAPI()

@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return PlainTextResponse(params.get("hub.challenge"))
    return PlainTextResponse("Verification failed", status_code=403)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    await handle_message(data)
    return JSONResponse(content={"status": "ok"})

@app.get("/")
def root():
    return {"status": "Bot is alive"}
