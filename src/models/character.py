from sqlmodel import Relationship, SQLModel as Model, Field
from typing import Optional


class CharacterBase(Model):
    username: str = Relationship(back_populates='user.username')
    story_id: Optional[int] = Field(default=None)
    user_description: Optional[str] = Field(nullable=True, default=None)
    description: Optional[str] = Field(nullable=True, default=None)
    strength: Optional[int] = Field(default=3)
    dexterity: Optional[int] = Field(default=3)
    con: Optional[int] = Field(default=3)
    intelligence: Optional[int] = Field(default=3)
    wisdom: Optional[int] = Field(default=3)
    charisma: Optional[int] = Field(default=3)
    location: Optional[str] = Field(default='The town of Hearth')
    goal: Optional[str] = Field(default='Find a quest to embark on and a party to join')


class CharacterCreate(CharacterBase):
    pass


class CharacterRead(CharacterBase):
    character_id: int


class CharacterUpdate(Model):
    username: str = Relationship(back_populates='user.username')
    story_id: Optional[int] = None
    user_description: Optional[str] = None
    description: Optional[str] = None
    strength: Optional[int] = None
    dexterity: Optional[int] = None
    con: Optional[int] = None
    intelligence: Optional[int] = None
    wisdom: Optional[int] = None
    charisma: Optional[int] = None
    location: Optional[str] = None
    goal: Optional[str] = None


class Character(CharacterBase, table=True):  # type: ignore
    character_id: Optional[int] = Field(default=None, primary_key=True)
