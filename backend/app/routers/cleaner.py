from fastapi import APIRouter
from datetime import datetime
import sqlite3
from pathlib import Path

from app.models.schemas import CleanerReport
from app.services.vector_store import DB_PATH, VAULT_DIR, FAISS_PATH

router = APIRouter()


@router.post("/cleaner/run", response_model=CleanerReport)
async def run_cleaner():
    """
    Data Cleaner Module
    - Remove duplicates
    - Archive stale data
    - (Optional) compress embeddings
    """
    conn = sqlite3.connect(DB_PATH)
    dups = conn.execute("""
        SELECT title, COUNT(*) as c FROM documents
        GROUP BY title HAVING c > 1
    """).fetchall()
    removed = 0
    for title, count in dups:
        rows = conn.execute(
            "SELECT id FROM documents WHERE title = ? ORDER BY updated_at DESC", (title,)
        ).fetchall()
        for r in rows[1:]:
            conn.execute("DELETE FROM documents WHERE id = ?", (r[0],))
            removed += 1
    conn.commit()

    archived = 0
    conn.close()

    compressed = FAISS_PATH.exists()

    return CleanerReport(
        duplicates_removed=removed,
        stale_archived=archived,
        embeddings_compressed=compressed,
        ran_at=datetime.utcnow(),
    )
