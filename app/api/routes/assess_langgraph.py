from fastapi import APIRouter, HTTPException
from app.services.langgraph_service import run_langgraph_assessment

router = APIRouter(prefix="/assess/flow", tags=["LangGraph"])

@router.post("/")
async def assess_with_flow(req: dict):
    text = req.get("text", "").strip()
    if not text:
        raise HTTPException(400, "Empty text")

    result = await run_langgraph_assessment(text)
    return result
