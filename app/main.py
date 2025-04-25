# app/main.py
from fastapi import FastAPI
from app.api.endpoints import upload , schema_fetch
from app.api.endpoints import upload , schema_fetch , llm_matcher




app = FastAPI()

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(schema_fetch.router, prefix="/api", tags=["Schema"])
app.include_router(llm_matcher.router , prefix="/api" , tags=["LLM"])

