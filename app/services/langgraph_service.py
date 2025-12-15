from app.services.langgraph_flow import medical_graph, MedicalState

async def run_langgraph_assessment(symptoms: str):
    initial_state = MedicalState(symptoms=symptoms)

    final_state = medical_graph.invoke(initial_state)

    return {
        "diagnosis": final_state.get("diagnosis"),
        "medications": final_state.get("medications", []),
        "precautions": final_state.get("precautions", []),
        "summary": final_state.get("summary")
    }
