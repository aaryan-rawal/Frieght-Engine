
"""Safe asynchronous PostgreSQL connectivity check."""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.db import get_engine


async def main():
    engine = get_engine()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

        print("[OK] PostgreSQL connection succeeded.")
        return 0

    except Exception as exc:
        print(
            f"[ERROR] PostgreSQL connection failed "
            f"({type(exc).__name__}). Check PostgreSQL service "
            "and root .env configuration."
        )
        return 1

    finally:
        await engine.dispose()
        get_engine.cache_clear()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
