from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.routes.assess import get_db
from app.db import crud_history
from app.models.history_models import ChatHistoryResponse

router = APIRouter(prefix="/history", tags=["History"])

@router.get("/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str, db: Session = Depends(get_db)):
    msgs = crud_history.get_history(db, session_id)
    if not msgs:
        raise HTTPException(404, "Session not found")

    messages = [
        {
            "id": m.id,
            "user_message": m.user_message,
            "ai_response": m.ai_response,
            "diagnosis": m.diagnosis,
            "created_at": m.created_at.isoformat(),
            "model_used": m.model_used,
        }
        for m in msgs
    ]

    return ChatHistoryResponse(session_id=session_id, messages=messages)

@router.delete("/{session_id}")
async def delete_history(session_id: str, db: Session = Depends(get_db)):
    deleted = crud_history.delete_history(db, session_id)
    if deleted == 0:
        raise HTTPException(404, "Session not found")
    return {"message": f"Deleted {deleted} messages."}

@router.get("/sessions/list")
async def list_sessions(db: Session = Depends(get_db), limit: int = 50):
    sessions = crud_history.list_sessions(db, limit)
    return {
        "sessions": [
            {"session_id": s.session_id, "last_updated": s.created_at.isoformat()}
            for s in sessions
        ]
    }
