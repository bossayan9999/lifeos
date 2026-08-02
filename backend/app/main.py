"""
LifeOS Query Processing & LLM Orchestrator
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import query, feedback, cleaner, plugins
from app.services.vector_store import init_vector_store

load_dotenv()

app = FastAPI(
    title="LifeOS Knowledge Base",
    description="AI Knowledge Base with MCP Plugin Hub",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api/v1", tags=["Query"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(cleaner.router, prefix="/api/v1", tags=["Cleaner"])
app.include_router(plugins.router, prefix="/api/v1", tags=["MCP Plugins"])


@app.on_event("startup")
async def startup():
    init_vector_store()
    print("LifeOS Orchestrator ready – local-first mode active")


@app.get("/health")
async def health():
    return {"status": "ok", "mode": "local-first"}
