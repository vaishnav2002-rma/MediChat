from app.services.langchain_client import run_assessment
from app.models.assess_models import AssessResponse, Medication


async def process_assessment(prompt: str, session_id: str):
    model_output = await run_assessment(prompt)

    if "error" in model_output:
        return None, model_output["error"]

    diagnosis = model_output.get("diagnosis")
    medications_raw = model_output.get("medications", [])
    precautions = model_output.get("precautions", [])

    medications = [
        Medication(
            name=m.get("name", "unknown"),
            dosage=m.get("dosage", "unspecified"),
            frequency=m.get("frequency", "unspecified"),
            notes=m.get("notes", "")
        ) for m in medications_raw[:3]
    ]

    return AssessResponse(
        diagnosis=diagnosis,
        medications=medications,
        precautions=precautions,
        session_id=session_id,
        message_id=0
    ), None
