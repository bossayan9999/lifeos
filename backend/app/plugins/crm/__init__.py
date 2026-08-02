"""
CRM MCP Plugin – Bridge to business tools
Stub with realistic structure; replace the data layer with HubSpot / Salesforce / etc.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import random

_CONTACTS = [
    {"id": "c1", "name": "Alice Chen", "email": "alice@acme.com", "stage": "Customer", "value": 48000, "last_touch": "2026-07-28"},
    {"id": "c2", "name": "Bob Rivera", "email": "bob@startup.io", "stage": "Prospect", "value": 12000, "last_touch": "2026-07-30"},
    {"id": "c3", "name": "Carol Nguyen", "email": "carol@bigco.com", "stage": "Negotiation", "value": 95000, "last_touch": "2026-08-01"},
    {"id": "c4", "name": "David Okonkwo", "email": "david@labs.dev", "stage": "Lead", "value": 0, "last_touch": "2026-07-15"},
]


async def handle(query: str, params: Optional[Dict[str, Any]] = None) -> str:
    params = params or {}
    q = query.lower()

    if "pipeline" in q or "deals" in q or "forecast" in q:
        total = sum(c["value"] for c in _CONTACTS if c["stage"] in ("Customer", "Negotiation"))
        return (
            f"[CRM Pipeline]\n"
            f"Open pipeline value: ${total:,}\n"
            f"- Customers: {sum(1 for c in _CONTACTS if c['stage']=='Customer')}\n"
            f"- Negotiation: {sum(1 for c in _CONTACTS if c['stage']=='Negotiation')}\n"
            f"- Prospects: {sum(1 for c in _CONTACTS if c['stage']=='Prospect')}\n"
            f"- Leads: {sum(1 for c in _CONTACTS if c['stage']=='Lead')}"
        )

    if "contact" in q or "who" in q or "find" in q:
        matches = [c for c in _CONTACTS if any(term in c["name"].lower() or term in c["email"].lower() for term in q.split())]
        if not matches:
            matches = _CONTACTS
        lines = [f"- **{c['name']}** ({c['stage']}) – {c['email']} – ${c['value']:,} – last touch {c['last_touch']}" for c in matches]
        return "[CRM Contacts]\n" + "\n".join(lines)

    return (
        f"[CRM] Query: {query}\n"
        f"Demo contacts loaded: {len(_CONTACTS)}. "
        "Try: “show pipeline”, “find Alice”, “list contacts”."
    )
