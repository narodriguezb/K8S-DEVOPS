from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Microservicio Demo")


@app.get("/live")
def liveness():
    print("hi nes")
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
def readiness():
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
def root():
    return {"message": "Microservicio funcionando"}
