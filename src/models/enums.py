from enum import StrEnum, auto

class CharacterType(StrEnum):
    PC = auto()
    NARRATOR = auto()
    SYSTEM = auto()

class TextModel(StrEnum):
    nvidia = auto()
    gpt = auto()
    none = auto()

class AudioModel(StrEnum):
    elevenlabs = auto()
    none = auto()

class ImageModel(StrEnum):
    dalle3 = auto()
    none = auto()