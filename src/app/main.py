from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.quantum.engine import run_simple_circuit
from app.database import SessionLocal, SolvedProblem

# Initialize OpenAI client and embedding model
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedder = SentenceTransformer("all-MiniLM-L6-v2")

app = FastAPI(title="Quantum Knowledge Network", version="1.0")

# Request body schema
class ProblemRequest(BaseModel):
    question: str
    method: str  # "quantum" or "ai"

@app.get("/")
def health_check():
    return {"message": "Quantum API is live!"}

@app.post("/solve")
async def solve_problem(payload: ProblemRequest):
    session: Session = SessionLocal()
    try:
        # Generate embedding for the question
        embedding = embedder.encode([payload.question])[0].tolist()

        if payload.method.lower() == "quantum":
            result = run_simple_circuit()
            problem = SolvedProblem(
                question=payload.question,
                method="quantum",
                answer=str(result),
                embedding=embedding
            )
            session.add(problem)
            session.commit()
            return {"method": "quantum", "result": result}

        elif payload.method.lower() == "ai":
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quantum computing assistant."},
                    {"role": "user", "content": payload.question}
                ]
            )
            answer = response.choices[0].message.content.strip()
            problem = SolvedProblem(
                question=payload.question,
                method="ai",
                answer=answer,
                embedding=embedding
            )
            session.add(problem)
            session.commit()
            return {"method": "ai", "answer": answer}

        else:
            return {"error": "Invalid method. Use 'quantum' or 'ai'."}

    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

    finally:
        session.close()

@app.get("/history")
def get_history():
    session: Session = SessionLocal()
    problems = session.query(SolvedProblem).order_by(SolvedProblem.timestamp.desc()).all()
    session.close()
    return [
        {
            "id": p.id,
            "question": p.question,
            "method": p.method,
            "answer": p.answer,
            "timestamp": p.timestamp.isoformat()
        }
        for p in problems
    ]

@app.get("/search")
def semantic_search(q: str = Query(..., description="Search similar questions")):
    session: Session = SessionLocal()
    problems = session.query(SolvedProblem).filter(SolvedProblem.embedding.isnot(None)).all()

    if not problems:
        session.close()
        return {"message": "No stored questions yet."}

    query_vec = embedder.encode([q])[0].reshape(1, -1)
    db_vecs = np.array([np.array(p.embedding) for p in problems])
    similarities = cosine_similarity(query_vec, db_vecs)[0]
    top_idxs = similarities.argsort()[::-1][:3]

    results = []
    for idx in top_idxs:
        p = problems[idx]
        results.append({
            "question": p.question,
            "method": p.method,
            "answer": p.answer,
            "similarity": float(similarities[idx]),
            "timestamp": p.timestamp.isoformat()
        })

    session.close()
    return results
