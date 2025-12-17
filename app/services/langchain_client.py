from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langfuse.callback import CallbackHandler 
from pydantic import BaseModel
from typing import List


from app.core.config import settings
from app.core.constants import SYSTEM_INSTRUCTION
from app.models.assess_models import Medication 

langfuse_handler = CallbackHandler()

class LLMAssessmentOutput(BaseModel):
    diagnosis: str 
    medications: List[Medication]
    precautions: List[str]

# ----- Define LLM -----
llm = ChatGoogleGenerativeAI(
    model=settings.DEFAULT_MODEL,
    api_key=settings.GEMINI_API_KEY,
    temperature=0.2,
    callbacks=[langfuse_handler]
)

# ----- Define Output Parser -----
parser = PydanticOutputParser(pydantic_object=LLMAssessmentOutput)

# ----- LangChain Prompt -----
prompt = PromptTemplate(
    template=SYSTEM_INSTRUCTION + "\n{format_instructions}\nPatient symptoms: {symptoms}",
    input_variables=["symptoms"],
    partial_variables={
        "format_instructions": parser.get_format_instructions()
    }
)

# ----- Create LCEL pipeline -----
chain = prompt | llm | parser
                                     

async def run_assessment(symptoms: str, session_id: str):
    return chain.invoke(
        {"symptoms":symptoms},
        config={
            "callbacks":[langfuse_handler],
            "metadata":{
                "session_id": session_id,
                "pipeline": "langchain_assessment"
            }
        }   
    )
