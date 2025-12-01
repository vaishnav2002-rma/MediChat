import json
from google.genai import Client
from app.core.config import settings
from app.core.constants import SYSTEM_INSTRUCTION

client = Client(api_key=settings.GEMINI_API_KEY)

def call_gemini(prompt: str):
    full_prompt = f"{SYSTEM_INSTRUCTION}\n\nPatient symptoms: {prompt}"

    response = client.models.generate_content(
        model=settings.DEFAULT_MODEL,
        contents=full_prompt
    )

    text = response.text

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        return json.loads(text[start:end+1])

    return {"raw": text}
