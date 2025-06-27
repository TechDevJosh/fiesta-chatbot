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
SIMILARITY_THRESHOLD = 0.3  # Lowered threshold slightly to catch more queries
GREETING_WORDS = {"hello", "hi", "good day", "good morning", "good evening", "helo", "gandang araw", "magandang araw"}

# --- Load Knowledge Base ---
try:
    with open("vector_index.json", "r", encoding="utf-8") as f:
        knowledge_base = json.load(f)
    print(f"✅ Knowledge base with {len(knowledge_base)} chunks loaded successfully.")
except FileNotFoundError:
    knowledge_base = []
    print("⚠️ WARNING: vector_index.json not found. The bot will have no knowledge base.")

def find_best_context(question: str) -> str | None:
    """Finds the most relevant context using simple keyword matching."""
    if not knowledge_base:
        return None

    question_words = set(re.findall(r'\w+', question.lower()))
    if not question_words:
        return None

    scored_chunks = []
    for item in knowledge_base:
        text_words = set(item["text"].lower().split())
        common_words = question_words.intersection(text_words)
        score = len(common_words)
        
        # Give a bonus to chunks with important keywords
        if any(kw in item["text"].lower() for kw in ["price", "financing", "model", " tripping", "process"]):
            score += 1

        scored_chunks.append({"score": score, "text": item["text"]})

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    best_chunk = scored_chunks[0]
    best_score_normalized = best_chunk["score"] / len(question_words) if len(question_words) > 0 else 0
    
    print(f"Top context match has a normalized score of: {best_score_normalized:.2f}")

    if best_score_normalized >= SIMILARITY_THRESHOLD and best_chunk["score"] > 0:
        return best_chunk["text"]
    return None

def query_rag(question: str) -> str:
    """
    The main function that handles user queries with robust logic and error handling.
    """
    print(f"Handling question: '{question}'")
    
    # 1. Handle Greetings
    if any(greet in question.lower() for greet in GREETING_WORDS):
        print("✅ Detected a greeting.")
        return "Hello po! Welcome to Fiesta Communities. How can I assist you today?"

    # 2. Attempt to find context
    context = find_best_context(question)
    
    # 3. Build the prompt based on whether context was found
    if context:
        print(f"✅ Found relevant context: {context[:100]}...")
        system_prompt = (
            "You are FiestaBot, a helpful and polite real estate assistant for Fiesta Communities. "
            "Use ONLY the provided context to answer the user's question. Your tone must be friendly and professional. "
            "Address the user with 'ma'am/sir' and use 'po' or 'opo' where appropriate."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        print("⚠️ No relevant context found. Using fallback.")
        system_prompt = (
            "You are FiestaBot, a helpful and polite real estate assistant for Fiesta Communities. "
            "The user asked a question you don't have specific information for in your knowledge base. "
            "Politely state that you don't have the details for that specific query and offer to connect them with a human agent for assistance. "
            "Do not make up an answer."
        )
        user_prompt = question

    # 4. Call the AI with robust error handling
    try:
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

        print("🚀 Sending request to Groq...")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status() # Raise an error for bad status codes
        
        answer = response.json()["choices"][0]["message"]["content"]
        print("✅ Received answer from Groq.")
        return answer.strip()

    except requests.exceptions.RequestException as e:
        print(f"🚨 Network or API Error: {e}")
        return "I'm sorry, I'm having trouble connecting to my knowledge base at the moment. Please try again shortly."
    except Exception as e:
        print(f"🚨 An unexpected error occurred: {e}")
        return "An unexpected error occurred. Our team has been notified."