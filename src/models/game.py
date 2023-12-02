from sqlmodel import SQLModel as Model, Field
from typing import Optional


class GameBase(Model):
    room_id: int = Field(foreign_key='room.room_id')


class GameCreate(Model):
    description: Optional[str]


class GameRead(GameBase):
    game_id: int


class Game(GameCreate, table=True):
    game_id: int = Field(default=None, primary_key=True)
    # users: list['User'] = Relationship(back_populates = 'game')
