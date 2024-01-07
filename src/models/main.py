from sqlmodel import SQLModel as Model, Field


class NewStoryRequest(Model):
    keywords: str = Field(min_length=0, max_length=5000)


class MessageRequest(Model):
    message: str = Field(min_length=0, max_length=5000)
