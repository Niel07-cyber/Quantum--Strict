# app/main.py
import os
import json
import requests
import numpy as np
from dotenv import load_dotenv

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import socketio

from openai import OpenAI
from app.quantum.engine import run_simple_circuit
from app.database     import SessionLocal, SolvedProblem

# ─── Load env & Pinata helper ─────────────────────────────────────────────────

load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")
if not PINATA_JWT:
    raise RuntimeError("Missing PINATA_JWT in .env")

def pin_json_to_pinata(record: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type":  "application/json",
    }
    r = requests.post(url, headers=headers, json=record)
    r.raise_for_status()
    return r.json()["IpfsHash"]


# ─── Socket.IO Setup ───────────────────────────────────────────────────────────

# 1) Create an Async Socket.IO server  
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"        # allow all origins for websocket (you can lock this down)
)

# 2) Wrap your FastAPI app with the Socket.IO ASGI app  
app = FastAPI(
    title="Quantum Knowledge Network",
    version="1.0",
)

# 3) Mount CORS (HTTP side)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # adjust in prod
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 4) Mount Socket.IO right next to FastAPI
#    The ASGIApp will serve both / and /socket.io/ endpoints.
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)


# 5) Optionally handle connect/disconnect
@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)


# 6) Helper to broadcast a newly‐solved problem
async def broadcast_new_problem(problem_dict: dict):
    # emit on channel "new_problem" to all connected clients
    await sio.emit("new_problem", problem_dict)


# ─── OpenAI + Embedding Setup ─────────────────────────────────────────────────

client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class ProblemRequest(BaseModel):
    question: str
    method:   str   # "quantum" or "ai"


# ─── HTTP Endpoints ───────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    return {"message": "Quantum API is live!"}


@app.post("/solve")
async def solve_problem(payload: ProblemRequest):
    session: Session = SessionLocal()
    try:
        q = payload.question
        m = payload.method.lower()

        # 1) compute embedding
        emb = embedder.encode([q])[0].tolist()

        # 2) run either quantum or AI
        if m == "quantum":
            resp_data = run_simple_circuit()

        elif m == "ai":
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role":"system", "content":"You are a quantum computing assistant."},
                    {"role":"user",   "content":q}
                ],
            )
            resp_data = resp.choices[0].message.content.strip()

        else:
            return {"error": "Invalid method. Use 'quantum' or 'ai'."}

        # 3) persist to DB
        prob = SolvedProblem(
            question=q,
            method=m,
            answer=str(resp_data),
            embedding=emb,
        )
        session.add(prob)
        session.commit()
        session.refresh(prob)

        # 4) pin to IPFS via Pinata
        record = {
            "id":        prob.id,
            "question":  prob.question,
            "method":    prob.method,
            "response":  resp_data,
            "timestamp": prob.timestamp.isoformat(),
        }
        cid = pin_json_to_pinata(record)

        # 5) update DB with CID
        prob.cid = cid
        session.commit()

        # 6) broadcast the new problem over websockets
        await broadcast_new_problem(record | {"cid": cid})

        # 7) return HTTP response
        key = "result" if m == "quantum" else "answer"
        return {"method": m, key: resp_data, "cid": cid}

    except Exception as e:
        return {"error": f"Processing failed: {e}"}

    finally:
        session.close()


@app.get("/history")
def get_history():
    session = SessionLocal()
    rows = session.query(SolvedProblem).order_by(SolvedProblem.timestamp.desc()).all()
    session.close()

    return [
        {
            "id":        r.id,
            "question":  r.question,
            "method":    r.method,
            "answer":    r.answer,
            "timestamp": r.timestamp.isoformat(),
            "cid":       r.cid,
        }
        for r in rows
    ]


@app.get("/search")
def semantic_search(q: str = Query(..., description="Search similar questions")):
    session = SessionLocal()
    rows = session.query(SolvedProblem).filter(SolvedProblem.embedding.isnot(None)).all()
    session.close()

    if not rows:
        return {"message": "No stored questions yet."}

    query_vec = embedder.encode([q]).reshape(1, -1)
    db_vecs    = np.vstack([r.embedding for r in rows])
    sims       = cosine_similarity(query_vec, db_vecs)[0]
    top_idxs   = sims.argsort()[::-1][:3]

    return [
        {
            "question":   rows[i].question,
            "method":     rows[i].method,
            "answer":     rows[i].answer,
            "similarity": float(sims[i]),
            "timestamp":  rows[i].timestamp.isoformat(),
            "cid":        rows[i].cid,
        }
        for i in top_idxs
    ]


# ─── HOW TO RUN ────────────────────────────────────────────────────────────────
#
# In your shell:
#
#   poetry add python-socketio               # if you haven’t already
#
#   uvicorn app.main:asgi_app --reload
#
# That command points Uvicorn at the `asgi_app` you built above,
# which serves both your FastAPI HTTP routes AND the /socket.io/* handlers.
