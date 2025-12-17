from app.services.langchain_client import run_assessment
from app.models.assess_models import AssessResponse, Medication

async def process_assessment(prompt: str, session_id: str):
    model_output = await run_assessment(prompt, session_id)

    # Error from parser or LLM
    if "error" in model_output:
        return None, model_output["error"]

    if "diagnosis" not in model_output:
        return None, model_output

    medications = [
        Medication(
            name=m.get("name", "unknown"),
            dosage=m.get("dosage", "unspecified"),
            frequency=m.get("frequency", "unspecified"),
            notes=m.get("notes", "")
        )
        for m in model_output.get("medications", [])[:3]
    ]

    precautions = model_output.get("precautions", [])
    if not isinstance(precautions, list):
        precautions = [precautions]

    return AssessResponse(
        diagnosis=model_output.get("diagnosis"),
        medications=medications,
        precautions=precautions,
        session_id=session_id,
        message_id=0
    ), None
