import os
from sqlmodel import SQLModel as Model, Field
from typing import Optional


class UserBase(Model):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(min_length=1, max_length=50, index=True)
    password: str = Field(min_length=1)
    openai_api_key: str | None =Field(default=os.getenv('OPENAI_API_KEY'))
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    elevenlabs_api_key: str | None = Field(default=os.getenv('ELEVENLABS_API_KEY'))
    elevenlabs_voice_id: str | None = Field(default=os.getenv('ELEVENLABS_VOICE_ID'))

class UserUpdate(Model):
    user_id: int = Field(primary_key=True)
    username: str | None = Field(default=None, min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=1)
    openai_api_key: str | None = Field(default=os.getenv('OPENAI_API_KEY'))
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    elevenlabs_api_key: str | None = Field(default=os.getenv('ELEVENLABS_API_KEY'))
    elevenlabs_voice_id: str | None = Field(default=os.getenv('ELEVENLABS_VOICE_ID'))


class UserRead(UserBase):
    username: str = Field(min_length=1, max_length=50, primary_key=True)


class User(UserBase, table=True):  # type: ignore
    pass
