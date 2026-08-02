# LifeOS – AI Knowledge Base with MCP Plugin Hub

Full-stack implementation of the architecture diagram.

## Architecture Alignment

| Layer | Implementation |
|-------|----------------|
| Content Sources | Documents / FAQs / Chat Logs → chunked into Obsidian-style Markdown |
| Obsidian Vault & Local Storage | `backend/data/vault/` + FAISS / SQLite vector store |
| Query Processing & LLM Orchestrator | FastAPI + local semantic search → A2A fallback → LLM |
| MCP Plugin Hub | Extensible plugin system (CRM, ERP, Code Repo, Analytics, Obsidian, custom APIs) |
| Data Cleaner Module | Weekly job: deduplicate + archive stale notes |
| User Interaction | React chat UI with sources + feedback loop |
| Feedback Loop | Query logging + gap reporting |

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Data Cleaner (manual)
```bash
python scripts/cleaner.py
```

## Environment
Copy `.env.example` → `.env` and set:
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / etc. (LLM of choice)
- `GOOGLE_API_KEY` (optional A2A web search)

## Project Structure
```
lifeos/
├── backend/          # FastAPI orchestrator + MCP plugins
├── frontend/         # React chat interface
├── scripts/          # Data Cleaner & maintenance
├── docs/             # Architecture notes
└── README.md
```

## MCP Plugins (implemented)

| Plugin | Category | Status |
|--------|----------|--------|
| **obsidian** | specialized | Live – semantic search, list/read/create notes, tags |
| **crm** | enterprise | Demo data |
| **code_repo** | specialized | Local + GitHub-ready |
| **analytics** | specialized | Live usage & gap stats |
| **project_mgmt** | enterprise | Stub |
| **erp** | enterprise | Disabled |
| **custom_api** | specialized | Stub |

Privacy: All internal data stays local. External calls are read-only and only triggered when local retrieval confidence is low.
