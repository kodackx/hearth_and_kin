import base64
import os
from typing import Iterator, Optional
import elevenlabs
from ..core.config import ELEVENLABS_VOICE_ID

def generate(text: str) -> bytes | Iterator[bytes]:
    audio = elevenlabs.generate(text, voice=ELEVENLABS_VOICE_ID, model="eleven_turbo_v2")
    return audio

def store(audio_bytes: bytes | Iterator[bytes], filename: Optional[str] = None) -> tuple[str, str]:
    if not filename:
        filename = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    dir_path = os.path.join('data', 'narration')
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f'{filename}.wav')
    with open(file_path, 'wb') as f:
        f.write(audio_bytes)  # type: ignore
    print(f"[GEN AUDIO] Audio file saved at: {file_path}")

    return filename, file_path


async def generate_audio(narrator_reply) -> str:
    audio_data = generate(narrator_reply)
    _, audio_path = store(audio_bytes=audio_data)
    return audio_path