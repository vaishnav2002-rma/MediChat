from pydantic import BaseModel

class AssessRequest(BaseModel):
    text: str
