from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.core.constants import SYSTEM_INSTRUCTION

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
    cleaned_symptoms: str
    diagnosis: str
    medications: list
    precautions: list
    summary: str


# -------------------------
# Node 1 — Clean Symptoms
# -------------------------
def symptom_cleaner_node(state: MedicalState):
    symptoms = state["symptoms"].strip()

    prompt = f"""
Extract only medically relevant symptoms from this text.

Input: "{symptoms}"

Return them as a clean, simple sentence.
"""

    cleaned = llm.invoke(prompt).text
    state["cleaned_symptoms"] = cleaned
    return state


# -------------------------
# Node 2 — Diagnosis Node
# -------------------------
def diagnosis_node(state: MedicalState):
    symptoms = state["cleaned_symptoms"]

    prompt = f"""
Based on the symptoms: "{symptoms}"
Provide ONLY the most likely diagnosis in one sentence.
"""

    result = llm.invoke(prompt).text
    state["diagnosis"] = result
    return state


# -------------------------
# Node 3 — Medication Node
# -------------------------
def medication_node(state: MedicalState):
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


# -------------------------
# Node 4 — Precautions Node
# -------------------------
def precautions_node(state: MedicalState):
    diagnosis = state["diagnosis"]

    prompt = f"""
Diagnosis: "{diagnosis}"

List 3–5 important precautions or red flags as bullet points (no extra text).
"""

    response = llm.invoke(prompt).text
    precautions = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]

    state["precautions"] = precautions
    return state


# -------------------------
# Node 5 — Summary Node
# -------------------------
def summary_node(state: MedicalState):
    summary = f"""
Diagnosis: {state['diagnosis']}
Medications: {state['medications']}
Precautions: {state['precautions']}
"""
    state["summary"] = summary.strip()
    return state


# -------------------------
# Build Graph
# -------------------------
workflow = StateGraph(MedicalState)

workflow.add_node("clean_symptoms", symptom_cleaner_node)
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
