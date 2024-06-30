import logging
import os
from elevenlabs import set_api_key
from dotenv import load_dotenv
DEBUG = True
GENERATE_IMAGE = True
GENERATE_AUDIO = True
GENERATE_REPLY = True
DEFAULT_TEXT_NARRATOR_MODEL = 'nvidia'
DEFAULT_AUDIO_NARRATOR_MODEL = 'elevenlabs'
DEFAULT_IMAGE_MODEL = 'dalle3'
SENTENCES_PER_SUBTITLE = 2
logger = logging.getLogger(__name__)

load_dotenv()
if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
assert OPENAI_API_KEY is not None, 'Add OPENAI_API_KEY to .env file'
assert ELEVENLABS_API_KEY is not None, 'Add ELEVENLABS_API_KEY to .env file'
assert ELEVENLABS_VOICE_ID is not None, 'Add ELEVENLABS_VOICE_ID to .env file'
set_api_key(ELEVENLABS_API_KEY)
