from sqlmodel import SQLModel as Model, Field
from sqlmodel import Relationship
from typing import Optional


class StoryBase(Model):
    story_id: int = Field(nullable=False, primary_key=True)


class StoryJoin(StoryBase):
    username: str = Field(foreign_key='user.username')
    character_id: int = Field(foreign_key='character.character_id')


class StoryCreate(StoryBase):
    creator: str = Field(foreign_key='user.username')


# story delete should not be based on storyJoin. instead, based on storyBase
# hoping this fixes the tests
class StoryDelete(StoryBase):
    username: str = Field(foreign_key='user.username')
    pass


class StoryRead(StoryCreate):
    active: bool = Field(default=False)


class Story(StoryBase, table=True):  # type: ignore
    # story_id: int = Field(primary_key=True)
    active: bool = Field(default=False)
    creator: str = Field(foreign_key='user.username')
    character_id: Optional[int] = Field(default=None, foreign_key="character.character_id")
    # character: "Character" = Relationship(back_populates="story", foreign_keys=[character_id])
