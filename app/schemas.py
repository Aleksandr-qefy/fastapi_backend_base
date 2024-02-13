import uuid
from typing import Union

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    nickname: str


class UserCreate(UserBase):
    email: str
    password: str


class UserUnconfirmed(UserBase):
    id: uuid.UUID
    email: str
    hashed_password: str


class User(UserBase):
    id: uuid.UUID
    email: str
    hashed_password: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    nick_or_email: str
    password: str

    class Config:
        from_attributes = True


class UserSettings(UserBase):
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: Union[str, None] = None
    exp: Union[int, None] = None


class OkMsg(BaseModel):
    detail: str = "This msg means, that all is OK"
    msg: str = "OK"

