from sqlmodel import SQLModel as Model, Field
from sqlmodel import Relationship
from typing import Optional


class StoryBase(Model):
    story_id: int = Field(nullable=False, primary_key=True)


class StoryCreate(StoryBase):
    creator: int = Field(foreign_key='character.character_id')


class StoryJoin(StoryBase):
    character_id: int = Field(foreign_key='character.character_id')


class StoryDelete(StoryJoin):
    pass


class StoryRead(StoryCreate):
    active: bool = Field(default=False)


class Story(StoryRead, table=True):  # type: ignore
    pass
