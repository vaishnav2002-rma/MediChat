from pydantic import BaseModel
from typing import List, Any

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
