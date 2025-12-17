from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.langfuse_client import langfuse 

# ---- Shared Gemini model ----
llm = ChatGoogleGenerativeAI(
    model=settings.DEFAULT_MODEL,
    api_key=settings.GEMINI_API_KEY,
    temperature=0.2
)

# ---- Graph State ----
# Every node receives & returns this dictionary
class MedicalState(dict):
    symptoms: str
    diagnosis: str
    medications: list
    precautions: list



# -------------------------
# Node 1 — Diagnosis Node
# -------------------------
def diagnosis_node(state: MedicalState):
    trace = langfuse.trace(
        name="diagnosis_node",
        metadata={"node": "diagnosis"}
    )

    try:
        symptoms = state["cleaned_symptoms"]

        prompt = f"""
    Based on the symptoms: "{symptoms}"
    Provide ONLY the most likely diagnosis in one sentence.
    """

        result = llm.invoke(prompt).text
        state["diagnosis"] = result
        return state
    except Exception as e:
        trace.end()


# -------------------------
# Node 2 — Medication Node
# -------------------------
def medication_node(state: MedicalState):
    trace = langfuse.trace(
        name="medication_node",
        metadata={"node": "diagnosis"}
    )

    try:
        diagnosis = state["diagnosis"]

        prompt = f"""
    Diagnosis: "{diagnosis}"

    Suggest 1–3 common OTC medications (generic names only), with:
    - dosage
    - frequency
    - notes

    Return as JSON list:
    [
    {{"name": "...", "dosage": "...", "frequency": "...", "notes": "..."}}
    ]
    """

        response = llm.invoke(prompt).text

        # best-effort JSON extraction
        import json
        try:
            meds = json.loads(response[response.find("["):response.rfind("]")+1])
        except:
            meds = []

        state["medications"] = meds
        return state
    except Exception as e:
        trace.end(status="error", error=str(e))
        raise 


# -------------------------
# Node 3 — Precautions Node
# -------------------------
def precautions_node(state: MedicalState):
    trace = langfuse.trace(
        name="precautions_node",
        metadata={"node": "diagnosis"}
    )

    try:
        diagnosis = state["diagnosis"]

        prompt = f"""
    Diagnosis: "{diagnosis}"

    List 3–5 important precautions or red flags as bullet points (no extra text).
    """

        response = llm.invoke(prompt).text
        precautions = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]

        state["precautions"] = precautions
        return state
    except Exception as e:
        trace.end(status="error", error=str(e))
        raise 


# -------------------------
# Node 4 — Summary Node
# -------------------------
def summary_node(state: MedicalState):
    trace = langfuse.trace(
        name="summary_node",
        metadata={"node": "diagnosis"}
    )

    try:
        summary = f"""
    Diagnosis: {state['diagnosis']}
    Medications: {state['medications']}
    Precautions: {state['precautions']}
    """
        state["summary"] = summary.strip()
        return state
    except Exception as e:
        trace.end(status="error", error=str(e))
        raise 


# -------------------------
# Build Graph
# -------------------------
workflow = StateGraph(MedicalState)

workflow.add_node("diagnosis", diagnosis_node)
workflow.add_node("medications", medication_node)
workflow.add_node("precautions", precautions_node)
workflow.add_node("summary", summary_node)

workflow.set_entry_point("clean_symptoms")
workflow.add_edge("clean_symptoms", "diagnosis")
workflow.add_edge("diagnosis", "medications")
workflow.add_edge("medications", "precautions")
workflow.add_edge("precautions", "summary")
workflow.add_edge("summary", END)

medical_graph = workflow.compile()
