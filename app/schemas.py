
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- POSTS ----------

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class PostOut(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    votes: int = 0

    model_config = ConfigDict(from_attributes=True)


# ---------- USERS ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- AUTHENTICATION ----------

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# ---------- VOTES ----------

class Vote(BaseModel):
    post_id: int
    dir: int
