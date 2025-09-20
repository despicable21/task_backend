from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional
from auth import create_access_token_for_user, get_current_user
from redis_client import redis_maker
from redis_logic import write_to_redis, read_immediate, longpoll
from settings import settings

router = APIRouter()

#модели
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class WriteRequest(BaseModel):
    data: str = Field(..., min_length=1, description="Task data cannot be empty")  #обязательное, иначе выкинет ошибку

class WriteResponse(BaseModel):
    status: str = "written"
    data: str

class ReadResponse(BaseModel):
    status: str = "ok"
    data: str

class ErrorResponse(BaseModel):
    detail: str

#для получения токена
@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    token = create_access_token_for_user(form_data.username)
    return TokenResponse(access_token=token)

#для записи данных в редис
@router.post("/write", response_model=WriteResponse, status_code=200)
async def write(data: WriteRequest, username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as r:
        await write_to_redis(r, username, data.data)  #в redis_logic
        return WriteResponse(status="written", data=data.data)

#для чтения данных из редис
@router.get("/read", response_model=ReadResponse, status_code=200, responses={408: {"model": ErrorResponse}})
async def read(username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as r:
        try:
            data = await read_immediate(r, username)  #в redis_logic
            return ReadResponse(status="ok", data=data)
        except HTTPException as e:
            raise e


#с ожиданием
@router.get("/longpoll", response_model=ReadResponse, status_code=200, responses={408: {"model": ErrorResponse}})
async def longpoll_endpoint(username: str = Depends(get_current_user), redis=Depends(redis_maker)):
    async with redis as r:
        data = await longpoll(r, username, timeout=settings.LONGPOLL_TIMEOUT)  #в redis_logic
        return ReadResponse(status="ok", data=data)


