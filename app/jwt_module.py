from typing import Union
from datetime import datetime, timedelta
from jose import jwt, exceptions
from fastapi import status, HTTPException

import config
import schemas
import crud

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                             config.JWT_SECRET_KEY,
                             algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def get_user_by_token(db, token: str) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        token_data = schemas.TokenData(**payload)
    except exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except exceptions.JWTError:
        raise credentials_exception

    if token_data.sub is None or token_data.exp is None:
        raise credentials_exception

    user = crud.get_user(db, user_id=token_data.sub)
    if user is None:
        raise credentials_exception
    return user


def get_token_by_user(user: schemas.User) -> schemas.Token:
    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")
