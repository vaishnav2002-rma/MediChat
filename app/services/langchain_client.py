from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.runnables import RunnableSequence
from app.core.config import settings
from app.core.constants import SYSTEM_INSTRUCTION


# ----------------------------
# 1. Define Output Schema
# ----------------------------
diagnosis_schema = ResponseSchema(
    name="diagnosis",
    description="Likely medical diagnosis based on symptoms."
)

medications_schema = ResponseSchema(
    name="medications",
    description="List of medications with name, dosage, frequency, notes."
)

precautions_schema = ResponseSchema(
    name="precautions",
    description="List of precautions or warnings."
)

parser = StructuredOutputParser.from_response_schemas([
    diagnosis_schema,
    medications_schema,
    precautions_schema
])

format_instructions = parser.get_format_instructions()


# ----------------------------
# 2. Define Prompt (Best Practice)
# ----------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTION + "\n\n{format_instructions}"),
    ("user", "Patient symptoms: {symptoms}")
])


# ----------------------------
# 3. Gemini LLM
# ----------------------------
llm = ChatGoogleGenerativeAI(
    model=settings.DEFAULT_MODEL,
    temperature=0.2,
    api_key=settings.GEMINI_API_KEY
)


# ----------------------------
# 4. LCEL Pipeline
# ----------------------------
chain: RunnableSequence = (
      prompt 
    | llm 
    | parser
)


# ----------------------------
# 5. Function to Run Pipeline
# ----------------------------
async def run_assessment(symptoms: str):
    try:
        return chain.invoke({
            "symptoms": symptoms,
            "format_instructions": format_instructions
        })
    except Exception as e:
        return {"error": str(e)}
