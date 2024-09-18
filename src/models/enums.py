from enum import StrEnum, auto

class CharacterType(StrEnum):
    player = auto()
    narrator = auto()
    system = auto()

class TextModel(StrEnum):
    nvidia_llama = auto()
    gpt = auto()
    claude = auto()
    groq = auto()
    gpt4o = auto()
    gpto1 = auto()

class AudioModel(StrEnum):
    elevenlabs = auto()
    none = auto()

class ImageModel(StrEnum):
    dalle3 = auto()
    stablediffusion = auto()
    none = auto()