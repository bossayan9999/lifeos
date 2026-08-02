"""
Local Vector Database (FAISS + SQLite metadata)
Matches: Obsidian Vault & Local Storage layer
"""
import os
import json
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
VAULT_DIR = DATA_DIR / "vault"
DB_PATH = DATA_DIR / "lifeos.db"
FAISS_PATH = DATA_DIR / "faiss.index"
EMBED_DIM = 384  # all-MiniLM-L6-v2

# Lazy load heavy deps
_index = None
_model = None


def init_vector_store():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VAULT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            source_type TEXT,
            path TEXT,
            created_at TEXT,
            updated_at TEXT,
            embedding_id INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id TEXT PRIMARY KEY,
            query TEXT,
            answer TEXT,
            confidence REAL,
            used_web INTEGER,
            used_plugin TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            query_id TEXT,
            rating INTEGER,
            comment TEXT,
            reported_gap TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

    # Seed sample knowledge if empty
    if not any(VAULT_DIR.iterdir()):
        _seed_sample_vault()


def _seed_sample_vault():
    samples = [
        {
            "id": "doc-001",
            "title": "LifeOS Architecture Overview",
            "content": "LifeOS is a local-first AI Knowledge Base. Content Sources (Documents, FAQs, Chat Logs) are collected and chunked, stored in Obsidian Vault with FAISS/SQLite vector DB. Query Processing uses Local Retrieval first, then A2A Web Search, then LLM. MCP Plugin Hub extends to CRM, ERP, Code Repo, Analytics.",
            "source_type": "document",
        },
        {
            "id": "faq-001",
            "title": "When does LifeOS call external APIs?",
            "content": "External A2A / Google connectors are used only when local semantic search confidence is below threshold or explicitly requested. All external calls are read-only. Internal data never leaves the vault.",
            "source_type": "faq",
        },
        {
            "id": "doc-002",
            "title": "Data Cleaner Module",
            "content": "The Data Cleaner runs weekly (or on demand). It removes duplicate notes, archives stale data older than retention policy, and optionally compresses embeddings to save disk.",
            "source_type": "document",
        },
    ]
    for s in samples:
        path = VAULT_DIR / f"{s['id']}.md"
        path.write_text(f"# {s['title']}\n\n{s['content']}\n")
        _upsert_document(s["id"], s["title"], s["content"], s["source_type"], str(path))


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_index():
    global _index
    if _index is None:
        import faiss
        if FAISS_PATH.exists():
            _index = faiss.read_index(str(FAISS_PATH))
        else:
            _index = faiss.IndexFlatIP(EMBED_DIM)
    return _index


def _upsert_document(doc_id: str, title: str, content: str, source_type: str, path: str):
    model = _get_model()
    emb = model.encode([content], normalize_embeddings=True)[0].astype("float32")
    index = _get_index()
    emb_id = index.ntotal
    index.add(np.array([emb]))
    import faiss
    faiss.write_index(index, str(FAISS_PATH))

    from datetime import datetime
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO documents
           (id, title, content, source_type, path, created_at, updated_at, embedding_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (doc_id, title, content, source_type, path, now, now, emb_id),
    )
    conn.commit()
    conn.close()


def semantic_search(query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
    """Local semantic search – primary retrieval path."""
    model = _get_model()
    q_emb = model.encode([query], normalize_embeddings=True).astype("float32")
    index = _get_index()

    if index.ntotal == 0:
        return []

    scores, ids = index.search(q_emb, min(top_k, index.ntotal))
    results = []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    for score, emb_id in zip(scores[0], ids[0]):
        if emb_id < 0:
            continue
        row = conn.execute(
            "SELECT * FROM documents WHERE embedding_id = ?", (int(emb_id),)
        ).fetchone()
        if row:
            results.append((dict(row), float(score)))
    conn.close()
    return results
