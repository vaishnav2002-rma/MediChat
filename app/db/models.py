from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.db.database import Base
from app.core.config import settings

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(JSON, nullable=False)
    diagnosis = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String(100), default=settings.DEFAULT_MODEL)
