from fastapi import APIRouter
from datetime import datetime
import uuid
import sqlite3

from app.models.schemas import FeedbackRequest
from app.services.vector_store import DB_PATH

router = APIRouter()


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """User Interaction & Feedback Loop – log ratings and knowledge gaps"""
    fid = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO feedback (id, query_id, rating, comment, reported_gap, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (fid, req.query_id, req.rating, req.comment, req.reported_gap, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return {"status": "recorded", "feedback_id": fid}


@router.get("/gaps")
async def list_gaps():
    """Report knowledge gaps from feedback"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT reported_gap, COUNT(*) as count FROM feedback WHERE reported_gap IS NOT NULL GROUP BY reported_gap ORDER BY count DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
