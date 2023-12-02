from typing import Optional

from sqlmodel import SQLModel as Model, Field

class Hero(Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None

class User(Model):
    username: str
    password: str

class CreateGameRequest(Model):
    room_id: str

class NewStoryRequest(Model):
    keywords: str

class MessageRequest(Model):
    message: str