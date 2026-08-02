# LifeOS MCP Plugin Overview

LifeOS exposes a modular MCP Plugin Hub.

## Available Plugins (2026-08)

- **obsidian** – Semantic search, list/read/create notes, tag cloud over the local vault
- **crm** – Contacts, pipeline, deals (demo data; replace with real CRM)
- **code_repo** – GitHub / local code search
- **analytics** – Query volume, local hit rate, knowledge gaps
- **project_mgmt** – Tasks & boards (stub)
- **erp** – Inventory & finance (disabled by default)
- **custom_api** – Generic REST bridge

## How to use from the chat UI

Select a plugin in the sidebar, then ask naturally:
- “list notes”
- “search for architecture decisions”
- “show pipeline”
- “what is the local hit rate?”

## Privacy

All Obsidian vault data stays inside `backend/data/vault/`. No notes are uploaded unless you explicitly enable an external embedding provider.
