import json
import requests
import os
import re
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- Constants ---
SIMILARITY_THRESHOLD = 0.4  # Lowered threshold to be more forgiving
GREETING_WORDS = {"hello", "hi", "good day", "good morning", "good evening", "helo", "gandang araw"}

# --- Load Knowledge Base ---
print("Loading knowledge base text...")
with open("vector_index.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)
print(f"Knowledge base with {len(knowledge_base)} chunks loaded.")


def find_best_context(question: str) -> str | None:
    """Finds the most relevant context chunk using keyword matching if it meets the threshold."""
    question_words = set(re.findall(r'\w+', question.lower()))
    if not question_words:
        return None

    scored_chunks = []
    for item in knowledge_base:
        text_words = set(item["text"].lower().split())
        common_words = question_words.intersection(text_words)
        score = len(common_words)
        scored_chunks.append({"score": score, "text": item["text"]})

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    best_chunk = scored_chunks[0]
    
    # Normalize score by the number of words in the question
    best_score_normalized = best_chunk["score"] / len(question_words) if len(question_words) > 0 else 0
    
    print(f"Top context match has a normalized score of: {best_score_normalized:.2f}")

    if best_score_normalized >= SIMILARITY_THRESHOLD:
        return best_chunk["text"]
    return None


def query_rag(question: str) -> str:
    """Handles user queries with improved logic for greetings and fallbacks."""
    print(f"Handling question: '{question}'")
    
    # Check for simple greetings first
    if any(greet in question.lower() for greet in GREETING_WORDS):
        print("Detected a greeting.")
        return "Hello po! Welcome to Fiesta Communities. How can I assist you today?"

    context = find_best_context(question)
    
    # This is the new, smarter part
    if context:
        print(f"Found relevant context: {context[:100]}...")
        system_prompt = (
            "You are FiestaBot, a helpful and polite real estate assistant for Fiesta Communities. "
            "Use ONLY the provided context to answer the user's question. Your tone must be friendly and professional. "
            "Address the user with 'ma'am/sir' and use 'po' or 'opo'."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        # If no good context is found, use this graceful fallback
        print("No relevant context found. Using fallback.")
        system_prompt = (
            "You are FiestaBot, a helpful and polite real estate assistant. "
            "The user asked a question you don't have specific context for. "
            "Politely ask them to rephrase their question or ask what specific information they need. "
            "For example: 'I'm not sure I have the exact details for that, could you please ask in a different way?'"
        )
        user_prompt = question

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    print("Sending request to Groq...")
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    
    answer = response.json()["choices"][0]["message"]["content"]
    print("Received answer from Groq.")
    return answer.strip()