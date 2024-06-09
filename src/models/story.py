from sqlmodel import SQLModel as Model, Field
from typing import Optional


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


class StoryCreate(StoryBase):
    party_lead: int = Field(foreign_key='character.character_id')


class StoryJoin(StoryBase):
    character_id: int = Field(foreign_key='character.character_id')


class StoryDelete(StoryJoin):
    character_id: int = Field(foreign_key='character.character_id')


class StoryRead(StoryCreate):
    has_started: bool = Field(default=False)


class Story(StoryRead, table=True):  # type: ignore
    pass

class StoryTransferOwnership(Model):
    story_id: int
    current_lead_id: int
    new_lead_id: int
