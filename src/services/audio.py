import base64
import os
# from ..core.mongodb import setup_mongodb

# client = OpenAI()
# Obtain your API key from elevenlabs.ai
# Using .env file to store API key
from dotenv import load_dotenv

# import simpleaudio as sa
from elevenlabs import generate, set_api_key

load_dotenv('.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
assert ELEVENLABS_API_KEY is not None
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
assert ELEVENLABS_VOICE_ID is not None
set_api_key(ELEVENLABS_API_KEY)

# mongodb = setup_mongodb()
# def encode_image(image_path):
#     while True:
#         try:
#             with open(image_path, "rb") as image_file:
#                 return base64.b64encode(image_file.read()).decode("utf-8")
#         except IOError as e:
#             if e.errno != errno.EACCES:
#                 # Not a "file in use" error, re-raise
#                 raise
#             # File is being written to, wait a bit and retry
#             time.sleep(0.1)


def obtain_audio(text: str) -> tuple[str, str]:
    audio = generate(text, voice=ELEVENLABS_VOICE_ID)

    audio_id = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8').rstrip('=')
    dir_path = os.path.join('data', 'narration', audio_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, 'audio.wav')
    # this writes audio to storage already, no need for below
    with open(file_path, 'wb') as f:
        f.write(audio)  # type: ignore

    return audio_id, file_path
    # play(audio)


# async def store_audio(audio_id: str, audio_path: str):
#     # TODO: store this on S3 rather than in mongodb.
#     dir_path = os.path.join('data', 'visuals', 'static', 'img')
#     with open(audio_path, 'rb') as audio_file:
#         encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
#         # save to local file for debugging
#         with open('./data/audio.txt', 'w') as f:
#             f.write(encoded_string)
        # collection = mongodb.get_collection('audio')
        # await collection.insert_one({'audio_id': audio_id, 'audio_data': encoded_string})


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
