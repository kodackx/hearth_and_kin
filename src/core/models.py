import os
from abc import ABC, abstractmethod
from fastapi import HTTPException
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from elevenlabs.client import ElevenLabs
import httpx
from enum import StrEnum, auto
import logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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


class BaseModel(ABC):
    def __init__(
        self, model_name: str, model_type: ModelType, api_key_name: str, api_key: str | dict[str, str], **kwargs
    ):
        self.api_key_name = api_key_name
        self.api_key = self._extract_api_key(api_key)
        self.kwargs = kwargs
        self.model_name = model_name
        self.model_type = model_type

    def _extract_api_key(self, api_key: str | dict[str, str]) -> str:
        """Extracts the API key from the request. If the API key is a dictionary of several keys, it will extract the key based on the api_key_name."""
        if isinstance(api_key, dict):
            try:
                api_key = api_key[self.api_key_name]
            except KeyError:
                raise HTTPException(401, f'You need to add a {self.api_key_name} API key to use the model.')
        if api_key is None:
            raise HTTPException(401, f'You need to add a {self.api_key_name} API key to use the model.')
        return api_key

    @abstractmethod
    def validate(self):
        pass


class GPTModel(BaseModel):
    def __init__(self, api_key: str | dict[str, str], temperature: float = 0.75, **kwargs):
        super().__init__(
            'gpt-4o',  # model_name
            TextModel.gpt,  # model_type
            'openai_api_key',  # api_key_name
            api_key,
            **kwargs,
        )
        self.temperature = temperature
        self.model = ChatOpenAI(model=self.model_name, temperature=self.temperature, api_key=self.api_key, **kwargs)

    def validate(self):
        #if not TEST_ENV:
        r = httpx.get(
            f'https://api.openai.com/v1/models/{self.model_name}',
            headers={'Authorization': f'Bearer {self.api_key}'},
        )
        if r.status_code != 200:
            raise HTTPException(
                401,
                'Invalid OpenAI API key. Error from OpenAI: '
                + r.json().get('error', {}).get('message', 'Unknown error'),
            )


class ElevenLabsModel(BaseModel):
    def __init__(self, api_key: str | dict[str, str], voice_id: str | None = None, **kwargs):
        super().__init__(
            'eleven_turbo_v2',  # model_name
            AudioModel.elevenlabs,  # model_type
            'elevenlabs_api_key',  # api_key_name
            api_key,
            **kwargs,
        )
        self.voice_id = voice_id
        self.model = ElevenLabs(api_key=self.api_key, **kwargs)

    def validate(self):
        #if not TEST_ENV:
        r = httpx.get('https://api.elevenlabs.io/v1/voices', headers={'xi-api-key': self.api_key})
        if r.status_code != 200:
            raise HTTPException(401, 'Invalid Elevenlabs API key. Error from OpenAI: ' + r.text)


class Dalle3Model(BaseModel):
    def __init__(self, api_key: str | dict[str, str], **kwargs):
        super().__init__(
            'dall-e-3',  # model_name
            ImageModel.dalle3,  # model_type
            'openai_api_key',  # api_key_name
            api_key,
            **kwargs,
        )
        self.model = DallEAPIWrapper(
            client=None, model=self.model_name, size='1024x1024', api_key=self.api_key, **kwargs
        )

    def validate(self):
        #if not TEST_ENV:
        r = httpx.get(
            f'https://api.openai.com/v1/models/{self.model_name}',
            headers={'Authorization': f'Bearer {self.api_key}'},
        )
        if r.status_code != 200:
            raise HTTPException(401, 'Invalid OpenAI API key. Error from OpenAI: ' + r.text)


class LlamaNvidiaModel(BaseModel):
    def __init__(self, api_key: str | dict[str, str], temperature: float = 0.75, **kwargs):
        super().__init__(
            'meta/llama-3.1-8b-instruct',  # model_name
            TextModel.nvidia,  # model_type
            'nvidia_api_key',  # api_key_name
            api_key,
            **kwargs,
        )
        self.temperature = temperature or 0.75
        self.model = ChatNVIDIA(
            model_name=self.model_name, temperature=self.temperature, api_key=self.api_key, **kwargs
        )

    def validate(self):
        #if not TEST_ENV:
        r = httpx.post(
            'https://integrate.api.nvidia.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'model': self.model_name},
        )
        
        # 400 is the expected status code, as the json is invalid. Returns 401 if the API key is invalid.
        if r.status_code != 400:  
            raise HTTPException(401, 'Invalid NVIDIA API key. Error from NVIDIA: ' + r.text)


type TextModelInstance = ChatOpenAI | ChatNVIDIA
type ImageModelInstance = DallEAPIWrapper
type AudioModelInstance = ElevenLabs
type ModelInstance = GPTModel | LlamaNvidiaModel | Dalle3Model | ElevenLabsModel


def get_model_instance(
    model: ModelType | str, api_key: str | dict[str, str], validate: bool = False, temperature: float = 0.75, **kwargs
) -> ModelInstance | None:
    """Returns an instance of the model based on the model type."""
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
