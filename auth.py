#!/usr/bin/env python3
import configparser
import secrets
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone

#чтение конфигурации из config.ini
config = configparser.ConfigParser()
config.read('config.ini')
SECRET_KEY = config.get('jwt', 'secret_key', fallback=secrets.token_urlsafe(32))
ALGORITHM = config.get('jwt', 'algorithm')
ACCESS_TOKEN_EXPIRE_MINUTES = config.getint('jwt', 'expire_minutes')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#создание токена из словаря
def _create_token(data: dict):
    to_encode = dict(data)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#токен для пользователя
def create_access_token_for_user(username: str):
    return _create_token({"sub": username})

#валидация токена
def validate_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

#получение пользователя из токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = validate_token(token)
    username = payload["sub"]
    return username