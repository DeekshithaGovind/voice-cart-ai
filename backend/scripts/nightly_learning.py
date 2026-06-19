import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.services.learning.nightly import run_nightly_learning


async def main() -> None:
    async with SessionLocal() as db:
        result = await run_nightly_learning(db)
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
