import os
import json
import numpy as np
from dotenv import load_dotenv
import requests

load_dotenv()

def embed(text):
    # Dummy embedding for deploy — replace with real model for local
    return [0.0] * 384

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_top_k_chunks(question, k=5):
    with open("vector_index.json", "r", encoding="utf-8") as f:
        index = json.load(f)

    question_vec = embed(question)
    scored = [
        {
            "text": chunk["text"],
            "source": chunk["source"],
            "score": cosine_similarity(question_vec, chunk["embedding"]),
        }
        for chunk in index
    ]
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:k]

def format_prompt(chunks, question):
    context = "\n\n---\n\n".join(c["text"] for c in chunks)
    return f"""
You are a helpful Fiesta Communities sales assistant. Use the provided context.
Speak in Taglish. Be polite and clear.

Context:
{context}

User Question:
{question}

Answer:
""".strip()

def ask_groq(prompt):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=payload)
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Groq API error: {str(e)}"

def query_bot(question):
    top_chunks = get_top_k_chunks(question)
    prompt = format_prompt(top_chunks, question)
    return ask_groq(prompt)

if __name__ == "__main__":
    q = input("Ask a question: ")
    print("\n🤖 Answer:\n")
    print(query_bot(q))
