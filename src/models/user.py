from sqlmodel import SQLModel as Model, Field
from typing import Optional


class UserBase(Model):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(min_length=1, max_length=50, index=True)
    password: str = Field(min_length=1)


class UserRead(UserBase):
    username: str = Field(min_length=1, max_length=50, primary_key=True)


class User(UserBase, table=True):  # type: ignore
    pass
