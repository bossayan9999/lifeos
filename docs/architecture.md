# LifeOS Architecture Mapping

This implementation follows the provided flowchart exactly.

## Content Sources
- Documents, FAQs, Chat Logs are stored as Markdown in `backend/data/vault/`
- Seeded with sample notes on first startup

## Obsidian Vault & Local Storage
- Parse Markdown → embed with `sentence-transformers` (all-MiniLM-L6-v2)
- Vector store: FAISS (IndexFlatIP) + SQLite metadata
- Files: `data/faiss.index`, `data/lifeos.db`

## Query Processing & LLM Orchestrator
1. **Local Retrieval** – semantic search (primary)
2. If confidence < 0.55 or `use_web=true` → **A2A Web Search** stub
3. Optional **MCP Plugin** injection
4. **LLM** (OpenAI / Anthropic / extractive fallback) generates answer + citations

## MCP Plugin Hub
Registered plugins (modular under `app/plugins/`):

| Plugin | Category | Status | Capabilities |
|--------|----------|--------|--------------|
| **obsidian** | specialized | Live | Semantic search, list/read/create notes, tag cloud over `data/vault/` |
| **crm** | enterprise | Demo data | Contacts, pipeline, deals |
| **code_repo** | specialized | Live (local) + GitHub-ready | Local LifeOS code + GitHub via connected tools |
| **analytics** | specialized | Live | Query stats, local hit rate, knowledge gaps |
| **project_mgmt** | enterprise | Stub | Ready for Jira/Linear/Asana |
| **erp** | enterprise | Disabled | Inventory/finance |
| **custom_api** | specialized | Stub | Generic REST |

Obsidian plugin follows the same patterns as Semantic Notes Vault MCP, Obsidian Intelligence, Analogy, and Vault Retrieval (local embeddings + MCP-style tools).

## Data Cleaner Module
- Endpoint: `POST /api/v1/cleaner/run`
- Script: `scripts/cleaner.py`
- Removes title-level duplicates, archives stale (stub)

## User Interaction & Feedback
- React chat UI with source citations, confidence, plugin routing
- Feedback endpoint logs ratings + knowledge gaps
- Gaps viewable via `GET /api/v1/gaps`

## Privacy
- Internal data never leaves the machine
- External calls only when local confidence is low or forced
- All external connectors are read-only by design
