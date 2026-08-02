from fastapi import APIRouter
from app.models.schemas import QueryRequest, QueryResponse
from app.services.orchestrator import process_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(req: QueryRequest):
    """Main entry: Local Retrieval → A2A / Plugin → LLM"""
    return await process_query(req)
