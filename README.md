# LifeOS – AI Knowledge Base with MCP Plugin Hub

Local-first AI knowledge base with Obsidian-style vault, FAISS semantic search, MCP plugin hub, and React chat UI.

## One-command local run (Docker)

```bash
git clone https://github.com/bossayan9999/lifeos.git
cd lifeos

# optional: set LLM keys
export OPENAI_API_KEY=sk-...
# or ANTHROPIC_API_KEY=...

docker compose up --build
```

Then open:
- **Chat UI** → http://localhost:5173  
- **API / Swagger** → http://localhost:8000/docs  
- **Health** → http://localhost:8000/health  

Vault data persists in the `lifeos-data` Docker volume.

---

## Manual local run (no Docker)

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

---

## One-click / permanent public deploy

### Option A – Railway (backend) + Vercel (frontend)

1. **Backend on Railway**  
   - Go to https://railway.app/new  
   - Deploy from GitHub → select `bossayan9999/lifeos`  
   - Root directory / Dockerfile: `backend/Dockerfile`  
   - Add env vars: `OPENAI_API_KEY` (optional)  
   - Note the public URL (e.g. `https://lifeos-backend.up.railway.app`)

2. **Frontend on Vercel**  
   - Go to https://vercel.com/new  
   - Import the same repo  
   - Root directory: `frontend`  
   - Build command: `npm run build`  
   - Output: `dist`  
   - Env var: `VITE_API_URL` = your Railway backend URL  
   - Deploy → you get a permanent public URL

### Option B – Render (both services)

1. Go to https://dashboard.render.com/blueprints  
2. New Blueprint → connect repo → select `render.yaml`  
3. After backend is live, set `VITE_API_URL` on the frontend service to the backend URL  
4. Redeploy frontend

### Option C – Fly.io

```bash
# Backend
cd backend
fly launch --config fly.toml
fly secrets set OPENAI_API_KEY=sk-...
fly deploy

# Frontend
cd ../frontend
# Edit fly.toml VITE_API_URL to your backend URL
fly launch --config fly.toml
fly deploy
```

---

## Architecture

| Layer | Implementation |
|-------|----------------|
| Content Sources | Documents / FAQs / Chat Logs → Markdown |
| Obsidian Vault & Local Storage | `backend/data/vault/` + FAISS / SQLite |
| Query Processing & LLM Orchestrator | Local semantic search → A2A → LLM |
| MCP Plugin Hub | obsidian, crm, code_repo, analytics, … |
| Data Cleaner | Deduplicate + archive |
| User Interaction | React chat + sources + feedback |

## MCP Plugins

| Plugin | Category | Status |
|--------|----------|--------|
| **obsidian** | specialized | Live – search / list / read / create / tags |
| **crm** | enterprise | Demo data |
| **code_repo** | specialized | Local + GitHub-ready |
| **analytics** | specialized | Live usage stats |
| project_mgmt / erp / custom_api | – | Stubs |

## Environment

Copy `backend/.env.example` → `backend/.env`:

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
SERPER_API_KEY=
```

## Privacy

Internal data stays local (or in your own Docker volume / cloud account). External calls are read-only and only used when local confidence is low.

## Links

- Code: https://github.com/bossayan9999/lifeos  
- Obsidian vault notes: https://github.com/bossayan9999/obsidian-agent-vault  
