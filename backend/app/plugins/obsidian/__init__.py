"""
Obsidian Vault MCP Plugin
Treats the local vault (or a configured path) as a first-class knowledge source.
Mirrors patterns from Semantic Notes Vault MCP, Obsidian Intelligence, Analogy, etc.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime
import re

from app.services.vector_store import (
    VAULT_DIR,
    DB_PATH,
    semantic_search,
    _upsert_document,
)


def list_notes(limit: int = 50, folder: Optional[str] = None) -> List[Dict[str, Any]]:
    """List notes in the vault (optionally filtered by folder)."""
    notes = []
    base = VAULT_DIR
    if folder:
        base = base / folder
    if not base.exists():
        return []

    for p in sorted(base.rglob("*.md")):
        rel = p.relative_to(VAULT_DIR)
        notes.append({
            "path": str(rel),
            "title": p.stem,
            "size": p.stat().st_size,
            "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
        })
        if len(notes) >= limit:
            break
    return notes


def read_note(path: str) -> Optional[Dict[str, Any]]:
    """Read a single note by relative path."""
    full = VAULT_DIR / path
    if not full.exists() or not full.suffix == ".md":
        full = VAULT_DIR / f"{path}.md" if not path.endswith(".md") else full
    if not full.exists():
        return None
    content = full.read_text(encoding="utf-8", errors="replace")
    return {
        "path": str(full.relative_to(VAULT_DIR)),
        "title": full.stem,
        "content": content,
        "modified": datetime.fromtimestamp(full.stat().st_mtime).isoformat(),
    }


def search_notes(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search over the vault (uses LifeOS FAISS index)."""
    hits = semantic_search(query, top_k=top_k)
    results = []
    for doc, score in hits:
        results.append({
            "id": doc["id"],
            "title": doc["title"],
            "path": doc.get("path", ""),
            "excerpt": doc["content"][:400] + ("..." if len(doc["content"]) > 400 else ""),
            "score": round(score, 4),
            "source_type": doc["source_type"],
        })
    return results


def create_or_update_note(title: str, content: str, folder: str = "") -> Dict[str, Any]:
    """Create or update a Markdown note and re-embed it."""
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(" ", "-")
    rel_path = Path(folder) / f"{safe_title}.md" if folder else Path(f"{safe_title}.md")
    full = VAULT_DIR / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")

    doc_id = f"note-{safe_title.lower()}"
    _upsert_document(doc_id, title, content, "document", str(full))
    return {"path": str(rel_path), "id": doc_id, "status": "written"}


def get_tags() -> Dict[str, int]:
    """Simple tag extraction from frontmatter and #tags."""
    tag_counts: Dict[str, int] = {}
    for p in VAULT_DIR.rglob("*.md"):
        text = p.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---"):
            end = text.find("---", 3)
            if end > 0:
                fm = text[3:end]
                for line in fm.splitlines():
                    if line.strip().startswith("tags:"):
                        tags = re.findall(r'[\w-]+', line.split(":", 1)[1])
                        for t in tags:
                            tag_counts[t] = tag_counts.get(t, 0) + 1
        for m in re.finditer(r'(?<!\w)#([\w-]+)', text):
            t = m.group(1)
            tag_counts[t] = tag_counts.get(t, 0) + 1
    return dict(sorted(tag_counts.items(), key=lambda x: -x[1]))


async def handle(query: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Main entry for the Obsidian MCP plugin.
    Supports natural language routing + structured params.
    """
    params = params or {}
    action = params.get("action", "search")

    if action == "list" or "list notes" in query.lower() or "list files" in query.lower():
        notes = list_notes(limit=params.get("limit", 30), folder=params.get("folder"))
        if not notes:
            return "Vault is empty. Add Markdown files under backend/data/vault/ or use create."
        lines = [f"- **{n['title']}** (`{n['path']}`) — {n['modified'][:10]}" for n in notes]
        return f"Found {len(notes)} notes:\n" + "\n".join(lines)

    if action == "read" or query.lower().startswith("read "):
        path = params.get("path") or query[5:].strip()
        note = read_note(path)
        if not note:
            return f"Note not found: {path}"
        return f"# {note['title']}\n\nPath: {note['path']}\n\n{note['content'][:3000]}"

    if action == "tags" or "tags" in query.lower():
        tags = get_tags()
        if not tags:
            return "No tags found in the vault."
        return "Tag cloud:\n" + "\n".join(f"- #{t}: {c}" for t, c in list(tags.items())[:30])

    if action == "create" or query.lower().startswith("create note"):
        title = params.get("title") or "Untitled"
        content = params.get("content") or query
        result = create_or_update_note(title, content, params.get("folder", ""))
        return f"Note written: {result['path']} (id={result['id']})"

    # Default: semantic search
    results = search_notes(query, top_k=params.get("top_k", 5))
    if not results:
        return f"No relevant notes found for: {query}"
    lines = []
    for r in results:
        lines.append(f"**{r['title']}** (score {r['score']})\n{r['excerpt']}\n")
    return f"Semantic search results for “{query}”:\n\n" + "\n---\n".join(lines)
