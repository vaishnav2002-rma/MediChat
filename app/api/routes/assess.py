from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import SessionLocal
from app.db import crud_history

from app.models.assess_models import AssessRequest, AssessResponse
from app.services.assess_service import process_assessment
from app.core.config import settings

router = APIRouter(prefix="/assess", tags=["Assess"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AssessResponse)
async def assess(req: AssessRequest, db: Session = Depends(get_db)):
    prompt = req.text.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty input")

    session_id = req.session_id or f"session_{datetime.utcnow().timestamp()}"

    response_data, raw = await process_assessment(prompt, session_id)

    if raw:
        raise HTTPException(status_code=502, detail=f"LLM returned unparsable response: {raw}")

    # Store in DB
    saved = crud_history.create_chat_message(
        db,
        session_id=session_id,
        user_message=prompt,
        ai_response=response_data.dict(exclude={"session_id", "message_id"}),
        diagnosis=response_data.diagnosis,
        model=settings.DEFAULT_MODEL
    )

    response_data.message_id = saved.id
    return response_data
