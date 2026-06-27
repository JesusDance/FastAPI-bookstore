import json

from redis.asyncio import Redis
from starlette.requests import Request


def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client


class RedisCacheClient:
    def __init__(self, redis: Redis, cache_ttl_seconds: int | None = None):
        self.redis = redis
        self.cache_ttl_seconds = cache_ttl_seconds

    async def set_cache(self, key: str, value: dict) -> None:
        await self.redis.set(name=key, value=json.dumps(value), ex=self.cache_ttl_seconds)


    async def get(self, key: str):
        value = await self.redis.get(key)
        if value is None:
            return None
        return json.loads(value)


    async def delete(self, key: str) -> None:
        await self.redis.delete(key)


    async def delete_by_pattern(self, pattern: str) -> None:
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)