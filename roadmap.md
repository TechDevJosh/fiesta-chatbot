# 🗺️ Fiesta Messenger RAG Chatbot Roadmap (Python Version)

**Project Type:** Python + FastAPI + Groq + FB Messenger
**Version:** MVP to Fully Featured RAG Chatbot
**MVP Milestone:** ✅ Complete by Step 20
**Upgrades:** 🚀 Start from Step 21 to Step 50

---

## 🚧 MVP (Steps 1–20)

1. **Set up virtual environment and install** `fastapi`, `requests`, `uvicorn`, `python-dotenv`
2. **Install** `groq`, `openai`, `transformers`, `torch`, `huggingface_hub`
3. Create `kb/` folder and place all uploaded `.md` files
4. Write `embedder.py` to:

   - Read all `.md` files
   - Chunk into paragraphs
   - Generate embeddings via HuggingFace
   - Save to `vector_index.json`

5. Create `query.py` to:

   - Accept user question
   - Load `vector_index.json`
   - Compute query embedding
   - Return top-K similar chunks
   - Send prompt to Groq API and return answer

6. Write `main.py` using FastAPI with `/webhook` route (GET + POST)
7. Create `messenger.py` for:

   - Verifying webhook
   - Parsing incoming messages
   - Sending FB replies via Graph API

8. Create `.env` and load keys via `dotenv`
9. Run `embedder.py` locally to generate `vector_index.json`
10. Test `query.py` independently with sample inputs
11. Run `main.py` locally using `uvicorn main:app --reload`
12. Deploy FastAPI backend on **Render.com**
13. Create a new Facebook App via developers.facebook.com
14. Add webhook URL to Messenger tab with verify token
15. Subscribe webhook to `messages`, `messaging_postbacks`
16. Connect FB Page and approve permissions
17. Test webhook with GET request verification
18. Send a test message from your Page – ensure `/webhook` receives and responds
19. Implement logging of message flow and Groq response
20. Finalize prompt tone (Taglish, helpful, polite) — **MVP COMPLETE**

---

## 🔧 Upgrade Phase (Steps 21–50)

21. Add fallback if confidence is low (“Sorry, I don’t know yet.”)
22. Allow retry logic if no match is found
23. Implement logging to JSON (`log.json` or R2 bucket)
24. Add `/feedback` route for end-user sentiment
25. Store Messenger sender ID as `session_id`
26. Begin storing basic memory per user (in JSON or Redis later)
27. Add intent: “Who am I?” to recall last known session info
28. Allow `clear memory` command to reset session
29. Group KB chunks by tags (e.g., `#pricing`, `#promo`)
30. Filter top-k search by tag relevance
31. Add support for `/retrain` route to rerun `embedder.py` on updated docs
32. Refactor chunking logic to improve accuracy
33. Add basic NER (name, price, location) using regex or spaCy
34. Format Groq replies with Markdown (for price tables)
35. Enable support for receiving and logging media (screenshots from Messenger)
36. Collect structured lead data (name, contact, interest)
37. Score leads as cold/warm/hot based on query context
38. Send data to Airtable or Google Sheets
39. Implement postbacks: e.g., buttons for “Schedule Tripping”
40. Add multilingual toggle (Taglish ↔ English)
41. Add tripping scheduler logic with date recognition
42. Integrate reminder logic (e.g., follow-up tomorrow)
43. Add system fallback if Groq fails or times out
44. Stream partial responses to FB (typing simulation)
45. Export user chat history on demand
46. Add admin portal to view logs, leads, metrics
47. Filter hallucinations using keyword validation
48. Enable Messenger features: quick replies, typing indicators, etc.
49. Improve prompt with tone adjustments and closing strategy
50. Open-source clean version with README and setup instructions
