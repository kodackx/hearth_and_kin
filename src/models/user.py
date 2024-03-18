from bcrypt import gensalt, hashpw
from sqlmodel import SQLModel as Model, Field
from typing import Optional
from pydantic import field_validator


class UserBase(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    password: str = Field(min_length=1)


class UserRead(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)


class User(UserBase, UserRead, table=True):  # type: ignore
    @field_validator('password')
    def hash_password(cls, v: str):
        return hashpw(v.encode(), gensalt()).decode()
