import time
import os
from fastapi import FastAPI
from datetime import datetime

APP_ENV = os.getenv("APP_ENV", "dev")

print(f"Inicializando app... [ambiente: {APP_ENV}]", flush=True)
time.sleep(15)
print(f"App lista. [ambiente: {APP_ENV}]", flush=True)

app = FastAPI(title=f"Microservicio Demo - {APP_ENV.upper()}")


@app.get("/live")
def liveness():
    return {
        "status": "alive",
        "env": APP_ENV,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready")
def readiness():
    return {
        "status": "ready",
        "env": APP_ENV,
        "change": "probando cambios para ver todo el flujo",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
def root():
    return {
        "message": "Microservicio funcionando",
        "env": APP_ENV,
    }
