import os
import json
import requests
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.quantum.engine import run_simple_circuit
from app.database import SessionLocal, SolvedProblem

# Load environment variables
load_dotenv()

# === Pinata helper using JWT ===
PINATA_JWT = os.getenv("PINATA_JWT")
if not PINATA_JWT:
    raise RuntimeError("Missing PINATA_JWT in .env")

def pin_json_to_pinata(record: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json=record)
    resp.raise_for_status()
    return resp.json()["IpfsHash"]
# === end Pinata helper ===

# Initialize OpenAI client and embedding model
client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI(title="Quantum Knowledge Network", version="1.0")

# … rest of your routes …

# Request schema
class ProblemRequest(BaseModel):
    question: str
    method:   str  # "quantum" or "ai"

@app.get("/")
def health_check():
    return {"message": "Quantum API is live!"}

@app.post("/solve")
async def solve_problem(payload: ProblemRequest):
    session: Session = SessionLocal()
    try:
        q      = payload.question
        m      = payload.method.lower()
        emb    = embedder.encode([q])[0].tolist()

        if m == "quantum":
            resp_data = run_simple_circuit()

        elif m == "ai":
            ai_resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role":"system","content":"You are a quantum computing assistant."},
                    {"role":"user",  "content":q}
                ]
            )
            resp_data = ai_resp.choices[0].message.content.strip()

        else:
            return {"error":"Invalid method. Use 'quantum' or 'ai'."}

        # Persist in DB
        prob = SolvedProblem(
            question=q,
            method=m,
            answer=str(resp_data),
            embedding=emb
        )
        session.add(prob)
        session.commit()

        # Pin via Pinata
        record = {
            "id":        prob.id,
            "question":  q,
            "method":    m,
            "response":  resp_data,
            "timestamp": prob.timestamp.isoformat()
        }
        cid = pin_json_to_pinata(record)

        # Save CID back to DB
        prob.cid = cid
        session.commit()

        key = "result" if m == "quantum" else "answer"
        return {"method":m, key:resp_data, "cid":cid}

    except Exception as e:
        return {"error":f"Processing failed: {e}"}

    finally:
        session.close()

@app.get("/history")
def get_history():
    session = SessionLocal()
    prods   = session.query(SolvedProblem).order_by(SolvedProblem.timestamp.desc()).all()
    session.close()

    return [
        {
            "id":        p.id,
            "question":  p.question,
            "method":    p.method,
            "answer":    p.answer,
            "timestamp": p.timestamp.isoformat(),
            "cid":       p.cid
        }
        for p in prods
    ]

@app.get("/search")
def semantic_search(q: str = Query(..., description="Search similar questions")):
    session  = SessionLocal()
    problems = session.query(SolvedProblem).filter(SolvedProblem.embedding.isnot(None)).all()
    session.close()

    if not problems:
        return {"message":"No stored questions yet."}

    query_vec = embedder.encode([q]).reshape(1, -1)
    db_vecs   = np.vstack([p.embedding for p in problems])
    sims      = cosine_similarity(query_vec, db_vecs)[0]
    top3      = sims.argsort()[::-1][:3]

    return [
        {
            "question":   problems[i].question,
            "method":     problems[i].method,
            "answer":     problems[i].answer,
            "similarity": float(sims[i]),
            "timestamp":  problems[i].timestamp.isoformat(),
            "cid":        problems[i].cid
        }
        for i in top3
    ]
