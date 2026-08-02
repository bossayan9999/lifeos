from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.plugins.hub import list_plugins, call_plugin, PLUGIN_REGISTRY
from app.models.schemas import PluginInfo

router = APIRouter()


class PluginCallRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None


@router.get("/plugins", response_model=list[PluginInfo])
async def get_plugins():
    """List all MCP plugins (Enterprise + Specialized)"""
    return await list_plugins()


@router.post("/plugins/{name}/call")
async def invoke_plugin(name: str, body: PluginCallRequest):
    if name not in PLUGIN_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found")
    result = await call_plugin(name, body.query, body.params)
    return {"plugin": name, "result": result}
