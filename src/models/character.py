from sqlmodel import Relationship, SQLModel as Model, Field
from typing import Optional
from enum import Enum

class CharacterType(str, Enum):
    PC = "PC"
    NARRATOR = "NARRATOR"
    SYSTEM = "SYSTEM"

class CharacterBase(Model):
    character_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")
    character_name: Optional[str] = Field(default="Adventurer")
    character_race: Optional[str] = Field(default=None)
    character_class: Optional[str] = Field(default=None)
    description: Optional[str] = Field(nullable=True, default=None)
    portrait_path: Optional[str] = Field(default=None)
    stat_str: Optional[int] = Field(default=10)
    stat_dex: Optional[int] = Field(default=10)
    stat_con: Optional[int] = Field(default=10)
    stat_int: Optional[int] = Field(default=10)
    stat_wis: Optional[int] = Field(default=10)
    stat_cha: Optional[int] = Field(default=10)

class CharacterCreateMessage(Model):
    message: str

    text_model: str | None = None
    image_model: str | None = None

class CharacterCreate(CharacterBase):
    pass


class CharacterRead(CharacterBase):
    character_id: int


class CharacterUpdate(Model):
    character_name: Optional[str]
    character_race: Optional[str]
    character_class: Optional[str]
    description: Optional[str]
    stat_str: Optional[int]
    stat_dex: Optional[int]
    stat_con: Optional[int]
    stat_int: Optional[int]
    stat_wis: Optional[int]
    stat_cha: Optional[int]

class CharacterDetails(Model):
    character_id: int
    character_name: str
    portrait_path: str


class Character(CharacterBase, table=True):  # type: ignore
    # Other fields for Character
    # Optional: Establish a back-reference to Story
    # story: "Story" = Relationship(back_populates="character")
    pass