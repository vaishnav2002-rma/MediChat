from datetime import datetime
from app.services.gemini_client import call_gemini
from app.models.assess_models import AssessResponse, Medication

def process_assessment(prompt: str, session_id: str):
    model_output = call_gemini(prompt)

    if "diagnosis" not in model_output:
        return None, model_output.get("raw")

    medications = [
        Medication(
            name=m.get("name", "unknown"),
            dosage=m.get("dosage", "unspecified"),
            frequency=m.get("frequency", "unspecified"),
            notes=m.get("notes", ""),
        )
        for m in model_output.get("medications", [])[:3]
    ]

    precautions = model_output.get("precautions", [])
    if not isinstance(precautions, list):
        precautions = [precautions]

    return AssessResponse(
        diagnosis=model_output.get("diagnosis", "unspecified"),
        medications=medications,
        precautions=precautions,
        session_id=session_id,
        message_id=0
    ), None
