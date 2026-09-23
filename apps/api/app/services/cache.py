import hashlib
import json

from redis.asyncio import Redis

class Cache:
    def __init__(self, url: str):
        self.redis = Redis.from_url(url, decode_responses=True)

    @staticmethod
    def key(namespace: str, payload: object) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str).encode()
        return f"atlasai:{namespace}:{hashlib.sha256(raw).hexdigest()}"

    async def get_json(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set_json(self, key: str, value: object, ttl: int = 60) -> None:
        await self.redis.set(key, json.dumps(value, default=str), ex=ttl)

    async def close(self) -> None:
        await self.redis.aclose()
