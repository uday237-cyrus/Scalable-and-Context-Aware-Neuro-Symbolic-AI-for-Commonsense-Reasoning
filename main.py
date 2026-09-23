from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.database import create_tables
from app.routers import chat, users

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield
    chat.knowledge_client.close()


app = FastAPI(
    title="NeuroSymbolic AI API",
    version="0.1.0",
    description="Explainable commonsense classification with symbolic knowledge-graph paths.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(chat.router)
app.include_router(users.router)


@app.get("/", tags=["health"])
def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "knowledge_source": chat.knowledge_client.source_name}
