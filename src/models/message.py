from sqlmodel import SQLModel as Model, Field
from typing import Optional


class MessageBase(Model):
    message: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    message_id: int
    audio: str
    image: str
    narrator_reply: str


class Message(MessageRead, table=True):
    message_id: Optional[int] = Field(default=None, primary_key=True)
