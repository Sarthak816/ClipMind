import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine, Base
from app.routes import auth, videos, me, transcripts, summaries
from app.workers import extraction, transcription, summarization, key_moments

app = FastAPI(title="ClipMind API", version="0.1.0")

cors_origins = settings.CORS_ORIGINS
origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(me.router)
app.include_router(videos.router)
app.include_router(transcripts.router)
app.include_router(summaries.router)
app.include_router(extraction.router)
app.include_router(transcription.router)
app.include_router(summarization.router)
app.include_router(key_moments.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": "clipmind-api"}
