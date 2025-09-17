#!/usr/bin/env python3
import asyncio

async def read_from_redis(redis, username: str):
    key = f"{username}:data"
    data = await redis.get(key)
    if data:
        return data
    channel = f"{username}:channel"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=120)
        return message["data"] if message else None
    finally:
        await pubsub.close()

async def write_to_redis(redis, username: str, data: str):
    key = f"{username}:data"
    channel = f"{username}:channel"
    await redis.setex(key, 60, data)
    await redis.publish(channel, data)