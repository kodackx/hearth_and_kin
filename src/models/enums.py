from enum import StrEnum, auto

class CharacterType(StrEnum):
    player = auto()
    narrator = auto()
    system = auto()

class TextModel(StrEnum):
    # better to use snapshot models due to cost and speed
    nvidia = auto()
    gpt = "gpt-4o-mini-2024-07-18"
    claude = "claude-3-5-sonnet-20240620"
    groq = "llama-3.1-70b-versatile"
    gpt4o = "gpt-4o-2024-08-06"
    gpto1 = "o1-preview-2024-09-12"

class AudioModel(StrEnum):
    elevenlabs = auto()
    none = auto()

class ImageModel(StrEnum):
    dalle3 = auto()
    stablediffusion = auto()
    none = auto()