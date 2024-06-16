from sqlmodel import SQLModel as Model, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class CharacterType(str, Enum):
    PC = "PC"
    NARRATOR = "NARRATOR"
    SYSTEM = "SYSTEM"

class MessageBase(Model):
    message_id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    story_id: int = Field(foreign_key="story.story_id")
    character: CharacterType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    soundtrack_path: Optional[str] = Field(default=None)
    audio_path: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)
    character_id: Optional[int] = Field(default=None, foreign_key="character.character_id")
    character_name: str = Field(foreign_key='character.character_name')
    
class MessageCreate(MessageBase):
    pass


class MessagePC(MessageBase):
    message_id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    story_id: int
    character: CharacterType
    character_id: int
    character_name: str
    portrait_path: str

    text_image_model: str | None = None
    image_model: str | None = None
    text_narrator_model: str | None = None

class MessageNARRATORorSYSTEM(MessageBase):
    message_id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    character: CharacterType
    audio_path: Optional[str]
    image_path: Optional[str]
    soundtrack_path: Optional[str]

class MessageRead(Model):
    message: str
    character: str
    character_name: str
    audio_path: Optional[str]
    image_path: Optional[str]
    
class Message(MessageBase, table=True):  # type: ignore
    pass
