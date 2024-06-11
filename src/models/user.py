from bcrypt import gensalt, hashpw
from sqlmodel import SQLModel as Model, Field
from typing import Optional
from pydantic import field_validator


class UserBase(Model):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str


class UserRead(UserBase):
    username: str = Field(min_length=1, max_length=50, primary_key=True)


class User(UserBase, table=True):  # type: ignore
    pass
