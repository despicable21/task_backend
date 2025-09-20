from redis.asyncio.client import PubSub
from fastapi import HTTPException
from typing import Optional
from settings import settings
import asyncio

KEY_TTL = 60  

async def write_to_redis(redis, username: str, data: str):
    key = f"{username}:data"
    channel = f"{username}:channel"
    await redis.setex(key, KEY_TTL, data)
    await redis.publish(channel, data)

async def _get_and_delete_key(redis, username: str):  #чтобы следующий read не возвращал ту же задачу
    key = f"{username}:data"

    try:
        data = await redis.execute_command("GETDEL", key)
        if data is None:
            return None
        return data
    except Exception:
        async with redis.pipeline() as pipe:
            await pipe.get(key)
            await pipe.delete(key)
            res = await pipe.execute()
            return res[0]  

async def read_immediate(redis, username: str) -> str:
    data = await _get_and_delete_key(redis, username)
    if data is None:
        raise HTTPException(status_code=408, detail="No data available")
    return data

async def longpoll(redis, username: str, timeout: int = None):
    if timeout is None:
        timeout = settings.LONGPOLL_TIMEOUT  #берем таймаут из settings

    data = await _get_and_delete_key(redis, username)
    if data is not None:  #проверяем, есть ли уже данные для пользователя
        return data

    channel = f"{username}:channel"
    pubsub: PubSub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        #между первой проверкой ключа и подпиской на канал другой процесс может записать задачу
        data = await _get_and_delete_key(redis, username)
        if data is not None:
            return data

        end_ts = asyncio.get_event_loop().time() + timeout  #время окончания ожидания
        while True:
            remaining = end_ts - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise HTTPException(status_code=408, detail="Timeout waiting for data")

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout= min(1.0, remaining))
            if message:
                payload = message.get("data")
                if payload is None:
                    await asyncio.sleep(0.05)  #если пустое, ждем и продолжаем цикл
                    continue
                
                data = await _get_and_delete_key(redis, username)
                #после публикации снова пробуем прочитать ключ
                if data is not None:
                    return data
                
                return payload
           
    finally:
        try:
            await pubsub.unsubscribe(channel)
        except Exception:
            pass
        try:
            await pubsub.close()
        except Exception:
            pass
