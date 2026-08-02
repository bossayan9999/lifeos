"""
Query Processing & LLM Orchestrator
Local Retrieval → (optional) A2A Web → LLM → Answer + Citations
"""
import os
import time
import uuid
from datetime import datetime
from typing import Optional

from app.models.schemas import QueryRequest, QueryResponse, Citation, SourceType
from app.services.vector_store import semantic_search, DB_PATH
import sqlite3


CONFIDENCE_THRESHOLD = 0.55  # below this → consider web / LLM more heavily


async def process_query(req: QueryRequest) -> QueryResponse:
    start = time.time()
    citations: list[Citation] = []
    used_web = False
    used_plugin = None
    local_hits = semantic_search(req.query, top_k=req.top_k)

    for doc, score in local_hits:
        citations.append(
            Citation(
                source_id=doc["id"],
                title=doc["title"],
                excerpt=doc["content"][:300] + ("..." if len(doc["content"]) > 300 else ""),
                score=round(score, 4),
                source_type=SourceType(doc["source_type"]),
            )
        )

    best_score = max((c.score for c in citations), default=0.0)
    need_external = req.use_web or best_score < CONFIDENCE_THRESHOLD

    context = "\n\n".join(
        f"[{c.title}] (score={c.score}): {c.excerpt}" for c in citations
    )

    if req.plugin:
        from app.plugins.hub import call_plugin
        plugin_result = await call_plugin(req.plugin, req.query)
        used_plugin = req.plugin
        context += f"\n\n[Plugin:{req.plugin}]: {plugin_result}"

    if need_external and not req.plugin:
        web_snippet = await _a2a_web_search(req.query)
        if web_snippet:
            used_web = True
            citations.append(
                Citation(
                    source_id="web-" + str(uuid.uuid4())[:8],
                    title="Web Search Result",
                    excerpt=web_snippet[:300],
                    score=0.5,
                    source_type=SourceType.WEB,
                )
            )
            context += f"\n\n[Web]: {web_snippet}"

    answer = await _generate_answer(req.query, context, best_score)

    query_id = str(uuid.uuid4())
    _log_query(query_id, req.query, answer, best_score, used_web, used_plugin)

    elapsed = int((time.time() - start) * 1000)
    return QueryResponse(
        answer=answer,
        citations=citations,
        confidence=round(best_score, 4),
        used_web=used_web,
        used_plugin=used_plugin,
        processing_ms=elapsed,
    )


async def _a2a_web_search(query: str) -> Optional[str]:
    """Stub for A2A / Google API. Returns None if no key configured."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("SERPER_API_KEY")
    if not api_key:
        return (
            "Web search not configured (set GOOGLE_API_KEY or SERPER_API_KEY). "
            "Local results only."
        )
    return f"[Stub] Web results for: {query}"


async def _generate_answer(query: str, context: str, confidence: float) -> str:
    """Call configured LLM. Falls back to extractive answer if no key."""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    system = (
        "You are LifeOS, a local-first knowledge assistant. "
        "Answer using ONLY the provided context. "
        "Cite sources by title. If context is insufficient, say so clearly. "
        "Be concise and accurate."
    )
    user_msg = f"Context:\n{context}\n\nQuestion: {query}"

    if openai_key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_key)
        resp = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
            max_tokens=800,
        )
        return resp.choices[0].message.content or "No answer generated."

    if anthropic_key:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=anthropic_key)
        resp = await client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=800,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return resp.content[0].text

    if context.strip():
        return (
            f"(Local extractive mode – set OPENAI_API_KEY or ANTHROPIC_API_KEY for full LLM)\n\n"
            f"Based on available knowledge (confidence {confidence:.2f}):\n\n{context[:1200]}"
        )
    return "No relevant local knowledge found and no external LLM configured."


def _log_query(qid: str, query: str, answer: str, conf: float, web: bool, plugin: Optional[str]):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO query_log (id, query, answer, confidence, used_web, used_plugin, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (qid, query, answer, conf, int(web), plugin, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
