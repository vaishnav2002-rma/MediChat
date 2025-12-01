from pydantic import BaseModel
from typing import List, Optional

class AssessRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    notes: str = ""

class AssessResponse(BaseModel):
    diagnosis: str
    medications: List[Medication]
    precautions: List[str]
    source: str = "generated"
    session_id: str
    message_id: int
