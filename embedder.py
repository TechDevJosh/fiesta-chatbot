import os
import json
import glob
import re
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import requests

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size())
    return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

def embed_text(text):
    encoded = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded)
    return mean_pooling(model_output, encoded['attention_mask']).squeeze().numpy()

def chunk_markdown(text, max_chunk_length=300):
    paragraphs = re.split(r'\n{2,}', text)
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) <= max_chunk_length:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def main():
    index = []
    for filepath in glob.glob("kb/*.md"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            chunks = chunk_markdown(text)
            for chunk in chunks:
                embedding = embed_text(chunk).tolist()
                index.append({"text": chunk, "embedding": embedding, "source": os.path.basename(filepath)})

    with open("vector_index.json", "w", encoding="utf-8") as out:
        json.dump(index, out, indent=2)

    print(f"✅ {len(index)} chunks embedded and saved to vector_index.json")

if __name__ == "__main__":
    main()
