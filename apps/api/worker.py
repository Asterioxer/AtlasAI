import asyncio
import os
from app.services.jobs import run_worker

async def handle_ingestion(job: dict) -> None:
    print(f"processing ingestion job: {job.get('id', 'unknown')}", flush=True)

if __name__ == "__main__":
    asyncio.run(run_worker(os.getenv("REDIS_URL", "redis://localhost:6379/0"), {"ingestion": handle_ingestion}))
