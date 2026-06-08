from fastapi import FastAPI
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SecurePulse",
    description="AI-Powered Log Analysis & Threat Detection",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "SecurePulse API",
        "version": "0.1.0"
    }