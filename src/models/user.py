from sqlmodel import SQLModel as Model, Field
from typing import Optional


class UserCreate(Model):
    username: str = Field(min_length=1, max_length=50, primary_key=True)
    password: str = Field(min_length=1)

    # @validator('password')
    # def hash_password(cls, v):
    #    assert len(v) > 0, 'Password can\t be empty'
    #    if v[:8] == '__hash__':  # Avoid double-hashing when creating a User()
    #        return v
    #    return '__hash__' + hashpw(v.encode('utf-8'), gensalt()).decode('utf-8')


class UserLogin(UserCreate):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class User(UserCreate, table=True):
    is_in_room: bool = Field(default=False, nullable=False)
    is_in_game: bool = Field(default=False, nullable=False)
    game_id: Optional[int] = Field(nullable=True, default=None, foreign_key='game.game_id')
    room_id: Optional[int] = Field(nullable=True, default=None, foreign_key='room.room_id')
    # character_id: list[int] = Field(nullable=True, default=None, foreign_key='character.character_id')
    # room: Optional[Room] = Relationship(back_populates='users')
    # game: Optional[Game] = Relationship(back_populates='users')
    # characters: list[Character] = Relationship(back_populates='users')
