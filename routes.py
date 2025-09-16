from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from redis_client import get_redis
from auth import create_access_token, get_current_user
import asyncio

#маршрут
router = APIRouter()

#модель для данных /write
class WriteData(BaseModel):
    data: str

#модель для /login
class User(BaseModel):
    username: str

#для получения токена
@router.post("/login")
async def login(user: User):
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

#для записи данных в Redis
@router.post("/write")
async def write_data(data: WriteData, username: str = Depends(get_current_user)):
    redis = await get_redis()
    await redis.setex(f"{username}:data", 60, data.data)
    await redis.publish(f"{username}:channel", data.data)
    return {"status": "written"}

#для чтения данных из Redis
@router.get("/read")
async def read_data(username: str = Depends(get_current_user)):
    redis = await get_redis()
    #проверяем ключ
    data = await redis.get(f"{username}:data")
    if data:
        return {"data": data}
    #если ключа нет, ждём сообщение в канале
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{username}:channel")
    try:
        async with asyncio.timeout(120):
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                return {"data": message["data"]}
            return {"data": None}
    except asyncio.TimeoutError:
        return {"data": None}
    finally:
        await pubsub.close()

#для longpoll
@router.get("/longpoll")
async def longpoll(username: str = Depends(get_current_user)):
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{username}:channel")
    try:
        async with asyncio.timeout(120):
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    return {"data": message["data"]}
        return {"data": None}
    except asyncio.TimeoutError:
        return {"data": None}
    finally:
        await pubsub.close()