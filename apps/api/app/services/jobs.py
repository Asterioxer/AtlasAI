import json
from collections.abc import Awaitable, Callable
from redis.asyncio import Redis

JobHandler = Callable[[dict], Awaitable[None]]

class JobQueue:
    def __init__(self, url: str, queue_name: str = "atlasai:jobs"):
        self.redis = Redis.from_url(url, decode_responses=True)
        self.queue_name = queue_name

    async def enqueue(self, job: dict) -> None:
        await self.redis.rpush(self.queue_name, json.dumps(job, default=str))

    async def run_forever(self, handlers: dict[str, JobHandler]) -> None:
        while True:
            item = await self.redis.blpop(self.queue_name, timeout=5)
            if not item:
                continue
            _, raw = item
            job = json.loads(raw)
            handler = handlers.get(job.get("type"))
            if handler:
                await handler(job)
            else:
                await self.redis.rpush("atlasai:dead-letter", raw)

    async def close(self) -> None:
        await self.redis.aclose()
