from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings
from app.core.constants import SYSTEM_INSTRUCTION

# ----- Define LLM -----
llm = ChatGoogleGenerativeAI(
    model=settings.DEFAULT_MODEL,
    api_key=settings.GEMINI_API_KEY,
    temperature=0.2
)

# ----- Define Output Parser -----
parser = JsonOutputParser()

# ----- LangChain Prompt -----
prompt = PromptTemplate(
    template=SYSTEM_INSTRUCTION + "\nPatient symptoms: {symptoms}",
    input_variables=["symptoms"]
)

# ----- Create LCEL pipeline -----
chain = prompt | llm | parser


async def run_assessment(symptoms: str):
    """
    Executes full LangChain pipeline:
    PromptTemplate → Gemini → JSON parser → dict
    """
    try:
        result = chain.invoke({"symptoms": symptoms})
        return result
    except Exception as e:
        return {"error": str(e)}
