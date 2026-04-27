# 🏥 MediChat API

A FastAPI-powered medical assessment backend that uses **Google Gemini** and **LangChain** to analyze patient symptoms, suggest diagnoses and medications, and find nearby hospitals. Supports multi-turn chat history with PostgreSQL and observability via Langfuse.

---

## ✨ Features

- **Symptom Assessment** — Accepts free-text symptoms and returns a structured diagnosis, medications, and precautions
- **LangGraph Flow** — Multi-node agentic pipeline (diagnosis → medications → precautions → summary) powered by LangGraph
- **Chat History** — Stores every session in PostgreSQL; supports retrieval, listing, and deletion
- **Hospital Finder** — Geocodes a user address (Nominatim → Gemini fallback) and queries OpenStreetMap for nearby hospitals
- **Langfuse Observability** — All LLM calls are traced end-to-end

---

## 🗂️ Project Structure

```
├── app/
│   ├── api/routes/
│   │   ├── assess.py              # POST /assess
│   │   ├── assess_langgraph.py    # POST /assess/flow
│   │   ├── history.py             # GET/DELETE /history
│   │   └── hospital_finder.py     # POST /hospital/find
│   ├── core/
│   │   ├── config.py              # Settings (env vars)
│   │   ├── constants.py           # System prompt
│   │   └── langfuse_client.py     # Langfuse setup
│   ├── db/
│   │   ├── database.py            # SQLAlchemy engine
│   │   ├── models.py              # ChatMessage ORM model
│   │   └── crud_history.py        # DB helpers
│   ├── models/                    # Pydantic schemas
│   ├── services/
│   │   ├── langchain_client.py    # LangChain LCEL pipeline
│   │   ├── langgraph_flow.py      # LangGraph graph definition
│   │   ├── langgraph_service.py   # LangGraph runner
│   │   ├── assess_service.py      # Assessment orchestration
│   │   ├── gemini_client.py       # Direct Gemini client
│   │   └── hospital_service.py    # Geocoding + Overpass API
│   └── main.py                    # FastAPI app entry point
├── run.py
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/medichat-api.git
cd medichat-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key

DATABASE_URL=postgresql://medichat:medichat123@localhost:5432/medichat

LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 5. Set up PostgreSQL

```bash
psql -U postgres -c "CREATE USER medichat WITH PASSWORD 'medichat123';"
psql -U postgres -c "CREATE DATABASE medichat OWNER medichat;"
```

Tables are created automatically on startup via SQLAlchemy.

### 6. Run the server

```bash
python run.py
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## 🔌 API Reference

### `POST /assess`
Analyze patient symptoms using LangChain + Gemini.

**Request:**
```json
{
  "text": "I have a sore throat, mild fever, and body aches since yesterday.",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "diagnosis": "Viral pharyngitis (common cold)",
  "medications": [
    { "name": "Paracetamol", "dosage": "500mg", "frequency": "Every 6 hours", "notes": "Take with food" }
  ],
  "precautions": ["Rest and stay hydrated", "Avoid contact with others"],
  "session_id": "session_1234567890",
  "message_id": 42
}
```

---

### `POST /assess/flow`
Runs the same assessment through a LangGraph multi-node pipeline.

**Request:**
```json
{ "text": "I have a headache and nausea." }
```

**Response:**
```json
{
  "diagnosis": "...",
  "medications": [...],
  "precautions": [...],
  "summary": "..."
}
```

---

### `GET /history/{session_id}`
Retrieve all messages for a session.

### `DELETE /history/{session_id}`
Delete all messages for a session.

### `GET /history/sessions/list`
List all sessions (most recent first, default limit: 50).

---

### `POST /hospital/find`
Find nearby hospitals from a given address.

**Request:**
```json
{
  "address": "Jubilee Hills, Hyderabad, Telangana",
  "radius_km": 5.0
}
```

**Response:**
```json
{
  "origin_address": "Jubilee Hills, Hyderabad, Telangana, India",
  "origin_coordinates": { "latitude": 17.43, "longitude": 78.41 },
  "total_hospitals_found": 8,
  "hospitals": [
    {
      "name": "Care Hospitals",
      "address": "Road No. 1, Jubilee Hills",
      "distance_km": 0.9,
      "latitude": 17.432,
      "longitude": 78.409,
      "google_maps_link": "https://www.google.com/maps/dir/...",
      "phone": "+91-40-...",
      "emergency": "yes"
    }
  ]
}
```

---

### `GET /health`
Returns `{ "status": "ok" }`.

---

## 🧠 Architecture

```
Client
  │
  ▼
FastAPI
  ├── /assess ──────────────── LangChain LCEL ──── Gemini ──── PostgreSQL
  ├── /assess/flow ─────────── LangGraph ─────────── Gemini
  ├── /history ─────────────── PostgreSQL (CRUD)
  └── /hospital/find ───────── Nominatim / Gemini ── Overpass API
                                             │
                                         Langfuse (tracing)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| LLM | Google Gemini 2.5 Flash |
| LLM Orchestration | LangChain, LangGraph |
| Database | PostgreSQL + SQLAlchemy |
| Observability | Langfuse |
| Geocoding | Nominatim (OpenStreetMap) |
| Hospital Data | OpenStreetMap Overpass API |

---

## 📋 Notes

- This API is for **informational purposes only** and is not a substitute for professional medical advice.
- Gemini is used as a fallback geocoder if Nominatim cannot resolve an address.
- All LLM responses are structured using Pydantic parsers to ensure consistent output.
