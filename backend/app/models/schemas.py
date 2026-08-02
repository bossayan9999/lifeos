from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    DOCUMENT = "document"
    FAQ = "faq"
    CHAT_LOG = "chat_log"
    WEB = "web"
    PLUGIN = "plugin"


class Citation(BaseModel):
    source_id: str
    title: str
    excerpt: str
    score: float
    source_type: SourceType
    url: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    use_web: bool = Field(default=False, description="Force A2A web search")
    plugin: Optional[str] = Field(default=None, description="Force MCP plugin")


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float
    used_web: bool = False
    used_plugin: Optional[str] = None
    processing_ms: int


class FeedbackRequest(BaseModel):
    query_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    reported_gap: Optional[str] = None


class CleanerReport(BaseModel):
    duplicates_removed: int
    stale_archived: int
    embeddings_compressed: bool
    ran_at: datetime


class PluginInfo(BaseModel):
    name: str
    description: str
    category: str  # enterprise | specialized
    enabled: bool
    config_schema: Dict[str, Any] = {}
