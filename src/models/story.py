from sqlmodel import SQLModel as Model, Field


class StoryBase(Model):
    story_id: int = Field(nullable=False, primary_key=True)

class StoryCreate(StoryBase):
    creator: str = Field(foreign_key='user.username')

class StoryJoin(StoryBase):
    username: str = Field(foreign_key='user.username')

class StoryDelete(StoryBase):
    username: str = Field(foreign_key='user.username')

class StoryRead(StoryCreate):
    active: bool = Field(default=False)

class Story(StoryCreate, table=True):  # type: ignore
    active: bool = Field(default=False)
