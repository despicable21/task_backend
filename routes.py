#!/usr/bin/env python3
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from redis_client import redis_maker
from redis_logic import write_to_redis, read_from_redis
from auth import create_access_token_for_user, get_current_user



router = APIRouter()

#модель для /write
class WriteData(BaseModel):
    data: str

#модель ответа
class ResponseData(BaseModel):
    status: str = "written"
    data: str | None = None
    access_token: str | None = None
    token_type: str | None = None

#для получения токена
@router.post("/login", response_model=ResponseData, status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = create_access_token_for_user(form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

#для записи данных в редис
@router.post("/write", response_model=ResponseData, status_code=200)
async def write_data(data: WriteData, username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as redis_client:
        await write_to_redis(redis_client, username, data.data)
        return ResponseData(status="written", data=data.data)

#для чтения данных из редис
@router.get("/read", response_model=ResponseData, status_code=200)
async def read_data(username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as redis_client:
        data = await read_from_redis(redis_client, username)
        if data is None:
            raise HTTPException(status_code=408, detail="Request Timeout")
        return {"data": data}


@router.get("/longpoll", response_model=ResponseData, status_code=200)
async def longpoll(username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as redis_client:
        data = await read_from_redis(redis_client, username)
        if data is None:
            raise HTTPException(status_code=408, detail="Request Timeout")
        return {"data": data}