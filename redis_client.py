#!/usr/bin/env python3
import configparser
import contextlib
from redis.asyncio import Redis
from typing import AsyncGenerator

#чтение конфигурации из config.ini
config = configparser.ConfigParser()
config.read('config.ini')
REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.getint('redis', 'port')
REDIS_DB = config.getint('redis', 'db')

def get_redis_client():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

@contextlib.asynccontextmanager
async def redis_maker() -> AsyncGenerator[Redis, None]:
    redis_client = get_redis_client()
    try:
        yield redis_client
    finally:
        await redis_client.aclose(True)