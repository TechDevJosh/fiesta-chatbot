🌟 Project Title:

Fiesta Communities Smart Messenger Chatbot (Scalable RAG Version)

🧠 Objective:

Build a lightweight but expandable Facebook-integrated chatbot that uses Retrieval-Augmented Generation (RAG) to:

Auto-answer client questions using a markdown-based knowledge base

Use Groq + HuggingFace for cost-free but high-performance inference

Store responses grounded in .md chunks

Run fully on open infra (Render, GitHub, FB Graph API)

Match Fiesta tone: warm, Taglish, polite, informative

Easily upgradable to add memory, leads, logs, scoring, and scheduling

⚙️ Tech Stack (Minimal to Scalable)

Layer

Tool / Service

Notes

LLM

Groq API (Mixtral / LLaMA3)

Long context, high speed, 1M tokens

Embeddings

HuggingFace MiniLM API

Light, free, decent quality

Vector Store

vector_index.json (local)

Starts as a file, can be swapped to DB

Retrieval

Python cosine/top-K

JSON-based, fast, no DB needed

Backend

FastAPI

Lightweight, async-ready Python backend

Messaging

Facebook Graph API

Send/receive messages

Deployment

Render (or Railway)

Free Python web app deployment

Dev Hosting

GitHub

Store full bot with version control

📁 Folder Layout

fiesta-chatbot/
├── kb/ # Markdown knowledge files (.md)
├── embedder.py # Script: loads .md, generates `vector_index.json`
├── vector_index.json # Final RAG search base
├── query.py # Core RAG function: given question, return answer
├── messenger.py # FB webhook: extract, respond, format
├── memory.py # (future) session memory engine
├── leads.py # (future) structured lead collector
├── main.py # FastAPI app with `/webhook` route
├── .env # API keys and tokens
├── requirements.txt # Python dependencies
└── roadmap.md # 50-step MVP to upgradeable vision

🔐 Required .env

GROQ_API_KEY=...
HUGGINGFACE_API_KEY=...
FB_PAGE_ACCESS_TOKEN=...
FB_VERIFY_TOKEN=fiestaVerify2025

✏️ Prompt Template (Version 1.0)

You are a helpful Fiesta Communities sales assistant. Use the provided context.
Speak in Taglish. Be polite and clear.

Context:
{{ top_chunks }}

User Question:
{{ user_input }}

Answer:

🌊 Message Flow

[Messenger User Message]
⬇
[FB Webhook to /webhook (FastAPI)]
⬇
[messenger.py parses message]
⬇
[query.py loads context, sends to Groq]
⬇
[Formatted reply sent back to FB Graph API]
⬇
[User receives grounded, warm response]

✅ MVP Completion Criteria (Step 20)

FastAPI webhook hosted on Render

Groq LLM responding from vector_index.json

HuggingFace MiniLM used for embedding

All .md files converted to vectors

One-click response to any question via Messenger

Responses grounded in context, Taglish, polite tone

⚡ Upgrade Paths (Steps 21–50)

Add memory, feedback, lead scoring

Connect to Airtable or R2 for lead logging

Add rich FB features: buttons, media, scheduled replies

Track user sessions, preferences, and follow-ups

Improve prompt, fallback flows, hallucination filters

Publish open-source version with public test page

With this blueprint and roadmap, you now have a clear, clean, and AI-ready foundation that grows with your mission. From solo MVP to full lead automation.

Let me know when ready to scaffold code!
