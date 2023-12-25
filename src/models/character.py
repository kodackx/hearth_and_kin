from sqlmodel import SQLModel as Model, Field
from typing import Optional


class CharacterBase(Model):
    # user_id: int = Relationship(back_populates='user.user_id')
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


class Character(CharacterBase, table=True):
    character_id: Optional[int] = Field(default=None, primary_key=True)
