from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

#создание токена из словаря
def _create_token(data: dict):
    to_encode = dict(data)
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

#токен для пользователя
def create_access_token_for_user(username: str):
    return _create_token({"sub": username})

#валидация токена
def validate_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

#получение пользователя из токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = validate_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return username
