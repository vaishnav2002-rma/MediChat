from pydantic import BaseModel
from typing import List

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
