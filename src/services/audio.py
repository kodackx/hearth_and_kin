import base64
import os

# client = OpenAI()
# Obtain your API key from elevenlabs.ai
# Using .env file to store API key
from dotenv import load_dotenv

# import simpleaudio as sa
from elevenlabs import generate, set_api_key

load_dotenv('.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
set_api_key(ELEVENLABS_API_KEY)


def obtain_audio(text: str) -> tuple[str, str]:
    audio = generate(text, voice=ELEVENLABS_VOICE_ID)

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
