from sqlmodel import SQLModel as Model, Field
from typing import Optional


class MessageBase(Model):
    message: str
    game_id: int = Field(foreign_key='game.game_id')
    username: str = Field(foreign_key='user.username')


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    message_id: int
    audio_path: Optional[str]
    image_path: Optional[str]
    narrator_reply: str


class Message(MessageRead, table=True):
    message_id: Optional[int] = Field(default=None, primary_key=True)
