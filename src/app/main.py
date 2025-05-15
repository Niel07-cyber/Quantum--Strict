from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
import os
from openai import OpenAI
from app.quantum.engine import run_simple_circuit

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Pydantic model for request validation
class ProblemRequest(BaseModel):
    question: str
    method: str  # "quantum" or "ai"

@app.get("/")
def run():
    return {"result": run_simple_circuit()}

@app.post("/solve")
async def solve_problem(payload: ProblemRequest):
    if payload.method.lower() == "quantum":
        result = run_simple_circuit()
        return {"method": "quantum", "result": result}
    
    elif payload.method.lower() == "ai":
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quantum computing assistant."},
                    {"role": "user", "content": payload.question}
                ]
            )
            answer = response.choices[0].message.content
            return {"method": "ai", "answer": answer.strip()}
        except Exception as e:
            return {"error": f"AI request failed: {str(e)}"}
    
    else:
        return {"error": "Invalid method. Use 'quantum' or 'ai'."}
