from sqlmodel import Relationship, SQLModel as Model, Field
from typing import Optional


class CharacterBase(Model):
    character_id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Relationship(back_populates='user.username')
    story_id: Optional[int] = Field(default=None, foreign_key="story.story_id")
    character_name: Optional[str] = Field(nullable=True, default=None)
    description: Optional[str] = Field(nullable=True, default=None)
    portrait_path: Optional[str] = Field(default=None)
    strength: Optional[int] = Field(default=3)
    dexterity: Optional[int] = Field(default=3)
    constitution: Optional[int] = Field(default=3)
    intelligence: Optional[int] = Field(default=3)
    wisdom: Optional[int] = Field(default=3)
    charisma: Optional[int] = Field(default=3)
    location: Optional[str] = Field(default='The town of Hearth')
    goal: Optional[str] = Field(default='Find a quest to embark on and a party to join')

class CharacterCreateMessage(Model):
    message: str

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
    character_id: Optional[int] = Field(primary_key=True)
    # Other fields for Character
    # Optional: Establish a back-reference to Story
    # story: "Story" = Relationship(back_populates="character")