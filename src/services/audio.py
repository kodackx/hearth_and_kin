import base64
import os
from typing import Iterator, Optional
import elevenlabs
from ..core.config import logger


def generate(text: str, api_key: str, voice_id: str) -> bytes | Iterator[bytes]:
    audio = elevenlabs.generate(text, api_key=api_key, voice=voice_id, model="eleven_turbo_v2")
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


async def generate_audio(narrator_reply: str, api_key: str, voice_id: str) -> str:
    audio_data = generate(text=narrator_reply, api_key=api_key, voice_id=voice_id)
    _, audio_path = store(audio_bytes=audio_data)
    return audio_path