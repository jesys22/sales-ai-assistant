import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio

from sqlalchemy import text

from app.db.session import engine


async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"Connected: {version}")

        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname='vector'")
        )
        vector_ext = result.scalar()
        print(f"pgvector: {vector_ext}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check())
