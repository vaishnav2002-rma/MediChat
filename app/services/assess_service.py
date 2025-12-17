from app.services.langchain_client import run_assessment
from app.models.assess_models import AssessResponse, Medication

async def process_assessment(prompt: str, session_id: str):
    try:
        model_output = await run_assessment(prompt, session_id)

        return AssessResponse(
            diagnosis=model_output.diagnosis,
            medications=model_output.medications,
            precautions=model_output.precautions,
            session_id=session_id,
            message_id=0 
        ), None 
    
    except Exception as e:
        return None, str(e)