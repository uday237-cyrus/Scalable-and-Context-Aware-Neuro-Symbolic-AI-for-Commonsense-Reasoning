from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.auth import get_current_user_optional
from app.brain.moral_reasoner import get_moral_reasoner
from app.brain.transformer_brain import reason_about
from app.db.database import get_db
from app.db.models import ChatMessage, User
from app.explain.explanation_gen import generate_explanation
from app.knowledge.neo4j_client import Neo4jClient
from app.nlp.nlp_engine import analyze_query
from app.reasoning.context_inference import ContextEngine
from app.reasoning.symbolic_engine import SymbolicReasoner

router = APIRouter(prefix="/api", tags=["chat"])
knowledge_client = Neo4jClient()
symbolic_reasoner = SymbolicReasoner(knowledge_client)
context_engine = ContextEngine()
moral_reasoner = get_moral_reasoner()


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=4_000)
    candidate_answers: list[Annotated[str, Field(min_length=1, max_length=120)]] = Field(default_factory=list, max_length=12)


class ChatResponse(BaseModel):
    answer: str
    explanation: str
    confidence: float
    reasoning_chains: list[list[str]]
    facts: list[dict[str, str]]
    engine: str


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> ChatResponse:
    analysis = analyze_query(payload.message)
    context_engine.update_context(payload.session_id, payload.message, analysis["key_concepts"], analysis["entities"])
    concepts = context_engine.enrich_concepts(payload.session_id, analysis["key_concepts"])
    reasoning = symbolic_reasoner.infer(concepts)
    brain_result = reason_about(payload.message, payload.candidate_answers)
    moral_result = moral_reasoner.deliberate(payload.message, payload.candidate_answers)
    final = generate_explanation(
        analysis["entities"],
        reasoning,
        brain_result,
        context_engine.get_context_summary(payload.session_id),
        moral_result=moral_result,
    )

    db.add_all(
        [
            ChatMessage(session_id=payload.session_id, user_id=user.id if user else None, role="user", content=payload.message),
            ChatMessage(
                session_id=payload.session_id,
                user_id=user.id if user else None,
                role="assistant",
                content=final["answer"],
                explanation=final["explanation"],
                confidence=str(final["confidence"]),
            ),
        ]
    )
    db.commit()
    return ChatResponse(**final)


@router.get("/history/{session_id}")
def history(
    session_id: str,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
) -> list[dict]:
    query = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    if user:
        query = query.where(ChatMessage.user_id == user.id)
    else:
        # Anonymous callers may retrieve only the anonymous conversations they created.
        # Authenticated conversations must never be exposed by guessing a session id.
        query = query.where(ChatMessage.user_id.is_(None))
    messages = db.scalars(query.limit(200)).all()
    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "explanation": message.explanation,
            "confidence": float(message.confidence) if message.confidence else None,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]


@router.get("/graph/{concept}")
def graph(concept: str) -> dict:
    if not concept.strip():
        raise HTTPException(status_code=400, detail="A concept is required")
    return symbolic_reasoner.infer([concept])
