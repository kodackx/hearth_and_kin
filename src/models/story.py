from sqlmodel import SQLModel as Model, Field
from typing import Optional
from sqlmodel import SQLModel, Field
import random
import string
import uuid

def generate_invite_code(length=5):
    invite_code =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    print('[CODEGEN]: Generated the following invite code: ', invite_code)
    return invite_code
    

class Invite(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    story_id: int
    invite_code: str = Field(default_factory=generate_invite_code)

class StoryBase(Model):
    story_id: Optional[int] = Field(default=None, primary_key=True)
    party_lead: int = Field(foreign_key="character.character_id")
    join_code: Optional[str]
    thread_id: Optional[int]
    party_member_1: Optional[int] = Field(foreign_key="character.character_id")
    party_member_2: Optional[int] = Field(foreign_key="character.character_id")
    has_started: Optional[bool] = Field(default=False)
    party_location: Optional[str]
    party_objective: Optional[str]
    genai_text_model: str = Field(default="nvidia")
    genai_audio_model: str = Field(default="elevenlabs")
    genai_image_model: str = Field(default="dalle3")

class StoryModelsUpdate(Model):
    character_id: int = Field(foreign_key="character.character_id")
    genai_text_model: Optional[str] = Field(default="nvidia")
    genai_audio_model: Optional[str] = Field(default="elevenlabs")
    genai_image_model: Optional[str] = Field(default="dalle3")


class StoryCreate(Model):
    party_lead: int = Field(foreign_key='character.character_id')


class StoryJoin(Model):
    story_id: int
    character_id: int = Field(foreign_key='character.character_id')


class StoryDelete(Model):
    character_id: int = Field(foreign_key='character.character_id')
    story_id: int


class StoryRead(Model):
    story_id: int
    has_started: bool = Field(default=False)
    party_lead: int
    party_member_1: Optional[int] = Field(default=None)
    party_member_2: Optional[int] = Field(default=None)
    genai_text_model: str = Field(default="nvidia")
    genai_audio_model: str = Field(default="elevenlabs")
    genai_image_model: str = Field(default="dalle3")


class Story(StoryBase, table=True):  # type: ignore
    pass

class StoryTransferOwnership(Model):
    story_id: int
    current_lead_id: int
    new_lead_id: int
