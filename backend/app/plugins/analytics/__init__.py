"""
Analytics MCP Plugin
Surfaces LifeOS usage metrics + simple vault stats.
"""
from typing import Optional, Dict, Any
import sqlite3
from pathlib import Path
from app.services.vector_store import DB_PATH, VAULT_DIR


async def handle(query: str, params: Optional[Dict[str, Any]] = None) -> str:
    q = query.lower()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    total_queries = conn.execute("SELECT COUNT(*) as c FROM query_log").fetchone()["c"]
    web_queries = conn.execute("SELECT COUNT(*) as c FROM query_log WHERE used_web = 1").fetchone()["c"]
    plugin_queries = conn.execute("SELECT COUNT(*) as c FROM query_log WHERE used_plugin IS NOT NULL").fetchone()["c"]
    avg_conf = conn.execute("SELECT AVG(confidence) as a FROM query_log").fetchone()["a"] or 0

    feedback_count = conn.execute("SELECT COUNT(*) as c FROM feedback").fetchone()["c"]
    gaps = conn.execute(
        "SELECT reported_gap, COUNT(*) as c FROM feedback WHERE reported_gap IS NOT NULL GROUP BY reported_gap ORDER BY c DESC LIMIT 5"
    ).fetchall()

    note_count = len(list(VAULT_DIR.rglob("*.md"))) if VAULT_DIR.exists() else 0
    doc_count = conn.execute("SELECT COUNT(*) as c FROM documents").fetchone()["c"]

    conn.close()

    local_hit_rate = 0.0
    if total_queries > 0:
        local_hit_rate = 1 - (web_queries / total_queries)

    report = [
        "[Analytics – LifeOS]",
        f"Total queries logged     : {total_queries}",
        f"Local hit rate           : {local_hit_rate:.1%}",
        f"Web fallback usage       : {web_queries}",
        f"Plugin invocations       : {plugin_queries}",
        f"Avg confidence           : {avg_conf:.3f}",
        f"Feedback entries         : {feedback_count}",
        f"Vault notes (.md)        : {note_count}",
        f"Indexed documents        : {doc_count}",
    ]

    if gaps:
        report.append("\nTop reported knowledge gaps:")
        for g in gaps:
            report.append(f"  - {g['reported_gap']} ({g['c']}×)")

    if "vault" in q or "notes" in q:
        report.append(f"\nVault path: {VAULT_DIR}")

    return "\n".join(report)
