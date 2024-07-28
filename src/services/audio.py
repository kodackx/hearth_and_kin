import base64
import os
from typing import Iterator, Optional
import elevenlabs
from ..core.config import ELEVENLABS_VOICE_ID, logger
from dotenv import load_dotenv

# Load environment variables from a .env file
# load_dotenv()

def generate(text: str) -> bytes | Iterator[bytes]:
    #ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
    # logger.debug("Will use voiceID " + ELEVENLABS_VOICE_ID)
    audio = elevenlabs.generate(text, voice=ELEVENLABS_VOICE_ID, model="eleven_turbo_v2_5")
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


async def generate_audio(narrator_reply) -> str:
    audio_data = generate(narrator_reply)
    _, audio_path = store(audio_bytes=audio_data)
    return audio_path