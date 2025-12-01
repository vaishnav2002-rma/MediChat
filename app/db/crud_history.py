from sqlalchemy.orm import Session
from app.db.models import ChatMessage

def create_chat_message(db: Session, session_id: str, user_message: str, ai_response: dict, diagnosis: str, model: str):
    chat = ChatMessage(
        session_id=session_id,
        user_message=user_message,
        ai_response=ai_response,
        diagnosis=diagnosis,
        model_used=model
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def get_history(db: Session, session_id: str):
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

def list_sessions(db: Session, limit: int = 50):
    return db.query(
        ChatMessage.session_id,
        ChatMessage.created_at
    ).group_by(
        ChatMessage.session_id, ChatMessage.created_at
    ).order_by(
        ChatMessage.created_at.desc()
    ).limit(limit).all()

def delete_history(db: Session, session_id: str):
    count = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).delete()
    db.commit()
    return count

