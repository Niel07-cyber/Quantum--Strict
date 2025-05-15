from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.quantum.engine import run_simple_circuit

app = FastAPI()

@app.get("/")
def run():
    return {"result": run_simple_circuit()}
