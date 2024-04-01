import base64
import os
from typing import Iterator

# client = OpenAI()
# Obtain your API key from elevenlabs.ai
# Using .env file to store API key
from dotenv import load_dotenv

# import simpleaudio as sa
import elevenlabs
from ..core import azure

load_dotenv('.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
assert ELEVENLABS_VOICE_ID is not None
elevenlabs.set_api_key(ELEVENLABS_API_KEY)

def generate(text: str) -> bytes | Iterator[bytes]:
    audio = elevenlabs.generate(text, voice=ELEVENLABS_VOICE_ID)

    return audio

def store(audio_bytes: bytes | Iterator[bytes]) -> tuple[str, str]:
    audio_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    
    audio_url = azure.store_public(remote_path=f'audio/{audio_id}.mp3', file=audio_bytes)

    return audio_id, audio_url

# def generate_new_line(base64_image):
#     return [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "Describe this image"},
#                 {
#                     "type": "image_url",
#                     "image_url": f"data:image/jpeg;base64,{base64_image}",
#                 },
#             ],
#         },
#     ]


# def analyze_image(base64_image, script):
#     response = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         messages=[
#             {
#                 "role": "system",
#                 "content": """
#                 You are Sir David Attenborough. Narrate the picture of the human as if it is a nature documentary.
#                 Make it snarky and funny. Don't repeat yourself. Make it short. If I do anything remotely interesting, make a big deal about it!
#                 """,
#             },
#         ]
#         + script
#         + generate_new_line(base64_image),
#         max_tokens=500,
#     )
#     response_text = response.choices[0].message.content
#     return response_text


# def obtain_voice():
#     script = []

#     while True:
# path to your image
# image_path = os.path.join(os.getcwd(), "./frames/frame.jpg")

# # getting the base64 encoding
# base64_image = encode_image(image_path)

# # analyze posture
# print("👀 David is watching...")
# analysis = analyze_image(base64_image, script=script)

# print("🎙️ David says:")
# print(analysis)

# play_audio(analysis)

# script = script + [{"role": "assistant", "content": analysis}]

# wait for 5 seconds
# time.sleep(5)


# if __name__ == "__main__":
#     main()
