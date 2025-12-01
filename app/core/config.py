import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DEFAULT_MODEL = "gemini-2.5-flash"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://medichat:medichat123@localhost:5432/medichat"
    )

settings = Settings()

