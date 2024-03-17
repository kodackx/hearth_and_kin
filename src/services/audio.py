import base64
import os
from dotenv import load_dotenv
import httpx
# from elevenlabs.client import AsyncElevenLabs
# from elevenlabs.client import ElevenLabs
# from elevenlabs import Voice, VoiceSettings, play
from elevenlabs import generate, set_api_key

load_dotenv('.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
assert ELEVENLABS_API_KEY is not None
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
assert ELEVENLABS_VOICE_ID is not None
set_api_key(ELEVENLABS_API_KEY)


async def obtain_audio(text: str) -> tuple[str, str]:
    # client = ElevenLabs(
    #     api_key=ELEVENLABS_API_KEY, # Defaults to ELEVEN_API_KEY
    # )

    # try to print a list of voices
    # response = client.voices.get_all()
    # print("Available voices.")
    # print(response)

    # alternatively, define a voice object with the ID and configs
    # custom_voice=Voice(
    #     voice_id='KloheXbZgyIqBs7HYCCD', # paddington voice
    #     settings=VoiceSettings(stability=0.45, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
    # )

    # this should use the turbo model for super fast inference
    # not sure if regular voice lab IDs still work with turbo though
    # audio = client.generate(
    #     text=text,
    #     voice="Callum",
    #     # voice=custom_voice,
    #     model="eleven_multilingual_v2"
    # )


    # back to legacy code
    audio = generate(text, voice="Callum", model='eleven_monolingual_v1')
    audio_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    dir_path = os.path.join('data', 'narration', audio_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, 'audio.wav')
    print(f"[GEN AUDIO] Audio file saved at: {file_path}")
    # this writes audio to storage already, no need for below
    with open(file_path, 'wb') as f:
        f.write(audio)  # type: ignore

    return audio_id, file_path
    # play(audio)