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
# We will only use context if its similarity score is above this value
SIMILARITY_THRESHOLD = 0.5 

# --- Load Knowledge Base ---
print("Loading knowledge base text...")
with open("vector_index.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)
print(f"Knowledge base with {len(knowledge_base)} chunks loaded.")


def find_best_context(question: str, top_k: int = 1) -> str | None:
    """
    Finds the most relevant context chunk if it's above a certain similarity threshold.
    This uses a simple keyword scoring method.
    """
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
    
    # Heuristic to decide if the match is good enough.
    # If the question has 2 words, a score of 2 is a perfect match. A score of 1 is 50%.
    best_score_normalized = best_chunk["score"] / len(question_words)
    
    print(f"Top context match has a normalized score of: {best_score_normalized:.2f}")

    if best_score_normalized >= SIMILARITY_THRESHOLD:
        return best_chunk["text"]
    else:
        # If the best match isn't good enough, don't use any context.
        return None


def query_rag(question: str) -> str:
    """
    Handles user queries by first checking for relevant context,
    then constructs a specific prompt for the Groq AI.
    """
    print(f"Handling question: '{question}'")
    context = find_best_context(question)
    
    # The system prompt changes based on whether we found good context or not
    if context:
        print(f"Found relevant context: {context[:100]}...")
        system_prompt = (
            "You are FiestaBot, a helpful and polite assistant for Fiesta Communities. "
            "Your tone should be friendly and use 'po' and 'opo' appropriately. "
            "Answer the user's question based ONLY on the detailed context provided."
        )
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        print("No relevant context found. Handling as a general question.")
        system_prompt = (
            "You are FiestaBot, a friendly and polite assistant for Fiesta Communities. "
            "Your tone should be friendly and use 'po' and 'opo' appropriately. "
            "Answer the user's question conversationally. If asked about topics outside of real estate, politely decline. "
            "If you are greeted, greet the user back."
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