import os
import base64
import json
import time
# import simpleaudio as sa
import errno
from elevenlabs import generate, play, set_api_key, voices
import base64

# client = OpenAI()

# Obtain your API key from elevenlabs.ai
# Using .env file to store API key
from dotenv import load_dotenv
load_dotenv('.env')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
set_api_key(os.environ.get("ELEVENLABS_API_KEY"))
# also read elevenlabs voice id from .env file
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')

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


def obtain_audio(text):
    audio = generate(text, voice=os.environ.get("ELEVENLABS_VOICE_ID"))

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    return file_path
    # play(audio)
    
def send_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        # save to local file for debugging
        with open('audio.txt', 'w') as f:
            f.write(encoded_string)
        
    return encoded_string


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
