#!/usr/bin/env python3
"""
Standalone Data Cleaner job (run weekly via cron or manually)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.routers.cleaner import run_cleaner
import asyncio


async def main():
    report = await run_cleaner()
    print("=== LifeOS Data Cleaner Report ===")
    print(f"Duplicates removed : {report.duplicates_removed}")
    print(f"Stale archived     : {report.stale_archived}")
    print(f"Embeddings OK      : {report.embeddings_compressed}")
    print(f"Ran at             : {report.ran_at.isoformat()}")


if __name__ == "__main__":
    asyncio.run(main())
