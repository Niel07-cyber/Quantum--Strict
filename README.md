# 🧠 Quantum Knowledge Network

> A full-stack, real-time Q&A platform combining quantum circuits, AI chat, IPFS pinning, and live updates.

---

## 🚀 Features

- **Quantum Simulator**  
  Run a simple two-qubit circuit under `POST /solve` with `"method": "quantum"`.
- **AI Assistant**  
  Generate GPT-3.5-Turbo responses under `POST /solve` with `"method": "ai"`.
- **Persistent Storage**  
  Solutions saved in a local SQLite database; fetch via `GET /history`.
- **Semantic Search**  
  Query past questions using vector embeddings (`GET /search?q=<query>`).
- **IPFS Pinning**  
  Pin each Q&A record to IPFS (via Pinata JWT).
- **Live Updates**  
  Broadcast new solutions over WebSockets (Socket.IO) to React clients.
- **Authentication** *(optional)*  
  Protect your API with Auth0 JWT.

---

## 🛠 Tech Stack

| Layer            | Technology                              |
| ---------------- | ---------------------------------------- |
| **Language**     | Python 3.11, TypeScript, JavaScript      |
| **Backend**      | FastAPI, Uvicorn (ASGI)                  |
| **WebSockets**   | python-socketio, socket.io-client        |
| **Database**     | SQLite + SQLAlchemy                      |
| **Quantum**      | Custom toy circuit (Qiskit-style)        |
| **AI**           | OpenAI GPT-3.5 (chat API)                |
| **Search**       | Sentence-Transformers (“all-MiniLM-L6”)  |
| **IPFS**         | Pinata JWT HTTP API                      |
| **Frontend**     | React + Vite, Tailwind CSS               |
| **Auth**         | Auth0 (OIDC/JWT)                         |
| **Packaging**    | Poetry, npm/yarn, dotenv                 |

---

## 📥 Getting Started

### 1️⃣ Back-End Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/quantum_strict.git
cd quantum_strict

# Install Python deps
py -3.11 -m poetry install

# Create a `.env` in project root:
# OPENAI_API_KEY=your_openai_key
# PINATA_JWT=your_pinata_jwt
# AUTH0_DOMAIN=your_auth0_domain      (optional)
# AUTH0_AUDIENCE=your_auth0_audience  (optional)

# Initialize SQLite schema
$env:PYTHONPATH="src"                  # Windows PowerShell
poetry run python - <<'EOF'
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
EOF

# Start ASGI server (HTTP + Socket.IO)
poetry run uvicorn app.main:asgi_app --reload


Swagger Docs: http://127.0.0.1:8000/docs

Socket.IO: ws://127.0.0.1:8000/socket.io/





## 🔥 API Endpoints

| Method | Endpoint     | Description                      |
|--------|--------------|----------------------------------|
| GET    | /            | Health check                     |
| POST   | /solve       | Solve problem using AI or quantum |
| GET    | /history     | Retrieve problem history         |

Example POST /solve:

```json
{
  "question": "What is quantum entanglement?",
  "method": "ai"
}
```

---

## 🧠 2️⃣ Front-End Setup
```bash
cd qkn-frontend
npm install           # or yarn install
npm run dev           # Vite dev server
```
🔎 API Reference 
```bash
POST /solve  
Solve a question using quantum or AI methods.  

## Request Body
```bash
{  
  "question": "What is superposition?",  
  "method":   "quantum"   /* or "ai" */  
}
```


## Response (200)
```bash
{
  "method": "quantum",
  "result": { "0": 520, "1": 504 },
  "cid":    "QmABC123..."
}
```

### or for AI
```bash
{
  "method": "ai",
  "answer": "Superposition is the ability …",
  "cid":    "QmXYZ789..."
}
```

## GET /history
## Fetch all solved problems (newest first).
Response (200)
```bash

[
  {
    "id":        1,
    "question":  "Define entanglement",
    "method":    "ai",
    "answer":    "Quantum entanglement …",
    "timestamp": "2025-06-01T12:34:56.789012",
    "cid":       "QmABC123..."
  },
  …
]
```


## GET /search?q=<query>
## Semantic search past questions.

Response (200)

```bash
[
  {
    "question":   "What is entanglement?",
    "method":     "quantum",
    "answer":     "{ \"0\": 501, \"1\": 523 }",
    "similarity": 0.91,
    "timestamp":  "2025-06-01T12:35:10.123456",
    "cid":        "QmDEF456..."
  },
  …
]

```

## 🔄 Real-Time Live Updates
Clients subscribe via Socket.IO:
```bash 
import { io } from 'socket.io-client';
const socket = io("http://localhost:8000");
socket.on("new_problem", (data) => {
  console.log("New Q&A:", data);
});



On each /solve, server emits on channel "new_problem":
{
  id, question, method, response, timestamp, cid
}

```

---

## 🤝 Contributing

Want to help build the future of intelligent problem-solving? Open a PR, suggest features, or file issues!

---

## 📜 License

MIT License © 2025 Othniel Aryee
