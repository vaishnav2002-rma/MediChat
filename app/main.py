from fastapi import FastAPI
from app.api.routes.assess import router as assess_router
from app.api.routes.history import router as history_router
from app.api.routes.hospital_finder import router as hospital_router

from app.db.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediChat API")

# Existing routers
app.include_router(assess_router)
app.include_router(history_router)

# NEW Hospital Finder Router
app.include_router(hospital_router)

@app.get("/health")
def health():
    return {"status": "ok"}
