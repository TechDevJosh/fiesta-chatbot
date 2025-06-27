import os
import json
import numpy as np
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import requests

load_dotenv()

# Load model once
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size())
    return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

def embed(text):
    # Dummy vector to avoid torch/transformers dependency in production
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
    top_k = sorted(scored, key=lambda x: x["score"], reverse=True)[:k]
    return top_k

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
        "model": "llama3-70b-8192",  # ✅ updated model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, json=payload)

    # 🔍 Debug Groq response
    print("🔍 Status:", response.status_code)
    print("🔍 Body:", response.text)

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Groq API error: {str(e)}"


def query_bot(question):
    top_chunks = get_top_k_chunks(question)
    prompt = format_prompt(top_chunks, question)
    answer = ask_groq(prompt)
    return answer

if __name__ == "__main__":
    # ✅ Test run
    q = input("Ask a question: ")
    print("\n🤖 Answer:\n")
    print(query_bot(q))
