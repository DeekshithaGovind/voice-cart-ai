# VoiceCart AI
## AI-Powered Voice Based 24/7 Booking System

### Overview
VoiceCart AI is a CPU-powered voice ordering prototype designed to automate phone-based order booking for supermarkets and distributors. Customers can speak their order in English, Hindi, or Tamil, and the system processes the request using a 3-tier understanding pipeline, validates it, confirms it back to the caller, and updates a live dashboard in real time.

> This project is currently in development as a prototype. Accuracy may vary depending on audio quality, accent, and language mixing.

---

## What It Does

Customers call a phone number and speak their order along with their phone number. The system transcribes the voice input, extracts product names and quantities, validates the order securely, and stores it in the backend. The business owner can monitor orders instantly through a live dashboard.

**Call Flow:**  
Customer Calls → Asterisk PBX → Whisper STT → 3-Tier NLU Pipeline → Secure Database → Live Dashboard

---

## Key Features

- Voice-based order booking system.
- Support for English, Hindi, and Tamil.
- Repeat caller shortcut with last-order preload.
- 3-tier order resolution:
  - Fast keyword / trie / fuzzy matching.
  - Synonym mapping + NER.
  - Local LLM fallback for rare cases.
- Stock, quantity, and credit validation.
- Voice confirmation before final order storage.
- Real-time dashboard updates.
- Call logs, customers, products, analytics, and monitoring.
- Redis Streams fan-out for parallel processing.
- Nightly learning loop for improving matching.
- CPU-only architecture.
- Dark, premium SaaS-style UI.

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Telephony | Asterisk PBX + ARI | Handles inbound calls and call routing. |
| Speech-to-Text | faster-whisper | CPU-friendly transcription for voice input. |
| NLU Pipeline | Trie + RapidFuzz + spaCy + local LLM fallback | Supports fast matching, synonym handling, and complex fallback cases. |
| Backend | FastAPI + Python | Powers APIs, call flow logic, and WebSocket handling. |
| Database | PostgreSQL | Stores orders, call logs, customers, and products reliably. |
| Cache / Event Bus | Redis | Used for caller profile caching and event streaming. |
| Frontend | React / Next.js | Builds the live dashboard and admin UI. |
| Styling | Tailwind CSS | Provides the dark, modern dashboard design. |
| Charts | Recharts | Displays analytics and live metrics. |
| Deployment | Docker + Docker Compose | Makes the project portable and easy to run locally or on a server. |
| Web Server | Nginx | Handles routing and production serving. |
| Monitoring | Prometheus / Grafana | Tracks performance, errors, and system health. |
| TTS | Kokoro TTS | Generates voice confirmation responses. |

---

## Architecture

The system is designed as a layered workflow:

1. Telephony Layer receives the call through Asterisk.
2. Profile Cache loads caller history and last orders from Redis.
3. Speech-to-Text converts audio into text using faster-whisper.
4. NLU Cascade resolves the order using:
   - Tier 1: fast keyword matching.
   - Tier 2: synonym + NER matching.
   - Tier 3: local LLM fallback.
5. Validation Engine checks stock, quantity, and credit.
6. TTS Confirmation reads the summary back to the caller.
7. Storage Layer saves orders and call logs in PostgreSQL.
8. Redis Streams fan out order events in parallel.
9. Dashboard shows live updates instantly.
10. Nightly Job improves aliases and matching over time.

---

## Project Structure

```text
voicecart/
├── asterisk/
├── backend/
│   ├── main.py
│   ├── call_handler.py
│   ├── config.py
│   ├── stt/
│   ├── nlu/
│   ├── validation/
│   ├── tts/
│   ├── storage/
│   ├── events/
│   ├── notifications/
│   └── learning/
├── dashboard/
│   ├── src/
│   ├── components/
│   └── hooks/
├── models/
├── requirements.txt
├── docker-compose.yml
├── nginx.conf
└── .env
```

---

## How It Works

- Customer calls the business number.
- Caller profile is loaded immediately.
- Voice is transcribed in streaming mode.
- The transcript is resolved through the 3-tier engine.
- The system validates the final cart.
- A spoken summary is returned to the caller.
- After confirmation, the order is saved and broadcast live.
- The dashboard updates without polling.

---

## UI Preview

The dashboard is built as a modern command center with:
- Sidebar navigation.
- Top status bar.
- Live orders panel.
- Analytics cards.
- Call logs table.
- Customer and product views.
- Health and monitoring widgets.

The interface uses a dark premium visual style with clean spacing, rounded cards, subtle gradients, and a business-grade presentation.

---

## Setup

### Backend
```bash
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend
```bash
cd dashboard
npm install
npm run dev
```

### Open the app
- Frontend: `http://localhost:3000`
- API: `http://localhost:8001`
- API Docs: `http://localhost:8001/docs`

---

## Current Status

This is a **simple prototype in active development**. The core flow is implemented, but real-world accuracy may vary depending on:
- audio clarity,
- accent variation,
- code-mixed speech,
- order complexity,
- and environment quality.

---

## Future Scope

- Full production telephony support.
- Better multilingual performance.
- More advanced NLU fallback handling.
- WhatsApp / SMS notifications.
- ERP integration.
- Enhanced analytics.
- Observability and load testing.
- Deployment hardening.

---

## Conclusion

VoiceCart AI demonstrates how a voice-based order automation platform can be built using a lightweight, CPU-friendly architecture. It is designed to reduce manual order-taking effort and provide a real-time dashboard for operational visibility.
