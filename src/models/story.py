from sqlmodel import SQLModel as Model, Field


class StoryBase(Model):
    story_id: int = Field(nullable=False, primary_key=True)


class StoryJoin(StoryBase):
    username: str = Field(foreign_key='user.username')


class StoryCreate(StoryBase):
    creator: str = Field(foreign_key='user.username')


class StoryDelete(StoryJoin):
    pass


class StoryRead(StoryCreate):
    active: bool = Field(default=False)


class Story(StoryRead, table=True):
    pass
