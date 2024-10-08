from sqlmodel import SQLModel as Model, Field
from typing import Optional
import random
import string
import uuid
from ..core.config import DEFAULT_TEXT_NARRATOR_MODEL, DEFAULT_AUDIO_NARRATOR_MODEL, DEFAULT_IMAGE_MODEL
from .enums import AudioModel, ImageModel, TextModel

def generate_invite_code(length=5):
    invite_code =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    print('[CODEGEN]: Generated the following invite code: ', invite_code)
    return invite_code
    

class Invite(Model, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    story_id: int = Field(foreign_key="story.story_id")  # Updated line
    invite_code: str = Field(default_factory=generate_invite_code)

class StoryBase(Model):
    story_id: Optional[int] = Field(default=None, primary_key=True)
    party_lead: int = Field(foreign_key="character.character_id")
    join_code: Optional[str] = Field(default=None, foreign_key="invite.invite_code")
    thread_id: Optional[int] = None
    party_member_1: Optional[int] = Field(default=None, foreign_key="character.character_id")
    party_member_2: Optional[int] = Field(default=None, foreign_key="character.character_id")
    has_started: Optional[bool] = Field(default=False)
    party_location: Optional[str] = None
    party_objective: Optional[str] = None
    genai_text_model: TextModel = Field(default=DEFAULT_TEXT_NARRATOR_MODEL)
    genai_audio_model: AudioModel = Field(default=DEFAULT_AUDIO_NARRATOR_MODEL)
    genai_image_model: ImageModel = Field(default=DEFAULT_IMAGE_MODEL)

class StoryModelsUpdate(Model):
    character_id: int = Field(foreign_key="character.character_id")
    genai_text_model: Optional[TextModel] = Field(default=DEFAULT_TEXT_NARRATOR_MODEL)
    genai_audio_model: Optional[AudioModel] = Field(default=DEFAULT_AUDIO_NARRATOR_MODEL)
    genai_image_model: Optional[ImageModel] = Field(default=DEFAULT_IMAGE_MODEL)


class StoryCreate(Model):
    party_lead: int = Field(foreign_key='character.character_id')


class StoryJoin(Model):
    story_id: int
    character_id: int = Field(foreign_key='character.character_id')


class StoryDelete(StoryJoin):
    pass


class StoryRead(StoryBase):
    pass


class Story(StoryBase, table=True):  # type: ignore
    pass

class StoryTransferOwnership(Model):
    story_id: int
    current_lead_id: int
    new_lead_id: int
