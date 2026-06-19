# VoiceCart AI
## AI-Powered Voice-Based 24/7 Booking System

### Executive Summary
VoiceCart AI is a simple prototype of a voice-based order booking system designed for supermarkets and distributors. It automates incoming phone orders, understands spoken requests in English, Hindi, and Tamil, validates products and quantities, and displays confirmed orders on a live dashboard.

This project is currently in the development phase, so accuracy and final results may vary depending on audio quality, language mixing, and order complexity.

---

## Project Overview

The goal of this project is to reduce manual phone-order handling and improve order-taking efficiency through an automated voice workflow. The system is designed to receive a call, transcribe speech, identify products, confirm the order with the caller, and store the final order in the backend.

It also provides a business dashboard for live monitoring, call tracking, analytics, and customer/product management.

---

## Key Features

- Voice-based order booking.
- Support for English, Hindi, and Tamil.
- Repeat caller shortcut with last-order preload.
- 3-tier order understanding pipeline.
- Stock, quantity, and credit validation.
- Voice confirmation before saving an order.
- Live dashboard with real-time updates.
- Call logs, customers, products, analytics, and monitoring.
- Redis Streams-based parallel processing.
- Nightly learning loop for alias improvement.
- CPU-only architecture.
- Premium dark-themed UI.

---

## Technology Stack

### Frontend
- Next.js / React
- Tailwind CSS
- Recharts
- WebSockets

### Backend
- FastAPI
- Python
- PostgreSQL
- Redis

### AI / Voice
- faster-whisper
- webrtcvad
- RapidFuzz
- pyahocorasick
- spaCy
- llama-cpp-python
- Kokoro TTS

### Deployment
- Docker
- Docker Compose
- Nginx

---

## System Architecture

The application is built using a modular architecture:

1. **Telephony layer** receives the inbound call.
2. **Caller profile cache** loads previous customer data from Redis.
3. **Speech-to-text layer** converts voice input into text.
4. **NLU cascade** resolves the order through three tiers:
   - Tier 1: fast keyword/trie matching.
   - Tier 2: synonym mapping + NER.
   - Tier 3: local LLM fallback.
5. **Validation engine** checks product availability, quantity, and credit.
6. **TTS confirmation** reads the summary back to the caller.
7. **Storage layer** saves the confirmed order and logs.
8. **Redis Streams** fan out updates in parallel.
9. **Dashboard** updates live through WebSockets.
10. **Learning job** improves aliases and matching over time.

---

## Project Structure

```text
voicecart/
├── backend/
├── dashboard/
├── asterisk/
├── models/
├── requirements.txt
├── docker-compose.yml
└── .env
```

---

## How It Works

- A customer places a call.
- The system loads the caller profile.
- Speech is transcribed in real time.
- The order is processed through the 3-tier cascade.
- Validation checks are applied.
- The system reads the summary back to the caller.
- The caller confirms the order.
- The confirmed order is saved.
- The dashboard updates instantly.

---

## Setup Instructions

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

### Access URLs
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8001`
- API Docs: `http://localhost:8001/docs`

---

## Current Status

This project is a working prototype and is still being improved. It demonstrates the core voice-order workflow, live dashboard, multilingual support, and backend integration.

Since the system is still under development, accuracy may differ based on speech clarity, accent variation, and multilingual input.

---

## Future Scope

- Full telephony integration.
- Better multilingual recognition.
- Higher-accuracy NLP handling.
- WhatsApp/SMS notifications.
- ERP integration.
- Enhanced monitoring and reporting.
- Production deployment support.

---

## Conclusion

VoiceCart AI demonstrates how voice commerce can be automated using a lightweight, CPU-friendly architecture. It is a practical prototype for businesses that want to reduce manual order-taking and move toward a real-time, AI-assisted workflow
