from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import OpenAI

from app.quantum.engine import run_simple_circuit
from app.database import SessionLocal, SolvedProblem

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="Quantum Knowledge Network", version="1.0")

# Request schema
class ProblemRequest(BaseModel):
    question: str
    method: str  # "quantum" or "ai"

# Health check
@app.get("/")
def health_check():
    return {"message": "Quantum API is live!"}

# Problem solver endpoint
@app.post("/solve")
async def solve_problem(payload: ProblemRequest):
    session = SessionLocal()

    if payload.method.lower() == "quantum":
        result = run_simple_circuit()

        problem = SolvedProblem(
            question=payload.question,
            method="quantum",
            answer=str(result)
        )
        session.add(problem)
        session.commit()
        session.close()

        return {"method": "quantum", "result": result}

    elif payload.method.lower() == "ai":
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant knowledgeable in quantum computing."},
                    {"role": "user", "content": payload.question}
                ]
            )
            answer = response.choices[0].message.content.strip()

            problem = SolvedProblem(
                question=payload.question,
                method="ai",
                answer=answer
            )
            session.add(problem)
            session.commit()
            session.close()

            return {"method": "ai", "answer": answer}

        except Exception as e:
            session.close()
            return {"error": f"AI request failed: {str(e)}"}

    else:
        session.close()
        return {"error": "Invalid method. Use 'quantum' or 'ai'."}

# History endpoint
@app.get("/history")
def get_history():
    session = SessionLocal()
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
