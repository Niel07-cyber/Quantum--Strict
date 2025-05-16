# 🧠 Quantum Knowledge Network

A next-generation backend architecture powered by quantum computing, AI, and decentralization. Built with FastAPI, Qiskit, and OpenAI, this project lays the foundation for an intelligent, collaborative knowledge engine.

---

## 📌 What It Does

- ✅ Runs quantum circuits via a FastAPI interface
- ✅ Generates responses using OpenAI GPT (AI Assistant)
- ✅ Stores & retrieves solved problems in a local SQLite DB
- ✅ REST API powered by FastAPI
- ⚙️ Modular backend: ready for semantic search, tokenization, and Web3 integration

---

## ⚙️ Tech Stack

- 🧠 Qiskit & Qiskit Aer — quantum circuit simulation
- 🤖 OpenAI GPT — natural language processing
- ⚡ FastAPI — high-performance API
- 🐍 Python 3.11 — via Poetry
- 🌐 Uvicorn — ASGI server
- 📦 SQLite — lightweight DB
- 🔐 python-dotenv — environment management

---

## 🚀 How to Run Locally

1. Clone the project:
   ```bash
   git clone https://github.com/YOUR_USERNAME/quantum_strict.git
   cd quantum_strict
   ```

2. Install dependencies with Poetry:
   ```bash
   py -3.11 -m poetry install
   ```

3. Create a .env file in the project root:
   ```ini
   OPENAI_API_KEY=your_openai_key_here
   ```

4. Run database migration:
   ```bash
   $env:PYTHONPATH="src"; poetry run python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

5. Start the server:
   ```bash
   $env:PYTHONPATH="src"; poetry run uvicorn app.main:app --reload
   ```

6. Open the docs:
   http://127.0.0.1:8000/docs

---

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

## 🧠 Phase 3 Complete

✅ Quantum backend  
✅ AI + GPT integration  
✅ Persistent DB (SQLite)  
✅ Clean modular FastAPI layout

---

## 🛠 Roadmap

- 🔍 Phase 4: Semantic search using vector embeddings (e.g. Sentence-BERT)
- 🌐 Phase 5: Decentralized storage (IPFS integration)
- 🪙 Phase 6: Token system & reputation via smart contracts
- 📊 Phase 7: Real-time collaboration & visualization

---

## 🤝 Contributing

Want to help build the future of intelligent problem-solving? Open a PR, suggest features, or file issues!

---

## 📜 License

MIT License © 2025 Othniel Aryee
