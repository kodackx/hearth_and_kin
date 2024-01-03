from bcrypt import gensalt, hashpw
from sqlmodel import SQLModel as Model, Field
from typing import Optional
from pydantic import validator


class UserBase(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    password: str = Field(min_length=1)


class UserRead(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    # character_id: list[int] = Field(nullable=True, default=None, foreign_key='character.character_id')
    story_id: Optional[int] = Field(default=None, foreign_key='story.story_id')
    # story_id: Optional[int] = Relationship(back_populates='users')
    # story: Optional[Story] = Relationship(back_populates='users')
    # characters: list[Character] = Relationship(back_populates='users')


class User(UserBase, UserRead, table=True):
    @validator('password')
    def hash_password(cls, v: str):
        return hashpw(v.encode(), gensalt()).decode()
