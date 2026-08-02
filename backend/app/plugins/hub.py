"""
MCP Plugin Hub – Extend to External Systems
Enterprise: CRM, Project Mgmt, ERP
Specialized: API, Code Repo, Analytics, Obsidian Vault
"""
from typing import Dict, Any, Optional
from app.models.schemas import PluginInfo

# Lazy imports inside handlers to keep startup light
PLUGIN_REGISTRY: Dict[str, PluginInfo] = {
    "obsidian": PluginInfo(
        name="obsidian",
        description="Local Obsidian vault: semantic search, list/read/create notes, tags (MCP-style)",
        category="specialized",
        enabled=True,
        config_schema={"vault_path": "string (optional override)"},
    ),
    "crm": PluginInfo(
        name="crm",
        description="Bridge to CRM systems (contacts, pipeline, deals)",
        category="enterprise",
        enabled=True,
        config_schema={"base_url": "string", "api_key": "string"},
    ),
    "project_mgmt": PluginInfo(
        name="project_mgmt",
        description="Project management tools (tasks, sprints, boards)",
        category="enterprise",
        enabled=True,
        config_schema={"base_url": "string", "token": "string"},
    ),
    "erp": PluginInfo(
        name="erp",
        description="ERP integration (inventory, orders, finance)",
        category="enterprise",
        enabled=False,
        config_schema={"base_url": "string", "client_id": "string"},
    ),
    "code_repo": PluginInfo(
        name="code_repo",
        description="Code repository search & context (GitHub, local LifeOS, GitLab)",
        category="specialized",
        enabled=True,
        config_schema={"provider": "github|local", "owner": "string", "repo": "string"},
    ),
    "analytics": PluginInfo(
        name="analytics",
        description="LifeOS usage analytics, vault stats, knowledge-gap reports",
        category="specialized",
        enabled=True,
        config_schema={},
    ),
    "custom_api": PluginInfo(
        name="custom_api",
        description="Generic REST API plugin",
        category="specialized",
        enabled=True,
        config_schema={"base_url": "string", "headers": "object"},
    ),
}


async def list_plugins() -> list[PluginInfo]:
    return list(PLUGIN_REGISTRY.values())


async def call_plugin(name: str, query: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Route call to the named MCP plugin."""
    plugin = PLUGIN_REGISTRY.get(name)
    if not plugin:
        return f"Plugin '{name}' not found. Available: {', '.join(PLUGIN_REGISTRY)}"
    if not plugin.enabled:
        return f"Plugin '{name}' is disabled."

    try:
        if name == "obsidian":
            from app.plugins.obsidian import handle
            return await handle(query, params)

        if name == "crm":
            from app.plugins.crm import handle
            return await handle(query, params)

        if name == "code_repo":
            from app.plugins.code_repo import handle
            return await handle(query, params)

        if name == "analytics":
            from app.plugins.analytics import handle
            return await handle(query, params)

        if name == "project_mgmt":
            return (
                f"[Project Mgmt] Query: {query}\n"
                "Stub – wire to Jira / Linear / Asana / ClickUp API.\n"
                "Example response: 3 high-priority tasks, 2 in progress related to the query."
            )

        if name == "erp":
            return (
                f"[ERP] Query: {query}\n"
                "Plugin disabled by default. Enable in hub.py and connect your ERP."
            )

        if name == "custom_api":
            return (
                f"[Custom API] Query: {query}\n"
                "Configure base_url + headers in plugin params to call any REST endpoint."
            )

    except Exception as e:
        return f"Plugin '{name}' error: {type(e).__name__}: {e}"

    return f"Plugin '{name}' executed (no specific handler)."
