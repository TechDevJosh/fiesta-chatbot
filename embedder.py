import os
import json
import glob
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# --- Configuration ---
# Load environment variables from .env file, if any
load_dotenv()

# Specify the model we'll use for embeddings.
# This is a high-performance model that is small and fast.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Define the directory containing your knowledge base markdown files
KB_DIR = "kb/"

# --- Main Embedding Logic ---

def chunk_markdown(text: str, max_chunk_length: int = 500) -> list[str]:
    """
    Splits text from a markdown file into manageable chunks for embedding.
    This version splits by paragraphs to maintain context.
    """
    # Normalize excessive newlines to a standard double newline for paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    paragraphs = text.split('\n\n')
    chunks = []

    for para in paragraphs:
        # Clean up whitespace and ensure the paragraph has content
        clean_para = para.strip()
        if clean_para:
            # If a paragraph is too long, we could split it further, but for now, we keep it whole
            # to preserve context, as your documents are well-structured.
            chunks.append(clean_para)

    return chunks

def main():
    """
    Main function to run the embedding process.
    """
    print(f"Loading embedding model: {MODEL_NAME}...")
    # Initialize the SentenceTransformer model.
    # This will download the model (approx. 230MB) on the first run.
    model = SentenceTransformer(MODEL_NAME)

    index_data = []

    # Find all markdown files in the specified knowledge base directory
    markdown_files = glob.glob(os.path.join(KB_DIR, "*.md"))

    if not markdown_files:
        print(f"Error: No markdown files found in the '{KB_DIR}' directory.")
        print("Please create the 'kb' folder and add your .md files to it.")
        return

    print(f"Found {len(markdown_files)} files to process in '{KB_DIR}' directory.")

    for filepath in markdown_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            chunks = chunk_markdown(content)

            if not chunks:
                continue

            print(f"  - Processing {os.path.basename(filepath)} ({len(chunks)} chunks)...")

            # Generate embeddings for all chunks in the file at once for efficiency
            embeddings = model.encode(chunks).tolist()

            for i, chunk_text in enumerate(chunks):
                # The key is "vector" to match what query.py will expect
                index_data.append({
                    "text": chunk_text,
                    "vector": embeddings[i],
                    "source": os.path.basename(filepath)
                })

    # Save the final index with real vectors to a JSON file
    output_path = "vector_index.json"
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(index_data, out_file, indent=2)

    print(f"\n✅ Success! {len(index_data)} chunks have been embedded with real vectors.")
    print(f"Output saved to '{output_path}'.")

if __name__ == "__main__":
    main()