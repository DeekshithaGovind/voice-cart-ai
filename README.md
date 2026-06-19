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
- 3-tier order resolution for higher accuracy:
  - Fast keyword / trie / fuzzy matching.
  - Synonym mapping + entity recognition.
  - AI fallback for complex or unclear orders.
- Supports multiple concurrent order requests efficiently.
- Stock, quantity, and customer validation.
- Order confirmation before final storage.
- Real-time dashboard updates.
- Call logs, customers, products, analytics, and monitoring.
- Redis Streams for parallel event processing.
- Continuous learning loop for improving product matching.
- CPU-efficient and scalable architecture.
- Modern dark-themed SaaS dashboard UI.

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

## System Workflow

VoiceCart AI follows a simple order processing workflow:

1. Customer places an order through a call or voice input.
2. The system identifies the customer and loads previous order history.
3. Voice input is converted into text.
4. The order is processed using a 3-tier understanding engine:
   - Tier 1: Fast product matching
   - Tier 2: Synonym and entity recognition
   - Tier 3: AI fallback for complex requests
5. The order is validated for product availability and quantity.
6. A confirmation is generated for the customer.
7. Order details are stored in PostgreSQL.
8. Redis broadcasts updates to connected services.
9. The dashboard updates in real time.
10. A learning process continuously improves product matching over time.

### Workflow Diagram

```text
Customer Call
      ↓
Customer Lookup
      ↓
Speech-to-Text
      ↓
Order Understanding Engine
      ↓
Order Validation
      ↓
Confirmation
      ↓
PostgreSQL Database
      ↓
Redis Events
      ↓
Live Dashboard
```
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
## Concurrent Call Handling

VoiceCart AI is designed using an asynchronous FastAPI architecture with Redis-backed event handling and WebSocket updates.

In its current prototype form, the system can comfortably support multiple simultaneous order sessions while maintaining dashboard responsiveness.

### Estimated Capacity

| Environment | Concurrent Sessions |
|------------|-------------------|
| Developer Laptop | 10–20 |
| Standard Cloud VM (2–4 vCPU) | 30–50 |
| Optimized Production Deployment | 100+ (with horizontal scaling) |

### Scalability Strategy

- Async FastAPI request handling
- PostgreSQL connection pooling
- Redis caching and Pub/Sub
- WebSocket-based live updates
- Stateless backend services

### Future Improvements

- Queue-based order processing
- Load balancing
- Multi-instance deployment
- Dedicated telephony workers
- Kubernetes scaling support


---

## Conclusion

VoiceCart AI demonstrates how a voice-based order automation platform can be built using a lightweight, CPU-friendly architecture. It is designed to reduce manual order-taking effort and provide a real-time dashboard for operational visibility.
