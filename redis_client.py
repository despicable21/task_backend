import contextlib
from typing import AsyncGenerator
from redis.asyncio import Redis
from settings import settings

def get_redis_client():
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
    )

@contextlib.asynccontextmanager
async def redis_maker() -> AsyncGenerator[Redis, None]:
    redis_client = get_redis_client()
    try:
        yield redis_client
    finally:
        await redis_client.aclose()
