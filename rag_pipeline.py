# rag_pipeline.py
import os
import requests
import json
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Config ---
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --- Load Markdown KB ---
# Replace with your markdown docs or load from .md files
knowledge_base = [
    {"title": "Check-in Policy", "content": "Guests can check in from 2:00 PM onwards at Subic Waterfront View Resort."},
    {"title": "Pet Policy", "content": "Pets are not allowed in guest rooms."},
    {"title": "Wi-Fi", "content": "Free Wi-Fi is available in all rooms and public areas."},
    {"title": "Breakfast", "content": "Complimentary breakfast is served from 7:00 AM to 10:00 AM."},
    # Add more entries or dynamically load
]

# --- Embed KB ---
kb_embeddings = MODEL.encode([item["content"] for item in knowledge_base])


def get_answer(question: str) -> str:
    question_embedding = MODEL.encode([question])
    similarities = cosine_similarity(question_embedding, kb_embeddings)[0]
    top_idx = int(np.argmax(similarities))
    top_context = knowledge_base[top_idx]["content"]

    prompt = f"""
    Answer the user's question using the context below. If unsure, say you don't know.

    Context:
    {top_context}

    Question: {question}
    Answer:
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
        },
        timeout=15
    )

    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Sorry, I couldn't generate an answer. ({e})"
