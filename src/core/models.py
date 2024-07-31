from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from elevenlabs.client import ElevenLabs
import httpx
from enum import StrEnum, auto

class CharacterType(StrEnum):
    player = auto()
    narrator = auto()
    system = auto()

class TextModel(StrEnum):
    nvidia = auto()
    gpt = auto()

class AudioModel(StrEnum):
    elevenlabs = auto()
    none = auto()

class ImageModel(StrEnum):
    dalle3 = auto()
    none = auto()

type ModelType = TextModel | ImageModel | AudioModel


class GPTModel:
    def __init__(self, api_key: str, temperature: float = 0.75, **kwargs):
        self.api_key = api_key
        self.temperature = temperature
        self.model_name = 'gpt-4o'
        self.model = ChatOpenAI(model=self.model_name, temperature=self.temperature, api_key=self.api_key, **kwargs)
        self.model_type = TextModel.gpt

    def validate(self):
        r = httpx.get(
            f'https://api.openai.com/v1/models/{self.model_name}', headers={'Authorization': f'Bearer {self.api_key}'}
        )
        assert r.status_code == 200, r.text


class ElevenLabsModel:
    def __init__(self, api_key: str, voice_id: str | None = None, **kwargs):
        self.api_key = api_key
        self.model_name = 'eleven_turbo_v2'
        self.voice_id = voice_id
        self.model = ElevenLabs(api_key=api_key, **kwargs)
        self.model_type = AudioModel.elevenlabs

    def validate(self):
        r = httpx.get('https://api.elevenlabs.io/v1/voices', headers={'xi-api-key': self.api_key})
        assert r.status_code == 200, r.text


class Dalle3Model:
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.model_name = 'dall-e-3'
        self.model = DallEAPIWrapper(client=None, model=self.model_name, size='1024x1024', api_key=api_key, **kwargs)
        self.model_type = ImageModel.dalle3

    def validate(self):
        r = httpx.get(
            f'https://api.openai.com/v1/models/{self.model_name}', headers={'Authorization': f'Bearer {self.api_key}'}
        )
        assert r.status_code == 200, r.text


class LlamaNvidiaModel:
    def __init__(self, api_key: str, temperature: float = 0.75, **kwargs):
        self.api_key = api_key
        self.temperature = temperature or 0.75
        self.model_name = 'meta/llama-3.1-8b-instruct'
        self.model = ChatNVIDIA(model_name=self.model_name, temperature=self.temperature, api_key=api_key, **kwargs)
        self.model_type = TextModel.nvidia

    def validate(self):
        r = httpx.post(
            'https://integrate.api.nvidia.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'model': self.model_name},
        )
        assert (
            r.status_code == 400
        ), r.text  # 400 is the expected status code, as the json is invalid. Returns 401 if the API key is invalid.


type TextModelInstance = ChatOpenAI | ChatNVIDIA
type ImageModelInstance = DallEAPIWrapper
type AudioModelInstance = ElevenLabs
type ModelInstance = GPTModel | LlamaNvidiaModel | Dalle3Model | ElevenLabsModel
#type ModelInstance = TextModelInstance | ImageModelInstance | AudioModelInstance


def get_model_instance(
    model: ModelType | str, api_key: str, validate: bool = False, temperature: float = 0.75, **kwargs
) -> ModelInstance | None:
    match model:
        case TextModel.gpt:
            selected_model = GPTModel(api_key, temperature, **kwargs)
        case TextModel.nvidia:
            selected_model = LlamaNvidiaModel(api_key, temperature, **kwargs)
        case ImageModel.dalle3:
            selected_model = Dalle3Model(api_key, **kwargs)
        case AudioModel.elevenlabs:
            selected_model = ElevenLabsModel(api_key, **kwargs)
        case ImageModel.none | AudioModel.none:
            return None
        case _:
            raise NotImplementedError(f'Invalid model: {model}')
    if validate:
        selected_model.validate()
    return selected_model
