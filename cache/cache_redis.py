import json
from typing import Any

from fastapi import HTTPException, status
from redis.asyncio import Redis
from starlette.requests import Request
from app.config import settings

def get_redis_client(request: Request) -> Redis:
    return request.app.state.redis_client


class RedisCacheClient:
    def __init__(self, redis: Redis, cache_ttl_seconds: int | None = None):
        self.redis = redis
        self.cache_ttl_seconds = cache_ttl_seconds

    async def set_cache(self, key: str, value: dict) -> Any:
        result = await self.redis.set(
            name=key, value=json.dumps(value), ex=self.cache_ttl_seconds
        )
        return result

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


async def rate_limit_by_ip(
        r: Request,
        redis_client: Redis,
        seconds: int = settings.CACHE_EX_SECONDS,
        limit: int = settings.LIMIT_OF_REQUESTS,
):
    credentials = HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests"
    )
    ip = r.client.host

    key = f"rate_limit:{ip}"

    request = await redis_client.incr(key)

    if request == 1:
        await redis_client.expire(name=key, time=seconds)

    if request > limit:
        raise credentials