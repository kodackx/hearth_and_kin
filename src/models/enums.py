from enum import Enum

class CharacterType(str, Enum):
    PC = "PC"
    NARRATOR = "NARRATOR"
    SYSTEM = "SYSTEM"

class TextModel(str, Enum):
    nvidia = "nvidia"
    gpt = "gpt"
    none = "none"

class AudioModel(str, Enum):
    elevenlabs = "elevenlabs"
    none = "none"

class ImageModel(str, Enum):
    dalle3 = "dalle3"
    none = "none"