from bcrypt import gensalt, hashpw
from sqlmodel import SQLModel as Model, Field, Relationship
from typing import Optional
from pydantic import validator

from src.models.room import Room


class UserBase(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    password: str = Field(min_length=1)


class UserRead(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)

    is_in_room: bool = Field(default=False, nullable=False)
    is_in_game: bool = Field(default=False, nullable=False)
    game_id: Optional[int] = Field(nullable=True, default=None, foreign_key='game.game_id')
    room_id: Optional[int] = Field(nullable=True, default=None, foreign_key='room.room_id')

    # character_id: list[int] = Field(nullable=True, default=None, foreign_key='character.character_id')
    room: Optional['Room'] = Relationship(back_populates='users')
    # game: Optional[Game] = Relationship(back_populates='users')
    # characters: list[Character] = Relationship(back_populates='users')


class User(UserBase, UserRead, table=True):
    @validator('password')
    def hash_password(cls, v: str):
        return hashpw(v.encode(), gensalt()).decode()
