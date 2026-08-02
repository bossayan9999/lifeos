"""
Code Repository MCP Plugin
Supports GitHub (via connected tools) and generic local/remote repos.
"""
from typing import Optional, Dict, Any
import os


async def handle(query: str, params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    provider = params.get("provider", "github")
    owner = params.get("owner") or os.getenv("GITHUB_OWNER")
    repo = params.get("repo") or os.getenv("GITHUB_REPO")

    if "lifeos" in query.lower() or "orchestrator" in query.lower() or "plugin" in query.lower():
        return (
            "[Code Repo – Local LifeOS]\n"
            "Relevant modules:\n"
            "- backend/app/services/orchestrator.py – Query → Local → A2A → LLM pipeline\n"
            "- backend/app/services/vector_store.py – FAISS + SQLite vault index\n"
            "- backend/app/plugins/hub.py – MCP Plugin registry\n"
            "- backend/app/plugins/obsidian/ – Vault read/search/create tools\n"
            "- frontend/src/components/ChatInterface.jsx – User chat UI\n"
            "Ask me to read a specific file or search the repo for symbols."
        )

    if provider == "github" and owner and repo:
        return (
            f"[Code Repo – GitHub {owner}/{repo}]\n"
            f"Query: {query}\n\n"
            "To enable live GitHub search, set GITHUB_OWNER and GITHUB_REPO "
            "or pass owner/repo in plugin params. "
            "LifeOS can then use the connected GitHub tools "
            "(search_code, get_file_contents, get_repository_tree, etc.).\n\n"
            "Example structured call:\n"
            '{"action": "search_code", "query": "semantic_search language:python"}'
        )

    return (
        f"[Code Repo]\n"
        f"Query: {query}\n"
        "No specific repository configured. "
        "Pass params: {\"provider\": \"github\", \"owner\": \"...\", \"repo\": \"...\"} "
        "or set GITHUB_OWNER / GITHUB_REPO environment variables."
    )
