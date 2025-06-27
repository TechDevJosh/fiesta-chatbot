from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from query import query_rag  # <-- CORRECTED LINE

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # This is a safe entry point that handles potential errors
    try:
        # Calls the function from query.py
        answer = query_rag(request.question)
        return {"answer": answer}
    except Exception as e:
        # If anything goes wrong, it returns a helpful error message
        print(f"An error occurred: {e}")
        return {"answer": f"Sorry, an error occurred on our end. Please try again in a moment."}