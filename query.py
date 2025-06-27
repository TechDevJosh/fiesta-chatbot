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

# --- Load Knowledge Base Text ---
print("Loading knowledge base text...")
with open("vector_index.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)
print(f"Knowledge base with {len(knowledge_base)} chunks loaded.")


def find_best_context(question: str, top_k: int = 3) -> str:
    """
    Finds the most relevant context chunks using simple keyword matching.
    This is a lightweight alternative to vector similarity search.
    """
    # Normalize and split the question into a set of unique words
    question_words = set(re.findall(r'\w+', question.lower()))
    
    if not question_words:
        return "No relevant information found."

    scored_chunks = []
    for item in knowledge_base:
        text_words = set(re.findall(r'\w+', item["text"].lower()))
        # Score based on the number of common words
        common_words = question_words.intersection(text_words)
        score = len(common_words)
        scored_chunks.append({"score": score, "text": item["text"], "source": item.get("source", "")})

    # Sort chunks by score in descending order
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter out chunks with a score of 0 and get the top_k
    top_chunks = [chunk["text"] for chunk in scored_chunks if chunk["score"] > 0][:top_k]
    
    if not top_chunks:
        return "No relevant information found."
        
    return "\n\n".join(top_chunks)


def query_rag(question: str) -> str:
    """
    Performs lightweight RAG by finding context with keywords
    and then querying the Groq AI for a final answer.
    """
    print(f"Searching for context for question: '{question}'")
    context = find_best_context(question)
    
    print(f"Found context: {context[:120]}...")

    # Build the prompt for Groq
    system_prompt = (
        "You are FiestaBot, a helpful and polite assistant for Fiesta Communities. "
        "Your tone should be friendly and use 'po' and 'opo' appropriately in a natural, conversational way. "
        "Answer the user's question based ONLY on the context provided. "
        "If the answer is not in the context, say: 'I'm sorry, I don't have that specific information right now, but I can have one of our property specialists get back to you shortly.'"
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

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
    response = requests.post(GROQ_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        print("Received answer from Groq.")
        return answer.strip()
    else:
        print(f"Error from Groq API: {response.text}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."