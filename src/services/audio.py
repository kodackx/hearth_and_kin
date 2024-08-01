import base64
import os
from typing import Iterator, Optional

from ..core.models import AudioModel, ElevenLabsModel, get_model_instance
from ..core.config import logger


def generate(model: AudioModel, text: str, api_key: str | dict[str, str]) -> bytes | Iterator[bytes]:
    model_instance = get_model_instance(model, api_key)
    assert isinstance(api_key, dict), 'API key must be a dictionary'
    if type(model_instance) is ElevenLabsModel:
        audio = model_instance.model.generate(text=text, voice=api_key['elevenlabs_voice_id'], model=model_instance.model_name)
    return audio

def store(audio_bytes: bytes | Iterator[bytes], filename: Optional[str] = None) -> tuple[str, str]:
    if not filename:
        filename = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    dir_path = os.path.join('data', 'narration')
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f'{filename}.wav')
    with open(file_path, 'wb') as f:
        f.write(audio_bytes)  # type: ignore
    logger.info(f"[GEN AUDIO] Audio file saved at: {file_path}")

    return filename, file_path


async def generate_audio(model: AudioModel, narrator_reply: str, api_key: str | dict[str, str]) -> str:
    audio_data = generate(model, text=narrator_reply, api_key=api_key)
    _, audio_path = store(audio_bytes=audio_data)
    return audio_path