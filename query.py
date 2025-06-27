import json
import numpy as np
import requests
import os
from sentence_transformers import SentenceTransformer # This is ok for the function, as it's a small part.
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# This part is now much lighter
print("Loading vector index...")
with open("vector_index.json", "r", encoding="utf-8") as f:
    vector_data = json.load(f)
print("Vector index loaded.")

# We will load the model once inside the function to manage memory
embedding_model = None

def get_embedding_model():
    """Loads the model only when it's first needed."""
    global embedding_model
    if embedding_model is None:
        print("Loading embedding model for the first time...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded.")
    return embedding_model

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)

def query_rag(question: str, top_k: int = 3) -> str:
    """
    Queries the knowledge base using a lightweight approach.
    """
    model = get_embedding_model()
    
    print(f"Embedding user query: '{question}'")
    question_vector = model.encode(question).tolist()

    # Find top-k most similar chunks from the pre-computed index
    scored_chunks = []
    for item in vector_data:
        similarity = cosine_similarity(question_vector, item["vector"])
        scored_chunks.append({"score": similarity, "text": item["text"]})

    # Sort by score and get the best context
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    top_chunks = [chunk["text"] for chunk in scored_chunks[:top_k]]
    context = "\n\n".join(top_chunks)
    print(f"Found context with score: {scored_chunks[0]['score']:.2f}")

    # Build the prompt for Groq
    system_prompt = (
        "You are FiestaBot, a helpful and polite assistant for Fiesta Communities. "
        "Answer the user's question based *only* on the context provided. "
        "If the answer is not in the context, say 'I'm sorry, I don't have that information, but I can ask our team for you.'"
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