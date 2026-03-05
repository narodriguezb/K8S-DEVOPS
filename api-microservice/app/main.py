import time
from fastapi import FastAPI
from datetime import datetime

print("Inicializando app...", flush=True)
time.sleep(15)
print("App lista.", flush=True)

app = FastAPI(title="Microservicio Demo")


@app.get("/live")
def liveness():
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@app.get("/ready")
def readiness():
    return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
def root():
    return {"message": "Microservicio funcionando"}
