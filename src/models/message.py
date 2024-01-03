from sqlmodel import SQLModel as Model, Field
from typing import Optional
from datetime import datetime


class MessageBase(Model):
    message: str
    story_id: int = Field(foreign_key='story.story_id')
    username: str = Field(foreign_key='user.username')
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    message_id: Optional[int] = Field(default=None, primary_key=True)
    audio_path: Optional[str]
    image_path: Optional[str]
    narrator_reply: str


class Message(MessageRead, table=True):
    pass
